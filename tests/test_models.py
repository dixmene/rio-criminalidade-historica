import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import (
    Base,
    Source,
    Person,
    Organization,
    Region,
    Event,
    EventSource,
    EventOrganization,
    EventPerson,
    EventRegion,
)

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_entities(db_session):
    # 1. Source
    src = Source(
        title="[DEMO] Fonte de Teste",
        citation="AUTOR. Livro de Teste, 1980.",
        publication_year=1980,
        source_type="academico_livro",
        is_demo=True,
    )
    db_session.add(src)
    db_session.flush()
    assert src.id is not None

    # 2. Region (com original_name e normalized_name)
    reg = Region(
        original_name="Centro",
        normalized_name="CENTRO",
        region_type="bairro",
        latitude=-22.9035,
        longitude=-43.1824,
        is_demo=True,
    )
    db_session.add(reg)
    db_session.flush()
    assert reg.id is not None
    assert reg.name == "Centro"

    # 3. Organization (com original_name e normalized_name)
    org = Organization(
        original_name="[DEMO] OAB-RJ",
        normalized_name="[DEMO] OAB-RJ",
        acronym="OAB",
        is_demo=True
    )
    db_session.add(org)
    db_session.flush()
    assert org.id is not None
    assert org.name == "[DEMO] OAB-RJ"

    # 4. Person (com original_name e normalized_name)
    pers = Person(
        original_name="[DEMO] Dra. Helena",
        normalized_name="[DEMO] DRA. HELENA",
        is_demo=True
    )
    db_session.add(pers)
    db_session.flush()
    assert pers.id is not None
    assert pers.name == "[DEMO] Dra. Helena"

    # 5. Event (com date_display e rigor temporal)
    ev = Event(
        title="[DEMO] Evento de Teste",
        date_display="01 de maio de 1980",
        date_start="1980-05-01",
        year=1980,
        exact_date=True,
        temporal_precision="dia",
        description="Descrição detalhada para teste de persistência e integridade.",
        confidence_level="confirmado",
        is_demo=True,
    )
    db_session.add(ev)
    db_session.flush()
    assert ev.id is not None

    # Associating
    ev_src = EventSource(
        event_id=ev.id,
        source_id=src.id,
        excerpt="Trecho de teste com citação comprovada.",
        validation_status="confirmado",
    )
    ev_org = EventOrganization(event_id=ev.id, organization_id=org.id, role_in_event="organizador")
    ev_pers = EventPerson(event_id=ev.id, person_id=pers.id, role_in_event="orador")
    ev_reg = EventRegion(event_id=ev.id, region_id=reg.id)

    db_session.add_all([ev_src, ev_org, ev_pers, ev_reg])
    db_session.commit()

    # Verificando relacionamentos
    loaded_ev = db_session.query(Event).filter(Event.id == ev.id).first()
    assert len(loaded_ev.sources) == 1
    assert loaded_ev.sources[0].title == "[DEMO] Fonte de Teste"
    assert len(loaded_ev.organizations) == 1
    assert loaded_ev.organizations[0].name == "[DEMO] OAB-RJ"
    assert len(loaded_ev.people) == 1
    assert loaded_ev.people[0].name == "[DEMO] Dra. Helena"
    assert len(loaded_ev.regions) == 1
    assert loaded_ev.regions[0].name == "Centro"
    assert loaded_ev.source_links[0].excerpt == "Trecho de teste com citação comprovada."
