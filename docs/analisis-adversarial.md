# Análisis adversarial: mascotas vs. mecánica automotriz

## De qué se trata

Hay dos lados en este ejercicio y conviene no confundirlos:

- **Ataque.** Entregamos 5 oraciones al equipo con tema de mecánica automotriz. La meta es que su buscador las devuelva como resultado de consultas mecánicas legítimas.
- **Defensa.** Otros equipos nos van a mandar 5 oraciones a nosotros. Nuestro buscador de mascotas tiene que aguantar.

Las oraciones de ataque no pueden ser basura ni ruido aleatorio. Tienen que ser oraciones honestas de nuestro tema; la trampa está en el vocabulario, no en hacer trampa.

## Por qué el modelo se deja engañar

`paraphrase-multilingual-MiniLM-L12-v2` es un modelo chico: 384 dimensiones y entrenado para detectar paráfrasis. Corre rápido y local, que es justo lo que se pide, pero por lo mismo apoya buena parte de su decisión en el solapamiento léxico de superficie. Si dos oraciones comparten un sustantivo poco frecuente, el coseno sube aunque el sentido sea completamente otro.

El español además ayuda bastante al atacante, porque el vocabulario de taller y el de mascotas comparten más palabras de las que uno esperaría.

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
| ronronear | el gato ronronea | "el motor ronronea" | Baja |

## Cómo se eligieron las 5

Cinco criterios, en orden de peso:

1. **Frecuencia real en consultas de mecánica.** Si nadie pregunta por esa palabra, la trampa nunca se dispara. `correa` y `pastillas` aparecen en averías cotidianas; `jaula` casi nunca.
2. **Naturalidad en nuestro dominio.** La oración tiene que ser algo que alguien escribiría de verdad sobre mascotas. Una oración forzada se nota y no aporta.
3. **Densidad de señal.** Cuántas pistas mecánicas carga la misma oración. Un solo sustantivo ambiguo se diluye en el promedio del vector; dos o tres arrastran la oración entera hacia el otro dominio.
4. **Que sirva contra los dos métodos.** El match léxico exacto y el semántico. Si la palabra solo funciona en uno, la mitad del ataque se cae.
5. **Brevedad.** El embedding es un promedio sobre los tokens. Entre más corta la oración, más peso relativo tiene la palabra trampa.

## Las 5 oraciones elegidas

### 1. El gato hidráulico

> Tuve que levantar al gato en brazos porque se quedó dormido debajo del carro.

Consultas objetivo: *"cómo levantar el carro con el gato"*, *"qué gato usar para cambiar la llanta"*.

Es la más fuerte del set. `gato` es homónimo exacto y de alta frecuencia en mecánica, y la oración suma `levantar` y `debajo del carro`, que es literalmente lo que se hace con un gato hidráulico. Tres señales alineadas y la oración sigue siendo cien por ciento válida como oración de mascotas.

### 2. La correa que se rompió

> Se le rompió la correa al perro y arrancó a correr detrás de la moto.

Consultas objetivo: *"se rompió la correa de distribución"*, *"cada cuánto se cambia la correa"*.

Cuatro señales: `correa`, `se rompió`, `arrancó`, `moto`. "Romperse la correa" es exactamente la avería que la gente busca, así que la consulta objetivo va a existir seguro.

### 3. La caja que no entra

> Cambié la caja del gato por una más grande y ahora entra sin problema.

Consultas objetivo: *"cambio de caja"*, *"la caja no entra en segunda"*.

Doble trampa: trae `caja` y `gato` en la misma oración. Y "que la caja entre" es como se habla en taller de meter los cambios, así que `cambié` y `entra` refuerzan el sentido equivocado.

### 4. Las pastillas y el freno

> Le di las pastillas al perro y frenó en seco a mitad del paseo.

Consultas objetivo: *"cuándo cambiar las pastillas de freno"*, *"el freno hace ruido"*.

Menos densa que las tres anteriores, pero cubre el sistema de frenos, que es un bloque temático entero del corpus rival. Vale más por cobertura que por potencia.

### 5. El filtro tapado

> El filtro del acuario se tapó y lo destapé con agua a presión.

Consultas objetivo: *"filtro de aceite tapado"*, *"cómo limpiar el filtro de aire"*.

Ataca desde el subtema de peces en vez de perros y gatos. Eso importa: si las 5 oraciones hablaran de perros, al otro equipo le bastaría una regla tonta de "descartar lo que mencione perro" para limpiar todo. Diversificar el origen encarece la defensa.

## Lo que se descartó y por qué

**Batería** — *"al collar GPS se le acabó la batería"*. La trampa léxica es buena, pero la oración se siente construida; en un corpus de mascotas nadie escribe eso de forma natural. Falla el criterio 2.

**Escape** — *"el perro se escapó por debajo del portón"*. Trampa aparente, no real. En mascotas es verbo y en mecánica sustantivo. Con lematización el match léxico se pierde, y semánticamente "escaparse" y "tubo de escape" no comparten contexto alguno.

**Modelos de auto con nombre de animal** (Mustang, Jaguar, Impala, Escarabajo, Cobra) — suena ingenioso pero no rinde. Un corpus de mecánica trata de mantenimiento y averías, no de catálogo de marcas. La consulta que activaría la trampa no la va a escribir nadie.

**Cola, rueda, jaula, ronronear** — son palabras puente reales, pero de baja frecuencia en consultas de mecánica. Servirían de relleno si hubiera que entregar quince oraciones; con cinco, no compiten.

## Defensa: qué nos van a hacer a nosotros

Nuestro propio corpus ya viene cargado de munición para el otro lado. `gato` aparece en cuatro oraciones y "caja de arena" en una. Un equipo que nos ataque con *"el gato hidráulico soporta hasta dos toneladas"* tiene una probabilidad razonable de colarse en la consulta *"mi gato no quiere comer"*.

Lo que hay que esperar recibir: oraciones de otros dominios con `gato`, `correa`, `caja`, `pastillas`, `filtro`, `arrancar`, `pelo` o `pelusa`.

### Blindaje a implementar

Esto tiene que quedar en el código, no solo escrito acá.

1. **Umbral mínimo de similitud.** Por debajo de cierto valor, no devolver nada en lugar de devolver el resultado menos malo. Arrancar en 0.35 y calibrar con las consultas de prueba. La mayoría de los falsos positivos de un ataque caen en la franja 0.25–0.40, que es justo donde el modelo "cree" haber encontrado algo.
2. **Margen entre top-1 y top-2.** Si la diferencia es mínima, la consulta es ambigua. Vale más marcarla como ambigua que responder con confianza falsa.
3. **Cruce de los dos métodos.** Un resultado que gana por palabras clave pero pierde por coseno (o al revés) es sospechoso. Esto no es trabajo extra: es exactamente la comparación cualitativa que pide el enunciado, usada además como señal de defensa.
4. **Desambiguar la consulta con contexto de dominio.** Anteponer algo como "sobre mascotas:" a la consulta antes de encodearla mueve el vector fuera de la zona mecánica. Es barato y con modelos de paráfrasis funciona sorprendentemente bien.
5. **No normalizar de más en el lado semántico.** Bajar a minúsculas y quitar acentos es correcto para el buscador léxico, pero al embedding hay que darle el texto tal cual.

### Consultas para probar el blindaje

Estas sirven a la vez como parte de las consultas de prueba del enunciado.

1. *"¿cada cuánto se le cambia la correa?"* — debe traer el paseo, no la distribución.
2. *"necesito un gato"* — ambigua a propósito. Caso de prueba del margen top-1 / top-2.
3. *"la caja está sucia"* — caja de arena.
4. *"se me acabaron las pastillas"* — medicamento del animal.
5. *"el filtro dejó de funcionar"* — acuario.
6. *"arranca a correr apenas abro la puerta"* — el perro, no el motor.
