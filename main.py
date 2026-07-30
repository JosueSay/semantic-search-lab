from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Corpus propio del proyecto. Tema: mascotas.
CORPUS_MASCOTAS = [
    # perros
    "Los perros necesitan al menos una caminata diaria para mantenerse sanos.",
    "Mi cachorro labrador aprendió a sentarse en apenas dos semanas de entrenamiento.",
    "Sacar al can a pasear todas las tardes mejora su comportamiento en casa.",
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
    "La desparasitación debe repetirse cada tres o cuatro meses.",
    "Esterilizar a los animales ayuda a controlar la sobrepoblación en las calles.",
    "Un cambio repentino de apetito puede ser señal de que algo anda mal.",

    # adopción y refugios
    "Adoptar un animal de un refugio le da una segunda oportunidad de vida.",
    "Antes de comprar una mascota conviene considerar la adopción responsable.",
    "Los albergues locales reciben decenas de animales abandonados cada mes.",

    # otras mascotas
    "Los peces tropicales requieren una temperatura estable en el acuario.",
    "Los conejos necesitan heno fresco como base principal de su dieta.",
    "Las aves domésticas cantan más cuando reciben luz natural por la mañana.",
]

# Oraciones de ataque que se le entregan al equipo con tema de mecánica
# automotriz. Son oraciones legítimas de mascotas, escogidas porque cargan
# vocabulario que en mecánica significa otra cosa.
# El criterio de selección está en docs/analisis-adversarial.md
CORPUS_MECANICA = [
    "Tuve que levantar al gato en brazos porque se quedó dormido debajo del carro.",
    "Se le rompió la correa al perro y arrancó a correr detrás de la moto.",
    "Cambié la caja del gato por una más grande y ahora entra sin problema.",
    "Le di las pastillas al perro y frenó en seco a mitad del paseo.",
    "El filtro del acuario se tapó y lo destapé con agua a presión.",
]

# Cargar el modelo
modelo = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# Generar embeddings del corpus
embeddings = modelo.encode(CORPUS_MASCOTAS)

print(f"Corpus: {len(CORPUS_MASCOTAS)} oraciones")
print(f"Embeddings: {embeddings.shape}")

# Consulta de ejemplo
consulta = "¿cada cuánto hay que llevar la mascota al veterinario?"
embedding_consulta = modelo.encode([consulta])

# Calcular similitud coseno
similitudes = cosine_similarity(
    embedding_consulta,
    embeddings
)[0]

# Ordenar de mayor a menor similitud
indices = similitudes.argsort()[::-1]

print(f"\nConsulta: {consulta}")
print("\nResultados ordenados:")
for i in indices:
    print(f"{similitudes[i]:.4f}  {CORPUS_MASCOTAS[i]}")
