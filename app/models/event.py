from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Event(Base):
    """
    Entidade Evento Histórico: Acontecimento documentado no tempo e no espaço.
    Regra de ouro: Todo evento deve possuir proveniência vinculada via EventSource.
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    
    # Temporalidade
    date_start = Column(String(50), nullable=False, index=True)  # Formato YYYY-MM-DD ou YYYY
    date_end = Column(String(50), nullable=True)
    year = Column(Integer, nullable=False, index=True)  # Ano de referência principal para timeline
    exact_date = Column(Boolean, default=True, nullable=False)
    
    # Conteúdo
    description = Column(Text, nullable=False)
    historical_context = Column(Text, nullable=True)  # Contexto histórico ampliado
    confidence_level = Column(String(30), default="confirmado", nullable=False, index=True)
    # Níveis: confirmado, provavel, conflitante, nao_verificado
    
    is_demo = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    source_links = relationship("EventSource", back_populates="event", cascade="all, delete-orphan")
    organization_links = relationship("EventOrganization", back_populates="event", cascade="all, delete-orphan")
    person_links = relationship("EventPerson", back_populates="event", cascade="all, delete-orphan")
    region_links = relationship("EventRegion", back_populates="event", cascade="all, delete-orphan")

    @property
    def sources(self):
        return [link.source for link in self.source_links]

    @property
    def organizations(self):
        return [link.organization for link in self.organization_links]

    @property
    def people(self):
        return [link.person for link in self.person_links]

    @property
    def regions(self):
        return [link.region for link in self.region_links]

    def __repr__(self):
        return f"<Event(id={self.id}, title='{self.title[:30]}...', year={self.year}, confidence='{self.confidence_level}')>"
