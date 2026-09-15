# -*- coding: utf-8 -*-
"""
Modelos Espaço-Temporais do Atlas Histórico (FASE 1)
=====================================================

Estrutura formal para cartografia histórica digital auditável e citável:
1. TerritorialDataset: Metadados arquivísticos de datasets geográficos (GENI, IPP, IBGE, etc.)
2. RegionVersion: Geometrias versionadas no tempo com vigência (valid_from/valid_to) e anacronismo
3. TerritorialRelation: Semântica estrita de Presença, Controle, Influência e Disputa
4. EventFootprint: Pegada espacial de acontecimentos (pontos, polígonos, buffers de incerteza)
5. InstitutionalFacility: Ciclo de vida de estruturas do Estado (presídios, UPPs, batalhões)
6. MovementFlow: Arcos espaço-temporais de transferências, fugas e deslocamentos
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime
)
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.event import HistoricalDate


def utc_now():
    return datetime.now(timezone.utc)


class TerritorialDataset(Base):
    """
    Toda camada geográfica é um dataset formalmente citável e auditável.
    Armazena metadados de proveniência, licenciamento, versão e hash criptográfico.
    """
    __tablename__ = "territorial_datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)                    # ex: "Mapa dos Grupos Armados — GENI/UFF"
    provider = Column(String(255), nullable=False)                # Instituição/pesquisa fornecedora
    provider_url = Column(String(500), nullable=True)
    version = Column(String(50), nullable=False)                  # ex: "2025.12", "v1.0"
    extraction_date = Column(DateTime, default=utc_now)
    reference_period_start = Column(HistoricalDate, nullable=True) # A que período o dado se refere
    reference_period_end = Column(HistoricalDate, nullable=True)
    methodology_summary = Column(Text, nullable=True)             # Como o fornecedor delimitou
    methodology_url = Column(String(500), nullable=True)
    license = Column(String(100), nullable=True)                  # CC BY 4.0, Domínio Público, etc.
    sha256 = Column(String(64), nullable=True)                    # Hash SHA-256 do arquivo original
    crs = Column(String(50), default="EPSG:4674", nullable=False) # CRS oficial: SIRGAS 2000
    geometry_type = Column(String(50), nullable=True)             # Polygon, MultiPolygon, Point
    feature_count = Column(Integer, default=0, nullable=False)    # Calculado dinamicamente via COUNT
    notes = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)

    # Relacionamento 1:N com as versões geográficas extraídas deste dataset
    region_versions = relationship("RegionVersion", back_populates="dataset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TerritorialDataset(id={self.id}, name='{self.name[:30]}...', v='{self.version}')>"


class RegionVersion(Base):
    """
    Geografia versionada no tempo para uma dada Region.
    Garante que não projetamos delimitações contemporâneas sobre acontecimentos pretéritos
    sem explicitar o anacronismo da malha.
    """
    __tablename__ = "region_versions"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="CASCADE"), nullable=False, index=True)
    dataset_id = Column(Integer, ForeignKey("territorial_datasets.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    geometry_geojson = Column(Text, nullable=False)               # WKB/GeoJSON geometry em texto
    valid_from = Column(HistoricalDate, nullable=True)            # Vigência inicial da geometria (NULL = aberta)
    valid_to = Column(HistoricalDate, nullable=True)              # Vigência final da geometria (NULL = aberta)
    geometry_source = Column(String(255), nullable=True)
    location_precision = Column(String(50), default="aproximada", nullable=False)
    # exata | aproximada | centroide | referencial | desconhecida
    
    is_anachronistic = Column(Boolean, default=False, nullable=False)
    # True quando a malha é posterior ao período em que está sendo usada
    anachronism_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relacionamentos
    region = relationship("Region", back_populates="versions")
    dataset = relationship("TerritorialDataset", back_populates="region_versions")
    territorial_relations = relationship("TerritorialRelation", back_populates="region_version", cascade="all, delete-orphan")
    footprints = relationship("EventFootprint", back_populates="region_version")
    facilities = relationship("InstitutionalFacility", back_populates="region_version")

    def is_valid_for_year(self, year: int) -> bool:
        """Verifica se este snapshot geométrico é contemporâneo ao ano t."""
        if self.valid_from and self.valid_from.year > year:
            return False
        if self.valid_to and self.valid_to.year < year:
            return False
        return True

    def __repr__(self):
        return f"<RegionVersion(id={self.id}, region_id={self.region_id}, dataset_id={self.dataset_id})>"


class TerritorialRelation(Base):
    """
    Semântica territorial de controle e presença armada.
    Separa rigorosamente Presença, Controle, Influência, Disputa e Presença Estatal.
    Nunca promove automaticamente presença a controle sem sustentação textual.
    """
    __tablename__ = "territorial_relations"

    id = Column(Integer, primary_key=True, index=True)
    region_version_id = Column(Integer, ForeignKey("region_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    
    relation_type = Column(String(50), nullable=False, index=True)
    # presenca | controle | influencia | disputa | presenca_estatal
    
    date_start = Column(HistoricalDate, nullable=True)
    date_end = Column(HistoricalDate, nullable=True)
    temporal_precision = Column(String(50), default="ano", nullable=False)
    # dia | mes | ano | decada | periodo
    date_is_estimated = Column(Boolean, default=False, nullable=False)
    
    claim_id = Column(Integer, ForeignKey("claims.id", ondelete="SET NULL"), nullable=True, index=True)
    evidence_strength = Column(String(50), default="alegada", nullable=False)
    # documentada_primaria | documentada_secundaria | alegada | inferida_por_pesquisa
    
    independent_root_count = Column(Integer, default=1, nullable=False)
    is_contested = Column(Boolean, default=False, nullable=False, index=True)
    contested_by_claim_ids = Column(Text, nullable=True)          # JSON list de claims conflitantes
    notes = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)

    # Relacionamentos
    region_version = relationship("RegionVersion", back_populates="territorial_relations")
    organization = relationship("Organization")
    claim = relationship("Claim")

    def __repr__(self):
        return f"<TerritorialRelation(id={self.id}, type='{self.relation_type}', org_id={self.organization_id})>"


class EventFootprint(Base):
    """
    Pegada espacial de um acontecimento histórico (Event).
    Substitui pins artificiais fixos por geometrias expressivas com raio de incerteza (buffer).
    """
    __tablename__ = "event_footprints"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    geometry_geojson = Column(Text, nullable=False)               # Ponto, linha ou polígono GeoJSON
    footprint_type = Column(String(50), default="local_exato", nullable=False)
    # local_exato | area_aproximada | regiao_referencial | trajetoria
    location_precision = Column(String(50), default="aproximada", nullable=False)
    # exata | aproximada | centroide | referencial | desconhecida
    buffer_meters = Column(Float, nullable=True)                  # Raio de incerteza em metros
    region_version_id = Column(Integer, ForeignKey("region_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    coordinate_source = Column(String(255), nullable=False)       # Fonte documental da coordenada (nunca chute de IA)
    created_at = Column(DateTime, default=utc_now)

    # Relacionamentos
    event = relationship("Event", back_populates="footprints")
    region_version = relationship("RegionVersion", back_populates="footprints")

    def __repr__(self):
        return f"<EventFootprint(id={self.id}, event_id={self.event_id}, type='{self.footprint_type}')>"


class InstitutionalFacility(Base):
    """
    Equipamentos e instituições do Estado no território com ciclo de vida (abertura/fechamento).
    Presídios, delegacias, batalhões PMERJ, UPPs, fóruns judiciais e hospitais de custódia.
    """
    __tablename__ = "institutional_facilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)                    # ex: "Instituto Penal Cândido Mendes (Ilha Grande)"
    facility_type = Column(String(50), nullable=False, index=True)
    # presidio | delegacia | batalhao_pmerj | upp | forum | hospital_referencia
    
    region_version_id = Column(Integer, ForeignKey("region_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    geometry_geojson = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    opened_at = Column(HistoricalDate, nullable=True)             # Início das atividades
    closed_at = Column(HistoricalDate, nullable=True)             # Desativação/demolição (ex: 1994 em Ilha Grande)
    capacity = Column(Integer, nullable=True)                     # Capacidade projetada (NULL se desconhecido)
    
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)

    # Relacionamentos
    region_version = relationship("RegionVersion", back_populates="facilities")
    source = relationship("Source")

    def is_operational_at_year(self, year: int) -> bool:
        """Verifica se a instituição existia operacionalmente no ano t."""
        if self.opened_at and self.opened_at.year > year:
            return False
        if self.closed_at and self.closed_at.year < year:
            return False
        return True

    def __repr__(self):
        return f"<InstitutionalFacility(id={self.id}, name='{self.name}', type='{self.facility_type}')>"


class MovementFlow(Base):
    """
    Fluxos e arcos de deslocamento espaço-temporal (origem -> destino).
    Transferências penitenciárias, deslocamento de lideranças, fugas e expansões territoriais.
    """
    __tablename__ = "movement_flows"

    id = Column(Integer, primary_key=True, index=True)
    flow_type = Column(String(50), nullable=False, index=True)
    # transferencia_penitenciaria | deslocamento_lideranca | expansao_territorial | fuga | operacao_estatal
    
    origin_geometry = Column(Text, nullable=True)                 # GeoJSON Point/Polygon
    origin_region_version_id = Column(Integer, ForeignKey("region_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    
    destination_geometry = Column(Text, nullable=True)            # GeoJSON Point/Polygon
    destination_region_version_id = Column(Integer, ForeignKey("region_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    
    person_id = Column(Integer, ForeignKey("people.id", ondelete="SET NULL"), nullable=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    
    date_start = Column(HistoricalDate, nullable=True)
    date_end = Column(HistoricalDate, nullable=True)
    temporal_precision = Column(String(50), default="dia", nullable=False)
    
    claim_id = Column(Integer, ForeignKey("claims.id", ondelete="SET NULL"), nullable=True, index=True)
    evidence_strength = Column(String(50), default="documentada_primaria", nullable=False)
    notes = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)

    # Relacionamentos
    origin_region_version = relationship("RegionVersion", foreign_keys=[origin_region_version_id])
    destination_region_version = relationship("RegionVersion", foreign_keys=[destination_region_version_id])
    person = relationship("Person")
    organization = relationship("Organization")
    claim = relationship("Claim")

    def __repr__(self):
        return f"<MovementFlow(id={self.id}, type='{self.flow_type}')>"
