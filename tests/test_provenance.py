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


def test_real_event_requires_sources_in_schema():
    """Valida que o schema Pydantic rejeita evento histórico real (is_demo=False) sem fontes."""
    with pytest.raises(ValidationError) as exc_info:
        EventCreate(
            title="Evento Real Sem Fonte",
            date_display="1980-01-01",
            description="Tentativa de inserção de evento real sem fonte documental.",
            confidence_level="confirmado",
            is_demo=False,
            sources=[],  # Deve falhar obrigatoriamente
        )
    assert "Regra de Proveniência Violada" in str(exc_info.value)


def test_real_event_rejected_in_service_without_sources(db_session):
    """Valida que o IngestionService rejeita inserção de evento histórico real sem fontes."""
    ingestion = IngestionService(db_session)

    # Cria dados mínimos usando schema com is_demo=True para burlar Pydantic inicial,
    # mas tentando forçar is_demo=False no serviço
    event_data = EventCreate(
        title="Evento Teste",
        date_display="1980-01-01",
        description="Tentativa direta de registrar evento sem fontes.",
        confidence_level="confirmado",
        is_demo=True,  # Inicialmente demo
        sources=[],
    )
    # Altera para evento real
    event_data.is_demo = False

    with pytest.raises(ValueError) as exc_info:
        ingestion.create_event(event_data)
    assert "Regra de Domínio Violada" in str(exc_info.value)


def test_real_event_with_valid_source_allowed(db_session):
    """Valida ingestão bem-sucedida de evento histórico real quando proveniência existe."""
    ingestion = IngestionService(db_session)

    src = ingestion.create_source(
        SourceCreate(
            title="Documento Histórico Oficial",
            citation="ARQUIVO NACIONAL. Fundo Documental, 1982.",
            publication_year=1982,
            source_type="oficial_relatorio",
            is_demo=False,
        )
    )

    event_data = EventCreate(
        title="Evento Comprovado em Fonte",
        date_display="10 de junho de 1982",
        description="Acontecimentos rigorosamente documentados em arquivo primário.",
        confidence_level="confirmado",
        is_demo=False,
        sources=[
            EventSourceLinkInput(
                source_id=src.id,
                page_or_section="Folha 42",
                excerpt="O registro documental atesta expressamente a deliberação na data indicada.",
                validation_status="confirmado",
            )
        ],
    )

    event = ingestion.create_event(event_data)
    assert event.id is not None
    assert event.is_demo is False
    assert len(event.sources) == 1
    assert event.sources[0].title == "Documento Histórico Oficial"
    assert event.source_links[0].excerpt.startswith("O registro documental")
