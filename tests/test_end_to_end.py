import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.schemas import (
    SourceCreate,
    RegionCreate,
    OrganizationCreate,
    PersonCreate,
    EventCreate,
    EventSourceLinkInput,
    EventOrganizationLinkInput,
    EventPersonLinkInput,
    EventRegionLinkInput,
)
from app.services import IngestionService, EventService


@pytest.fixture
def memory_db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_complete_end_to_end_lifecycle(memory_db):
    """
    TESTE END-TO-END:
    Fonte -> Ingestão -> Região -> Organização -> Pessoa -> Evento com Proveniência
    -> Consulta via EventService -> Validação do Grafo Completo.
    """
    ingestion = IngestionService(memory_db)
    service = EventService(memory_db)

    # 1. Criação da Fonte
    src = ingestion.create_source(
        SourceCreate(
            title="Dossiê do Arquivo Público do Estado",
            citation="APERJ. Relatório Histórico de Conflitos Territoriais. Rio de Janeiro: Fundo Segurança, 1982.",
            author="Pesquisador Arquivístico",
            publisher="Arquivo Público",
            publication_year=1982,
            source_type="oficial_relatorio",
            archive_ref="Caixa 18, Documento 4",
            is_demo=False,
        )
    )
    assert src.id is not None

    # 2. Criação de Território/Região (com normalização automática e coordenadas)
    reg_centro = ingestion.create_region(
        RegionCreate(
            original_name="Centro Histórico",
            region_type="bairro",
            municipality="Rio de Janeiro",
            latitude=-22.9035,
            longitude=-43.1824,
            location_precision="exata",
            is_demo=False,
        )
    )
    assert reg_centro.normalized_name == "CENTRO HISTORICO"

    # Criação de Território/Região SEM COORDENADAS (garante que não inventa coordenadas!)
    reg_sem_coords = ingestion.create_region(
        RegionCreate(
            original_name="Fronteira Histórica dos Loteamentos",
            region_type="territorio_historico",
            municipality="Nova Iguaçu",
            latitude=None,
            longitude=None,
            location_precision="desconhecida",
            is_demo=False,
        )
    )
    assert reg_sem_coords.has_coordinates is False
    assert reg_sem_coords.latitude is None

    # 3. Criação de Organização (com normalização automática)
    org = ingestion.create_organization(
        OrganizationCreate(
            original_name="Associação dos Moradores da Guanabara",
            acronym="AMG",
            org_type="sociedade_civil",
            foundation_year=1978,
            is_demo=False,
        )
    )
    assert org.normalized_name == "ASSOCIACAO DOS MORADORES DA GUANABARA"

    # 4. Criação de Pessoa/Liderança (com normalização automática)
    person = ingestion.create_person(
        PersonCreate(
            original_name="Manoel Gonçalves de Souza",
            aliases="Mané da Associação",
            role_description="Representante Comunitário",
            birth_year=1935,
            is_demo=False,
        )
    )
    assert person.normalized_name == "MANOEL GONCALVES DE SOUZA"

    # 5. Criação do Evento Histórico Real (com rigor temporal e proveniência obrigatória)
    event_input = EventCreate(
        title="Fundação da Coordenação Unificada de Bairros",
        date_display="14 de novembro de 1982",
        event_type="fundacao",
        description="Assembleia geral reunindo lideranças comunitárias no Centro do Rio de Janeiro.",
        historical_context="Processo de abertura política e reorganização social.",
        confidence_level="confirmado",
        is_demo=False,
        sources=[
            EventSourceLinkInput(
                source_id=src.id,
                page_or_section="p. 15-18",
                excerpt="Em 14 de novembro de 1982, representantes aprovaram o estatuto da coordenação unificada.",
                claim_assertion="Fundação documentada em ata oficial.",
                validation_status="confirmado",
                confidence_notes="Ata registrada em cartório público.",
            )
        ],
        organizations=[
            EventOrganizationLinkInput(
                organization_id=org.id,
                role_in_event="entidade_fundadora"
            )
        ],
        people=[
            EventPersonLinkInput(
                person_id=person.id,
                role_in_event="orador_principal"
            )
        ],
        regions=[
            EventRegionLinkInput(
                region_id=reg_centro.id,
                specific_location_name="Sede Histórica no Centro"
            )
        ],
    )

    created_event = ingestion.create_event(event_input)
    assert created_event.id is not None
    assert created_event.year == 1982
    assert created_event.exact_date is True

    # 6. Consulta através do EventService (simulando a interface e filtros)
    events_found = service.list_events(
        year_min=1980,
        year_max=1985,
        region_id=reg_centro.id,
        organization_id=org.id,
        person_id=person.id,
        is_demo=False,
    )

    assert len(events_found) == 1
    ev = events_found[0]
    assert ev.title == "Fundação da Coordenação Unificada de Bairros"
    assert ev.date_display == "14 de novembro de 1982"

    # 7. Verificação do Grafo Completo e Rastreabilidade
    # Fontes
    assert len(ev.sources) == 1
    assert ev.sources[0].title == "Dossiê do Arquivo Público do Estado"
    assert ev.source_links[0].excerpt.startswith("Em 14 de novembro de 1982")
    assert ev.source_links[0].validation_status == "confirmado"

    # Organizações
    assert len(ev.organizations) == 1
    assert ev.organizations[0].original_name == "Associação dos Moradores da Guanabara"
    assert ev.organizations[0].normalized_name == "ASSOCIACAO DOS MORADORES DA GUANABARA"

    # Pessoas
    assert len(ev.people) == 1
    assert ev.people[0].original_name == "Manoel Gonçalves de Souza"
    assert ev.people[0].normalized_name == "MANOEL GONCALVES DE SOUZA"

    # Territórios
    assert len(ev.regions) == 1
    assert ev.regions[0].original_name == "Centro Histórico"
    assert ev.regions[0].has_coordinates is True
