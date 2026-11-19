#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reproducible Benchmark Suite for rio-criminalidade-historica.

Measures real computational and data-pipeline hotspots across the repository:
  1. db_event_queries           - EventService & DataService SQLite/ORM queries (scaled DB)
  2. genealogy_verification     - GenealogyService + VerificationService queue (scaled DAG)
  3. integrity_audit_prod       - 13-pillar Research Integrity Audit on production SQLite DB
  4. claim_validation_verbatim  - ClaimValidator anti-hallucination over real transcripts
  5. normalization_classifier   - Unicode/temporal normalization & legislative classifier
  6. geospatial_and_spatial     - GeoJSON faction distribution, Parquet loading & TSE AISP join
  7. isp_timeseries_aggregation - ISP-RJ CISP-to-AISP/State timeseries aggregation
  8. provenance_sha256          - Streaming SHA-256 verification on geospatial & transcript files

Usage:
    python scripts/benchmark_suite.py
    python scripts/benchmark_suite.py --json reports/benchmark_latest.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable, Dict, List

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import Base
from app.models import (
    Claim,
    ClaimSource,
    Event,
    EventOrganization,
    EventPerson,
    EventRegion,
    EventSource,
    Organization,
    Person,
    Region,
    Source,
    SourceDerivation,
)
from app.map.layers import load_aisp_dataframe, load_aisp_polygons, load_bairros_dataframe
from app.services.claim_validator import ClaimValidator
from app.services.data_service import DataService
from app.services.event_service import EventService
from app.services.genealogy_service import GenealogyService
from app.services.verification_service import VerificationService
from scripts.audit_research_integrity import run_integrity_audit
from scripts.classifier_pautas import classify_legislative_text
from scripts.etl_tse_votacao import generate_baseline_locais_votacao, match_point_to_aisp
from scripts.geospatial.process_isp_timeseries import aggregate_isp_timeseries
from scripts.ingestion.ingest_source import calculate_sha256
from src.normalization.rules import (
    normalize_location,
    normalize_name,
    normalize_nulls,
    normalize_organization,
    normalize_temporal_expression,
)


@dataclass
class BenchmarkResult:
    name: str
    description: str
    iterations: int
    median_ms: float
    mean_ms: float
    min_ms: float
    max_ms: float
    ops_per_sec: float
    metadata: Dict[str, Any]


def time_benchmark(
    name: str,
    description: str,
    fn: Callable[[], Any],
    iterations: int = 5,
    warmup: int = 1,
    metadata: Dict[str, Any] | None = None,
) -> BenchmarkResult:
    """Runs warmup + timed iterations using time.perf_counter()."""
    for _ in range(warmup):
        fn()

    timings_ms: List[float] = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        fn()
        t1 = time.perf_counter()
        timings_ms.append((t1 - t0) * 1000.0)

    median_ms = statistics.median(timings_ms)
    mean_ms = statistics.mean(timings_ms)
    ops_per_sec = 1000.0 / median_ms if median_ms > 0 else 0.0
    return BenchmarkResult(
        name=name,
        description=description,
        iterations=iterations,
        median_ms=round(median_ms, 3),
        mean_ms=round(mean_ms, 3),
        min_ms=round(min(timings_ms), 3),
        max_ms=round(max(timings_ms), 3),
        ops_per_sec=round(ops_per_sec, 2),
        metadata=metadata or {},
    )


def _build_scaled_sqlite_session(
    n_events: int = 120,
    n_sources: int = 240,
    n_claims_per_event: int = 2,
) -> tuple[Session, Any]:
    """Creates a realistic scaled in-memory SQLite DB with rich relations & derivation DAG."""
    engine = create_engine("sqlite:///:memory:", future=True)

    @event.listens_for(engine, "connect")
    def _set_fk(dbapi_conn, _):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(bind=engine)
    SessionCls = sessionmaker(bind=engine)
    db = SessionCls()

    # Regions, Orgs, People
    regions = [
        Region(
            original_name=f"Bairro Histórico {i}",
            normalized_name=f"BAIRRO HISTORICO {i}",
            region_type="bairro",
            latitude=-22.90 + (i % 15) * 0.01 if i % 6 != 0 else None,
            longitude=-43.20 - (i % 15) * 0.01 if i % 6 != 0 else None,
            geometry_source="IPP/Data.Rio" if i % 6 != 0 else None,
            is_demo=False,
        )
        for i in range(30)
    ]
    orgs = [
        Organization(
            original_name=f"Organização {i}",
            normalized_name=f"ORGANIZACAO {i}",
            acronym=f"ORG{i}",
            org_type="faccao_criminosa" if i % 2 == 0 else "orgao_estatal",
            is_demo=False,
        )
        for i in range(20)
    ]
    people = [
        Person(
            original_name=f"Personagem {i}",
            normalized_name=f"PERSONAGEM {i}",
            is_demo=False,
        )
        for i in range(30)
    ]

    source_types = [
        "documento_judicial",
        "oficial_relatorio",
        "academico_livro",
        "jornalismo_hemeroteca",
        "audiovisual_youtube",
    ]
    sources = [
        Source(
            title=f"Fonte Documental Histórica #{i}",
            citation=f"AUTOR {i}. Documento #{i}. Rio de Janeiro, {1955 + (i % 70)}.",
            author=f"Autor {i % 40}",
            source_type=source_types[i % len(source_types)],
            publication_year=1955 + (i % 70),
            file_hash_sha256=hashlib.sha256(f"src-{i}".encode()).hexdigest() if i % 3 == 0 else None,
            is_demo=False,
        )
        for i in range(n_sources)
    ]
    db.add_all(regions + orgs + people + sources)
    db.flush()

    # Build multi-level source derivation chains (depth 4) for genealogy traversal
    derivations = []
    for i in range(40, n_sources):
        parent_idx = i - 40
        derivations.append(
            SourceDerivation(
                parent_source_id=sources[parent_idx].id,
                derived_source_id=sources[i].id,
                derivation_type="reproduz" if i % 2 == 0 else "deriva_dado",
                is_independent=(i % 7 == 0),
            )
        )
    db.add_all(derivations)
    db.flush()

    conf_levels = ["confirmado", "provavel", "conflitante", "nao_verificado"]
    events = []
    for i in range(n_events):
        yr = 1955 + (i % 70)
        events.append(
            Event(
                title=f"Evento Histórico Documentado #{i} no Rio de Janeiro",
                event_type="conflito_armado" if i % 2 == 0 else "politica_publica_seguranca",
                date_display=f"{yr}",
                date_start=date(yr, 1, 1),
                date_end=date(yr, 12, 31),
                year=yr,
                temporal_precision="ano",
                exact_date=False,
                description=f"Descrição historiográfica detalhada do evento #{i} em {yr}.",
                confidence_level=conf_levels[i % len(conf_levels)],
                is_demo=False,
            )
        )
    db.add_all(events)
    db.flush()

    # Attach 3 sources, 2 regions, 2 orgs, 2 people, and 2 claims (with 3 sources each) per event
    links: List[Any] = []
    claims: List[Claim] = []
    for idx, ev in enumerate(events):
        for k in range(3):
            s = sources[(idx * 3 + k) % n_sources]
            links.append(
                EventSource(
                    event_id=ev.id,
                    source_id=s.id,
                    page=f"p. {10 + k}",
                    excerpt=f"Trecho documental literal comprobatório do evento {idx} na fonte {s.id}.",
                    confidence_level="confirmado",
                )
            )
        for k in range(2):
            links.append(EventRegion(event_id=ev.id, region_id=regions[(idx + k) % len(regions)].id))
            links.append(EventOrganization(event_id=ev.id, organization_id=orgs[(idx + k) % len(orgs)].id))
            links.append(EventPerson(event_id=ev.id, person_id=people[(idx + k) % len(people)].id))

        for c_i in range(n_claims_per_event):
            claims.append(
                Claim(
                    event_id=ev.id,
                    claim_type="fato" if c_i == 0 else "territorio",
                    statement=f"Afirmação factual #{idx}-{c_i} sobre dinâmica territorial no RJ.",
                    confidence_level=conf_levels[(idx + c_i) % len(conf_levels)],
                    is_disputed=((idx + c_i) % 10 == 0),
                    is_demo=False,
                )
            )
    db.add_all(links + claims)
    db.flush()

    claim_links = []
    stances = ["apoia", "apoia", "matiza", "contesta"]
    for c_idx, cl in enumerate(claims):
        for k in range(3):
            # Intentionally create chains sharing root for false triangulation tests
            if c_idx % 4 == 0:
                base_root = c_idx % 40
                src = sources[base_root + (k + 1) * 40]
            else:
                src = sources[(c_idx * 3 + k) % n_sources]
            claim_links.append(
                ClaimSource(
                    claim_id=cl.id,
                    source_id=src.id,
                    stance="contesta" if (cl.is_disputed and k == 2) else stances[(c_idx + k) % 3],
                    page=f"0{k}:15",
                    excerpt=f"Citação literal verificada da afirmação {cl.id} na fonte {src.id}.",
                )
            )
    db.add_all(claim_links)
    db.commit()
    return db, engine


def _build_synthetic_isp_cisp_df(n_years: int = 10, n_aisps: int = 35, cisps_per_aisp: int = 3) -> pd.DataFrame:
    """Builds a deterministic ~12,600-row CISP-level ISP dataframe for aggregation benchmarking."""
    rng = np.random.default_rng(42)
    rows_aisp = []
    rows_cisp = []
    rows_ano = []
    rows_mes = []
    cisp_id = 1
    aisp_ids = list(range(1, n_aisps + 1))
    cisp_map = []
    for a in aisp_ids:
        for _ in range(cisps_per_aisp):
            cisp_map.append((a, cisp_id))
            cisp_id += 1

    for ano in range(2005, 2005 + n_years):
        for mes in range(1, 13):
            for a, c in cisp_map:
                rows_aisp.append(a)
                rows_cisp.append(c)
                rows_ano.append(ano)
                rows_mes.append(mes)

    n = len(rows_aisp)
    df = pd.DataFrame(
        {
            "aisp": rows_aisp,
            "cisp": rows_cisp,
            "ano": rows_ano,
            "mes": rows_mes,
            "hom_doloso": rng.integers(0, 20, size=n),
            "hom_por_interv_policial": rng.integers(0, 10, size=n),
            "letalidade_violenta": rng.integers(0, 30, size=n),
            "roubo_veiculo": rng.integers(0, 120, size=n),
            "roubo_carga": rng.integers(0, 40, size=n),
            "roubo_transeunte": rng.integers(0, 250, size=n),
            "roubo_rua": rng.integers(0, 300, size=n),
            "armas_apreendidas": np.where(np.array(rows_ano) < 2007, np.nan, rng.integers(0, 25, size=n)),
            "fuzil_apreendido": np.where(np.array(rows_ano) < 2007, np.nan, rng.integers(0, 4, size=n)),
            "latrocinio": rng.integers(0, 3, size=n),
            "cvli": rng.integers(0, 35, size=n),
            "total_roubos": rng.integers(0, 500, size=n),
            "recuperacao_veiculos": rng.integers(0, 60, size=n),
            "registro_ocorrencias": rng.integers(50, 1500, size=n),
        }
    )
    return df


def run_all_benchmarks() -> List[BenchmarkResult]:
    results: List[BenchmarkResult] = []

    # ------------------------------------------------------------------
    # 1. SQLite / ORM Event Queries & Analytics (scaled DB)
    # ------------------------------------------------------------------
    db_scaled, engine_scaled = _build_scaled_sqlite_session(
        n_events=120, n_sources=240, n_claims_per_event=2
    )
    try:
        ds_scaled = DataService(db_scaled)

        def bench_db_events():
            db_scaled.expire_all()
            events = ds_scaled.list_events(is_demo=False)
            _ = ds_scaled.get_timeline_bounds(is_demo=False)
            _ = ds_scaled.get_analytics_summary(events=events)
            _ = ds_scaled.events_to_dataframe(events=events)
            return len(events)

        results.append(
            time_benchmark(
                name="db_event_queries",
                description="EventService.list_events + timeline_bounds + analytics + dataframe (120 events, rich joins)",
                fn=bench_db_events,
                iterations=7,
                warmup=1,
                metadata={"events": 120, "sources": 240, "claims": 240},
            )
        )

        # ------------------------------------------------------------------
        # 2. Genealogy Graph Traversal & Verification Queue (scaled DAG)
        # ------------------------------------------------------------------
        def bench_genealogy_verification():
            db_scaled.expire_all()
            q = VerificationService.generate_verification_queue(db_scaled, include_demo=True)
            return q["total_claims_audited"]

        results.append(
            time_benchmark(
                name="genealogy_verification",
                description="VerificationService.generate_verification_queue + GenealogyService (240 claims, 4-level DAG)",
                fn=bench_genealogy_verification,
                iterations=7,
                warmup=1,
                metadata={"claims": 240, "sources": 240, "derivations": 200},
            )
        )
    finally:
        db_scaled.close()
        engine_scaled.dispose()

    # ------------------------------------------------------------------
    # 3. Research Integrity Audit (13 Pillars on production DB)
    # ------------------------------------------------------------------
    results.append(
        time_benchmark(
            name="integrity_audit_prod",
            description="scripts.audit_research_integrity.run_integrity_audit(include_demo=False)",
            fn=lambda: run_integrity_audit(include_demo=False),
            iterations=7,
            warmup=1,
            metadata={"checks": 13},
        )
    )

    # ------------------------------------------------------------------
    # 4. Epistemology Anti-Hallucination Claim Validation (Real Transcripts)
    # ------------------------------------------------------------------
    transcripts_dir = PROJECT_ROOT / "data" / "raw" / "audiovisual" / "transcripts"
    transcript_files = sorted(transcripts_dir.glob("*.json"))[:3]
    transcript_texts: List[str] = []
    for tf in transcript_files:
        with open(tf, "r", encoding="utf-8") as f:
            transcript_texts.append(json.load(f).get("full_text", ""))

    # Build a deterministic workload of exact, ellipsis, fuzzy (ASR drift), and hallucinated claims
    claim_workloads: List[tuple[str, str]] = []
    for txt in transcript_texts:
        words = txt.split()
        if len(words) < 120:
            continue
        # 5 exact excerpts
        for start in (20, 150, 350, 600, 900):
            if start + 18 < len(words):
                claim_workloads.append((" ".join(words[start : start + 18]), txt))
        # 4 multi-clause ellipsis excerpts (one slightly mutated for fuzzy fallback)
        for start in (40, 220, 480, 720):
            if start + 60 < len(words):
                c1 = " ".join(words[start : start + 12])
                c2_words = list(words[start + 35 : start + 48])
                if start == 480:
                    c2_words[2] = c2_words[2] + "x"  # slight ASR typo
                c2 = " ".join(c2_words)
                claim_workloads.append((f"{c1} ... {c2}", txt))
        # 4 fuzzy excerpts (ASR typos)
        for start in (100, 300, 550, 800):
            if start + 16 < len(words):
                seg = list(words[start : start + 16])
                seg[3] = seg[3] + "s"
                seg[9] = "erroasr"
                claim_workloads.append((" ".join(seg), txt))
        # 4 hallucinated excerpts (worst-case full scan)
        for idx_h in range(4):
            claim_workloads.append(
                (
                    f"submarino nuclear invisivel pousou no corcovado em 194{idx_h} com alienigenas de marte",
                    txt,
                )
            )

    def bench_claim_validation():
        valid_count = 0
        for excerpt, txt in claim_workloads:
            res = ClaimValidator.validate_verbatim_excerpt(excerpt, txt)
            if res["valid"]:
                valid_count += 1
        return valid_count

    results.append(
        time_benchmark(
            name="claim_validation_verbatim",
            description=f"ClaimValidator.validate_verbatim_excerpt ({len(claim_workloads)} mixed claims over 3 real transcripts)",
            fn=bench_claim_validation,
            iterations=5,
            warmup=1,
            metadata={"claims": len(claim_workloads), "transcripts": len(transcript_texts)},
        )
    )

    # ------------------------------------------------------------------
    # 5. Normalization Rules + Legislative Taxonomy Classifier
    # ------------------------------------------------------------------
    sample_dates = [
        "1981-04-30",
        "15/03/1983",
        "12 de maio de 1994",
        "agosto de 1979",
        "1978-05",
        "década de 1980",
        "c. 1982",
        "1975",
        "por volta de 1993 na Zona Oeste",
        "s/d",
        "não informado",
    ] * 200
    sample_names = [
        "São Gonçalo",
        "Rogério Lemgruber",
        "Complexo do Alemão",
        "Élcio de Queiroz",
        "Praça Seca",
        "Duque de Caxias",
        "Comando Vermelho",
        "não consta",
    ] * 250
    sample_bills = [
        ("Regulamenta o itinerário e permissão de vans e mototáxis na Zona Oeste", ""),
        ("Dispõe sobre a desafetação de área pública e regularização fundiária em loteamento irregular", ""),
        ("Estabelece regras para distribuição de botijão de gás GLP e água mineral", ""),
        ("Dispõe sobre fiscalização de ferro-velho e combate à receptação de fios de cobre", ""),
        ("Concede moção de aplauso e medalha Tiradentes ao comandante de batalhão", ""),
        ("Aprova a prestação de contas do exercício financeiro municipal e diretrizes orçamentárias", ""),
    ] * 250

    def bench_norm_and_classifier():
        for d in sample_dates:
            normalize_temporal_expression(d)
        for n in sample_names:
            normalize_name(n)
            normalize_location(n)
            normalize_organization(n)
            normalize_nulls(n)
        for ementa, txt in sample_bills:
            classify_legislative_text(ementa, txt)

    results.append(
        time_benchmark(
            name="normalization_classifier",
            description="normalize_temporal_expression (2.2k) + entity/null norm (8k) + classify_legislative_text (1.5k)",
            fn=bench_norm_and_classifier,
            iterations=5,
            warmup=1,
            metadata={"dates": len(sample_dates), "names": len(sample_names), "bills": len(sample_bills)},
        )
    )

    # ------------------------------------------------------------------
    # 6. Geospatial Loading, Faction Distribution & TSE Point-in-Polygon
    # ------------------------------------------------------------------
    aisp_geo = load_aisp_polygons()
    aisp_features = aisp_geo.get("features", []) if aisp_geo else []
    base_locais = generate_baseline_locais_votacao()
    # 30 query points (5x the baseline locais with tiny offsets)
    query_points = [
        (loc["latitude"] + (k * 0.0005), loc["longitude"] - (k * 0.0005))
        for k in range(5)
        for loc in base_locais
    ]
    tmp_engine = create_engine("sqlite:///:memory:", future=True)
    tmp_db = sessionmaker(bind=tmp_engine)()
    ds_geo = DataService(tmp_db)

    def bench_geospatial():
        # Repeated analytics call (faction distribution) + Parquet loads + point-in-polygon
        for _ in range(3):
            _ = ds_geo.get_faction_distribution()
        _ = load_aisp_dataframe()
        _ = load_bairros_dataframe()
        matched = 0
        for lat, lon in query_points:
            if match_point_to_aisp(lat, lon, aisp_features):
                matched += 1
        return matched

    results.append(
        time_benchmark(
            name="geospatial_and_spatial",
            description="3x get_faction_distribution (4.8MB GeoJSON) + Parquet loads + 30x TSE point-in-polygon (16.7MB AISP)",
            fn=bench_geospatial,
            iterations=5,
            warmup=1,
            metadata={"points": len(query_points), "aisp_features": len(aisp_features)},
        )
    )
    tmp_db.close()
    tmp_engine.dispose()

    # ------------------------------------------------------------------
    # 7. ISP-RJ Timeseries Aggregation Pipeline
    # ------------------------------------------------------------------
    df_cisp_synth = _build_synthetic_isp_cisp_df(n_years=10, n_aisps=35, cisps_per_aisp=3)

    # Suppress verbose prints inside aggregate_isp_timeseries during benchmark
    import io
    import contextlib

    def bench_isp_aggregation():
        with contextlib.redirect_stdout(io.StringIO()):
            out = aggregate_isp_timeseries(df_cisp_synth)
        return len(out)

    results.append(
        time_benchmark(
            name="isp_timeseries_aggregation",
            description=f"aggregate_isp_timeseries on {len(df_cisp_synth):,} CISP rows (10 yrs x 35 AISPs x 3 CISPs)",
            fn=bench_isp_aggregation,
            iterations=5,
            warmup=1,
            metadata={"input_rows": len(df_cisp_synth)},
        )
    )

    # ------------------------------------------------------------------
    # 8. Provenance SHA-256 Verification (Geospatial + Transcripts)
    # ------------------------------------------------------------------
    geo_files = [
        PROJECT_ROOT / "data" / "geospatial" / "faccoes_rj_1671_poligonos.geojson",
        PROJECT_ROOT / "data" / "geospatial" / "bairros_rio_166_poligonos.geojson",
        PROJECT_ROOT / "data" / "geospatial" / "aisps_batalhoes_pmerj.geojson",
    ]
    all_transcripts = sorted(transcripts_dir.glob("*.json"))

    def bench_provenance_sha256():
        hashes = []
        for gf in geo_files:
            if gf.exists():
                hashes.append(calculate_sha256(gf))
        for tf in all_transcripts:
            with open(tf, "r", encoding="utf-8") as f:
                tdata = json.load(f)
            hashes.append(hashlib.sha256(tdata.get("full_text", "").encode("utf-8")).hexdigest())
        return len(hashes)

    results.append(
        time_benchmark(
            name="provenance_sha256",
            description="Streaming SHA-256 on 32MB geospatial GeoJSONs + 10 audiovisual transcript JSONs",
            fn=bench_provenance_sha256,
            iterations=5,
            warmup=1,
            metadata={"geo_files": len(geo_files), "transcript_files": len(all_transcripts)},
        )
    )

    return results


def print_results_table(results: List[BenchmarkResult]) -> None:
    print("=" * 98)
    print(f"{'Benchmark':<28} {'Median (ms)':>12} {'Mean (ms)':>11} {'Min (ms)':>10} {'Max (ms)':>10} {'Ops/s':>10}")
    print("-" * 98)
    total_median = 0.0
    for r in results:
        total_median += r.median_ms
        print(
            f"{r.name:<28} {r.median_ms:>12.2f} {r.mean_ms:>11.2f} {r.min_ms:>10.2f} {r.max_ms:>10.2f} {r.ops_per_sec:>10.2f}"
        )
    print("-" * 98)
    print(f"{'TOTAL (sum of medians)':<28} {total_median:>12.2f} ms")
    print("=" * 98)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run reproducible benchmark suite.")
    parser.add_argument("--json", type=str, default=None, help="Optional path to save JSON results.")
    args = parser.parse_args()

    results = run_all_benchmarks()
    print_results_table(results)

    if args.json:
        out_path = Path(args.json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "python": sys.version,
            "total_median_ms": round(sum(r.median_ms for r in results), 3),
            "benchmarks": [
                {
                    "name": r.name,
                    "description": r.description,
                    "iterations": r.iterations,
                    "median_ms": r.median_ms,
                    "mean_ms": r.mean_ms,
                    "min_ms": r.min_ms,
                    "max_ms": r.max_ms,
                    "ops_per_sec": r.ops_per_sec,
                    "metadata": r.metadata,
                }
                for r in results
            ],
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"[+] Benchmark JSON saved to: {out_path}")


if __name__ == "__main__":
    main()
