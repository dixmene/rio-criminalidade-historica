import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.schemas import (
    EventCreate,
    EventSourceLinkInput,
    SourceCreate,
)
from app.services import IngestionService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_event_requires_sources():
    """Valida que o schema rejeita evento sem nenhuma fonte vinculada."""
    with pytest.raises(ValidationError):
        EventCreate(
            title="[DEMO] Evento Sem Fonte",
            date_start="1980-01-01",
            year=1980,
            description="Tentativa de inserção de evento sem comprovação bibliográfica.",
            confidence_level="confirmado",
            sources=[],  # Deve falhar (min_length=1)
        )


def test_event_ingestion_with_valid_source(db_session):
    """Valida ingestão completa com proveniência de fonte comprovada."""
    ingestion = IngestionService(db_session)

    # 1. Cria fonte
    src = ingestion.create_source(
        SourceCreate(
            title="[DEMO] Arquivo Histórico Oficial",
            citation="ARQUIVO. Documentos Oficiais, 1982.",
            publication_year=1982,
            source_type="documento_oficial",
            is_demo=True,
        )
    )

    # 2. Cria evento apontando para a fonte
    event_data = EventCreate(
        title="[DEMO] Evento Comprovado",
        date_start="1982-06-10",
        year=1982,
        description="Evento histórico rigorosamente documentado.",
        confidence_level="confirmado",
        is_demo=True,
        sources=[
            EventSourceLinkInput(
                source_id=src.id,
                page_or_section="p. 15-18",
                excerpt="O registro documental atesta expressamente o acontecimento na data indicada.",
                validation_status="confirmado",
            )
        ],
    )

    created_event = ingestion.create_event(event_data)
    assert created_event.id is not None
    assert len(created_event.source_links) == 1
    assert created_event.source_links[0].source_id == src.id
    assert created_event.source_links[0].validation_status == "confirmado"
