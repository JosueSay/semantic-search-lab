# Comparación cualitativa: búsqueda semántica contra búsqueda por palabras clave

Documento parcial del laboratorio de búsqueda semántica. Índice completo en el [README](../README.md).

Los dos buscadores corren sobre el mismo corpus de 25 oraciones y las mismas 6 consultas de prueba. La corrida completa está en [`logs/prueba.log`](../logs/prueba.log) y se reproduce con `python main.py prueba`.

Lo interesante no es cuál gana en promedio, sino dónde se separan.

## Qué hace cada uno

| | Semántico | Léxico |
| --- | --- | --- |
| Representación | Embedding de 384 dimensiones | Conjunto de tokens |
| Puntaje | Similitud del coseno, 0 a 1 | Cantidad de términos en común |
| Preprocesamiento | Ninguno, texto tal cual | Minúsculas, sin acentos, sin puntuación, sin stopwords |
| Si no encuentra nada | Devuelve el vecino menos malo | No devuelve nada |

El baseline es deliberadamente simple: no hay TF-IDF ni librerías, solo intersección de conjuntos. Su valor no es competir, es dar una referencia contra la cual sostener que lo semántico aporta algo.

## Resultado global

Coinciden en el top-1 en **3 de 6** consultas. Las tres en que se separan son las informativas.

| Consulta | Top-1 semántico | Top-1 léxico | ¿Coinciden? |
| --- | --- | --- | --- |
| ¿cada cuánto hay que llevar la mascota al veterinario? | veterinario (0.8159) | veterinario (3) | Sí |
| ¿qué alimentos son tóxicos para perros y gatos? | chocolate y cebolla (0.8554) | chocolate y cebolla (3) | Sí |
| ¿cómo saber si mi mascota está enferma? | veterinario (0.6707) | comida de humanos (1) | No |
| ¿qué cuidados necesita un gato adulto? | gato adulto (0.6761) | gato adulto (2) | Sí |
| ¿cómo entrenar a un cachorro...? | caminata diaria (0.6875) | cachorro labrador (1) | No |
| ¿cuánto tiempo pasan dormidos los felinos? | gatos duermen (0.7932) | sin resultados | No |

## Dónde se separan

### 1. El léxico no encuentra nada y el semántico acierta

Consulta: *"¿cuánto tiempo pasan dormidos los felinos?"*

```text
Semántico   0.7932  Los gatos duermen entre catorce y dieciséis horas al día.
Léxico      (sin resultados)
```

La consulta y el documento no comparten un solo token: `felinos` contra `gatos`, `dormidos` contra `duermen`. El léxico no tiene por dónde entrar. El semántico no solo la encuentra, la coloca en primer lugar con el segundo puntaje más alto de la corrida.

Un buscador literal le habría dicho al usuario que no hay documentación sobre el tema, teniendo la respuesta exacta en el corpus.

### 2. Ambos aciertan, pero el léxico acierta por accidente

Consulta: *"¿qué alimentos son tóxicos para perros y gatos?"*

```text
Semántico   0.8554  El chocolate y la cebolla son tóxicos para perros y gatos.
            0.5787  Darle comida de humanos a la mascota puede causarle problemas digestivos.
Léxico           3  El chocolate y la cebolla son tóxicos para perros y gatos.
                 1  Los perros necesitan al menos una caminata diaria para mantenerse sanos.
                 1  Los gatos duermen entre catorce y dieciséis horas al día.
```

El top-1 es el mismo, pero por razones distintas. El léxico gana porque la consulta copia casi textualmente el documento (`tóxicos`, `perros`, `gatos`); en cuanto se reformula, ese acierto desaparece. Y su segundo y tercer resultado son irrelevantes: entran solo por mencionar `perros` o `gatos`. El semántico ordena el resto por pertinencia real, poniendo la oración de problemas digestivos por encima de la de las caminatas.

La diferencia no está en el top-1 sino en la **calidad de la cola del ranking**, que es justamente lo que se le entrega a un modelo generativo en RAG.

### 3. El semántico se va por la tangente y el léxico está más cerca

Consulta: *"¿cómo entrenar a un cachorro para que haga sus necesidades afuera?"*

```text
Semántico   0.6875  Los perros necesitan al menos una caminata diaria para mantenerse sanos.
            0.6451  Mi cachorro labrador aprendió a sentarse en apenas dos semanas de entrenamiento.
Léxico           1  Mi cachorro labrador aprendió a sentarse en apenas dos semanas de entrenamiento.
```

Acá el semántico pierde. La consulta pregunta por entrenamiento y el modelo devuelve la oración de las caminatas porque `afuera` y `necesidades` lo arrastran hacia el concepto de salir a la calle. El léxico, con una sola coincidencia (`cachorro`), apunta al documento correcto.

Es la generalización del modelo trabajando en contra: aproxima la consulta al concepto general más cercano del dominio, y el concepto general acá no es el que se pedía.

### 4. Ninguno responde bien, y solo el semántico lo disimula

Consulta: *"¿cómo saber si mi mascota está enferma?"*

```text
Semántico   0.6707  Llevar la mascota al veterinario una vez al año previene enfermedades graves.
Léxico           1  Darle comida de humanos a la mascota puede causarle problemas digestivos.
```

El documento correcto es *"Un cambio repentino de apetito puede ser señal de que algo anda mal"*, y ninguno de los dos lo pone primero. La diferencia está en cómo fallan: el léxico entrega un resultado con puntaje 1, visiblemente débil; el semántico entrega uno con 0.6707, que se lee como una respuesta confiable. **El fallo del semántico es más peligroso porque no se nota.**

## Conclusión

Los dos métodos fallan, pero fallan distinto, y esa asimetría es lo aprovechable:

- El léxico tiene **precisión frágil y honestidad alta**. Cuando no sabe, lo dice. Nunca inventa relevancia.
- El semántico tiene **cobertura alta y honestidad baja**. Encuentra lo que el léxico no puede, y también encuentra cosas donde no hay nada.

De ahí sale la decisión de diseño del proyecto: no elegir uno, sino cruzarlos. Un resultado que gana por coseno pero pierde por palabras clave es sospechoso, y esa señal se convirtió en una de las tres reglas del blindaje descrito en [analisis-adversarial.md](analisis-adversarial.md). La comparación que pide el enunciado terminó siendo también un mecanismo de defensa.

Para RAG la conclusión es la misma en otra escala: el semántico es el que recupera, pero entregarle al generador un top-k sin filtrar es entregarle falsos positivos con apariencia de certeza.
