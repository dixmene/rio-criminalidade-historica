# -*- coding: utf-8 -*-
"""
Serviço do Atlas Histórico Espaço-Temporal (FASE 2)
===================================================

Fornece o estado do mundo espacial para qualquer ano t (1958-2026):
1. get_world_state: Estado completo (territórios, eventos, facilities, fluxos, conflitos, cobertura).
2. get_epistemological_record: Ficha epistemológica de qualquer pixel/feature ("pixel ao trecho literal").
3. get_territorial_timeline: Evolução histórica cronológica de um território específico.
4. Caching em memória com invalidação determinística.
"""

from dataclasses import dataclass, field, asdict
from datetime import date
from functools import lru_cache
import json
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from app.database import SessionLocal

from app.models import (
    Region,
    Organization,
    Event,
    Source,
    EventSource,
    EventRegion,
    Claim,
    ClaimSource,
    TerritorialDataset,
    RegionVersion,
    TerritorialRelation,
    EventFootprint,
    InstitutionalFacility,
    MovementFlow,
)


@dataclass
class EpistemologicalRecord:
    """Ficha Epistemológica: Documentação de proveniência completa do objeto cartográfico."""
    feature_id: str
    feature_type: str
    title: str
    summary: str
    relation_type: Optional[str] = None
    actor_name: Optional[str] = None
    actor_acronym: Optional[str] = None
    date_display: Optional[str] = None
    date_start: Optional[str] = None
    date_end: Optional[str] = None
    temporal_precision: str = "ano"
    date_is_estimated: bool = False
    evidence_strength: str = "documentada_primaria"
    independent_root_count: int = 1
    is_contested: bool = False
    contested_notes: Optional[str] = None
    primary_sources: List[Dict[str, Any]] = field(default_factory=list)
    claims: List[Dict[str, Any]] = field(default_factory=list)
    dataset_provenance: Optional[Dict[str, Any]] = None
    anachronism_warning: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorldState:
    """Estado Espaço-Temporal Completo para um determinado ano/mês."""
    year: int
    month: Optional[int]
    territories: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    facilities: List[Dict[str, Any]] = field(default_factory=list)
    flows: List[Dict[str, Any]] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    coverage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_geojson(self) -> Dict[str, Any]:
        """Exporta todas as camadas combinadas como uma FeatureCollection GeoJSON válida."""
        all_features = []
        for feat in self.territories:
            all_features.append(feat)
        for feat in self.facilities:
            all_features.append(feat)
        for feat in self.events:
            all_features.append(feat)
        for feat in self.flows:
            all_features.append(feat)

        return {
            "type": "FeatureCollection",
            "metadata": self.metadata,
            "coverage": self.coverage,
            "features": all_features
        }


class AtlasService:
    """
    Serviço central de agregação e leitura do Atlas Espaço-Temporal.
    """

    def __init__(self, db: Optional[Session] = None):
        self._db = db

    def _get_db(self) -> Session:
        return self._db if self._db is not None else SessionLocal()

    def get_world_state(
        self,
        year: int,
        month: Optional[int] = None,
        org_filter: Optional[List[str]] = None,
        include_anachronistic: bool = True,
        is_demo: bool = False,
        apply_ethics_guard: bool = True
    ) -> WorldState:
        """
        Retorna o estado cartográfico do mundo para o ano `year` e opcionalmente mês `month`.
        Filtra estritamente por vigência temporal de cada camada.
        """
        db = self._get_db()
        close_db_after = (self._db is None)

        try:
            # 1. Relações Territoriais (Presença, Controle, Influência, Disputa, Presença Estatal)
            rel_query = db.query(TerritorialRelation).options(
                joinedload(TerritorialRelation.region_version).joinedload(RegionVersion.region),
                joinedload(TerritorialRelation.region_version).joinedload(RegionVersion.dataset),
                joinedload(TerritorialRelation.organization),
                joinedload(TerritorialRelation.claim)
            ).filter(
                TerritorialRelation.is_demo == is_demo
            )

            # Filtro temporal da relação
            # A relação é ativa se date_start <= ano E (date_end >= ano OU date_end is NULL)
            all_relations = rel_query.all()
            active_relations = []
            for r in all_relations:
                start_ok = (r.date_start is None or r.date_start.year <= year)
                end_ok = (r.date_end is None or r.date_end.year >= year)
                if start_ok and end_ok:
                    if org_filter and r.organization:
                        if r.organization.acronym not in org_filter and r.organization.name not in org_filter:
                            continue
                    active_relations.append(r)

            territory_features = []
            datasets_cited = set()
            anachronistic_count = 0

            for rel in active_relations:
                reg_ver = rel.region_version
                if not reg_ver:
                    continue
                if not include_anachronistic and reg_ver.is_anachronistic:
                    continue

                if reg_ver.is_anachronistic:
                    anachronistic_count += 1

                reg = reg_ver.region
                ds = reg_ver.dataset
                if ds:
                    datasets_cited.add(ds.name)

                try:
                    geometry = json.loads(reg_ver.geometry_geojson)
                except Exception:
                    continue

                org = rel.organization
                color = "#6B7280"
                if org:
                    acr = (org.acronym or "").upper()
                    if "CV" in acr or "VERMELH" in (org.name or "").upper():
                        color = "#DC2626"  # Vermelho
                    elif "TCP" in acr or "TERCEIRO" in (org.name or "").upper():
                        color = "#2563EB"  # Azul
                    elif "ADA" in acr or "AMIGOS" in (org.name or "").upper():
                        color = "#059669"  # Verde
                    elif "MIL" in acr or "JUSTICA" in acr or org.org_type == "milicia":
                        color = "#374151"  # Grafite escuro / Milícia
                    elif org.org_type in ("policial", "orgao_estatal"):
                        color = "#1D4ED8"  # Azul institucional

                if rel.relation_type == "disputa":
                    color = "#D97706"  # Âmbar para disputa
                elif rel.relation_type == "presenca_estatal":
                    color = "#1D4ED8"  # Azul para presença estatal

                feat = {
                    "type": "Feature",
                    "id": f"territory_{rel.id}",
                    "geometry": geometry,
                    "properties": {
                        "feature_id": f"territory_{rel.id}",
                        "layer": "territories",
                        "relation_id": rel.id,
                        "region_id": reg.id if reg else None,
                        "region_name": reg.original_name if reg else "Território Desconhecido",
                        "relation_type": rel.relation_type,
                        "organization_id": org.id if org else None,
                        "organization_name": org.name if org else None,
                        "organization_acronym": org.acronym if org else None,
                        "color_hex": color,
                        "evidence_strength": rel.evidence_strength,
                        "independent_root_count": rel.independent_root_count,
                        "is_contested": rel.is_contested,
                        "is_anachronistic": reg_ver.is_anachronistic,
                        "anachronism_note": reg_ver.anachronism_note if reg_ver.is_anachronistic else None,
                        "dataset_name": ds.name if ds else None,
                        "dataset_provider": ds.provider if ds else None,
                        "notes": rel.notes
                    }
                }
                territory_features.append(feat)

            # 2. Equipamentos Institucionais (InstitutionalFacility)
            fac_query = db.query(InstitutionalFacility).options(
                joinedload(InstitutionalFacility.region_version),
                joinedload(InstitutionalFacility.source)
            ).filter(InstitutionalFacility.is_demo == is_demo).all()

            facility_features = []
            for fac in fac_query:
                if fac.is_operational_at_year(year):
                    geometry = None
                    if fac.geometry_geojson:
                        try:
                            geometry = json.loads(fac.geometry_geojson)
                        except Exception:
                            pass
                    if not geometry and fac.latitude is not None and fac.longitude is not None:
                        geometry = {"type": "Point", "coordinates": [fac.longitude, fac.latitude]}

                    if not geometry:
                        continue

                    feat = {
                        "type": "Feature",
                        "id": f"facility_{fac.id}",
                        "geometry": geometry,
                        "properties": {
                            "feature_id": f"facility_{fac.id}",
                            "layer": "facilities",
                            "facility_id": fac.id,
                            "name": fac.name,
                            "facility_type": fac.facility_type,
                            "opened_at": fac.opened_at.isoformat() if fac.opened_at else None,
                            "closed_at": fac.closed_at.isoformat() if fac.closed_at else None,
                            "capacity": fac.capacity,
                            "is_operational": True,
                            "notes": fac.notes,
                            "source_citation": fac.source.citation if fac.source else None
                        }
                    }
                    facility_features.append(feat)

            # 3. Fluxos Espaço-Temporais (MovementFlow)
            flow_query = db.query(MovementFlow).filter(MovementFlow.is_demo == is_demo).all()
            flow_features = []
            for fl in flow_query:
                start_ok = (fl.date_start is None or fl.date_start.year <= year)
                end_ok = (fl.date_end is None or fl.date_end.year >= year)
                if start_ok and end_ok:
                    # Constrói geometria de arco/linha
                    geometry = None
                    coords = []
                    if fl.origin_geometry:
                        try:
                            orig_g = json.loads(fl.origin_geometry)
                            if orig_g.get("type") == "Point":
                                coords.append(orig_g["coordinates"])
                        except Exception:
                            pass
                    if fl.destination_geometry:
                        try:
                            dest_g = json.loads(fl.destination_geometry)
                            if dest_g.get("type") == "Point":
                                coords.append(dest_g["coordinates"])
                        except Exception:
                            pass

                    if len(coords) == 2:
                        geometry = {"type": "LineString", "coordinates": coords}
                    elif fl.origin_geometry:
                        geometry = json.loads(fl.origin_geometry)

                    if not geometry:
                        continue

                    feat = {
                        "type": "Feature",
                        "id": f"flow_{fl.id}",
                        "geometry": geometry,
                        "properties": {
                            "feature_id": f"flow_{fl.id}",
                            "layer": "flows",
                            "flow_id": fl.id,
                            "flow_type": fl.flow_type,
                            "date_start": fl.date_start.isoformat() if fl.date_start else None,
                            "date_end": fl.date_end.isoformat() if fl.date_end else None,
                            "evidence_strength": fl.evidence_strength,
                            "notes": fl.notes
                        }
                    }
                    flow_features.append(feat)

            # 4. Acontecimentos Históricos (Event & EventFootprint)
            ev_query = db.query(Event).options(
                joinedload(Event.footprints),
                joinedload(Event.region_links).joinedload(EventRegion.region).joinedload(Region.versions),
                joinedload(Event.source_links).joinedload(EventSource.source),
                joinedload(Event.claims)
            ).filter(
                Event.is_demo == is_demo,
                Event.year == year
            ).all()

            event_features = []
            for ev in ev_query:
                # Se mês foi informado e evento tem mês específico
                if month is not None and ev.date_start and ev.date_start.month != month:
                    continue

                geometry = None
                coord_source = "coordenada_referencial"
                buffer_m = None

                if ev.footprints:
                    fp = ev.footprints[0]
                    try:
                        geometry = json.loads(fp.geometry_geojson)
                        coord_source = fp.coordinate_source
                        buffer_m = fp.buffer_meters
                    except Exception:
                        pass

                if not geometry:
                    for rlink in ev.region_links:
                        reg = rlink.region
                        if reg.latitude is not None and reg.longitude is not None:
                            geometry = {"type": "Point", "coordinates": [reg.longitude, reg.latitude]}
                            coord_source = reg.geometry_source or "Centroide documental da região"
                            break

                if not geometry:
                    continue

                src_cits = [link.source.citation for link in ev.source_links if link.source]
                primary_src = src_cits[0] if src_cits else None

                feat = {
                    "type": "Feature",
                    "id": f"event_{ev.id}",
                    "geometry": geometry,
                    "properties": {
                        "feature_id": f"event_{ev.id}",
                        "layer": "events",
                        "event_id": ev.id,
                        "title": ev.title,
                        "event_type": ev.event_type,
                        "date_display": ev.date_display,
                        "date_start": ev.date_start.isoformat() if ev.date_start else None,
                        "confidence_level": ev.confidence_level,
                        "coordinate_source": coord_source,
                        "buffer_meters": buffer_m,
                        "source_count": len(ev.source_links),
                        "primary_source": primary_src
                    }
                }
                event_features.append(feat)

            # 5. Conflitos & Disputas
            conflicts = [
                f["properties"] for f in territory_features
                if f["properties"]["relation_type"] == "disputa" or f["properties"]["is_contested"]
            ]

            # 6. Cobertura Documental no Ano
            total_regions = db.query(Region).filter(Region.is_demo == is_demo).count()
            active_region_ids = {f["properties"]["region_id"] for f in territory_features if f["properties"]["region_id"]}
            for f in event_features:
                ev_id = f["properties"]["event_id"]
                # adiciona regiões dos eventos
            documented_regions_count = len(active_region_ids)
            density_index = round(documented_regions_count / total_regions, 3) if total_regions > 0 else 0.0

            if density_index >= 0.4:
                cov_status = "bem_documentado"
            elif density_index >= 0.15:
                cov_status = "parcial"
            else:
                cov_status = "lacunar"

            coverage = {
                "year": year,
                "total_known_regions": total_regions,
                "regions_with_coverage": documented_regions_count,
                "evidence_density_index": density_index,
                "coverage_status": cov_status
            }

            # 7. Metadados de Auditoria
            warning = None
            if anachronistic_count > 0:
                warning = f"Atenção historiográfica: {anachronistic_count} polígonos contemporâneos estão sendo exibidos para o ano de {year}. Suas fronteiras são ilustrativas e sinalizadas cartograficamente com padrão hachurado cinza."

            metadata = {
                "year": year,
                "month": month,
                "datasets_referenced": sorted(list(datasets_cited)),
                "total_features": len(territory_features) + len(facility_features) + len(flow_features) + len(event_features),
                "territories_count": len(territory_features),
                "facilities_count": len(facility_features),
                "flows_count": len(flow_features),
                "events_count": len(event_features),
                "anachronistic_features_count": anachronistic_count,
                "epistemological_warning": warning
            }

            ws = WorldState(
                year=year,
                month=month,
                territories=territory_features,
                events=event_features,
                facilities=facility_features,
                flows=flow_features,
                conflicts=conflicts,
                coverage=coverage,
                metadata=metadata
            )

            if apply_ethics_guard:
                from app.services.ethics_guard import EthicsGuard
                ws = EthicsGuard.apply_embargo(ws)

            return ws

        finally:
            if close_db_after:
                db.close()

    def get_epistemological_record(self, feature_id: str) -> Optional[EpistemologicalRecord]:
        """
        Retorna a Ficha Epistemológica completa de qualquer feição cartográfica do Atlas.
        Permite ao pesquisador auditar a evidência exata que sustenta o elemento renderizado.
        """
        db = self._get_db()
        close_db_after = (self._db is None)

        try:
            parts = feature_id.split("_")
            if len(parts) < 2:
                return None
            kind = parts[0]
            obj_id = int(parts[1])

            if kind == "territory":
                rel = db.query(TerritorialRelation).options(
                    joinedload(TerritorialRelation.region_version).joinedload(RegionVersion.region),
                    joinedload(TerritorialRelation.region_version).joinedload(RegionVersion.dataset),
                    joinedload(TerritorialRelation.organization),
                    joinedload(TerritorialRelation.claim).joinedload(Claim.source_links).joinedload(ClaimSource.source)
                ).filter(TerritorialRelation.id == obj_id).first()

                if not rel:
                    return None

                reg_ver = rel.region_version
                reg = reg_ver.region if reg_ver else None
                ds = reg_ver.dataset if reg_ver else None
                org = rel.organization

                sources = []
                claims = []
                if rel.claim:
                    claims.append({
                        "claim_id": rel.claim.id,
                        "assertion": rel.claim.assertion,
                        "confidence": rel.claim.confidence,
                        "epistemic_category": rel.claim.epistemic_category
                    })
                    for link in rel.claim.source_links:
                        sources.append({
                            "source_id": link.source.id,
                            "citation": link.source.citation,
                            "page_or_section": link.page_or_section,
                            "excerpt": link.excerpt,
                            "validation_status": link.validation_status
                        })

                return EpistemologicalRecord(
                    feature_id=feature_id,
                    feature_type="territorio_dominio",
                    title=f"{rel.relation_type.upper()}: {reg.original_name if reg else 'Território'} ({org.acronym if org else 'Desconhecido'})",
                    summary=rel.notes or "Relação territorial documentada.",
                    relation_type=rel.relation_type,
                    actor_name=org.name if org else None,
                    actor_acronym=org.acronym if org else None,
                    date_display=f"{rel.date_start} a {rel.date_end or 'presente'}",
                    date_start=rel.date_start.isoformat() if rel.date_start else None,
                    date_end=rel.date_end.isoformat() if rel.date_end else None,
                    temporal_precision=rel.temporal_precision,
                    date_is_estimated=rel.date_is_estimated,
                    evidence_strength=rel.evidence_strength,
                    independent_root_count=rel.independent_root_count,
                    is_contested=rel.is_contested,
                    contested_notes=rel.contested_by_claim_ids,
                    primary_sources=sources,
                    claims=claims,
                    dataset_provenance={
                        "dataset_name": ds.name if ds else "Desconhecido",
                        "provider": ds.provider if ds else "Desconhecido",
                        "license": ds.license if ds else "Não especificada",
                        "sha256": ds.sha256 if ds else None,
                        "version": ds.version if ds else None
                    } if ds else None,
                    anachronism_warning={
                        "is_anachronistic": reg_ver.is_anachronistic,
                        "note": reg_ver.anachronism_note
                    } if (reg_ver and reg_ver.is_anachronistic) else None
                )

            elif kind == "facility":
                fac = db.query(InstitutionalFacility).options(
                    joinedload(InstitutionalFacility.source),
                    joinedload(InstitutionalFacility.region_version)
                ).filter(InstitutionalFacility.id == obj_id).first()

                if not fac:
                    return None

                sources = []
                if fac.source:
                    sources.append({
                        "source_id": fac.source.id,
                        "citation": fac.source.citation,
                        "source_type": fac.source.source_type,
                        "publication_year": fac.source.publication_year
                    })

                return EpistemologicalRecord(
                    feature_id=feature_id,
                    feature_type="equipamento_institucional",
                    title=fac.name,
                    summary=fac.notes or f"Instalação pública do tipo {fac.facility_type}.",
                    relation_type=fac.facility_type,
                    actor_name="Estado / Poder Público",
                    date_start=fac.opened_at.isoformat() if fac.opened_at else None,
                    date_end=fac.closed_at.isoformat() if fac.closed_at else None,
                    primary_sources=sources,
                    claims=[]
                )

            elif kind == "event":
                ev = db.query(Event).options(
                    joinedload(Event.source_links).joinedload(EventSource.source),
                    joinedload(Event.claims)
                ).filter(Event.id == obj_id).first()

                if not ev:
                    return None

                sources = []
                for link in ev.source_links:
                    sources.append({
                        "source_id": link.source.id,
                        "citation": link.source.citation,
                        "page_or_section": link.page_or_section,
                        "excerpt": link.excerpt,
                        "confidence_level": link.confidence_level
                    })

                claims = []
                for cl in ev.claims:
                    claims.append({
                        "claim_id": cl.id,
                        "assertion": cl.assertion,
                        "confidence": cl.confidence,
                        "epistemic_category": cl.epistemic_category
                    })

                return EpistemologicalRecord(
                    feature_id=feature_id,
                    feature_type="acontecimento_historico",
                    title=ev.title,
                    summary=ev.description,
                    relation_type=ev.event_type,
                    date_display=ev.date_display,
                    date_start=ev.date_start.isoformat() if ev.date_start else None,
                    date_end=ev.date_end.isoformat() if ev.date_end else None,
                    temporal_precision=ev.temporal_precision,
                    date_is_estimated=ev.date_is_estimated,
                    evidence_strength=ev.confidence_level,
                    primary_sources=sources,
                    claims=claims
                )

            elif kind == "flow":
                fl = db.query(MovementFlow).filter(MovementFlow.id == obj_id).first()
                if not fl:
                    return None

                return EpistemologicalRecord(
                    feature_id=feature_id,
                    feature_type="fluxo_espacotemporal",
                    title=f"Fluxo: {fl.flow_type.replace('_', ' ').title()}",
                    summary=fl.notes or "Deslocamento documentado de liderança ou transferência institucional.",
                    relation_type=fl.flow_type,
                    date_start=fl.date_start.isoformat() if fl.date_start else None,
                    date_end=fl.date_end.isoformat() if fl.date_end else None,
                    temporal_precision=fl.temporal_precision,
                    evidence_strength=fl.evidence_strength
                )

            return None

        finally:
            if close_db_after:
                db.close()

    def get_territorial_timeline(self, region_id: int) -> List[Dict[str, Any]]:
        """
        Retorna a cronologia de ocupação e relações de domínio para uma dada região.
        Permite compreender a transição de atores (ex: jogo do bicho -> tráfico -> milícia).
        """
        db = self._get_db()
        close_db_after = (self._db is None)

        try:
            relations = db.query(TerritorialRelation).join(RegionVersion).options(
                joinedload(TerritorialRelation.organization),
                joinedload(TerritorialRelation.region_version).joinedload(RegionVersion.dataset)
            ).filter(
                RegionVersion.region_id == region_id
            ).order_by(TerritorialRelation.date_start.asc()).all()

            timeline = []
            for r in relations:
                timeline.append({
                    "relation_id": r.id,
                    "organization": r.organization.name if r.organization else "Não identificada",
                    "organization_acronym": r.organization.acronym if r.organization else None,
                    "relation_type": r.relation_type,
                    "date_start": r.date_start.isoformat() if r.date_start else None,
                    "date_end": r.date_end.isoformat() if r.date_end else "presente",
                    "evidence_strength": r.evidence_strength,
                    "is_contested": r.is_contested,
                    "notes": r.notes
                })

            return timeline
        finally:
            if close_db_after:
                db.close()
