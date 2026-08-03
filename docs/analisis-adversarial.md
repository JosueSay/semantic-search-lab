# Análisis adversarial: mascotas contra mecánica automotriz

Documento parcial del laboratorio de búsqueda semántica. Índice completo en el [README](../README.md).

## De qué se trata

Hay dos lados y conviene no confundirlos:

- **Ataque.** Entregamos 5 oraciones al equipo de mecánica automotriz. La meta es que su buscador las devuelva ante consultas mecánicas legítimas.
- **Defensa.** Otros equipos nos mandan 5 oraciones. Nuestro buscador de mascotas tiene que aguantar.

Las oraciones de ataque no pueden ser basura ni ruido aleatorio. Tienen que ser oraciones honestas de nuestro tema; la trampa está en el vocabulario, no en hacer trampa.

## Por qué el modelo se deja engañar

`paraphrase-multilingual-MiniLM-L12-v2` es un modelo chico: 384 dimensiones, entrenado para detectar paráfrasis. Corre rápido y local, que es lo que se pide, pero por lo mismo apoya buena parte de su decisión en el solapamiento léxico de superficie. Si dos oraciones comparten un sustantivo poco frecuente, el coseno sube aunque el sentido sea otro.

El español además ayuda al atacante, porque el vocabulario de taller y el de mascotas comparten más palabras de las esperables.

## Palabras puente

| Palabra | En mascotas | En mecánica automotriz | Fuerza |
| --- | --- | --- | --- |
| gato | el felino | gato hidráulico / de tijera | Alta |
| correa | correa de paseo | correa de distribución, serpentina | Alta |
| caja | caja de arena | caja de cambios | Alta |
| pastillas | medicamento del animal | pastillas de freno | Media-alta |
| filtro | filtro del acuario | filtro de aceite, aire, combustible | Media-alta |
| batería | collar GPS, cerca eléctrica | batería del carro | Media |
| arrancar | arrancar a correr | arrancar el motor | Media |
| aceite | aceite de pescado para el pelaje | aceite de motor | Media |
| manguera | bañar al perro | manguera del radiador | Media |
| escape | escaparse del patio | tubo de escape | Baja |
| rueda | rueda del hámster | rueda, llanta | Baja |
| jaula | jaula de aves | jaula de rodamientos | Baja |
| cola | cola del animal | fila, pegamento | Baja |

## Cómo medimos el ataque en vez de solo argumentarlo

No tenemos el corpus del equipo de mecánica automotriz, así que razonar sobre qué oración es más fuerte era pura especulación. Para resolverlo se construyó `CORPUS_MECANICA_PROXY` en `corpus.py`.

`python main.py ataque` inyecta nuestras 5 oraciones en ese proxy y reporta en qué posición del top-5 entra cada una. El proxy es una reconstrucción nuestra, así que los resultados **indican por dónde entra cada oración, no garantizan el resultado contra su corpus real**. Aun así cambió las decisiones: dos de las cinco oraciones originales no entraban en ningún top-5 y hubo que rehacerlas.

### Lo que la medición corrigió

| Oración original | Predicción del análisis | Medición |
| --- | --- | --- |
| Tuve que levantar al gato en brazos... | "la más fuerte del set" | Posición 2, entra en 2 consultas |
| Se le rompió la correa al perro y arrancó a correr detrás de la moto | "cuatro señales, la consulta va a existir seguro" | **No entra en ningún top-5** |
| Cambié la caja del gato por una más grande... | tercera en importancia | **Posición 1, entra en 5 consultas** |
| Le di las pastillas al perro y frenó en seco... | "menos densa, vale por cobertura" | **Posición 5, entra en 1 consulta** |
| El filtro del acuario se tapó... | quinta, "ataca desde otro subtema" | Posición 1, entra en 3 consultas |

Dos aprendizajes concretos:

- **Contar palabras puente no predice nada.** La oración de la correa cargaba cuatro señales (`correa`, `se rompió`, `arrancó`, `moto`) y fue la peor. El embedding promedia la oración completa, y `perro corriendo detrás de una moto` es una escena tan coherente y tan de mascotas que domina el vector entero. Las señales sueltas no suman, compiten.
- **Lo que sí funciona es imitar la estructura de la consulta objetivo.** Las consultas de mantenimiento tienen forma de "cada cuánto se cambia X" o "X está gastado". Las oraciones que ganaron son las que replican esa estructura, no las que acumulan más sustantivos ambiguos.

### Las oraciones rehechas

Aplicando ese criterio se reemplazaron las dos que fallaban:

- `correa`: *"Se le rompió la correa al perro y arrancó a correr detrás de la moto"* pasó a **"La correa del perro se desgastó y hay que cambiarla cada cierto tiempo."** Se perdieron `arrancó` y `moto`, se ganaron `se desgastó`, `cambiarla` y `cada cierto tiempo`. De 0 apariciones a posición 1 en 5 consultas.
- `pastillas`: *"Le di las pastillas al perro y frenó en seco a mitad del paseo"* pasó a **"Las pastillas del perro se gastan rápido y hay que cambiarlas cada mes."** De posición 5 a posición 2, en 3 consultas.

Ambas siguen siendo oraciones cien por ciento válidas sobre mascotas.

## Las 5 oraciones que se entregan

Definidas en `ORACIONES_ATAQUE_ENTREGADAS` (`corpus.py`). Resultados contra el proxy:

| # | Oración | Mejor posición | Similitud | Consultas alcanzadas |
| --- | --- | --- | --- | --- |
| 1 | Tuve que levantar al gato en brazos porque se quedó dormido debajo del carro. | 2 | 0.6999 | 2 de 10 |
| 2 | La correa del perro se desgastó y hay que cambiarla cada cierto tiempo. | 1 | 0.5060 | 5 de 10 |
| 3 | Cambié la caja del gato por una más grande y ahora entra sin problema. | 1 | 0.5426 | 5 de 10 |
| 4 | Las pastillas del perro se gastan rápido y hay que cambiarlas cada mes. | 2 | 0.4792 | 3 de 10 |
| 5 | El filtro del acuario se tapó y lo destapé con agua a presión. | 1 | 0.6363 | 3 de 10 |

En conjunto, alguna de las cinco entra en el top-5 de **9 de las 10** consultas mecánicas probadas, y en 3 de ellas se lleva el primer lugar. Cuatro de las cinco entran además por el buscador léxico, así que el ataque no depende de que el otro equipo use embeddings.

Las cinco atacan desde subtemas distintos (gatos, perros, peces) a propósito: si todas hablaran de perros, bastaría una regla de "descartar lo que mencione perro" para limpiarlas de un golpe.

### Las mismas 5 usadas como consulta

El ejercicio admite dos lecturas (ver la sección de defensa), así que el otro equipo podría correr nuestras oraciones como consultas en vez de indexarlas. `python main.py ataque` reporta también ese escenario:

| Oración | Top-1 que devolvería su buscador | Similitud | Con blindaje |
| --- | --- | --- | --- |
| Tuve que levantar al gato en brazos... | El gato hidráulico permite levantar el carro... | 0.6332 | Aceptado |
| Cambié la caja del gato por una más grande... | El gato hidráulico permite levantar el carro... | 0.5440 | Aceptado |
| El filtro del acuario se tapó... | El filtro de aire sucio reduce el rendimiento... | 0.4611 | Discrepancia |
| Las pastillas del perro se gastan rápido... | Revisar la presión de las llantas cada mes... | 0.4598 | Aceptado |
| La correa del perro se desgastó... | El embrague patina cuando el disco está desgastado. | 0.4009 | Discrepancia |

**5 de 5 superan el umbral** y 3 de 5 pasarían incluso un blindaje completo como el nuestro. El set funciona en las dos modalidades, así que no hace falta preparar oraciones distintas según cómo decidan usarlas.

Vale notar que la oración de las pastillas engancha por la estructura, no por el sustantivo: devuelve la presión de las llantas porque comparte "cada mes", no porque hable de frenos. Es el mismo efecto observado en [analisis-modelo.md](analisis-modelo.md): el patrón de mantenimiento periódico pesa más que el objeto.

## Lo que se descartó y por qué

**Batería** — *"al collar GPS se le acabó la batería"*. La trampa léxica es buena, pero en un corpus de mascotas nadie escribe eso de forma natural.

**Escape** — *"el perro se escapó por debajo del portón"*. Trampa aparente, no real: en mascotas es verbo y en mecánica sustantivo, y semánticamente no comparten contexto.

**Modelos de auto con nombre de animal** (Mustang, Jaguar, Impala, Cobra) — suena ingenioso pero un corpus de mecánica trata de mantenimiento y averías, no de catálogo de marcas. La consulta que activaría la trampa no la escribe nadie.

**Cola, rueda, jaula** — palabras puente reales, pero de baja frecuencia en consultas de mecánica.

## Defensa

### Las dos lecturas del ejercicio

Cuando el otro equipo entrega sus 5 oraciones, hay dos formas de someterlas al buscador propio y conviene tener las dos corridas:

| Lectura | Qué se hace | Qué mide | Modo |
| --- | --- | --- | --- |
| A. Como documentos | Las 5 se indexan junto al corpus propio y se corren **nuestras** consultas | Si el intruso contamina el índice y se cuela en el top-k | `defensa` |
| B. Como consultas | Las 5 se lanzan como consulta contra el corpus limpio, **sin indexarlas** | Si el buscador responde con confianza a algo fuera de su dominio | `consulta` |

La lectura A es la que sostiene el enunciado, por la frase "buscando que el buscador de ese equipo **las devuelva** ante consultas de su dominio": un buscador solo puede devolver documentos que están en su índice, así que las oraciones tienen que entrar al corpus. La lectura B es igual de razonable y mide algo complementario, así que se implementaron ambas.

Indexar las oraciones del rival no es hacer trampa ni vuelve trivial la prueba, porque **las oraciones intrusas nunca se usan como consulta en el modo `defensa`**: las consultas son siempre las propias. Buscar una oración contra sí misma daría una similitud cercana a 1 y no probaría nada. La pregunta real es si un usuario que pregunta por la correa de su perro recibe la correa de distribución del rival.

Lo que sí sería trampa: filtrar las oraciones por lista negra antes de indexar, o ajustar el umbral después de verlas hasta que bloquee justo esas 5. El blindaje son reglas generales, definidas sin conocer las oraciones concretas.

### Lectura A: oraciones indexadas

`python main.py defensa` inyecta las oraciones recibidas en nuestro corpus y corre las 12 consultas propias (6 de prueba y 6 ambiguas) para ver si los intrusos se cuelan.

Mientras el otro equipo no entregue las suyas, el modo usa `ORACIONES_ATAQUE_SIMULADAS`: oraciones de mecánica cargadas de vocabulario de mascotas, o sea el ataque que nosotros mismos haríamos si estuviéramos del otro lado. En cuanto lleguen las reales se pegan en `ORACIONES_ATAQUE_RECIBIDAS` y se vuelve a correr.

### El corpus tenía un hueco

La primera corrida mostró algo que el análisis en papel no había anticipado: nuestro corpus **no contenía** `correa`, `pastillas` ni `filtro` en su lectura de mascotas. Sin un documento propio que compita, un ataque por esas palabras gana el top-1 por defecto — no porque el intruso sea bueno, sino porque no hay rival.

Se corrigió insertando las tres palabras en oraciones que ya existían, sin agregar ninguna. El corpus sigue en 25:

- "Sacar al can **con su correa** a pasear todas las tardes..."
- "La desparasitación **con pastillas** debe repetirse cada tres o cuatro meses."
- "Los peces tropicales requieren **un filtro limpio** y temperatura estable en el acuario."

Efecto medido: la consulta *"el filtro dejó de funcionar"* pasó a recuperar la oración correcta en primer lugar, y *"¿cada cuánto se le cambia la correa?"* dejó de aceptarse a ciegas.

### Blindaje, implementado en `busqueda.py`

1. **Umbral mínimo de similitud** (`UMBRAL_SIMILITUD = 0.35`). Por debajo no se devuelve nada. El valor no es arbitrario: los falsos positivos medidos caen en la franja 0.23–0.40.
2. **Margen entre top-1 y top-2** (`MARGEN_MINIMO = 0.05`). Si la diferencia es mínima, la consulta se marca ambigua en lugar de responder con confianza falsa.
3. **Cruce de los dos métodos.** Si el top-1 semántico y el léxico apuntan a documentos distintos, se marca discrepancia. Es la comparación cualitativa del enunciado reutilizada como señal de defensa.
4. **Prefijo de dominio** (`PREFIJO_DOMINIO = "sobre mascotas: "`). Anteponerlo a la consulta antes de encodearla mueve el vector fuera de la zona mecánica.
5. **No normalizar de más en el lado semántico.** Minúsculas y sin acentos es correcto para el buscador léxico; al embedding se le pasa el texto tal cual.

### Resultados de la defensa

Sobre 12 consultas con el corpus envenenado:

| Métrica | Resultado |
| --- | --- |
| Intruso en el top-1 sin blindaje | 3 de 12 |
| Intruso entregado como respuesta con blindaje | **0 de 12** |
| Casos recuperados por el prefijo de dominio | 3 de 3 |

De los tres intrusos que ganaban el top-1, uno se frena por umbral y dos por discrepancia entre métodos. Los tres se corrigen además con el prefijo de dominio, que en cada caso devuelve el primer lugar a una oración propia.

Sobre las 6 consultas ambiguas sin envenenar, el blindaje reparte: 3 rechazadas por umbral, 2 marcadas ambiguas por margen y 1 por discrepancia. Ninguna se entrega a ciegas.

Vale anotar el costo: el blindaje también marca consultas legítimas. La regla de discrepancia entre métodos es la más ruidosa, porque los dos buscadores difieren en la mitad de las consultas normales. Sirve como advertencia, no como criterio para descartar.

### Lectura B: oraciones como consulta

`python main.py consulta` lanza las 5 oraciones recibidas como consultas contra el corpus limpio de 25, sin indexarlas. Corrida en [`logs/consulta.log`](../logs/consulta.log).

| Consulta intrusa | Top-1 propio | Similitud | Qué la frenó |
| --- | --- | --- | --- |
| El gato hidráulico soporta hasta dos toneladas... | Es importante limpiar la caja de arena del gato... | **0.5796** | Discrepancia entre métodos |
| La caja de cambios empezó a fallar al meter la segunda. | Un cambio repentino de apetito puede ser señal... | 0.3026 | Umbral |
| Las pastillas de freno ya están gastadas y chillan al frenar. | Los mininos marcan su territorio... | 0.2809 | Umbral |
| La correa de distribución se cambia cada sesenta mil kilómetros. | La desparasitación con pastillas debe repetirse... | 0.2571 | Umbral |
| El filtro de aceite se tapó y hubo que cambiarlo en el taller. | La desparasitación con pastillas debe repetirse... | 0.1798 | Umbral |

Ninguna se entrega como respuesta, pero **no todas se frenan por la misma razón**, y ahí está lo interesante.

Cuatro de las cinco ni se acercan al umbral: 0.18 a 0.30. Una oración completa de mecánica arrastra tanto contexto de taller que el vector queda lejos de la región de mascotas, y la palabra puente no alcanza a compensarlo.

La del **gato hidráulico es la excepción, y por mucho**: 0.5796, sesenta por ciento por encima del umbral. El homónimo `gato` es tan dominante que arrastra una oración de toneladas y cajuelas hasta la caja de arena del felino. El umbral no la detiene; la frena únicamente el cruce con el buscador léxico, que apunta a otro documento.

Dos conclusiones para la defensa:

- El umbral solo no basta. Si el blindaje fuera únicamente el umbral de 0.35, esta consulta se habría respondido con aparente confianza. La tercera regla, que parecía la más ruidosa, es la que salva el caso.
- El riesgo no se reparte parejo entre las palabras puente. `gato` es una categoría aparte: homónimo exacto, alta frecuencia en ambos dominios y presencia fuerte en nuestro corpus. Contra `gato` hay que asumir que la similitud va a ser alta y defenderse con las otras reglas, no esperar que el coseno lo resuelva.

Los dos modos se complementan: en la lectura B ninguna respuesta sale, en la lectura A el blindaje se pone a prueba de verdad.
