import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.connection import Base
from database.schema.models import (
    Source,
    Organization,
    Person,
    Region,
    Event,
    EventSource,
    TerritorialRelation,
    TerritorialRelationSource,
)


@pytest.fixture
def memory_db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_territorial_relation_with_provenance(memory_db):
    # 1. Fonte
    src = Source(
        title="[DEMO] Relatório Histórico",
        citation="RELATÓRIO. Documentação Histórica, 1980.",
        publication_year=1980,
        source_type="oficial_relatorio",
        is_demo=True,
    )
    memory_db.add(src)
    memory_db.flush()

    # 2. Região e Organização
    reg = Region(
        original_name="Complexo do Alemão",
        normalized_name="COMPLEXO DO ALEMAO",
        latitude=-22.8600,
        longitude=-43.2750,
        is_demo=True,
    )
    org = Organization(
        original_name="Comando Vermelho",
        normalized_name="COMANDO VERMELHO",
        acronym="CV",
        org_type="faccao_criminosa",
        is_demo=True,
    )
    memory_db.add_all([reg, org])
    memory_db.flush()

    # 3. Relação Territorial no Tempo
    rel = TerritorialRelation(
        organization_id=org.id,
        region_id=reg.id,
        date_start="1982-01-01",
        date_end="1985-12-31",
        relation_type="presenca_documentada",
        confidence_level="confirmado",
        is_demo=True,
    )
    memory_db.add(rel)
    memory_db.flush()

    # 4. Proveniência da Relação Territorial
    rel_src = TerritorialRelationSource(
        territorial_relation_id=rel.id,
        source_id=src.id,
        page_or_section="p. 33-35",
        excerpt="Documento atesta início da presença de lideranças no território.",
        validation_status="confirmado",
    )
    memory_db.add(rel_src)
    memory_db.commit()

    # Verificação
    loaded_rel = memory_db.query(TerritorialRelation).filter_by(id=rel.id).first()
    assert loaded_rel is not None
    assert loaded_rel.organization.normalized_name == "COMANDO VERMELHO"
    assert loaded_rel.region.normalized_name == "COMPLEXO DO ALEMAO"
    assert len(loaded_rel.source_links) == 1
    assert loaded_rel.source_links[0].source.title == "[DEMO] Relatório Histórico"
