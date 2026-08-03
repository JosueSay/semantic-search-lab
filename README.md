# Semantic Search Lab

Búsqueda semántica sobre un corpus en español usando embeddings locales, comparada contra una búsqueda léxica por palabras clave. Tema del corpus: **mascotas**.

Laboratorio de la semana 4 del curso de Procesamiento de Lenguaje Natural. Además de los dos buscadores, el proyecto incluye el ejercicio adversarial: atacar el buscador del equipo de mecánica automotriz y defender el propio.

## Instalación

```bash
pip install sentence-transformers numpy scikit-learn
```

Detalle en [docs/instalacion.md](docs/instalacion.md).

## Uso

```bash
python main.py prueba      # consultas del enunciado, semántico contra léxico
python main.py ambiguas    # consultas con palabras puente, con blindaje
python main.py palabras    # consultas de una sola palabra
python main.py ataque      # nuestras 5 oraciones contra un proxy de mecánica
python main.py defensa     # oraciones intrusas inyectadas en el corpus propio
python main.py consulta    # oraciones intrusas usadas como consulta, sin indexar
```

`defensa` y `consulta` son las dos lecturas del ejercicio adversarial: la primera indexa las oraciones del rival, la segunda las usa como consulta sin indexarlas.

## Estructura

```text
corpus.py     corpus, consultas y oraciones del ejercicio adversarial
busqueda.py   los dos buscadores y el blindaje
main.py       orquestación y salida por modo
docs/         enunciado y análisis
logs/         corridas guardadas, una por modo
embeddings/   caché de embeddings, indexada por huella del corpus
```

Datos en `corpus.py`:

- `CORPUS_MASCOTAS` — 25 oraciones del tema propio.
- `CONSULTAS_PRUEBA` — 6 consultas del enunciado.
- `CONSULTAS_AMBIGUAS` — consultas que activan palabras puente con mecánica.
- `CONSULTAS_UNA_PALABRA` — sonda para medir el peso del solapamiento léxico.
- `ORACIONES_ATAQUE_ENTREGADAS` — las 5 que se entregan al otro equipo.
- `ORACIONES_ATAQUE_RECIBIDAS` — vacía hasta que el otro equipo entregue.
- `CORPUS_MECANICA_PROXY` — fixture para medir el ataque, no es el corpus rival.

## Resultados

| Medición | Resultado |
| --- | --- |
| Top-1 coincidente entre ambos buscadores | 3 de 6 consultas |
| Consulta sin ninguna palabra en común con su documento | 0.7932 en semántico, léxico no recupera nada |
| Consultas mecánicas penetradas por nuestras 5 oraciones | 9 de 10 |
| Intrusos en top-1 con el corpus envenenado | 3 de 12 sin blindaje, 0 entregados con blindaje |
| Oraciones del rival usadas como consulta contra el corpus limpio | 0 de 5 respondidas |
| Nuestras 5 usadas como consulta contra el proxy de mecánica | 5 de 5 superan el umbral |

## Documentación

| Archivo | Qué tiene |
| --- | --- |
| [docs/entrega.md](docs/entrega.md) | **Resumen de entrega**: todo el proyecto en dos hojas, con diagramas |
| [docs/instrucciones.md](docs/instrucciones.md) | Enunciado y dónde se cumple cada requisito |
| [docs/instalacion.md](docs/instalacion.md) | Dependencias, modos y regeneración de logs |
| [docs/comparacion-cualitativa.md](docs/comparacion-cualitativa.md) | Semántico contra léxico y dónde se separan |
| [docs/analisis-modelo.md](docs/analisis-modelo.md) | Comportamiento del modelo, fortalezas y limitaciones |
| [docs/analisis-adversarial.md](docs/analisis-adversarial.md) | Palabras puente, selección medida de las 5 oraciones y blindaje |
