from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime
)
from sqlalchemy.orm import relationship
from src.database.connection import Base


def utc_now():
    return datetime.now(timezone.utc)


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    citation = Column(Text, nullable=False)
    author = Column(String(255), nullable=True)
    publisher = Column(String(255), nullable=True)
    source_type = Column(String(100), nullable=False, default="oficial_relatorio")
    publication_year = Column(Integer, nullable=True, index=True)
    publication_date = Column(String(50), nullable=True)
    document_date = Column(String(50), nullable=True)
    url = Column(String(500), nullable=True)
    archive_ref = Column(String(255), nullable=True)
    file_hash_sha256 = Column(String(64), nullable=True)
    reliability_rating = Column(Integer, default=5)
    notes = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    # Relacionamentos
    event_links = relationship("EventSource", back_populates="source", cascade="all, delete-orphan")
    territorial_links = relationship("TerritorialRelationSource", back_populates="source", cascade="all, delete-orphan")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    original_name = Column(String(255), nullable=False)
    normalized_name = Column(String(255), nullable=False, index=True)
    acronym = Column(String(50), nullable=True, index=True)
    org_type = Column(String(100), nullable=False, default="faccao_criminosa")
    foundation_year = Column(Integer, nullable=True)
    dissolution_year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    event_links = relationship("EventOrganization", back_populates="organization", cascade="all, delete-orphan")
    territorial_relations = relationship("TerritorialRelation", back_populates="organization", cascade="all, delete-orphan")


class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, index=True)
    original_name = Column(String(255), nullable=False)
    normalized_name = Column(String(255), nullable=False, index=True)
    aliases = Column(String(255), nullable=True)
    role_description = Column(String(255), nullable=True)
    birth_year = Column(Integer, nullable=True)
    death_year = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    event_links = relationship("EventPerson", back_populates="person", cascade="all, delete-orphan")


class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    original_name = Column(String(255), nullable=False)
    normalized_name = Column(String(255), nullable=False, index=True)
    region_type = Column(String(100), nullable=False, default="bairro")
    municipality = Column(String(100), nullable=False, default="Rio de Janeiro")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geojson_boundary = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    event_links = relationship("EventRegion", back_populates="region", cascade="all, delete-orphan")
    territorial_relations = relationship("TerritorialRelation", back_populates="region", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, default="acontecimento_geral")
    date_start = Column(String(50), nullable=False, index=True)
    date_end = Column(String(50), nullable=True)
    year = Column(Integer, nullable=False, index=True)
    exact_date = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=False)
    historical_context = Column(Text, nullable=True)
    confidence_level = Column(String(30), default="confirmado", nullable=False, index=True)
    is_demo = Column(Boolean, default=False, nullable=False)
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


class EventSource(Base):
    __tablename__ = "event_sources"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    page_or_section = Column(String(100), nullable=True)
    excerpt = Column(Text, nullable=False)
    claim_assertion = Column(Text, nullable=True)
    validation_status = Column(String(30), default="confirmado", nullable=False)
    confidence_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    event = relationship("Event", back_populates="source_links")
    source = relationship("Source", back_populates="event_links")


class TerritorialRelation(Base):
    __tablename__ = "territorial_relations"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    date_start = Column(String(50), nullable=False)
    date_end = Column(String(50), nullable=True)
    relation_type = Column(String(100), nullable=False, default="dominio_hegemonico")
    confidence_level = Column(String(30), nullable=False, default="confirmado")
    notes = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    organization = relationship("Organization", back_populates="territorial_relations")
    region = relationship("Region", back_populates="territorial_relations")
    source_links = relationship("TerritorialRelationSource", back_populates="territorial_relation", cascade="all, delete-orphan")


class TerritorialRelationSource(Base):
    __tablename__ = "territorial_relation_sources"

    id = Column(Integer, primary_key=True, index=True)
    territorial_relation_id = Column(Integer, ForeignKey("territorial_relations.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    page_or_section = Column(String(100), nullable=True)
    excerpt = Column(Text, nullable=False)
    validation_status = Column(String(30), nullable=False, default="confirmado")
    created_at = Column(DateTime, default=utc_now)

    territorial_relation = relationship("TerritorialRelation", back_populates="source_links")
    source = relationship("Source", back_populates="territorial_links")


class EventOrganization(Base):
    __tablename__ = "event_organizations"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    role_in_event = Column(String(100), nullable=True)

    event = relationship("Event", back_populates="organization_links")
    organization = relationship("Organization", back_populates="event_links")


class EventPerson(Base):
    __tablename__ = "event_people"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), nullable=False, index=True)
    role_in_event = Column(String(100), nullable=True)

    event = relationship("Event", back_populates="person_links")
    person = relationship("Person", back_populates="event_links")


class EventRegion(Base):
    __tablename__ = "event_regions"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    specific_location_name = Column(String(255), nullable=True)

    event = relationship("Event", back_populates="region_links")
    region = relationship("Region", back_populates="event_links")
