"""
Laboratorio de búsqueda semántica. Tema: mascotas.

Modos:
    python main.py prueba      Consultas del enunciado, semántico vs. léxico.
    python main.py ambiguas    Consultas con palabras puente, con blindaje.
    python main.py palabras    Consultas de una sola palabra (sonda léxica).
    python main.py ataque      Mide nuestras 5 oraciones contra un corpus
                               proxy de mecánica automotriz.
    python main.py defensa     Inyecta las oraciones recibidas en el corpus
                               propio y revisa si se cuelan en el top-k.
    python main.py consulta    Usa las oraciones recibidas como consultas
                               contra el corpus limpio, sin indexarlas.
"""

import sys

from busqueda import (
    MARGEN_MINIMO,
    PREFIJO_DOMINIO,
    TOP_K,
    UMBRAL_SIMILITUD,
    buscar_lexico,
    buscar_semantico,
    cargar_modelo,
    evaluar_blindaje,
    obtener_embeddings,
)
from corpus import (
    CONSULTAS_AMBIGUAS,
    CONSULTAS_MECANICA,
    CONSULTAS_PRUEBA,
    CONSULTAS_UNA_PALABRA,
    CORPUS_MASCOTAS,
    CORPUS_MECANICA_PROXY,
    ORACIONES_ATAQUE_ENTREGADAS,
    ORACIONES_ATAQUE_RECIBIDAS,
    ORACIONES_ATAQUE_SIMULADAS,
)


def imprimir_ranking(titulo, resultados, formato):
    print(f"{titulo}")

    if not resultados:
        print("\t(sin resultados)")
        return

    for resultado in resultados:
        print(f"\t{formato(resultado['puntaje'])}  {resultado['documento']}")


def comparar(modelo, embeddings, corpus, consultas):
    """
    Corre las mismas consultas por los dos caminos y marca dónde se separan
    """
    coincidencias = 0

    for consulta in consultas:
        semanticos = buscar_semantico(modelo, embeddings, corpus, consulta, TOP_K)
        lexicos = buscar_lexico(corpus, consulta, TOP_K)

        print(f"\nConsulta: {consulta}")
        imprimir_ranking("Semántico", semanticos, lambda p: f"{p:.4f}")
        imprimir_ranking("Léxico", lexicos, lambda p: f"{p:>6}")

        if not lexicos:
            print("\tSe separan: el léxico no recuperó nada.")
        elif semanticos[0]["indice"] == lexicos[0]["indice"]:
            print("\tCoinciden en el top-1.")
            coincidencias += 1
        else:
            print("\tSe separan en el top-1.")

    print(f"\nTop-1 coincidente en {coincidencias}/{len(consultas)} consultas.")


def con_blindaje(modelo, embeddings, corpus, consultas):
    """
    Muestra qué decide el blindaje sobre cada consulta
    """
    print(f"Umbral: {UMBRAL_SIMILITUD} | Margen mínimo: {MARGEN_MINIMO}")

    for consulta in consultas:
        semanticos = buscar_semantico(modelo, embeddings, corpus, consulta, TOP_K)
        lexicos = buscar_lexico(corpus, consulta, TOP_K)
        veredicto = evaluar_blindaje(semanticos, lexicos)

        print(f"\nConsulta: {consulta}")
        imprimir_ranking("Semántico", semanticos, lambda p: f"{p:.4f}")

        estado = veredicto["estado"].upper()
        motivo = f"\t({veredicto['motivo']})" if veredicto["motivo"] else ""
        print(f"\tBlindaje: {estado}{motivo}")

        if veredicto["estado"] == "aceptado":
            print(f"\tRespuesta: {veredicto['candidato']['documento']}")


def modo_ataque(modelo):
    """
    Inyecta nuestras 5 oraciones en el corpus proxy de mecánica automotriz y
    revisa si aparecen en el top-k de consultas mecánicas legítimas.

    El corpus proxy es una reconstrucción nuestra, no el corpus real del otro
    equipo: los resultados indican por dónde entra cada oración, no garantizan
    el resultado final.
    """
    corpus = CORPUS_MECANICA_PROXY + ORACIONES_ATAQUE_ENTREGADAS
    inicio_intrusos = len(CORPUS_MECANICA_PROXY)

    embeddings = obtener_embeddings(modelo, corpus)

    print("\nCorpus proxy de mecánica automotriz "
          f"({len(CORPUS_MECANICA_PROXY)} oraciones) "
          f"+ {len(ORACIONES_ATAQUE_ENTREGADAS)} oraciones nuestras.")

    infiltradas = {}
    consultas_alcanzadas = 0

    for consulta in CONSULTAS_MECANICA:
        semanticos = buscar_semantico(modelo, embeddings, corpus, consulta, TOP_K)
        lexicos = buscar_lexico(corpus, consulta, TOP_K)

        print(f"\nConsulta mecánica: {consulta}")

        for posicion, resultado in enumerate(semanticos, start=1):
            marca = "  <-- NUESTRA" if resultado["indice"] >= inicio_intrusos else ""
            print(f"\t{posicion}. {resultado['puntaje']:.4f}  "
                  f"{resultado['documento']}{marca}")

            if resultado["indice"] >= inicio_intrusos:
                registro = infiltradas.setdefault(resultado["indice"], [])
                registro.append((consulta, posicion, resultado["puntaje"]))

        golpe_lexico = [
            r for r in lexicos if r["indice"] >= inicio_intrusos
        ]

        if golpe_lexico:
            print(f"\tTambién entra por léxico: {golpe_lexico[0]['documento']}")

        if any(r["indice"] >= inicio_intrusos for r in semanticos):
            consultas_alcanzadas += 1

    print("\n" + "=" * 70)
    print("Resumen del ataque")
    print("=" * 70)
    print(f"Consultas mecánicas penetradas: "
          f"{consultas_alcanzadas}/{len(CONSULTAS_MECANICA)}")

    for i, oracion in enumerate(ORACIONES_ATAQUE_ENTREGADAS):
        indice = inicio_intrusos + i
        apariciones = infiltradas.get(indice, [])

        print(f"\n{i + 1}. {oracion}")

        if not apariciones:
            print("\tNo entró en ningún top-5.")
            continue

        mejor = min(apariciones, key=lambda a: a[1])
        print(f"\tEntró en {len(apariciones)} consulta(s). "
              f"Mejor posición: {mejor[1]} ({mejor[2]:.4f}) en \"{mejor[0]}\"")

    ataque_como_consulta(modelo)


def ataque_como_consulta(modelo):
    """
    Segunda lectura del ataque: nuestras 5 oraciones usadas como CONSULTA
    contra el corpus de mecánica, sin inyectarlas.

    Si el otro equipo las corre como consulta en vez de indexarlas, el ataque
    funciona cuando su buscador responde con confianza a una oración que en
    realidad es de mascotas.
    """
    embeddings = obtener_embeddings(modelo, CORPUS_MECANICA_PROXY, verbose=False)

    print("\n" + "=" * 70)
    print("Las 5 oraciones usadas como consulta contra el corpus de mecánica")
    print("=" * 70)

    responderian = 0
    pasarian_blindaje = 0

    for oracion in ORACIONES_ATAQUE_ENTREGADAS:
        semanticos = buscar_semantico(
            modelo, embeddings, CORPUS_MECANICA_PROXY, oracion, TOP_K
        )
        lexicos = buscar_lexico(CORPUS_MECANICA_PROXY, oracion, TOP_K)
        veredicto = evaluar_blindaje(semanticos, lexicos)

        mejor = semanticos[0]

        print(f"\n{oracion}")
        print(f"\t{mejor['puntaje']:.4f}  {mejor['documento']}")
        print(f"\tSin blindaje respondería: "
              f"{'sí' if mejor['puntaje'] >= UMBRAL_SIMILITUD else 'no'}")
        print(f"\tCon blindaje: {veredicto['estado'].upper()}")

        if mejor["puntaje"] >= UMBRAL_SIMILITUD:
            responderian += 1

        if veredicto["estado"] == "aceptado":
            pasarian_blindaje += 1

    total = len(ORACIONES_ATAQUE_ENTREGADAS)
    print(f"\nSuperan el umbral: {responderian}/{total}")
    print(f"Pasarían un blindaje completo: {pasarian_blindaje}/{total}")


def obtener_recibidas():
    """
    Devuelve las oraciones del otro equipo, o las simuladas si aún no llegan.
    """
    if ORACIONES_ATAQUE_RECIBIDAS:
        return ORACIONES_ATAQUE_RECIBIDAS, False

    print("ORACIONES_ATAQUE_RECIBIDAS está vacía: se usan las simuladas.")
    print("Pegá las oraciones reales en corpus.py cuando lleguen.\n")

    return ORACIONES_ATAQUE_SIMULADAS, True


def modo_consulta(modelo):
    """
    Usa las oraciones recibidas como CONSULTAS contra el corpus propio limpio.

    Es la lectura alternativa del ejercicio: en vez de preguntar si el intruso
    contamina el índice, pregunta si el buscador responde con confianza a algo
    que está fuera de su dominio. El corpus queda en 25 oraciones y las
    oraciones del otro equipo nunca se indexan, así que no hay forma de que se
    recuperen a sí mismas.
    """
    recibidas, simuladas = obtener_recibidas()

    embeddings = obtener_embeddings(modelo, CORPUS_MASCOTAS)

    print(f"\nCorpus propio limpio ({len(CORPUS_MASCOTAS)} oraciones). "
          f"Las {len(recibidas)} oraciones del otro equipo se usan como "
          "consulta, no se indexan.")
    print(f"Umbral: {UMBRAL_SIMILITUD} | Margen mínimo: {MARGEN_MINIMO}")

    respondidas = 0

    for consulta in recibidas:
        semanticos = buscar_semantico(
            modelo, embeddings, CORPUS_MASCOTAS, consulta, TOP_K
        )
        lexicos = buscar_lexico(CORPUS_MASCOTAS, consulta, TOP_K)
        veredicto = evaluar_blindaje(semanticos, lexicos)

        print(f"\nConsulta intrusa: {consulta}")
        imprimir_ranking("Semántico", semanticos, lambda p: f"{p:.4f}")
        imprimir_ranking("Léxico", lexicos, lambda p: f"{p:>6}")

        estado = veredicto["estado"].upper()
        motivo = f" ({veredicto['motivo']})" if veredicto["motivo"] else ""
        print(f"\tBlindaje: {estado}{motivo}")

        if veredicto["estado"] == "aceptado":
            respondidas += 1
            print(f"\tSe respondió: {veredicto['candidato']['documento']}")

    print("\n" + "=" * 70)
    print("Resumen: consultas fuera de dominio")
    print("=" * 70)
    print(f"Consultas intrusas evaluadas: {len(recibidas)}")
    print(f"Respondidas con confianza pese a ser de otro dominio: {respondidas}")
    print("Lo correcto es 0: una consulta de mecánica no debería obtener "
          "respuesta de un corpus de mascotas.")

    if simuladas:
        print("\nCorrida con oraciones simuladas.")


def modo_defensa(modelo):
    """
    Inyecta las oraciones recibidas en el corpus propio y revisa si se cuelan
    en el top-k de nuestras consultas, con y sin blindaje.

    Las oraciones intrusas se indexan pero NUNCA se usan como consulta: las
    consultas son las propias. Buscar una oración contra sí misma daría una
    similitud cercana a 1 y no probaría nada.
    """
    recibidas, simuladas = obtener_recibidas()

    corpus = CORPUS_MASCOTAS + recibidas
    inicio_intrusos = len(CORPUS_MASCOTAS)

    embeddings = obtener_embeddings(modelo, corpus)

    print(f"\nCorpus propio ({len(CORPUS_MASCOTAS)} oraciones) "
          f"+ {len(recibidas)} oraciones intrusas.")

    consultas = CONSULTAS_PRUEBA + CONSULTAS_AMBIGUAS

    colados_sin_blindaje = 0
    colados_con_blindaje = 0
    bloqueados_por_prefijo = 0

    for consulta in consultas:
        semanticos = buscar_semantico(modelo, embeddings, corpus, consulta, TOP_K)
        lexicos = buscar_lexico(corpus, consulta, TOP_K)
        veredicto = evaluar_blindaje(semanticos, lexicos)

        print(f"\nConsulta: {consulta}")

        for posicion, resultado in enumerate(semanticos, start=1):
            marca = "  <-- INTRUSO" if resultado["indice"] >= inicio_intrusos else ""
            print(f"\t{posicion}. {resultado['puntaje']:.4f}  "
                  f"{resultado['documento']}{marca}")

        intruso_en_top1 = semanticos[0]["indice"] >= inicio_intrusos

        if intruso_en_top1:
            colados_sin_blindaje += 1

        estado = veredicto["estado"].upper()
        motivo = f" ({veredicto['motivo']})" if veredicto["motivo"] else ""
        print(f"  Blindaje: {estado}{motivo}")

        if intruso_en_top1 and veredicto["estado"] == "aceptado":
            colados_con_blindaje += 1
            print(f"\tEl intruso pasó el blindaje.")

        if intruso_en_top1:
            con_prefijo = buscar_semantico(
                modelo, embeddings, corpus, consulta, TOP_K,
                prefijo=PREFIJO_DOMINIO
            )

            if con_prefijo[0]["indice"] < inicio_intrusos:
                bloqueados_por_prefijo += 1
                print(f"\tCon prefijo de dominio el top-1 vuelve a ser propio: "
                      f"{con_prefijo[0]['puntaje']:.4f} "
                      f"{con_prefijo[0]['documento']}")

    print("\n" + "=" * 70)
    print("Resumen de la defensa")
    print("=" * 70)
    print(f"Consultas evaluadas: {len(consultas)}")
    print(f"Intruso en top-1 sin blindaje: {colados_sin_blindaje}")
    print(f"Intruso entregado como respuesta con blindaje: {colados_con_blindaje}")
    print(f"Recuperadas por el prefijo de dominio: {bloqueados_por_prefijo}")

    if simuladas:
        print("\nCorrida con oraciones simuladas.")


MODOS = ("prueba", "ambiguas", "palabras", "ataque", "defensa", "consulta")


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "prueba"

    if modo not in MODOS:
        print(f"Modo desconocido: {modo}")
        print(__doc__)
        return

    print(f"Modo: {modo}")

    modelo = cargar_modelo()

    if modo == "ataque":
        modo_ataque(modelo)
        return

    if modo == "consulta":
        modo_consulta(modelo)
        return

    if modo == "defensa":
        modo_defensa(modelo)
        return

    embeddings = obtener_embeddings(modelo, CORPUS_MASCOTAS)

    if modo == "prueba":
        comparar(modelo, embeddings, CORPUS_MASCOTAS, CONSULTAS_PRUEBA)
    elif modo == "ambiguas":
        con_blindaje(modelo, embeddings, CORPUS_MASCOTAS, CONSULTAS_AMBIGUAS)
    elif modo == "palabras":
        comparar(modelo, embeddings, CORPUS_MASCOTAS, CONSULTAS_UNA_PALABRA)


if __name__ == "__main__":
    main()
