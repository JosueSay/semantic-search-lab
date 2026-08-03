# Instalación y uso

Documento parcial del laboratorio de búsqueda semántica. Índice completo en el [README](../README.md).

## Dependencias

```bash
pip install sentence-transformers numpy scikit-learn
```

Con el entorno virtual del repositorio:

```bash
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install sentence-transformers numpy scikit-learn
```

La primera corrida descarga `paraphrase-multilingual-MiniLM-L12-v2` desde Hugging Face (varios cientos de MB) y lo deja cacheado en `~/.cache/huggingface`. De ahí en adelante corre offline.

## Modos

```bash
python main.py prueba      # consultas del enunciado, semántico contra léxico
python main.py ambiguas    # consultas con palabras puente, con blindaje
python main.py palabras    # consultas de una sola palabra
python main.py ataque      # nuestras 5 oraciones contra el proxy de mecánica
python main.py defensa     # oraciones intrusas inyectadas en el corpus propio
python main.py consulta    # oraciones intrusas usadas como consulta, sin indexar
```

Sin argumento corre `prueba`.

Los modos `defensa` y `consulta` son las dos lecturas del ejercicio adversarial y conviene correr los dos. Ver [analisis-adversarial.md](analisis-adversarial.md).

## Regenerar los logs

```bash
for m in prueba ambiguas palabras ataque defensa consulta; do
    python main.py $m > logs/$m.log
done
```

En Windows, si la salida sale con caracteres rotos, forzar UTF-8:

```bash
python -X utf8 main.py prueba > logs/prueba.log
```

## Caché de embeddings

Los embeddings se guardan en `embeddings/embeddings-<huella>.npy`, donde la huella es un hash del corpus. Al cambiar el corpus se genera un archivo nuevo en lugar de reutilizar el viejo, que ya no correspondería a las oraciones actuales.

Para forzar el recálculo:

```bash
rm -rf embeddings
```
