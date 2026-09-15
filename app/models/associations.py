import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime, UniqueConstraint
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
    
    page = Column(String(50), nullable=True)
    section = Column(String(100), nullable=True)
    page_or_section = Column(String(100), nullable=True)
    
    excerpt = Column(Text, nullable=False)
    claim = Column(Text, nullable=True)
    claim_assertion = Column(Text, nullable=True)
    
    source_assessment = Column(String(100), nullable=True)
    assessment_notes = Column(Text, nullable=True)
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
    confidence_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    event = relationship("Event", back_populates="source_links")
    source = relationship("Source", back_populates="event_links")


class SourceDerivation(Base):
    """
    Grafo de linhagem documental entre duas fontes.

    A relação não presume que duas fontes sejam independentes apenas porque
    têm títulos/autores/URLs diferentes. Ela registra explicitamente quando
    uma fonte reproduz, resume, cita ou deriva informação de outra.
    """
    __tablename__ = "source_derivations"
    __table_args__ = (
        UniqueConstraint(
            "parent_source_id",
            "derived_source_id",
            name="uq_source_derivation_pair",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    parent_source_id = Column(
        Integer,
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    derived_source_id = Column(
        Integer,
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    derivation_type = Column(String(50), nullable=False, default="desconhecida")
    # reproduz, resume, cita, deriva_dado, adapta, compila, desconhecida

    # Se False, a fonte derivada não deve contar como uma raiz documental
    # independente para triangulação em relação à sua fonte ascendente.
    is_independent = Column(Boolean, nullable=False, default=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    parent_source = relationship(
        "Source",
        foreign_keys=[parent_source_id],
        back_populates="derived_sources",
    )
    derived_source = relationship(
        "Source",
        foreign_keys=[derived_source_id],
        back_populates="source_derivations",
    )


class EventOrganization(Base):
    """Associação entre Evento e Organização envolvida."""
    __tablename__ = "event_organizations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    role_in_event = Column(String(100), nullable=True)

    event = relationship("Event", back_populates="organization_links")
    organization = relationship("Organization", back_populates="event_links")


class EventPerson(Base):
    """Associação entre Evento e Pessoa/Liderança envolvida."""
    __tablename__ = "event_people"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), nullable=False, index=True)
    role_in_event = Column(String(100), nullable=True)

    event = relationship("Event", back_populates="person_links")
    person = relationship("Person", back_populates="event_links")


class EventRegion(Base):
    """Associação entre Evento e Região/Território geográfico."""
    __tablename__ = "event_regions"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    specific_location_name = Column(String(255), nullable=True)

    event = relationship("Event", back_populates="region_links")
    region = relationship("Region", back_populates="event_links")
