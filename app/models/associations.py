import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime, Enum
)
from sqlalchemy.orm import relationship
from app.database import Base


class ValidationStatusEnum(str, enum.Enum):
    CONFIRMADO = "confirmado"
    PROVAVEL = "provavel"
    CONFLITANTE = "conflitante"
    NAO_VERIFICADO = "nao_verificado"


class EventSource(Base):
    """
    Tabela de Proveniência: Conecta um Evento a uma Fonte histórica.
    Registra o trecho literal, página e nível de validação.
    """
    __tablename__ = "event_sources"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    
    page_or_section = Column(String(100), nullable=True)
    excerpt = Column(Text, nullable=False)  # Trecho/citação textual comprobatória
    claim_assertion = Column(Text, nullable=True)  # Afirmação sustentada
    validation_status = Column(
        String(30),
        default=ValidationStatusEnum.CONFIRMADO.value,
        nullable=False
    )
    confidence_notes = Column(Text, nullable=True)  # Divergências ou observações críticas
    created_at = Column(DateTime, default=datetime.utcnow)

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
