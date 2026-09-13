from datetime import date
from typing import List
from sqlalchemy.orm import Session
from app.models import (
    Event,
    Source,
    Person,
    Organization,
    Region,
    Claim,
    ClaimSource,
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
    ClaimCreate,
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

    def create_claim(self, data: ClaimCreate) -> Claim:
        """Cria uma afirmação historiográfica vinculada a fontes com postura explícita."""
        claim_dict = data.model_dump(exclude={"sources"})
        claim = Claim(**claim_dict)
        self.db.add(claim)
        self.db.flush()

        for s_in in data.sources:
            source_exists = self.db.query(Source).filter(Source.id == s_in.source_id).first()
            if not source_exists:
                raise ValueError(f"Fonte ID {s_in.source_id} não encontrada para a afirmação.")
            cs = ClaimSource(
                claim_id=claim.id,
                source_id=s_in.source_id,
                stance=s_in.stance,
                page=s_in.page,
                section=s_in.section,
                excerpt=s_in.excerpt.strip(),
                source_assessment=s_in.source_assessment,
                assessment_notes=s_in.assessment_notes,
                confidence_level=s_in.confidence_level,
            )
            self.db.add(cs)

        self.db.commit()
        self.db.refresh(claim)
        return claim

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

        # Trata temporalidade rigorosa (intervalos de conhecimento)
        event_dict = data.model_dump(exclude={"sources", "claims", "organizations", "people", "regions"})
        if event_dict.get("year") is None and event_dict.get("date_display"):
            dt, yr, exact = normalize_date(event_dict["date_display"])
            if event_dict.get("date_start") is None:
                event_dict["date_start"] = dt
            if event_dict.get("year") is None:
                event_dict["year"] = yr
            if not event_dict.get("exact_date"):
                event_dict["exact_date"] = exact

        # Conversão para date se string ISO for informada
        for date_field in ("date_start", "date_end"):
            val = event_dict.get(date_field)
            if isinstance(val, str):
                try:
                    event_dict[date_field] = date.fromisoformat(val)
                except Exception:
                    pass

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
                page=s_in.page,
                section=s_in.section,
                page_or_section=s_in.page_or_section or s_in.page,
                excerpt=s_in.excerpt.strip(),
                claim=s_in.claim or s_in.claim_assertion,
                claim_assertion=s_in.claim_assertion or s_in.claim,
                source_assessment=s_in.source_assessment,
                assessment_notes=s_in.assessment_notes,
                confidence_level=s_in.confidence_level or s_in.validation_status or "confirmado",
                validation_status=s_in.validation_status or s_in.confidence_level or "confirmado",
                confidence_notes=s_in.confidence_notes or s_in.assessment_notes,
            )
            self.db.add(event_source)

        # Inserção de Claims (Afirmações atomizadas se fornecidas)
        if data.claims:
            for c_in in data.claims:
                c_dict = c_in.model_dump(exclude={"sources"})
                c_dict["event_id"] = event.id
                claim_obj = Claim(**c_dict)
                self.db.add(claim_obj)
                self.db.flush()

                for cs_in in c_in.sources:
                    cs = ClaimSource(
                        claim_id=claim_obj.id,
                        source_id=cs_in.source_id,
                        stance=cs_in.stance,
                        page=cs_in.page,
                        section=cs_in.section,
                        excerpt=cs_in.excerpt.strip(),
                        source_assessment=cs_in.source_assessment,
                        assessment_notes=cs_in.assessment_notes,
                        confidence_level=cs_in.confidence_level,
                    )
                    self.db.add(cs)

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
