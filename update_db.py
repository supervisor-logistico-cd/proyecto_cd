import argparse
import datetime
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
EXCEL_FILE = PROJECT_ROOT / "base_clientes_bees (7).xlsx"
DB_FILE = PROJECT_ROOT / "clientes.db"

GIT_EXE = shutil.which("git") or Path(r"C:\Program Files\Git\cmd\git.exe")


def run_command(command, cwd=PROJECT_ROOT):
    print("Ejecutando:", " ".join(str(p) for p in command))
    subprocess.run(command, cwd=cwd, check=True)


def ensure_git_available():
    if not GIT_EXE:
        raise RuntimeError("No se encontró git en PATH ni en la ruta esperada.")
    return str(GIT_EXE)


def regenerate_database():
    if not EXCEL_FILE.exists():
        raise FileNotFoundError(f"No se encontró el archivo de datos: {EXCEL_FILE}")
    run_command([sys.executable, "convert_excel_to_sqlite.py"])
    print("Base de datos regenerada en:", DB_FILE)


def git_commit_and_push(message: str, push: bool):
    git = ensure_git_available()
    if not DB_FILE.exists():
        raise FileNotFoundError(f"No se encontró el archivo de base de datos: {DB_FILE}")

    run_command([git, "add", str(DB_FILE)])
    run_command([git, "commit", "-m", message])
    if push:
        run_command([git, "push"])


def main():
    parser = argparse.ArgumentParser(description="Regenera clientes.db desde Excel y opcionalmente hace git commit/push.")
    parser.add_argument("--no-push", action="store_true", help="No hace push al repositorio después del commit.")
    parser.add_argument("--no-commit", action="store_true", help="No hace commit ni push, solo regenera la base de datos.")
    parser.add_argument("--message", default=None, help="Mensaje de commit para los cambios de la base de datos.")
    args = parser.parse_args()

    regenerate_database()

    if args.no_commit:
        print("Se regeneró la base de datos. No se hizo commit ni push.")
        return

    message = args.message or f"Actualizar clientes.db tras cambios en Excel ({datetime.datetime.now():%Y-%m-%d %H:%M})"
    git_commit_and_push(message, not args.no_push)
    print("Actualización completada.")


if __name__ == "__main__":
    main()
