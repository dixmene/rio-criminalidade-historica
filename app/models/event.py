from datetime import datetime, timezone, date
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.types import TypeDecorator, Date
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class HistoricalDate(TypeDecorator):
    """
    Tipo temporal histórico robusto:
    Aceita instâncias de datetime.date ou strings ISO 'YYYY-MM-DD',
    convertendo transparentemente para datetime.date.
    Garante integridade tanto no SQLite quanto no PostgreSQL sem quebrar chamadas.
    """
    impl = Date
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            val_str = value.strip()
            if not val_str:
                return None
            try:
                return date.fromisoformat(val_str[:10])
            except Exception:
                return None
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return date.fromisoformat(value[:10])
            except Exception:
                return None
        return value


class Event(Base):
    """
    Entidade Evento Histórico: Acontecimento documentado no tempo e no espaço.
    
    Regra de Temporalidade Rigorosa (Intervalos de Conhecimento):
    - date_display: armazena a grafia exata informada pela fonte (ex: 'maio de 1978', '1978', '15/03/1983').
    - date_start: data inicial (Date) do intervalo de conhecimento (ex: 1978-01-01 para ano de 1978).
    - date_end: data final (Date) do intervalo de conhecimento (ex: 1978-12-31 para ano de 1978).
    - year: ano de referência para indexação da linha do tempo (NULL permitido se desconhecido).
    - temporal_precision: dia, mes, ano, decada, intervalo, aproximado, desconhecido.
    - date_is_estimated: indica se os limites de date_start/date_end foram inferidos ou estimados.
    - exact_date: booleano indicando se o dia e mês são conhecidos com exatidão documental.
    
    Regra de Proveniência & Epistemologia:
    - Nenhum evento histórico real (is_demo=False) pode existir sem pelo menos uma fonte vinculada.
    - Suporta afirmações atomizadas via 'claims' para permitir confronto de versões historiográficas.
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, default="acontecimento_geral")
    
    # Temporalidade rigorosa (Intervalos de Conhecimento)
    date_display = Column(String(100), nullable=False)  # Como a fonte informa o tempo
    date_start = Column(HistoricalDate, nullable=True, index=True)  # Limite temporal inicial (Date)
    date_end = Column(HistoricalDate, nullable=True)  # Limite temporal final (Date)
    year = Column(Integer, nullable=True, index=True)  # Ano de referência principal para timeline
    temporal_precision = Column(String(50), nullable=False, default="dia")
    # precisão: dia, mes, ano, decada, intervalo, aproximado, desconhecido
    exact_date = Column(Boolean, default=False, nullable=False)
    date_is_estimated = Column(Boolean, default=False, nullable=False)  # Baliza temporal estimada
    
    # Conteúdo factual e contexto
    description = Column(Text, nullable=False)
    historical_context = Column(Text, nullable=True)
    confidence_level = Column(String(30), default="confirmado", nullable=False, index=True)
    # Níveis: confirmado, provavel, conflitante, nao_verificado
    
    is_demo = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)

    # Relacionamentos
    claims = relationship("Claim", back_populates="event", cascade="all, delete-orphan")
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
