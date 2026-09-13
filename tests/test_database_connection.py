import pytest
from sqlalchemy import text
from src.database.connection import engine, check_database_health, SessionLocal, Base
import database.schema.models  # Registra modelos


def test_database_health():
    health = check_database_health()
    assert health["status"] == "healthy"
    assert "dialect" in health


def test_database_tables_creation():
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        # Verifica se as tabelas principais foram criadas
        result = conn.execute(text("SELECT 1 FROM sources LIMIT 1"))
        assert result is not None
