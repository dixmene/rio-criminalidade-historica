"""
Script de Verificação de Conectividade e Integridade do Banco de Dados.
"""
import sys
from src.database.connection import check_database_health, engine, Base
import database.schema.models  # Garante registro dos modelos

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def verify_database():
    print("=== VERIFICAÇÃO DE SAÚDE DO BANCO DE DADOS ===\n")
    health = check_database_health()
    print(f"Status: {health.get('status')}")
    print(f"Dialeto: {health.get('dialect')}")
    print(f"URL: {health.get('database_url')}")

    if health.get("status") == "healthy":
        print("\nCriando/verificando tabelas do schema...")
        Base.metadata.create_all(bind=engine)
        print("[OK] Conexão ativa e tabelas verificadas com sucesso!")
    else:
        print(f"\n[ERRO] Falha ao conectar: {health.get('error')}")


if __name__ == "__main__":
    verify_database()
