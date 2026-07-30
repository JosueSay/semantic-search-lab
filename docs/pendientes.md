# Pendientes

El corpus ya está y el script corre un ejemplo de punta a punta. Falta armar el pipeline completo y escribir el informe comparativo.

## Mínimo 20 oraciones en español

Hecho. `CORPUS_MASCOTAS` en `main.py` tiene 25, repartidas en perros, gatos, alimentación, salud, adopción y otras mascotas. Se pasó de 20 a propósito: con pocas oraciones el top-k siempre devuelve lo mismo y no se alcanza a notar la diferencia entre los dos buscadores.

## Mínimo 5 consultas de prueba

Falta fijarlas en el código. En [analisis-adversarial.md](analisis-adversarial.md) ya hay seis candidatas, todas apuntando a las palabras ambiguas. Conviene agregar dos o tres consultas fáciles como control, para tener con qué comparar cuando las difíciles fallen.

## Generación de embeddings locales

Medio hecho. El modelo carga y `modelo.encode()` funciona sobre el corpus. Falta calcular los embeddings una sola vez al inicio y reusarlos, en vez de recalcular por consulta — es lo que vuelve la cosa usable.

## Ranking top-k por similitud coseno

Falta. Hoy el script ordena el corpus completo e imprime todo. Hay que recortar a k (3 o 5), devolver el score junto al texto, y meter ahí el umbral y el margen top-1 / top-2 que salieron del análisis.

## Búsqueda simple por palabras clave

Falta entera. Normalizar a minúsculas, quitar acentos y signos, partir en tokens, y puntuar por cantidad de términos de la consulta presentes en cada oración. Sin TF-IDF ni librerías: la gracia es que sea el baseline tonto contra el cual comparar.

## Comparación cualitativa entre ambos métodos

Falta. Correr las mismas consultas por los dos caminos y escribir dónde se separan. Lo interesante no es cuál gana en promedio, sino los casos donde el léxico acierta y el semántico se va por la tangente — o al revés. Ahí es donde aparece el material del análisis adversarial y donde el informe tiene algo que decir.

## Aparte del enunciado

- Las 5 oraciones de ataque ya están elegidas y justificadas (`CORPUS_MECANICA` en `main.py`). Falta entregarlas al equipo de mecánica automotriz.
- El blindaje descrito en el análisis (umbral, margen, cruce de métodos) todavía no está en el código.
