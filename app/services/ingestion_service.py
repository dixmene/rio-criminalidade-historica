from datetime import date
from typing import Iterable, List, Set

from sqlalchemy.orm import Session

from app.models import (
    Claim,
    ClaimSource,
    Event,
    EventOrganization,
    EventPerson,
    EventRegion,
    EventSource,
    Organization,
    Person,
    Region,
    Source,
)
from app.schemas import (
    ClaimCreate,
    EventCreate,
    OrganizationCreate,
    PersonCreate,
    RegionCreate,
    SourceCreate,
)
from src.normalization.rules import (
    normalize_date,
    normalize_location,
    normalize_name,
    normalize_organization,
)


class IngestionService:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_sources_exist(self, source_ids: Iterable[int], context_msg: str) -> None:
        """Batch-validates that all referenced Source IDs exist in a single SQL query."""
        needed: List[int] = list(dict.fromkeys(source_ids))
        if not needed:
            return
        existing: Set[int] = {
            row[0]
            for row in self.db.query(Source.id).filter(Source.id.in_(needed)).all()
        }
        for sid in needed:
            if sid not in existing:
                raise ValueError(context_msg.format(source_id=sid))

    @staticmethod
    def _build_claim_source_links(claim_id: int, sources_in: Iterable) -> List[ClaimSource]:
        return [
            ClaimSource(
                claim_id=claim_id,
                source_id=s_in.source_id,
                stance=s_in.stance,
                page=s_in.page,
                section=s_in.section,
                excerpt=s_in.excerpt.strip(),
                source_assessment=s_in.source_assessment,
                assessment_notes=s_in.assessment_notes,
                confidence_level=s_in.confidence_level,
            )
            for s_in in sources_in
        ]

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
        self._ensure_sources_exist(
            (s_in.source_id for s_in in data.sources),
            "Fonte ID {source_id} não encontrada para a afirmação.",
        )

        claim_dict = data.model_dump(exclude={"sources"})
        claim = Claim(**claim_dict)
        self.db.add(claim)
        self.db.flush()

        links = self._build_claim_source_links(claim.id, data.sources)
        if links:
            self.db.add_all(links)

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

        # Valida existência de fontes em batch antes de criar registros
        self._ensure_sources_exist(
            (s_in.source_id for s_in in data.sources),
            "Fonte ID {source_id} não encontrada no acervo.",
        )
        for s_in in data.sources:
            if not s_in.excerpt or len(s_in.excerpt.strip()) < 5:
                raise ValueError("O trecho comprobatório (excerpt) da fonte é obrigatório.")

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
                except ValueError:
                    pass

        event = Event(**event_dict)
        self.db.add(event)
        self.db.flush()

        # Inserção em lote de Fontes Obrigatórias
        if data.sources:
            self.db.add_all(
                [
                    EventSource(
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
                    for s_in in data.sources
                ]
            )

        # Inserção de Claims (Afirmações atomizadas se fornecidas)
        if data.claims:
            claim_objs = []
            for c_in in data.claims:
                c_dict = c_in.model_dump(exclude={"sources"})
                c_dict["event_id"] = event.id
                claim_objs.append((Claim(**c_dict), c_in.sources))
            self.db.add_all([c for c, _ in claim_objs])
            self.db.flush()

            claim_source_links: List[ClaimSource] = []
            for claim_obj, cs_list in claim_objs:
                claim_source_links.extend(self._build_claim_source_links(claim_obj.id, cs_list))
            if claim_source_links:
                self.db.add_all(claim_source_links)

        # Organizações, Pessoas e Regiões em lote
        if data.organizations:
            self.db.add_all(
                [
                    EventOrganization(
                        event_id=event.id,
                        organization_id=o_in.organization_id,
                        role_in_event=o_in.role_in_event,
                    )
                    for o_in in data.organizations
                ]
            )

        if data.people:
            self.db.add_all(
                [
                    EventPerson(
                        event_id=event.id,
                        person_id=p_in.person_id,
                        role_in_event=p_in.role_in_event,
                    )
                    for p_in in data.people
                ]
            )

        if data.regions:
            self.db.add_all(
                [
                    EventRegion(
                        event_id=event.id,
                        region_id=r_in.region_id,
                        specific_location_name=r_in.specific_location_name,
                    )
                    for r_in in data.regions
                ]
            )

        self.db.commit()
        self.db.refresh(event)
        return event
