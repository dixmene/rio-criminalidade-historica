from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import DATABASE_URL

# SQLite requires check_same_thread=False for multithreaded environments like Streamlit
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    future=True,
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record) -> None:
    """Apply integrity and read-performance PRAGMAs on SQLite connections."""
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.execute("PRAGMA cache_size=-16000")
            cursor.execute("PRAGMA mmap_size=67108864")
        finally:
            cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency helper to yield database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
