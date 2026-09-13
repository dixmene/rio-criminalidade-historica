from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models import (
    Event,
    EventSource,
    EventOrganization,
    EventPerson,
    EventRegion,
    Region,
    Organization,
    Person,
    Source
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
        Consulta eventos aplicando filtros temporais, geográficos e temáticos.
        Retorna os relacionamentos carregados.
        """
        query = self.db.query(Event).options(
            joinedload(Event.source_links).joinedload(EventSource.source),
            joinedload(Event.organization_links).joinedload(EventOrganization.organization),
            joinedload(Event.person_links).joinedload(EventPerson.person),
            joinedload(Event.region_links).joinedload(EventRegion.region),
        )

        if year_min is not None:
            query = query.filter(Event.year >= year_min)
        if year_max is not None:
            query = query.filter(Event.year <= year_max)
        if confidence_level:
            query = query.filter(Event.confidence_level == confidence_level)
        if is_demo is not None:
            query = query.filter(Event.is_demo == is_demo)
        if search_query:
            search = f"%{search_query}%"
            query = query.filter(
                (Event.title.ilike(search)) | (Event.description.ilike(search))
            )

        if region_id:
            query = query.join(Event.region_links).filter(EventRegion.region_id == region_id)
        if organization_id:
            query = query.join(Event.organization_links).filter(EventOrganization.organization_id == organization_id)
        if person_id:
            query = query.join(Event.person_links).filter(EventPerson.person_id == person_id)

        return query.order_by(Event.year.asc(), Event.date_start.asc()).all()

    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Recupera um evento por ID com todos os vínculos de fontes e entidades."""
        return (
            self.db.query(Event)
            .options(
                joinedload(Event.source_links).joinedload(EventSource.source),
                joinedload(Event.organization_links).joinedload(EventOrganization.organization),
                joinedload(Event.person_links).joinedload(EventPerson.person),
                joinedload(Event.region_links).joinedload(EventRegion.region),
            )
            .filter(Event.id == event_id)
            .first()
        )

    def get_timeline_bounds(self) -> tuple[int, int]:
        """Retorna o ano mínimo e máximo dos eventos no banco."""
        min_year = self.db.query(Event.year).order_by(Event.year.asc()).first()
        max_year = self.db.query(Event.year).order_by(Event.year.desc()).first()
        if min_year and max_year:
            return (min_year[0], max_year[0])
        return (1970, 1989)

    def list_regions(self) -> List[Region]:
        return self.db.query(Region).order_by(Region.name.asc()).all()

    def list_organizations(self) -> List[Organization]:
        return self.db.query(Organization).order_by(Organization.name.asc()).all()

    def list_people(self) -> List[Person]:
        return self.db.query(Person).order_by(Person.name.asc()).all()

    def list_sources(self) -> List[Source]:
        return self.db.query(Source).order_by(Source.publication_year.asc()).all()
