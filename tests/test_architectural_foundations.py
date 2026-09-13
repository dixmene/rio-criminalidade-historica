"""
Testes de Fundamentação Arquitetural e Epistemológica.
Valida:
1. Modelo Temporal Rigoroso (Intervalos de Conhecimento: date_start, date_end, date_is_estimated)
2. Proveniência Granular em EventSource (page, section, excerpt, claim, source_assessment)
3. Ausência de Defaults Artificiais (Region.municipality estritamente NULL quando não informado)
4. Geografia PostGIS e Vigência Temporal de Perímetros (geometry_type, valid_from/to)
5. Entidade Epistemológica Claim (Controvérsias historiográficas e posturas apoia/contesta)
"""

from datetime import date
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from app.models import (
    Base,
    Event,
    Source,
    Region,
    Claim,
    ClaimSource,
    EventSource,
)
from app.schemas import (
    EventCreate,
    EventSourceLinkInput,
    SourceCreate,
    RegionCreate,
    ClaimCreate,
    ClaimSourceLinkInput,
)
from app.services.ingestion_service import IngestionService
from app.services.event_service import EventService


@pytest.fixture
def db():
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    
    @event.listens_for(test_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=test_engine)
    TestingSession = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


def test_rigorous_temporal_model_intervals(db):
    """1. Testa o modelo temporal com intervalos de conhecimento (date_start/end como Date)."""
    ingestion = IngestionService(db)
    
    # Criar fonte para garantir proveniência
    src = ingestion.create_source(SourceCreate(
        title="[TESTE] Documento Temporal",
        citation="DOC. Rio de Janeiro, 1978.",
        publication_year=1978,
        source_type="oficial_relatorio",
        is_demo=True,
    ))

    # Evento com ano de 1978 (intervalo de conhecimento: 01/01/1978 a 31/12/1978)
    ev_data = EventCreate(
        title="[TESTE] Evento com Intervalo Temporal Anual",
        date_display="em 1978",
        date_start=date(1978, 1, 1),
        date_end=date(1978, 12, 31),
        temporal_precision="ano",
        date_is_estimated=True,
        exact_date=False,
        year=1978,
        description="Acontecimento histórico documentado apenas com o ano na fonte primária.",
        confidence_level="provavel",
        is_demo=True,
        sources=[
            EventSourceLinkInput(
                source_id=src.id,
                excerpt="Ocorrido durante o decorrer do ano de 1978 no sistema penitenciário.",
                page="45",
                section="Capítulo 2",
                source_assessment="oficial",
                confidence_level="provavel"
            )
        ]
    )
    ev = ingestion.create_event(ev_data)
    assert ev.id is not None
    assert isinstance(ev.date_start, date)
    assert isinstance(ev.date_end, date)
    assert ev.date_start == date(1978, 1, 1)
    assert ev.date_end == date(1978, 12, 31)
    assert ev.date_is_estimated is True
    assert ev.temporal_precision == "ano"

    # Consulta temporal: buscar se 15 de junho de 1978 está dentro do intervalo
    found = db.query(Event).filter(
        Event.date_start <= date(1978, 6, 15),
        Event.date_end >= date(1978, 6, 15),
        Event.id == ev.id
    ).first()
    assert found is not None, "Consulta por intervalo de conhecimento deve localizar o evento de 1978."


def test_region_municipality_has_no_artificial_default(db):
    """2. Testa a regra NULL ≠ 0: ausência de município DEVE persistir como NULL estrito."""
    ingestion = IngestionService(db)

    # Criação sem informar município
    reg_data = RegionCreate(
        original_name="[TESTE] Morro Desconhecido",
        region_type="favela",
        municipality=None,
        is_demo=True
    )
    reg = ingestion.create_region(reg_data)
    assert reg.id is not None
    assert reg.municipality is None, "Município não informado deve ser estritamente NULL, sem preenchimento automático."


def test_region_spatial_temporal_fields_postgis_readiness(db):
    """3. Testa campos de vigência temporal de perímetros e tipologia geométrica."""
    ingestion = IngestionService(db)

    reg_data = RegionCreate(
        original_name="[TESTE] Complexo da Maré (Perímetro Histórico 1980–1995)",
        region_type="complexo",
        municipality="Rio de Janeiro",
        geometry_type="Polygon",
        geometry_source="IPP Sabren",
        geometry_confidence="alta",
        geometry_valid_from=date(1980, 1, 1),
        geometry_valid_to=date(1995, 12, 31),
        latitude=-22.855,
        longitude=-43.245,
        location_precision="centroide",
        is_demo=True
    )
    reg = ingestion.create_region(reg_data)
    assert reg.id is not None
    assert reg.geometry_type == "Polygon"
    assert reg.geometry_source == "IPP Sabren"
    assert reg.geometry_valid_from == date(1980, 1, 1)
    assert reg.geometry_valid_to == date(1995, 12, 31)


def test_eventsource_granular_provenance_fields(db):
    """4. Testa a proveniência detalhada na tabela associativa EventSource."""
    ingestion = IngestionService(db)
    src = ingestion.create_source(SourceCreate(
        title="[TESTE] Inquérito Policial Militar nº 45",
        citation="IPM 45. Relatório do encarregado, 1982.",
        publication_year=1982,
        source_type="documento_judicial",
        is_demo=True,
    ))

    ev_data = EventCreate(
        title="[TESTE] Operação de Cerco",
        date_display="14 de maio de 1982",
        date_start=date(1982, 5, 14),
        date_end=date(1982, 5, 14),
        temporal_precision="dia",
        exact_date=True,
        year=1982,
        description="Cerco policial com confronto armado.",
        confidence_level="conflitante",
        is_demo=True,
        sources=[
            EventSourceLinkInput(
                source_id=src.id,
                page="143",
                section="Anexo Pericial B",
                excerpt="O grupo realizou disparos de fuzil Fal 7.62 a partir do topo da laje.",
                claim="Disparos de fuzil efetuados a partir da laje",
                source_assessment="pericial_oficial",
                assessment_notes="Laudo balístico preliminar da polícia técnica.",
                confidence_level="conflitante"
            )
        ]
    )
    ev = ingestion.create_event(ev_data)
    assert len(ev.source_links) == 1
    link = ev.source_links[0]
    assert link.page == "143"
    assert link.section == "Anexo Pericial B"
    assert "Fal 7.62" in link.excerpt
    assert link.claim == "Disparos de fuzil efetuados a partir da laje"
    assert link.source_assessment == "pericial_oficial"
    assert link.confidence_level == "conflitante"


def test_claim_entity_and_conflicting_historical_stances(db):
    """5. Testa a entidade epistemológica Claim com versões conflitantes (apoia vs contesta)."""
    ingestion = IngestionService(db)
    service = EventService(db)

    # Criar duas fontes com versões divergentes sobre o mesmo acontecimento
    src_oficial = ingestion.create_source(SourceCreate(
        title="[TESTE] Boletim da Secretaria de Segurança (1984)",
        citation="BOLETIM SSP-RJ. Ocorrências Zona Norte. 1984.",
        publication_year=1984,
        source_type="oficial_relatorio",
        is_demo=True,
    ))
    src_imprensa = ingestion.create_source(SourceCreate(
        title="[TESTE] Reportagem Investigativa Jornal do Brasil (1984)",
        citation="JORNAL DO BRASIL. Disputa armada no morro. Edição de 12/08/1984.",
        publication_year=1984,
        source_type="jornalismo_investigativo",
        is_demo=True,
    ))

    # Evento guarda-chuva
    ev = ingestion.create_event(EventCreate(
        title="[TESTE] Confronto e Disputa Territorial em Brás de Pina",
        date_display="agosto de 1984",
        date_start=date(1984, 8, 1),
        date_end=date(1984, 8, 31),
        temporal_precision="mes",
        year=1984,
        description="Confronto territorial gerando versões conflitantes sobre controle de pontos de venda.",
        confidence_level="conflitante",
        is_demo=True,
        sources=[
            EventSourceLinkInput(
                source_id=src_oficial.id,
                excerpt="Ocorrência registrada como tiroteio entre quadrilhas rivais sem domínio consolidado.",
                confidence_level="conflitante"
            )
        ]
    ))

    # Criar Afirmação 1: CV consolidou o controle do território
    claim1 = ingestion.create_claim(ClaimCreate(
        event_id=ev.id,
        claim_type="territorio",
        statement="A facção Comando Vermelho consolidou hegemonia territorial sobre os pontos em agosto de 1984.",
        confidence_level="conflitante",
        is_disputed=True,
        epistemological_notes="A imprensa afirma controle consolidado, enquanto a polícia registrava como disputa aberta.",
        is_demo=True,
        sources=[
            ClaimSourceLinkInput(
                source_id=src_imprensa.id,
                stance="apoia",
                page="p. 8",
                section="Caderno Cidade",
                excerpt="Fontes locais confirmam que os novos operadores ligados ao CV passaram a gerenciar a venda.",
                source_assessment="jornalistica_independente",
                confidence_level="provavel"
            ),
            ClaimSourceLinkInput(
                source_id=src_oficial.id,
                stance="contesta",
                page="p. 12",
                section="Relatório de Inteligência",
                excerpt="Não há elementos probatórios de domínio consolidado de qualquer facção na localidade até o fim do trimestre.",
                source_assessment="oficial_policial",
                confidence_level="conflitante"
            )
        ]
    ))

    assert claim1.id is not None
    assert claim1.is_disputed is True
    assert len(claim1.source_links) == 2
    assert len(claim1.supporting_sources) == 1
    assert len(claim1.contradicting_sources) == 1
    assert claim1.supporting_sources[0].id == src_imprensa.id
    assert claim1.contradicting_sources[0].id == src_oficial.id

    # Consultar claims do evento via service
    event_claims = service.list_claims(event_id=ev.id)
    assert len(event_claims) == 1
    assert event_claims[0].claim_type == "territorio"
    assert event_claims[0].is_disputed is True
