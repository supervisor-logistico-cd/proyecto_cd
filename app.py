import sqlite3
from pathlib import Path
from flask import Flask, jsonify, render_template, request, send_from_directory

PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "clientes.db"

app = Flask(__name__, template_folder=".", static_folder=".")


@app.route('/favicon.png')
def favicon():
    return send_from_directory(str(PROJECT_ROOT), 'favicon.png')


def normalize_code(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.endswith('.0'):
        text = text[:-2]
    return text


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("consulta_cliente.html")


@app.route("/api/indice")
def api_indice():
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT codigocliente, cliente FROM base_bees WHERE codigocliente IS NOT NULL"
        )
        items = [
            {"c": normalize_code(row["codigocliente"]), "n": row["cliente"] or ""}
            for row in cursor.fetchall()
        ]
    return jsonify(items)


@app.route("/api/detalle")
def api_detalle():
    codigo = normalize_code(request.args.get("codigo", ""))
    if not codigo:
        return jsonify({"ok": False, "msg": "Código vacío."})

    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM base_bees WHERE CAST(codigocliente AS TEXT)=? OR CAST(identificacion AS TEXT)=? LIMIT 1",
            (codigo, codigo),
        ).fetchone()
        if not row:
            return jsonify({"ok": False, "msg": "Cliente no encontrado."})

        com = (row["com"] or "").strip()
        representante = ""
        if com:
            rep = conn.execute(
                "SELECT nombre FROM representantes WHERE sector=? LIMIT 1",
                (com,),
            ).fetchone()
            if rep:
                representante = rep["nombre"] or ""

        eta_row = conn.execute(
            "SELECT eta_inicia, eta_final FROM eta WHERE CAST(codigo AS TEXT)=? LIMIT 1",
            (codigo,),
        ).fetchone()
        eta_inicia = eta_row["eta_inicia"] if eta_row else ""
        eta_final = eta_row["eta_final"] if eta_row else ""

        estado = {
            "cashless": bool(conn.execute("SELECT 1 FROM cashless WHERE CAST(codigo AS TEXT)=? LIMIT 1", (codigo,)).fetchone()),
            "nps": bool(conn.execute("SELECT 1 FROM predictiva WHERE CAST(poc_id AS TEXT)=? LIMIT 1", (codigo,)).fetchone()),
            "rechazo": bool(conn.execute("SELECT 1 FROM rechazos WHERE CAST(codigo AS TEXT)=? LIMIT 1", (codigo,)).fetchone()),
        }

        def parse_float(value):
            try:
                s = str(value).strip().replace(',', '.')
                v = float(s)
                # valores plausibles ya en grados
                if -90 <= v <= 90:
                    return v
                # intentar divisores comunes: 1e6 (microgrados) preferido si da valor >=1
                v6 = v / 1e6
                if -90 <= v6 <= 90 and abs(v6) >= 1:
                    return v6
                # probar 1e5 (posible falta de un decimal)
                v5 = v / 1e5
                if -90 <= v5 <= 90 and abs(v5) >= 1:
                    return v5
                # si ninguno >=1, escoger el que quede en rango -90..90 con valor más grande
                candidates = []
                if -90 <= v6 <= 90:
                    candidates.append(v6)
                if -90 <= v5 <= 90:
                    candidates.append(v5)
                if candidates:
                    # elegir candidato con mayor magnitud
                    return max(candidates, key=lambda x: abs(x))
                return v6 if -90 <= v6 <= 90 else (v5 if -90 <= v5 <= 90 else None)
            except Exception:
                return None

        lat = parse_float(row["latitud"])
        lng = parse_float(row["longitud"])

        result = {
            "ok": True,
            "codigo": normalize_code(row["codigocliente"]),
            "cliente": row["cliente"] or "",
            "propietario": row["propietario"] or "",
            "com": com,
            "representante": representante,
            "municipio": row["municipio"] or "",
            "barrio": row["barrio"] or "",
            "direccion": row["direccion"] or "",
            "dias_entrega": row["dias_entrega"] or "",
            "telefono": normalize_code(row["telefono_final"]),
            "eta_inicia": eta_inicia or "",
            "eta_final": eta_final or "",
            "lat": lat,
            "lng": lng,
            "estado": estado,
        }

    return jsonify(result)


@app.route("/api/contacto")
def api_contacto():
    codigo = normalize_code(request.args.get("codigo", ""))
    if not codigo:
        return jsonify({"ok": False, "msg": "Código vacío."})

    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT codigocliente, cliente, com, telefono_final FROM base_bees WHERE CAST(codigocliente AS TEXT)=? OR CAST(identificacion AS TEXT)=? LIMIT 1",
            (codigo, codigo),
        ).fetchone()
        if not row:
            return jsonify({"ok": False, "msg": "Cliente no encontrado."})

        return jsonify({
            "ok": True,
            "codigo": normalize_code(row["codigocliente"]),
            "cliente": row["cliente"] or "",
            "com": (row["com"] or "").strip(),
            "telefono": normalize_code(row["telefono_final"]),
        })


@app.route("/api/guardar", methods=["POST"])
def api_guardar():
    datos = request.get_json(silent=True) or {}
    codigo = normalize_code(datos.get("codigo"))
    nuevo = normalize_code(datos.get("numero_nuevo"))
    encargado = str(datos.get("encargado", "")).strip()
    numero_actual = normalize_code(datos.get("numero_actual"))

    if not codigo:
        return jsonify({"ok": False, "msg": "Falta el código del cliente."})
    if len(nuevo) < 7:
        return jsonify({"ok": False, "msg": "El número nuevo no es válido."})
    if not encargado:
        return jsonify({"ok": False, "msg": "Indica quién está actualizando."})

    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO actualizado (codigocliente, cliente, com, numero_actual, numero_actualizado, encargado) VALUES (?, ?, ?, ?, ?, ?)",
            (codigo, datos.get("cliente", ""), datos.get("com", ""), numero_actual, nuevo, encargado),
        )
        conn.commit()

    return jsonify({"ok": True, "msg": "Contacto actualizado y guardado."})


if __name__ == "__main__":
    if not DB_PATH.exists():
        raise RuntimeError("Primero ejecuta convert_excel_to_sqlite.py para crear clientes.db")
    app.run(host="0.0.0.0", port=5000, debug=True)
