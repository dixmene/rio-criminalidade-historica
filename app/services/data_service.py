# -*- coding: utf-8 -*-
"""
Serviço Analítico e de Agregação de Dados Historiográficos.
Extende EventService provendo métricas, agregações e conversões estruturadas.
"""

from collections import Counter
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from sqlalchemy.orm import Session

from app.models import Claim, Event, Organization, Region, Source
from app.services.event_service import EventService

# Cache keyed by (resolved_path, mtime_ns, size) for faction GeoJSON aggregation
_FACTION_DIST_CACHE: Dict[Tuple[str, int, int], Dict[str, Any]] = {}


def _clone_faction_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    """Returns a shallow defensive copy so callers cannot mutate cached dicts."""
    return {
        "total_areas": summary["total_areas"],
        "factions": dict(summary["factions"]),
        "percentages": dict(summary["percentages"]),
    }


class DataService(EventService):
    """
    DataService: Fornece inteligência de dados, agregações estatísticas,
    relatórios de qualidade e integração com bases geoespaciais vetoriais.
    """

    def __init__(self, db: Session):
        super().__init__(db)

    def get_analytics_summary(
        self,
        events: Optional[List[Event]] = None,
        is_demo: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Calcula indicadores analíticos para um conjunto de eventos ou para a base inteira.
        Garante tratamento estrito da regra ZERO ≠ NULL.
        """
        if events is None:
            events = self.list_events(is_demo=is_demo)

        total_events = len(events)
        if total_events == 0:
            return {
                "total_events": 0,
                "events_by_decade": {},
                "events_by_confidence": {},
                "events_by_organization": {},
                "events_by_region": {},
                "events_with_coordinates": 0,
                "events_without_coordinates": 0,
                "total_claims": 0,
                "disputed_claims": 0,
                "total_sources_referenced": 0,
                "sources_coverage_pct": 0.0,
            }

        decades_counter: Counter = Counter()
        conf_counter: Counter = Counter()
        org_counter: Counter = Counter()
        reg_counter: Counter = Counter()
        with_coords = 0
        without_coords = 0
        total_claims = 0
        disputed_claims = 0
        events_with_sources = 0
        all_source_ids = set()

        for ev in events:
            # Década
            yr = ev.year
            if yr:
                decades_counter[(yr // 10) * 10] += 1
            else:
                decades_counter["S/D"] += 1

            # Confiança
            conf_counter[ev.confidence_level or "nao_verificado"] += 1

            # Coordenadas e Regiões
            has_point = False
            for link in ev.region_links:
                reg = link.region
                if reg is not None:
                    reg_counter[reg.original_name] += 1
                    if not has_point and reg.has_coordinates:
                        has_point = True

            if has_point:
                with_coords += 1
            else:
                without_coords += 1

            # Organizações
            for org_link in ev.organization_links:
                org = org_link.organization
                if org is not None:
                    org_counter[org.original_name] += 1

            # Claims e Fontes
            claims = getattr(ev, "claims", None)
            if claims:
                total_claims += len(claims)
                disputed_claims += sum(1 for c in claims if c.is_disputed)

            source_links = ev.source_links
            if source_links:
                events_with_sources += 1
                for sl in source_links:
                    if sl.source_id:
                        all_source_ids.add(sl.source_id)

        coverage_pct = round((events_with_sources / total_events) * 100, 1)

        return {
            "total_events": total_events,
            "events_by_decade": dict(sorted(decades_counter.items(), key=lambda x: str(x[0]))),
            "events_by_confidence": dict(conf_counter),
            "events_by_organization": dict(org_counter.most_common(15)),
            "events_by_region": dict(reg_counter.most_common(15)),
            "events_with_coordinates": with_coords,
            "events_without_coordinates": without_coords,
            "total_claims": total_claims,
            "disputed_claims": disputed_claims,
            "total_sources_referenced": len(all_source_ids),
            "sources_coverage_pct": coverage_pct,
        }

    def get_faction_distribution(
        self,
        geojson_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Lê e resume a distribuição das 1.671 áreas de facções e milícias.
        Utiliza cache validado por mtime e tamanho do arquivo.
        """
        if geojson_path is None:
            geojson_path = Path("data/geospatial/faccoes_rj_1671_poligonos.geojson")
        else:
            geojson_path = Path(geojson_path)

        if not geojson_path.exists():
            return {
                "total_areas": 0,
                "factions": {},
                "percentages": {},
            }

        stat = geojson_path.stat()
        cache_key = (str(geojson_path.resolve()), stat.st_mtime_ns, stat.st_size)
        cached = _FACTION_DIST_CACHE.get(cache_key)
        if cached is not None:
            return _clone_faction_summary(cached)

        with open(geojson_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        features = data.get("features", [])
        total = len(features)
        f_counts: Counter = Counter()

        for ft in features:
            props = ft.get("properties", {})
            fac = props.get("faccao_sigla") or props.get("faccao") or "NEU"
            f_counts[fac] += 1

        percentages = (
            {k: round((v / total) * 100, 1) for k, v in f_counts.items()}
            if total > 0
            else {}
        )

        result = {
            "total_areas": total,
            "factions": dict(f_counts),
            "percentages": percentages,
        }
        _FACTION_DIST_CACHE[cache_key] = result
        return _clone_faction_summary(result)

    def get_sources_summary(self, is_demo: Optional[bool] = None) -> Dict[str, Any]:
        """
        Resume o acervo de fontes bibliográficas e arquivísticas.
        """
        sources = self.list_sources(is_demo=is_demo)
        total = len(sources)
        type_counts: Counter = Counter()
        with_sha = 0

        for s in sources:
            type_counts[s.source_type or "indefinido"] += 1
            if s.file_hash_sha256:
                with_sha += 1

        return {
            "total_sources": total,
            "sources_by_type": dict(type_counts.most_common()),
            "sources_with_custody_hash": with_sha,
            "sources_remote_only": total - with_sha,
        }

    def events_to_dataframe(self, events: Optional[List[Event]] = None) -> pd.DataFrame:
        """
        Converte lista de eventos para DataFrame estruturado.
        """
        cols = [
            "ID",
            "Ano",
            "Data Documentada",
            "Acontecimento",
            "Territórios",
            "Organizações",
            "Fontes",
            "Claims",
            "Confiabilidade",
            "Origem",
        ]
        if events is None:
            events = self.list_events()

        if not events:
            return pd.DataFrame(columns=cols)

        rows = [
            {
                "ID": ev.id,
                "Ano": ev.year if ev.year else "S/D",
                "Data Documentada": ev.date_display,
                "Acontecimento": ev.title,
                "Territórios": (
                    ", ".join(rl.region.original_name for rl in ev.region_links if rl.region is not None)
                    or "Geral / Não delimitado"
                ),
                "Organizações": (
                    ", ".join(
                        ol.organization.original_name
                        for ol in ev.organization_links
                        if ol.organization is not None
                    )
                    or "—"
                ),
                "Fontes": len(ev.source_links),
                "Claims": len(ev.claims) if hasattr(ev, "claims") else 0,
                "Confiabilidade": ev.confidence_level.capitalize() if ev.confidence_level else "—",
                "Origem": "DEMO" if ev.is_demo else "Real",
            }
            for ev in events
        ]
        return pd.DataFrame(rows)

    def sources_to_dataframe(self, sources: Optional[List[Source]] = None) -> pd.DataFrame:
        """
        Converte lista de fontes para DataFrame estruturado.
        """
        cols = [
            "ID",
            "Título",
            "Autor",
            "Ano",
            "Tipologia",
            "Editora/Veículo",
            "Custódia SHA-256",
            "Origem",
        ]
        if sources is None:
            sources = self.list_sources()

        if not sources:
            return pd.DataFrame(columns=cols)

        rows = [
            {
                "ID": s.id,
                "Título": s.title,
                "Autor": s.author or "Não informado",
                "Ano": s.publication_year or "S/D",
                "Tipologia": s.source_type,
                "Editora/Veículo": s.publisher or "—",
                "Custódia SHA-256": (
                    s.file_hash_sha256[:16] + "..." if s.file_hash_sha256 else "Remoto"
                ),
                "Origem": "DEMO" if s.is_demo else "Real",
            }
            for s in sources
        ]
        return pd.DataFrame(rows)
