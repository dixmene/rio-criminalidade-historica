from typing import List
from sqlalchemy.orm import Session
from app.models import (
    Event,
    Source,
    Person,
    Organization,
    Region,
    EventSource,
    EventOrganization,
    EventPerson,
    EventRegion,
)
from app.schemas import (
    EventCreate,
    SourceCreate,
    PersonCreate,
    OrganizationCreate,
    RegionCreate,
)


class IngestionService:
    def __init__(self, db: Session):
        self.db = db

    def create_source(self, data: SourceCreate) -> Source:
        source = Source(**data.model_dump())
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def create_person(self, data: PersonCreate) -> Person:
        person = Person(**data.model_dump())
        self.db.add(person)
        self.db.commit()
        self.db.refresh(person)
        return person

    def create_organization(self, data: OrganizationCreate) -> Organization:
        org = Organization(**data.model_dump())
        self.db.add(org)
        self.db.commit()
        self.db.refresh(org)
        return org

    def create_region(self, data: RegionCreate) -> Region:
        region = Region(**data.model_dump())
        self.db.add(region)
        self.db.commit()
        self.db.refresh(region)
        return region

    def create_event(self, data: EventCreate) -> Event:
        """
        Cria um evento histórico garantindo a proveniência estrita de fontes.
        """
        # 1. Cria o evento base
        event_dict = data.model_dump(exclude={"sources", "organizations", "people", "regions"})
        event = Event(**event_dict)
        self.db.add(event)
        self.db.flush()  # Obtém o event.id

        # 2. Registra proveniência de fontes (Obrigatório)
        for s_in in data.sources:
            # Verifica se fonte existe
            source_exists = self.db.query(Source).filter(Source.id == s_in.source_id).first()
            if not source_exists:
                raise ValueError(f"Fonte ID {s_in.source_id} não encontrada.")

            event_source = EventSource(
                event_id=event.id,
                source_id=s_in.source_id,
                page_or_section=s_in.page_or_section,
                excerpt=s_in.excerpt,
                claim_assertion=s_in.claim_assertion,
                validation_status=s_in.validation_status,
                confidence_notes=s_in.confidence_notes,
            )
            self.db.add(event_source)

        # 3. Associa Organizações
        if data.organizations:
            for o_in in data.organizations:
                event_org = EventOrganization(
                    event_id=event.id,
                    organization_id=o_in.organization_id,
                    role_in_event=o_in.role_in_event,
                )
                self.db.add(event_org)

        # 4. Associa Pessoas
        if data.people:
            for p_in in data.people:
                event_person = EventPerson(
                    event_id=event.id,
                    person_id=p_in.person_id,
                    role_in_event=p_in.role_in_event,
                )
                self.db.add(event_person)

        # 5. Associa Territórios/Regiões
        if data.regions:
            for r_in in data.regions:
                event_region = EventRegion(
                    event_id=event.id,
                    region_id=r_in.region_id,
                    specific_location_name=r_in.specific_location_name,
                )
                self.db.add(event_region)

        self.db.commit()
        self.db.refresh(event)
        return event
