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
   python update_db.py
   ```
   Esto regenerará `clientes.db`, hará commit y hará push al repositorio.
3. Si quieres solo regenerar localmente sin commit ni push, usa:
   ```
   python update_db.py --no-commit
   ```
4. Si quieres regenerar y commitear, pero no hacer push todavía, usa:
   ```
   python update_db.py --no-push
   ```
5. Verifica la aplicación localmente:
   ```
   python app.py
   ```

### ¿Qué hace `update_db.py`?

- regenera `clientes.db` desde el Excel
- agrega `clientes.db` a git
- crea un commit con un mensaje automático
- empuja los cambios al remoto si no usas `--no-push`

> Si el repositorio está conectado a Render y la implementación automática está activada, cada push a `main` disparará un nuevo despliegue.

## Despliegue en Render

1. Crea una cuenta en https://render.com si no tienes una.
2. Conecta tu cuenta de GitHub desde Render.
3. En Render, crea un nuevo servicio de tipo **Web Service**.
4. Selecciona el repositorio `supervisor-logistico-cd/proyecto_cd`.
5. Elige la rama `main`.
6. Configura los comandos:
   - Build command: `python -m pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
7. Deja el entorno en Python 3.x (Render detecta la versión compatible).
8. Despliega el servicio.

### Opcional: recrear la base en Render

Si prefieres regenerar `clientes.db` en cada despliegue en lugar de subir el archivo, cambia el Build command a:

```bash
python -m pip install -r requirements.txt && python convert_excel_to_sqlite.py
```

> Con esta opción, Render crea `clientes.db` desde el Excel al desplegar.

## Despliegue posterior y actualizaciones

- Cada vez que hagas cambios en el Excel, ejecuta `python update_db.py`.
- Si usas el repositorio conectado a Render, el push hará que Render redepliegue automáticamente.
- Si Render no despliega automáticamente, puedes activar el deploy automático en la configuración del servicio o usar el botón de deploy manual desde el panel de Render.

1. Conecta este repositorio a tu cuenta de Render.
2. Crea un nuevo servicio Web Service.
3. Usa estos comandos:
   - Build command: `python -m pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
4. El archivo `clientes.db` ya está incluido en el repositorio para que la app funcione en Render.

> Nota: Si actualizas los datos en `base_clientes_bees (7).xlsx`, vuelve a ejecutar `python convert_excel_to_sqlite.py` para regenerar `clientes.db`.
