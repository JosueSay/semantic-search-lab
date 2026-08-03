import hashlib
import os
import re
import string
import unicodedata

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 5

# Parámetros del blindaje
UMBRAL_SIMILITUD = 0.35
MARGEN_MINIMO = 0.05

# Prefijo se antepone a la consulta antes de encodearla para mover el vector fuera de la zona mecánica
PREFIJO_DOMINIO = "sobre mascotas: "

DIRECTORIO_EMBEDDINGS = "embeddings"

STOPWORDS = {
    "el", "la", "los", "las",
    "un", "una", "unos", "unas",
    "de", "del", "al",
    "y", "o",
    "que", "como", "cuanto", "cual", "cuales", "donde", "quien",
    "en", "por", "para",
    "con", "sin",
    "mi", "tu", "su",
    "es", "son", "esta", "estan", "ser", "hay",
    "se", "lo", "le", "me",
    "muy", "mas", "ya",
    "a",
}


def normalizar(texto):
    """
    Baja a minúsculas, quita acentos y elimina signos de puntuación
    """
    texto = texto.lower()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    texto = texto.translate(str.maketrans("", "", string.punctuation + "¿¡"))

    return re.sub(r"\s+", " ", texto).strip()


def tokenizar(texto):
    """
    Devuelve el conjunto de tokens de contenido del texto
    """
    return {
        token for token in normalizar(texto).split()
        if token and token not in STOPWORDS
    }


def _huella(corpus):
    """
    Huella del corpus, para invalidar la caché de embeddings cuando cambia.

    Sin esto, agregar oraciones al corpus deja los embeddings viejos en disco y
    los índices dejan de corresponder: el buscador devuelve documentos que no
    son los que produjeron esa similitud
    """
    contenido = "\n".join(corpus).encode("utf-8")

    return hashlib.sha256(contenido).hexdigest()[:12]


def cargar_modelo():
    """
    Carga el modelo de embeddings. Se descarga una vez y queda cacheado local
    """
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODELO)


def obtener_embeddings(modelo, corpus, verbose=True):
    """
    Calcula los embeddings del corpus una sola vez y los reusa.

    La caché está indexada por la huella del corpus, así que un corpus distinto
    (por ejemplo el corpus envenenado del modo defensa) genera su propio
    archivo en lugar de reutilizar el equivocado
    """
    os.makedirs(DIRECTORIO_EMBEDDINGS, exist_ok=True)

    ruta = os.path.join(
        DIRECTORIO_EMBEDDINGS,
        f"embeddings-{_huella(corpus)}.npy"
    )

    if os.path.exists(ruta):
        embeddings = np.load(ruta)
    else:
        embeddings = modelo.encode(corpus)
        np.save(ruta, embeddings)

    if verbose:
        print(f"Corpus: {len(corpus)} oraciones")
        print(f"Embeddings: {embeddings.shape} ({ruta})")

    return embeddings


def buscar_semantico(modelo, embeddings, corpus, consulta, top_k=TOP_K,
                     prefijo=""):
    """
    Ranking top-k por similitud del coseno contra los embeddings del corpus.

    Al embedding se le pasa el texto tal cual, sin normalizar: bajar a
    minúsculas y quitar acentos es correcto para el buscador léxico, pero acá
    destruye señal que el modelo sí usa
    """
    embedding_consulta = modelo.encode([prefijo + consulta])

    similitudes = cosine_similarity(embedding_consulta, embeddings)[0]
    indices = similitudes.argsort()[::-1][:top_k]

    return [
        {
            "indice": int(i),
            "puntaje": float(similitudes[i]),
            "documento": corpus[i],
        }
        for i in indices
    ]


def buscar_lexico(corpus, consulta, top_k=TOP_K):
    """
    Baseline por palabras clave: cuenta cuántos términos de la consulta
    aparecen en cada oración.

    Los documentos con cero coincidencias se descartan en lugar de rellenar el
    top-k: un puntaje de 0 no es un resultado, y dejarlo pasar hace que el
    baseline parezca responder cuando en realidad no encontró nada
    """
    tokens_consulta = tokenizar(consulta)

    resultados = []

    for i, documento in enumerate(corpus):
        coincidencias = len(tokens_consulta & tokenizar(documento))

        if coincidencias > 0:
            resultados.append({
                "indice": i,
                "puntaje": coincidencias,
                "documento": documento,
            })

    resultados.sort(key=lambda r: r["puntaje"], reverse=True)

    return resultados[:top_k]


def evaluar_blindaje(resultados_semanticos, resultados_lexicos,
                     umbral=UMBRAL_SIMILITUD, margen=MARGEN_MINIMO):
    """
    Cruza las tres defensas del análisis adversarial y decide si la respuesta
    se entrega, se marca como ambigua o se rechaza.

    Devuelve el estado y el motivo, no solo el documento: en la defensa
    interesa poder decir por qué se rechazó, no únicamente qué se devolvió
    """
    if not resultados_semanticos:
        return {"estado": "rechazado", "motivo": "sin resultados"}

    mejor = resultados_semanticos[0]

    if mejor["puntaje"] < umbral:
        return {
            "estado": "rechazado",
            "motivo": f"similitud {mejor['puntaje']:.4f} bajo el umbral {umbral}",
            "candidato": mejor,
        }

    if len(resultados_semanticos) > 1:
        diferencia = mejor["puntaje"] - resultados_semanticos[1]["puntaje"]

        if diferencia < margen:
            return {
                "estado": "ambiguo",
                "motivo": f"margen top-1/top-2 de {diferencia:.4f}",
                "candidato": mejor,
            }

    if resultados_lexicos and resultados_lexicos[0]["indice"] != mejor["indice"]:
        return {
            "estado": "discrepancia",
            "motivo": "los dos métodos apuntan a documentos distintos",
            "candidato": mejor,
        }

    return {"estado": "aceptado", "motivo": "", "candidato": mejor}
