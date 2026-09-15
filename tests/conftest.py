# -*- coding: utf-8 -*-
"""
Fixtures Globais de Teste (pytest).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base


@pytest.fixture
def db_session():
    """Cria uma sessão de banco em memória SQLite isolada para testes."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
