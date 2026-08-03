"""
Datos del laboratorio: corpus propio, consultas de prueba y oraciones del
ejercicio adversarial

Restricciones del laboratorio:
- El corpus propio se mantiene en 25 oraciones (el enunciado pide mínimo 20).
- Las oraciones recibidas de otro equipo NO forman parte del corpus propio:
  se inyectan aparte, solo para probar la defensa
"""

# Tema propio: mascotas. 25 oraciones
CORPUS_MASCOTAS = [
    # perros
    "Los perros necesitan al menos una caminata diaria para mantenerse sanos.",
    "Mi cachorro labrador aprendió a sentarse en apenas dos semanas de entrenamiento.",
    "Sacar al can con su correa a pasear todas las tardes mejora su comportamiento en casa.",
    "Las razas grandes suelen requerir más espacio y ejercicio que las pequeñas.",
    "Un perro que ladra en exceso puede estar sufriendo ansiedad por separación.",

    # gatos
    "Los gatos duermen entre catorce y dieciséis horas al día.",
    "Mi felino se pasa la tarde durmiendo en la ventana bajo el sol.",
    "Es importante limpiar la caja de arena del gato todos los días.",
    "Los mininos marcan su territorio frotando la cabeza contra los muebles.",
    "Un gato adulto suele ser más independiente que un perro de la misma edad.",

    # alimentación
    "La alimentación balanceada previene la obesidad en animales domésticos.",
    "El chocolate y la cebolla son tóxicos para perros y gatos.",
    "Darle comida de humanos a la mascota puede causarle problemas digestivos.",
    "Siempre hay que dejar un recipiente con agua limpia al alcance del animal.",

    # veterinaria y salud
    "Llevar la mascota al veterinario una vez al año previene enfermedades graves.",
    "Las vacunas contra la rabia son obligatorias en la mayoría de los países.",
    "La desparasitación con pastillas debe repetirse cada tres o cuatro meses.",
    "Esterilizar a los animales ayuda a controlar la sobrepoblación en las calles.",
    "Un cambio repentino de apetito puede ser señal de que algo anda mal.",

    # adopción y refugios
    "Adoptar un animal de un refugio le da una segunda oportunidad de vida.",
    "Antes de comprar una mascota conviene considerar la adopción responsable.",
    "Los albergues locales reciben decenas de animales abandonados cada mes.",

    # otras mascotas
    "Los peces tropicales requieren un filtro limpio y temperatura estable en el acuario.",
    "Los conejos necesitan heno fresco como base principal de su dieta.",
    "Las aves domésticas cantan más cuando reciben luz natural por la mañana.",
]

# Consultas de prueba del enunciado (mínimo 5).
# La última es el control de paráfrasis pura: no comparte ninguna palabra con
# la oración que debería recuperar, así que separa búsqueda semántica real de
# coincidencia literal disfrazada.
CONSULTAS_PRUEBA = [
    "¿cada cuánto hay que llevar la mascota al veterinario?",
    "¿qué alimentos son tóxicos para perros y gatos?",
    "¿cómo saber si mi mascota está enferma?",
    "¿qué cuidados necesita un gato adulto?",
    "¿cómo entrenar a un cachorro para que haga sus necesidades afuera?",
    "¿cuánto tiempo pasan dormidos los felinos?",
]

# Consultas del lado defensivo: cada una activa una palabra puente entre
# mascotas y mecánica automotriz. Sirven para verificar que el blindaje
# distingue la lectura de mascotas de la lectura mecánica.
CONSULTAS_AMBIGUAS = [
    "¿cada cuánto se le cambia la correa?",
    "necesito un gato",
    "la caja está sucia",
    "se me acabaron las pastillas",
    "el filtro dejó de funcionar",
    "arranca a correr apenas abro la puerta",
]

# Consultas de una sola palabra. No son consultas realistas: son la sonda que
# mide cuánto del puntaje del modelo viene del solapamiento léxico de
# superficie. La evidencia que producen sustenta docs/analisis-modelo.md.
CONSULTAS_UNA_PALABRA = [
    "gato",
    "correa",
    "caja",
    "filtro",
    "pastillas",
]

# Ataque: las 5 oraciones que entregamos al equipo de mecánica automotriz.
# Son oraciones honestas de mascotas; la trampa está en el vocabulario.
# La justificación de cada una está en docs/analisis-adversarial.md.
ORACIONES_ATAQUE_ENTREGADAS = [
    "Tuve que levantar al gato en brazos porque se quedó dormido debajo del carro.",
    "La correa del perro se desgastó y hay que cambiarla cada cierto tiempo.",
    "Cambié la caja del gato por una más grande y ahora entra sin problema.",
    "Las pastillas del perro se gastan rápido y hay que cambiarlas cada mes.",
    "El filtro del acuario se tapó y lo destapé con agua a presión.",
]

# Proxy del corpus rival. No tenemos el corpus real del equipo de mecánica
# automotriz, así que se reconstruye uno plausible para poder MEDIR el ataque
# en lugar de solo argumentarlo: se inyectan nuestras 5 oraciones acá dentro y
# se corre `python main.py ataque`.
# No es parte del corpus propio ni cuenta contra el límite de 25: es un fixture
# de prueba. Sus resultados son indicativos, no la prueba definitiva.
CORPUS_MECANICA_PROXY = [
    "El gato hidráulico permite levantar el carro para cambiar la llanta.",
    "La correa de distribución debe cambiarse según el kilometraje del motor.",
    "La caja de cambios manual requiere revisar el nivel de aceite.",
    "Las pastillas de freno gastadas producen un chillido al frenar.",
    "El filtro de aceite se reemplaza en cada cambio de aceite del motor.",
    "El filtro de aire sucio reduce el rendimiento del combustible.",
    "La batería descargada impide que el motor arranque en frío.",
    "El radiador se sobrecalienta cuando la manguera tiene una fuga.",
    "Los amortiguadores desgastados hacen que el carro rebote en los baches.",
    "El tubo de escape suelto genera un ruido metálico al acelerar.",
    "La bujía en mal estado provoca fallos de encendido en el motor.",
    "Revisar la presión de las llantas cada mes alarga su vida útil.",
    "El embrague patina cuando el disco está desgastado.",
    "La alineación y el balanceo corrigen el desgaste irregular de las llantas.",
    "El aceite del motor debe cambiarse cada cinco mil kilómetros.",
]

# Consultas que un usuario le haría al buscador de mecánica automotriz.
# Son el disparador del ataque: si nuestras oraciones aparecen en el top-k de
# alguna de estas, el ataque funcionó.
CONSULTAS_MECANICA = [
    "¿cómo levantar el carro con el gato?",
    "¿qué gato usar para cambiar la llanta?",
    "¿cada cuánto se cambia la correa?",
    "se rompió la correa de distribución",
    "¿cuándo cambiar la caja?",
    "la caja no entra en segunda",
    "¿cuándo cambiar las pastillas de freno?",
    "el freno hace ruido",
    "el filtro está tapado",
    "¿cómo limpiar el filtro de aire?",
]

# Defensa: acá se pegan las 5 oraciones que nos entregue el otro equipo.
# Se inyectan al corpus como documentos intrusos y se corre `python main.py
# defensa` para ver si se cuelan en el top-k de nuestras propias consultas.
ORACIONES_ATAQUE_RECIBIDAS = []

# Suplente mientras el otro equipo no entrega: nuestras propias oraciones de
# ataque leídas al revés, es decir, oraciones de mecánica que cargan
# vocabulario de mascotas. Sirven para dejar el modo defensa probado de
# antemano; se descartan en cuanto lleguen las reales.
ORACIONES_ATAQUE_SIMULADAS = [
    "El gato hidráulico soporta hasta dos toneladas y se guarda en la cajuela.",
    "La correa de distribución se cambia cada sesenta mil kilómetros.",
    "La caja de cambios empezó a fallar al meter la segunda.",
    "Las pastillas de freno ya están gastadas y chillan al frenar.",
    "El filtro de aceite se tapó y hubo que cambiarlo en el taller.",
]
