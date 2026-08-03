# Enunciado del laboratorio

Documento parcial del laboratorio de búsqueda semántica. Índice completo en el [README](../README.md).

Laboratorio en parejas de la semana 4 del curso de Procesamiento de Lenguaje Natural.

## Requisitos

| # | Requisito | Dónde está |
| --- | --- | --- |
| 1 | Mínimo 20 oraciones en español | `CORPUS_MASCOTAS` en `corpus.py` (25) |
| 2 | Mínimo 5 consultas de prueba | `CONSULTAS_PRUEBA` en `corpus.py` (6) |
| 3 | Generación de embeddings locales | `obtener_embeddings()` en `busqueda.py` |
| 4 | Ranking top-k por similitud del coseno | `buscar_semantico()` en `busqueda.py` |
| 5 | Búsqueda simple por palabras clave | `buscar_lexico()` en `busqueda.py` |
| 6 | Comparación cualitativa entre ambos métodos | [comparacion-cualitativa.md](comparacion-cualitativa.md) |

## Restricciones

- El corpus propio no pasa de 25 oraciones.
- El modelo es `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` y no se cambia.
- La búsqueda por palabras clave se implementa a mano: normalización, tokenización y conteo de coincidencias, sin TF-IDF ni librerías. Es el baseline contra el cual se mide el buscador semántico.

## Tema

Cada pareja eligió un tema distinto. El de este proyecto es **mascotas**.

## Componente adversarial

Además de los requisitos anteriores, el ejercicio tiene dos lados:

- **Ataque.** Entregar 5 oraciones legítimas del tema propio a otro equipo, buscando que su buscador las devuelva ante consultas de su dominio. El equipo objetivo de este proyecto es el de **mecánica automotriz**.
- **Defensa.** El buscador propio tiene que aguantar las oraciones que manden los demás.

La restricción es lo que hace valioso el ejercicio: las oraciones de ataque no pueden ser ruido ni basura, tienen que ser oraciones honestas del tema propio. La trampa está en el vocabulario, no en hacer trampa.

El desarrollo está en [analisis-adversarial.md](analisis-adversarial.md).

## Criterio adicional

Al elegir las consultas conviene que al menos una **no comparta ninguna palabra** con la oración que debería recuperar. Si el sistema igual la encuentra, la búsqueda semántica está funcionando; si solo acierta cuando las palabras coinciden, se está midiendo coincidencia literal disfrazada de semántica.

En este proyecto esa consulta es *"¿cuánto tiempo pasan dormidos los felinos?"*.
