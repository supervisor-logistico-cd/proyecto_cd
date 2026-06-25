# App Web de Consulta de Clientes

Esta aplicación usa SQLite como base de datos y Flask como backend.

## Cómo usar

1. Ejecuta `python convert_excel_to_sqlite.py` para crear `clientes.db` desde `base_clientes_bees (7).xlsx`.
2. Ejecuta `python app.py` para iniciar el servidor.
3. Abre `http://127.0.0.1:5000` en tu navegador.

## Despliegue en Render

1. Sube este proyecto a GitHub o a un repositorio Git accesible.
2. Crea una cuenta en render.com y conecta tu repositorio.
3. Crea un nuevo servicio web (Web Service).
4. Selecciona la rama del repositorio.
5. En `Build Command`, usa:
   - `pip install -r requirements.txt`
   - Si quieres generar `clientes.db` durante el despliegue, usa `python convert_excel_to_sqlite.py` después de la instalación.
6. En `Start Command`, usa:
   - `gunicorn app:app`

> Render detecta automáticamente Python y usará el archivo `Procfile` si existe.

## Archivos

- `consulta_cliente.html`: interfaz principal de la app.
- `convert_excel_to_sqlite.py`: convierte el Excel a `clientes.db`.
- `clientes.db`: base de datos SQLite generada.
- `app.py`: servidor Flask con las APIs de búsqueda y actualización.
- `requirements.txt`: dependencias Python necesarias.
- `base_clientes_bees (7).xlsx`: datos originales en Excel.
