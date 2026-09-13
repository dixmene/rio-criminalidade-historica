from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Event(Base):
    """
    Entidade Evento Histórico: Acontecimento documentado no tempo e no espaço.
    
    Regra de Temporalidade:
    - date_display: armazena a grafia exata informada pela fonte (ex: 'maio de 1978', '1975', '15/03/1983').
    - year: ano de referência para indexação da linha do tempo (NULL permitido se desconhecido).
    - Não transforma '1970' em '1970-01-01' ficticiamente.
    
    Regra de Proveniência:
    - Nenhum evento histórico real (is_demo=False) pode existir sem pelo menos uma fonte vinculada.
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, default="acontecimento_geral")
    
    # Temporalidade rigorosa
    date_display = Column(String(100), nullable=False)  # Como a fonte informa o tempo
    date_start = Column(String(50), nullable=True, index=True)  # YYYY-MM-DD se dia exato, ou YYYY-MM ou YYYY
    date_end = Column(String(50), nullable=True)
    year = Column(Integer, nullable=True, index=True)  # Ano de referência principal para timeline
    temporal_precision = Column(String(50), nullable=False, default="dia")
    # precisão: dia, mes, ano, intervalo, aproximado, desconhecido
    exact_date = Column(Boolean, default=False, nullable=False)
    
    # Conteúdo factual e contexto
    description = Column(Text, nullable=False)
    historical_context = Column(Text, nullable=True)
    confidence_level = Column(String(30), default="confirmado", nullable=False, index=True)
    # Níveis: confirmado, provavel, conflitante, nao_verificado
    
    is_demo = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)

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
        return f"<Event(id={self.id}, title='{self.title[:30]}...', date='{self.date_display}', confidence='{self.confidence_level}')>"
