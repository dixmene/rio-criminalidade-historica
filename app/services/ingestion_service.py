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
from src.normalization.rules import (
    normalize_name,
    normalize_location,
    normalize_organization,
    normalize_date,
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
        dump = data.model_dump()
        if not dump.get("normalized_name"):
            norm = normalize_name(dump["original_name"])
            dump["normalized_name"] = norm["normalized_name"]
        
        person = Person(**dump)
        self.db.add(person)
        self.db.commit()
        self.db.refresh(person)
        return person

    def create_organization(self, data: OrganizationCreate) -> Organization:
        dump = data.model_dump()
        if not dump.get("normalized_name"):
            norm = normalize_organization(dump["original_name"])
            dump["normalized_name"] = norm["normalized_name"]

        org = Organization(**dump)
        self.db.add(org)
        self.db.commit()
        self.db.refresh(org)
        return org

    def create_region(self, data: RegionCreate) -> Region:
        dump = data.model_dump()
        if not dump.get("normalized_name"):
            norm = normalize_location(dump["original_name"])
            dump["normalized_name"] = norm["normalized_name"]

        region = Region(**dump)
        self.db.add(region)
        self.db.commit()
        self.db.refresh(region)
        return region

    def create_event(self, data: EventCreate) -> Event:
        """
        Cria um evento histórico com garantia de proveniência e temporalidade rigorosa.
        
        Regra Inegociável:
        - Se is_demo=False, pelo menos uma fonte documental deve estar associada.
        """
        if not data.is_demo and (not data.sources or len(data.sources) == 0):
            raise ValueError(
                "Regra de Domínio Violada: Nenhum evento histórico real pode ser inserido sem comprovação de fonte."
            )

        # Trata temporalidade
        event_dict = data.model_dump(exclude={"sources", "organizations", "people", "regions"})
        if event_dict.get("year") is None and event_dict.get("date_display"):
            dt, yr, exact = normalize_date(event_dict["date_display"])
            if event_dict.get("date_start") is None:
                event_dict["date_start"] = dt
            if event_dict.get("year") is None:
                event_dict["year"] = yr
            if not event_dict.get("exact_date"):
                event_dict["exact_date"] = exact

        event = Event(**event_dict)
        self.db.add(event)
        self.db.flush()

        # Inserção de Fontes Obrigatórias
        for s_in in data.sources:
            source_exists = self.db.query(Source).filter(Source.id == s_in.source_id).first()
            if not source_exists:
                raise ValueError(f"Fonte ID {s_in.source_id} não encontrada no acervo.")

            if not s_in.excerpt or len(s_in.excerpt.strip()) < 5:
                raise ValueError("O trecho comprobatório (excerpt) da fonte é obrigatório.")

            event_source = EventSource(
                event_id=event.id,
                source_id=s_in.source_id,
                page_or_section=s_in.page_or_section,
                excerpt=s_in.excerpt.strip(),
                claim_assertion=s_in.claim_assertion,
                validation_status=s_in.validation_status,
                confidence_notes=s_in.confidence_notes,
            )
            self.db.add(event_source)

        # Organizações
        if data.organizations:
            for o_in in data.organizations:
                event_org = EventOrganization(
                    event_id=event.id,
                    organization_id=o_in.organization_id,
                    role_in_event=o_in.role_in_event,
                )
                self.db.add(event_org)

        # Pessoas
        if data.people:
            for p_in in data.people:
                event_person = EventPerson(
                    event_id=event.id,
                    person_id=p_in.person_id,
                    role_in_event=p_in.role_in_event,
                )
                self.db.add(event_person)

        # Regiões
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
