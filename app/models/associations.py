import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime
)
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class ValidationStatusEnum(str, enum.Enum):
    CONFIRMADO = "confirmado"
    PROVAVEL = "provavel"
    CONFLITANTE = "conflitante"
    NAO_VERIFICADO = "nao_verificado"


class EventSource(Base):
    """
    Tabela de Proveniência & Evidência Documental: Conecta um Evento a uma Fonte histórica.
    Registra o trecho literal exato, página, seção, afirmação sustentada e avaliação crítica da fonte.
    """
    __tablename__ = "event_sources"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Localização exata dentro da fonte
    page = Column(String(50), nullable=True)
    section = Column(String(100), nullable=True)
    page_or_section = Column(String(100), nullable=True)  # Compatibilidade retroativa
    
    # Trecho literal mandatório e afirmação sustentada
    excerpt = Column(Text, nullable=False)  # Citação textual literal comprobatória
    claim = Column(Text, nullable=True)  # Proposição factual sustentada
    claim_assertion = Column(Text, nullable=True)  # Compatibilidade retroativa
    
    # Avaliação historiográfica e confiança granular na ligação
    source_assessment = Column(String(100), nullable=True)  # ex: oficial, academica, testemunhal, pericial, jornalistica
    assessment_notes = Column(Text, nullable=True)  # Notas de análise crítica da fonte
    confidence_level = Column(
        String(30),
        default=ValidationStatusEnum.CONFIRMADO.value,
        nullable=False
    )
    validation_status = Column(
        String(30),
        default=ValidationStatusEnum.CONFIRMADO.value,
        nullable=False
    )
    confidence_notes = Column(Text, nullable=True)  # Compatibilidade retroativa
    created_at = Column(DateTime, default=utc_now)

    # Relacionamentos
    event = relationship("Event", back_populates="source_links")
    source = relationship("Source", back_populates="event_links")


class EventOrganization(Base):
    """Associação entre Evento e Organização envolvida."""
    __tablename__ = "event_organizations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    role_in_event = Column(String(100), nullable=True)  # ex: executor, alvo, investigador, mediador

    event = relationship("Event", back_populates="organization_links")
    organization = relationship("Organization", back_populates="event_links")


class EventPerson(Base):
    """Associação entre Evento e Pessoa/Liderança envolvida."""
    __tablename__ = "event_people"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), nullable=False, index=True)
    role_in_event = Column(String(100), nullable=True)  # ex: vitima, lideranca, testemunha, acusado

    event = relationship("Event", back_populates="person_links")
    person = relationship("Person", back_populates="event_links")


class EventRegion(Base):
    """Associação entre Evento e Região/Território geográfico."""
    __tablename__ = "event_regions"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    specific_location_name = Column(String(255), nullable=True)  # ex: Riocentro - Pavilhão São Cristóvão

    event = relationship("Event", back_populates="region_links")
    region = relationship("Region", back_populates="event_links")
