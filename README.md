# App Web de Consulta de Clientes

Este repositorio contiene una aplicación Flask que busca clientes en una base de datos SQLite y permite actualizar el contacto.

Repositorio GitHub:
https://github.com/supervisor-logistico-cd/proyecto_cd

## Contenido

- `app.py`: servidor Flask con APIs para búsqueda y actualización.
- `consulta_cliente.html`: interfaz web principal.
- `convert_excel_to_sqlite.py`: crea `clientes.db` desde el archivo Excel local.
- `clientes.db`: base de datos SQLite incluida para que la app funcione directamente.
- `requirements.txt`: dependencias Python.
- `Procfile`: comando de inicio para Render.
- `base_clientes_bees (7).xlsx`: fuente de datos original local (no se incluye en el repositorio).

## Uso local

1. Instala dependencias:
   ```
   python -m pip install -r requirements.txt
   ```
2. Genera la base de datos si necesitas recrearla o si cambias los datos en el Excel:
   ```
   python convert_excel_to_sqlite.py
   ```
3. Inicia el servidor:
   ```
   python app.py
   ```
4. Abre en el navegador:
   ```
   http://127.0.0.1:5000
   ```

## Actualizar datos

Si cambias cualquiera de las hojas de datos en `base_clientes_bees (7).xlsx` —por ejemplo la hoja de clientes, la hoja de `cashless` o cualquier otra hoja— sigue estos pasos:

1. Guarda el archivo Excel con los cambios.
2. Ejecuta:
   ```
   python convert_excel_to_sqlite.py
   ```
   Esto volverá a crear `clientes.db` con todas las hojas.
3. Verifica la aplicación localmente:
   ```
   python app.py
   ```
4. Haz commit y push de `clientes.db` al repositorio si quieres que el servidor en Render tome los datos actualizados:
   ```
   git add clientes.db
   git commit -m "Actualizar clientes.db tras cambios en Excel"
   git push
   ```

> Nota: Si no quieres subir `clientes.db` al repositorio, puedes mantenerlo local y regenerarlo en cada despliegue usando `python convert_excel_to_sqlite.py` antes de iniciar el servidor.

## Despliegue en Render

1. Conecta este repositorio a tu cuenta de Render.
2. Crea un nuevo servicio Web Service.
3. Usa estos comandos:
   - Build command: `python -m pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
4. El archivo `clientes.db` ya está incluido en el repositorio para que la app funcione en Render.

> Nota: Si actualizas los datos en `base_clientes_bees (7).xlsx`, vuelve a ejecutar `python convert_excel_to_sqlite.py` para regenerar `clientes.db`.
