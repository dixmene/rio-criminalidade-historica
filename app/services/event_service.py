from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

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


def _event_eager_options() -> tuple:
    """
    Eager-loading strategy using selectinload for 1-to-N collections and
    joinedload for N-to-1 leaf entities, avoiding SQL Cartesian-product blowup.
    """
    return (
        selectinload(Event.source_links).joinedload(EventSource.source),
        selectinload(Event.claims)
        .selectinload(Claim.source_links)
        .joinedload(ClaimSource.source),
        selectinload(Event.organization_links).joinedload(EventOrganization.organization),
        selectinload(Event.person_links).joinedload(EventPerson.person),
        selectinload(Event.region_links).joinedload(EventRegion.region),
    )


class EventService:
    def __init__(self, db: Session):
        self.db = db

    def list_events(
        self,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        region_id: Optional[int] = None,
        organization_id: Optional[int] = None,
        person_id: Optional[int] = None,
        confidence_level: Optional[str] = None,
        search_query: Optional[str] = None,
        is_demo: Optional[bool] = None,
    ) -> List[Event]:
        """
        Consulta eventos aplicando filtros temporais, geográficos e de isolamento DEMO.
        Retorna os relacionamentos carregados por eager loading (fontes, claims, regiões, etc.).
        """
        query = self.db.query(Event).options(*_event_eager_options())

        if is_demo is not None:
            query = query.filter(Event.is_demo == is_demo)

        if year_min is not None:
            query = query.filter(Event.year >= year_min)
        if year_max is not None:
            query = query.filter(Event.year <= year_max)
        if confidence_level:
            query = query.filter(Event.confidence_level == confidence_level)
        if search_query:
            search = f"%{search_query}%"
            query = query.filter(
                (Event.title.ilike(search)) | (Event.description.ilike(search))
            )

        if region_id is not None:
            query = query.filter(Event.region_links.any(EventRegion.region_id == region_id))
        if organization_id is not None:
            query = query.filter(
                Event.organization_links.any(EventOrganization.organization_id == organization_id)
            )
        if person_id is not None:
            query = query.filter(Event.person_links.any(EventPerson.person_id == person_id))

        return query.order_by(Event.year.asc(), Event.date_display.asc()).all()

    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Recupera um evento por ID com todos os vínculos de fontes, afirmações (claims) e entidades."""
        return (
            self.db.query(Event)
            .options(*_event_eager_options())
            .filter(Event.id == event_id)
            .first()
        )

    def list_claims(
        self,
        event_id: Optional[int] = None,
        is_disputed: Optional[bool] = None,
    ) -> List[Claim]:
        """Lista afirmações históricas atomizadas, com filtro opcional por evento ou controvérsia."""
        query = self.db.query(Claim).options(
            selectinload(Claim.source_links).joinedload(ClaimSource.source)
        )
        if event_id is not None:
            query = query.filter(Claim.event_id == event_id)
        if is_disputed is not None:
            query = query.filter(Claim.is_disputed == is_disputed)
        return query.order_by(Claim.created_at.desc()).all()

    def get_timeline_bounds(self, is_demo: Optional[bool] = None) -> Tuple[int, int]:
        """Retorna o ano mínimo e máximo dos eventos no banco para a visualização ativa."""
        query = self.db.query(func.min(Event.year), func.max(Event.year)).filter(
            Event.year.isnot(None)
        )
        if is_demo is not None:
            query = query.filter(Event.is_demo == is_demo)

        min_year, max_year = query.one()
        if min_year is not None and max_year is not None:
            return (int(min_year), int(max_year))
        return (1970, 1989)

    def count_real_events(self) -> int:
        """Conta eventos históricos reais (is_demo=False)."""
        return (
            self.db.query(func.count(Event.id))
            .filter(Event.is_demo == False)
            .scalar()
            or 0
        )

    def count_demo_events(self) -> int:
        """Conta eventos de teste técnico [DEMO] (is_demo=True)."""
        return (
            self.db.query(func.count(Event.id))
            .filter(Event.is_demo == True)
            .scalar()
            or 0
        )

    def list_regions(self, is_demo: Optional[bool] = None) -> List[Region]:
        query = self.db.query(Region)
        if is_demo is not None:
            query = query.filter(Region.is_demo == is_demo)
        return query.order_by(Region.original_name.asc()).all()

    def list_organizations(self, is_demo: Optional[bool] = None) -> List[Organization]:
        query = self.db.query(Organization)
        if is_demo is not None:
            query = query.filter(Organization.is_demo == is_demo)
        return query.order_by(Organization.original_name.asc()).all()

    def list_people(self, is_demo: Optional[bool] = None) -> List[Person]:
        query = self.db.query(Person)
        if is_demo is not None:
            query = query.filter(Person.is_demo == is_demo)
        return query.order_by(Person.original_name.asc()).all()

    def list_sources(self, is_demo: Optional[bool] = None) -> List[Source]:
        query = self.db.query(Source)
        if is_demo is not None:
            query = query.filter(Source.is_demo == is_demo)
        return query.order_by(Source.publication_year.asc()).all()
