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
        source_type="livro",
        is_demo=True,
    )
    db_session.add(src)
    db_session.flush()
    assert src.id is not None

    # 2. Region
    reg = Region(
        name="Centro",
        region_type="bairro",
        latitude=-22.9035,
        longitude=-43.1824,
        is_demo=True,
    )
    db_session.add(reg)
    db_session.flush()
    assert reg.id is not None

    # 3. Organization
    org = Organization(name="[DEMO] OAB-RJ", acronym="OAB", is_demo=True)
    db_session.add(org)
    db_session.flush()
    assert org.id is not None

    # 4. Person
    pers = Person(name="[DEMO] Dra. Helena", is_demo=True)
    db_session.add(pers)
    db_session.flush()
    assert pers.id is not None

    # 5. Event
    ev = Event(
        title="[DEMO] Evento de Teste",
        date_start="1980-05-01",
        year=1980,
        description="Descrição detalhada para teste de persistência.",
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
    assert len(loaded_ev.people) == 1
    assert len(loaded_ev.regions) == 1
    assert loaded_ev.source_links[0].excerpt == "Trecho de teste com citação comprovada."
