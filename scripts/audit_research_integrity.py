#!/usr/bin/env python3
"""
Auditoria de Integridade da Pesquisa Histórica Digital (Research Integrity Audit)
================================================================================

Executa a verificação dos 13 pilares metodológicos e epistemológicos do projeto:

 1. Eventos sem Fontes Documentais (events_without_sources)
 2. Eventos sem Intervalos Temporais Explícitos (events_without_temporal_intervals)
 3. Claims sem Fontes Associadas (claims_without_sources)
 4. Claims sem Citação Literal / Excerpt (claims_without_excerpts)
 5. Claims Audiovisuais sem Timestamp Auditável (audiovisual_claims_without_timestamps)
 6. Falsa Triangulação de Fontes (false_triangulation_violations)
 7. Contaminação por Dados Demo/Sintéticos (demo_contamination_in_prod)
 8. Inconsistência Cronológica de Datas (impossible_chronology_dates)
 9. Violação de Nulidade Geoespacial (Zero vs NULL) (geospatial_zero_as_null_violations)
10. Derivações com Referências Órfãs (derived_sources_missing_parent)
11. Ciclos e Dependências Circulares na Genealogia (circular_derivation_dependencies)
12. Transcrições sem Hash SHA-256 ou Adulteradas (unhashed_transcripts)
13. Controvérsias Historiográficas sem Nota Epistemológica (unanchored_controversial_claims)

Gera: 'reports/research_integrity_report.json'
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Dict, List

from sqlalchemy.orm import joinedload, selectinload

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database import SessionLocal
from app.models.associations import EventSource, SourceDerivation
from app.models.claim import Claim, ClaimSource
from app.models.event import Event
from app.models.source import Source
from app.services.genealogy_service import GenealogyService

_AUDIOVISUAL_SOURCE_TYPES = frozenset({"audiovisual_youtube", "video_youtube"})
_TIMESTAMP_KEYWORDS = ("timestamp", ":", "minuto")


def run_integrity_audit(include_demo: bool = False) -> Dict[str, Any]:
    session = SessionLocal()
    try:
        report: Dict[str, Any] = {
            "audit_date": datetime.now(timezone.utc).isoformat(),
            "scope": "producao_apenas" if not include_demo else "completo_com_demo",
            "total_checks": 13,
            "passed_checks": 0,
            "failed_checks": 0,
            "warning_checks": 0,
            "checks": {},
            "integrity_score": 0.0,
        }

        def filter_demo(q, model):
            if not include_demo and hasattr(model, "is_demo"):
                return q.filter(model.is_demo == False)
            return q

        # Eager-load events, claims, claim_sources, and genealogy graph upfront (zero N+1)
        ev_query = filter_demo(
            session.query(Event).options(
                selectinload(Event.source_links).joinedload(EventSource.source),
                selectinload(Event.claims).selectinload(Claim.source_links),
            ),
            Event,
        ).all()

        cl_query = filter_demo(
            session.query(Claim).options(
                selectinload(Claim.source_links).joinedload(ClaimSource.source)
            ),
            Claim,
        ).all()

        cs_query = (
            session.query(ClaimSource)
            .options(joinedload(ClaimSource.source))
            .all()
        )

        genealogy_index = GenealogyService.build_genealogy_index(session)
        root_cache = genealogy_index.root_cache

        # -------------------------------------------------------------
        # CHECKS 1, 2, 8, 9: Single pass over ev_query
        # -------------------------------------------------------------
        ev_no_src: List[Dict[str, Any]] = []
        ev_no_temp: List[Dict[str, Any]] = []
        date_inconsistencies: List[Dict[str, Any]] = []
        geo_violations: List[Dict[str, Any]] = []

        for ev in ev_query:
            has_ev_sources = len(ev.source_links) > 0
            has_claim_sources = any(len(c.source_links) > 0 for c in ev.claims)
            if not has_ev_sources and not has_claim_sources:
                ev_no_src.append({"id": ev.id, "title": ev.title})

            if not ev.date_start or not ev.date_end or not ev.temporal_precision:
                ev_no_temp.append({"id": ev.id, "title": ev.title, "date_display": ev.date_display})

            if ev.date_start and ev.date_end and ev.date_start > ev.date_end:
                date_inconsistencies.append({
                    "id": ev.id,
                    "title": ev.title,
                    "error": f"date_start ({ev.date_start}) posterior a date_end ({ev.date_end})",
                })

            if (
                hasattr(ev, "latitude")
                and ev.latitude == 0.0
                and hasattr(ev, "longitude")
                and ev.longitude == 0.0
            ):
                geo_violations.append({
                    "id": ev.id,
                    "title": ev.title,
                    "error": "Coordenada (0.0, 0.0) em vez de NULL",
                })

        report["checks"]["1_events_without_sources"] = {
            "title": "Eventos sem Fontes Documentais",
            "status": "PASS" if not ev_no_src else "FAIL",
            "violations_count": len(ev_no_src),
            "details": ev_no_src,
        }

        report["checks"]["2_events_without_temporal_intervals"] = {
            "title": "Eventos sem Intervalos Temporais Explícitos",
            "status": "PASS" if not ev_no_temp else "FAIL",
            "violations_count": len(ev_no_temp),
            "details": ev_no_temp,
        }

        # -------------------------------------------------------------
        # CHECKS 3, 6, 13: Single pass over cl_query
        # -------------------------------------------------------------
        cl_no_src: List[Dict[str, Any]] = []
        false_triangulations: List[Dict[str, Any]] = []
        unanchored_disputes: List[Dict[str, Any]] = []

        for cl in cl_query:
            if not cl.source_links:
                cl_no_src.append({"id": cl.id, "statement": cl.statement[:50]})

            if cl.confidence_level == "confirmado":
                eval_res = GenealogyService.evaluate_claim_epistemology(cl, root_cache=root_cache)
                if eval_res["independent_root_count"] < 2 and eval_res["evidence_count"] > 1:
                    false_triangulations.append({
                        "claim_id": cl.id,
                        "statement": cl.statement[:40],
                        "evidence_count": eval_res["evidence_count"],
                        "independent_root_count": eval_res["independent_root_count"],
                    })

            if cl.is_disputed or cl.confidence_level == "conflitante":
                if not cl.epistemological_notes or len(cl.epistemological_notes.strip()) < 15:
                    unanchored_disputes.append({"claim_id": cl.id, "statement": cl.statement[:40]})

        report["checks"]["3_claims_without_sources"] = {
            "title": "Claims sem Fontes Associadas",
            "status": "PASS" if not cl_no_src else "FAIL",
            "violations_count": len(cl_no_src),
            "details": cl_no_src,
        }

        # -------------------------------------------------------------
        # CHECKS 4 & 5: Single pass over cs_query
        # -------------------------------------------------------------
        cs_no_excerpt: List[Dict[str, Any]] = []
        av_no_timestamp: List[Dict[str, Any]] = []

        for cs in cs_query:
            if not cs.excerpt or not cs.excerpt.strip():
                cs_no_excerpt.append({
                    "claim_source_id": cs.id,
                    "claim_id": cs.claim_id,
                    "source_id": cs.source_id,
                })

            src = cs.source
            if src and src.source_type in _AUDIOVISUAL_SOURCE_TYPES:
                sec = (cs.section or "").lower()
                pag = (cs.page or "").lower()
                if not any(kw in sec or kw in pag for kw in _TIMESTAMP_KEYWORDS):
                    av_no_timestamp.append({
                        "claim_id": cs.claim_id,
                        "source_id": cs.source_id,
                        "source_title": src.title,
                    })

        report["checks"]["4_claims_without_excerpts"] = {
            "title": "Claims sem Citação Literal (Excerpt)",
            "status": "PASS" if not cs_no_excerpt else "FAIL",
            "violations_count": len(cs_no_excerpt),
            "details": cs_no_excerpt,
        }

        report["checks"]["5_audiovisual_claims_without_timestamps"] = {
            "title": "Claims Audiovisuais sem Timestamp",
            "status": "PASS" if not av_no_timestamp else "FAIL",
            "violations_count": len(av_no_timestamp),
            "details": av_no_timestamp,
        }

        report["checks"]["6_false_triangulation_violations"] = {
            "title": "Falsa Triangulação de Fontes",
            "status": "PASS" if not false_triangulations else "FAIL",
            "violations_count": len(false_triangulations),
            "details": false_triangulations,
        }

        # -------------------------------------------------------------
        # CHECK 7: Contaminação por Dados Demo em Produção
        # -------------------------------------------------------------
        prod_events = ev_query if not include_demo else [ev for ev in ev_query if not ev.is_demo]
        demo_leaks: List[Dict[str, Any]] = []
        for ev in prod_events:
            for c in ev.claims:
                if c.is_demo:
                    demo_leaks.append({
                        "type": "claim_demo_in_prod_event",
                        "event_id": ev.id,
                        "claim_id": c.id,
                    })
            for sl in ev.source_links:
                if sl.source and sl.source.is_demo:
                    demo_leaks.append({
                        "type": "source_demo_in_prod_event",
                        "event_id": ev.id,
                        "source_id": sl.source.id,
                    })

        report["checks"]["7_demo_contamination_in_prod"] = {
            "title": "Isolamento Estrito de Dados Demo vs Produção",
            "status": "PASS" if not demo_leaks else "FAIL",
            "violations_count": len(demo_leaks),
            "details": demo_leaks,
        }

        report["checks"]["8_impossible_chronology_dates"] = {
            "title": "Consistência Cronológica de Intervalos",
            "status": "PASS" if not date_inconsistencies else "FAIL",
            "violations_count": len(date_inconsistencies),
            "details": date_inconsistencies,
        }

        report["checks"]["9_geospatial_zero_as_null_violations"] = {
            "title": "Rigor Geoespacial (Zero != NULL)",
            "status": "PASS" if not geo_violations else "FAIL",
            "violations_count": len(geo_violations),
            "details": geo_violations,
        }

        # -------------------------------------------------------------
        # CHECK 10: Derivações com Referências Órfãs (from preloaded index)
        # -------------------------------------------------------------
        all_source_ids = genealogy_index.sources_by_id
        orphan_derivations = [
            {"id": d_id, "parent": parent_id, "derived": derived_id}
            for d_id, parent_id, derived_id, _ in genealogy_index.all_derivations
            if parent_id not in all_source_ids or derived_id not in all_source_ids
        ]

        report["checks"]["10_derived_sources_missing_parent"] = {
            "title": "Integridade Referencial da Genealogia",
            "status": "PASS" if not orphan_derivations else "FAIL",
            "violations_count": len(orphan_derivations),
            "details": orphan_derivations,
        }

        # -------------------------------------------------------------
        # CHECK 11: Ciclos na Genealogia Documental (O(V + E) em memória)
        # -------------------------------------------------------------
        cycles_detected = GenealogyService.find_cyclic_sources(genealogy_index)

        report["checks"]["11_circular_derivation_dependencies"] = {
            "title": "Aciclicidade da Árvore Genealógica (DAG)",
            "status": "PASS" if not cycles_detected else "FAIL",
            "violations_count": len(cycles_detected),
            "details": cycles_detected,
        }

        # -------------------------------------------------------------
        # CHECK 12: Transcrições com Hash SHA-256 Válido
        # -------------------------------------------------------------
        transcripts_dir = PROJECT_ROOT / "data" / "raw" / "audiovisual" / "transcripts"
        trx_violations: List[Dict[str, Any]] = []
        if transcripts_dir.exists():
            for tfile in transcripts_dir.glob("*.json"):
                try:
                    with open(tfile, "r", encoding="utf-8") as f:
                        tdata = json.load(f)
                    stored_hash = tdata.get("sha256_hash")
                    ftext = tdata.get("full_text", "")
                    computed_hash = hashlib.sha256(ftext.encode("utf-8")).hexdigest()
                    if not stored_hash or stored_hash != computed_hash:
                        trx_violations.append({
                            "file": tfile.name,
                            "stored_hash": stored_hash,
                            "computed_hash": computed_hash,
                        })
                except Exception as e:
                    trx_violations.append({"file": tfile.name, "error": str(e)})

        report["checks"]["12_unhashed_transcripts"] = {
            "title": "Integridade Criptográfica das Transcrições (SHA-256)",
            "status": "PASS" if not trx_violations else "FAIL",
            "violations_count": len(trx_violations),
            "details": trx_violations,
        }

        report["checks"]["13_unanchored_controversial_claims"] = {
            "title": "Fundamentação Epistemológica de Controvérsias",
            "status": "PASS" if not unanchored_disputes else "WARNING",
            "violations_count": len(unanchored_disputes),
            "details": unanchored_disputes,
        }

        # -------------------------------------------------------------
        # Estatísticas Globais
        # -------------------------------------------------------------
        passed = sum(1 for c in report["checks"].values() if c["status"] == "PASS")
        failed = sum(1 for c in report["checks"].values() if c["status"] == "FAIL")
        warnings = sum(1 for c in report["checks"].values() if c["status"] == "WARNING")

        report["passed_checks"] = passed
        report["failed_checks"] = failed
        report["warning_checks"] = warnings
        report["integrity_score"] = round((passed / report["total_checks"]) * 100.0, 1)

        return report

    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Auditoria de Integridade da Pesquisa Histórica")
    parser.add_argument(
        "--output",
        type=str,
        default="reports/research_integrity_report.json",
        help="Caminho para o relatório de integridade",
    )
    parser.add_argument(
        "--include-demo",
        action="store_true",
        help="Inclui dados de demonstração na auditoria",
    )
    args = parser.parse_args()

    out_file = PROJECT_ROOT / args.output
    out_file.parent.mkdir(parents=True, exist_ok=True)

    print("=== Auditoria de Integridade da Pesquisa Histórica Digital ===")
    print(f"Data: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("-" * 65)

    report = run_integrity_audit(include_demo=args.include_demo)

    for key, c in sorted(report["checks"].items()):
        symbol = "[PASS]" if c["status"] == "PASS" else ("[WARN]" if c["status"] == "WARNING" else "[FAIL]")
        print(f"{symbol:6} {c['title']:<50} -> Violações: {c['violations_count']}")
        if 0 < c["violations_count"] <= 3:
            for d in c["details"]:
                print(f"       -> {d}")

    print("-" * 65)
    print(f"Resultado Geral: {report['passed_checks']}/{report['total_checks']} checagens aprovadas.")
    print(f"Integridade Metodológica: {report['integrity_score']}%")
    print(f"[+] Relatório salvo em: {out_file}")
    print("=" * 65)

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
