from typing import List, Optional, Tuple
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
        Consulta eventos aplicando filtros temporais, geográficos e de isolamento DEMO.
        Retorna os relacionamentos carregados por eager loading.
        """
        query = self.db.query(Event).options(
            joinedload(Event.source_links).joinedload(EventSource.source),
            joinedload(Event.organization_links).joinedload(EventOrganization.organization),
            joinedload(Event.person_links).joinedload(EventPerson.person),
            joinedload(Event.region_links).joinedload(EventRegion.region),
        )

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

        if region_id:
            query = query.join(Event.region_links).filter(EventRegion.region_id == region_id)
        if organization_id:
            query = query.join(Event.organization_links).filter(EventOrganization.organization_id == organization_id)
        if person_id:
            query = query.join(Event.person_links).filter(EventPerson.person_id == person_id)

        return query.order_by(Event.year.asc(), Event.date_display.asc()).all()

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

    def get_timeline_bounds(self, is_demo: Optional[bool] = None) -> Tuple[int, int]:
        """Retorna o ano mínimo e máximo dos eventos no banco para a visualização ativa."""
        query = self.db.query(Event.year).filter(Event.year.isnot(None))
        if is_demo is not None:
            query = query.filter(Event.is_demo == is_demo)
        
        min_year = query.order_by(Event.year.asc()).first()
        max_year = query.order_by(Event.year.desc()).first()
        if min_year and max_year:
            return (min_year[0], max_year[0])
        return (1970, 1989)

    def count_real_events(self) -> int:
        """Conta eventos históricos reais (is_demo=False)."""
        return self.db.query(Event).filter(Event.is_demo == False).count()

    def count_demo_events(self) -> int:
        """Conta eventos de teste técnico [DEMO] (is_demo=True)."""
        return self.db.query(Event).filter(Event.is_demo == True).count()

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
