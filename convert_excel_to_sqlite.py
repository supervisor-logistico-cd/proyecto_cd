import datetime
import re
import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent
EXCEL_FILE = PROJECT_ROOT / "base_clientes_bees (7).xlsx"
SQLITE_FILE = PROJECT_ROOT / "clientes.db"


def normalize_name(value: str) -> str:
    text = str(value).strip()
    text = re.sub(r"[^\w]+", "_", text, flags=re.UNICODE)
    text = re.sub(r"_+", "_", text)
    return text.strip("_").lower() or "col"


def sqlite_type(series: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(series.dtype):
        return "TEXT"
    if pd.api.types.is_integer_dtype(series.dtype):
        return "INTEGER"
    if pd.api.types.is_float_dtype(series.dtype):
        return "REAL"
    if pd.api.types.is_bool_dtype(series.dtype):
        return "INTEGER"
    return "TEXT"


def normalize_value(value):
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, datetime.time):
        return value.isoformat()
    if isinstance(value, bool):
        return int(value)
    return value


def write_table(conn: sqlite3.Connection, table_name: str, df: pd.DataFrame) -> None:
    df = df.copy()
    df.columns = [normalize_name(col) for col in df.columns]
    df = df.where(pd.notna(df), None)
    columns = [(col, sqlite_type(df[col])) for col in df.columns]

    conn.execute(f'DROP TABLE IF EXISTS "{table_name}"')
    columns_sql = ", ".join(f'"{col}" {sql_type}' for col, sql_type in columns)
    conn.execute(f'CREATE TABLE "{table_name}" ({columns_sql})')

    placeholders = ", ".join("?" for _ in columns)
    column_names = ", ".join(f'"{col}"' for col, _ in columns)
    insert_sql = f'INSERT INTO "{table_name}" ({column_names}) VALUES ({placeholders})'

    rows = [tuple(normalize_value(value) for value in row) for row in df.itertuples(index=False, name=None)]
    if rows:
        conn.executemany(insert_sql, rows)
    if "codigocliente" in df.columns:
        conn.execute(
            f'CREATE INDEX IF NOT EXISTS idx_{table_name}_codigocliente ON "{table_name}" ("codigocliente")'
        )
    if "cliente" in df.columns:
        conn.execute(
            f'CREATE INDEX IF NOT EXISTS idx_{table_name}_cliente ON "{table_name}" ("cliente")'
        )


def main() -> None:
    if not EXCEL_FILE.exists():
        raise FileNotFoundError(f"No se encontró el archivo Excel: {EXCEL_FILE}")

    xls = pd.ExcelFile(EXCEL_FILE)
    print("Hojas encontradas:", xls.sheet_names)

    with sqlite3.connect(SQLITE_FILE) as conn:
        for sheet_name in xls.sheet_names:
            print(f"Importando hoja: {sheet_name}")
            df = pd.read_excel(xls, sheet_name=sheet_name)
            if df.empty:
                print("  (hoja vacía, se omite)")
                continue
            table_name = normalize_name(sheet_name)
            write_table(conn, table_name, df)
            print(f"  tabla '{table_name}' creada con {len(df)} filas")

    print("Base de datos creada en:", SQLITE_FILE)


if __name__ == "__main__":
    main()
