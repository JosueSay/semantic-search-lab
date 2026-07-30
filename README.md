# semantic-search-lab

Búsqueda semántica sobre un corpus en español usando embeddings locales, comparada contra una búsqueda léxica por palabras clave. El corpus es sobre **mascotas**.

## Instalación

```bash
pip install sentence-transformers numpy scikit-learn
```

Si vas a usar el entorno virtual del repo:

```bash
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install sentence-transformers numpy scikit-learn
```

## Uso

```bash
python main.py
```

La primera corrida descarga el modelo `paraphrase-multilingual-MiniLM-L12-v2` desde Hugging Face (varios cientos de MB) y lo deja cacheado en `~/.cache/huggingface`. De ahí en adelante corre offline.

## Estructura

```bash
main.py     corpus + pipeline de búsqueda
docs/       enunciado, análisis y pendientes
```

- `CORPUS_MASCOTAS` — 25 oraciones del tema propio.
- `CORPUS_MECANICA` — las 5 oraciones de ataque que se entregan al equipo de mecánica automotriz.

## Documentación

| Archivo | Qué tiene |
| --- | --- |
| [docs/instrucciones.md](docs/instrucciones.md) | Enunciado de la tarea |
| [docs/analisis-adversarial.md](docs/analisis-adversarial.md) | Palabras ambiguas entre mascotas y mecánica, selección de las 5 oraciones de ataque y blindaje del lado defensivo |
| [docs/pendientes.md](docs/pendientes.md) | Qué falta implementar |
