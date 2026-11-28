import subprocess
import time
from pathlib import Path
from uuid import uuid4

RAIZ = Path(__file__).resolve().parents[1]


def esperar_postgres(contenedor):
    # La instancia temporal de initdb usa solo sockets Unix.
    for _ in range(60):
        resultado = subprocess.run(
            ["docker", "exec", contenedor, "pg_isready", "-h", "127.0.0.1", "-U", "postgres"],
            stdout=subprocess.DEVNULL,
        )
        if resultado.returncode == 0:
            return
        time.sleep(1)
    raise SystemExit("Postgres no estuvo disponible en 60 segundos")


def aplicar_sql(contenedor, ruta):
    print(f"Aplicando {ruta.relative_to(RAIZ)}", flush=True)
    subprocess.run(
        ["docker", "exec", "-i", "-e", "PGCLIENTENCODING=UTF8", contenedor,
         "psql", "-X", "-U", "postgres", "-v", "ON_ERROR_STOP=1"],
        input=ruta.read_bytes(),
        check=True,
    )


def main():
    contenedor = f"portika-esquema-{uuid4().hex}"
    subprocess.run(
        ["docker", "run", "--rm", "-d", "--name", contenedor, "-p", "127.0.0.1::5432",
         "-e", "POSTGRES_HOST_AUTH_METHOD=trust", "postgres:15.8", "-c", "wal_level=logical"],
        check=True,
    )
    try:
        esperar_postgres(contenedor)
        pruebas = RAIZ / "tests/esquema"
        migraciones = sorted((RAIZ / "supabase/migrations").glob("*.sql"))
        for ruta in [pruebas / "stubs_supabase.sql", *migraciones,
                     RAIZ / "supabase/seed.sql", pruebas / "verificar.sql"]:
            aplicar_sql(contenedor, ruta)
    finally:
        subprocess.run(["docker", "rm", "-f", contenedor], check=True)
    print("Esquema verificado en PostgreSQL 15.8")


if __name__ == "__main__":
    main()
