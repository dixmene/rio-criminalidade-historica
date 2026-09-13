"""Script para inicializar todas as tabelas do banco de dados."""
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.database import engine, Base
import app.models  # Garante registro de todos os modelos


def init_database():
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Tabelas criadas com sucesso!")


if __name__ == "__main__":
    init_database()
