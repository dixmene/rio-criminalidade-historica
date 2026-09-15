# -*- coding: utf-8 -*-
"""
Testes Automatizados do Script de Auditoria de Integridade Metodológica (13 Pilares).
"""

import pytest
from scripts.audit_research_integrity import run_integrity_audit


def test_research_integrity_audit_passes_all_13_checks():
    """Valida que o banco de dados de produção passa em todos os 13 critérios de integridade."""
    report = run_integrity_audit(include_demo=False)
    
    assert report["total_checks"] == 13
    assert report["failed_checks"] == 0
    assert report["integrity_score"] == 100.0
    
    checks = report["checks"]
    assert checks["1_events_without_sources"]["status"] == "PASS"
    assert checks["2_events_without_temporal_intervals"]["status"] == "PASS"
    assert checks["3_claims_without_sources"]["status"] == "PASS"
    assert checks["4_claims_without_excerpts"]["status"] == "PASS"
    assert checks["5_audiovisual_claims_without_timestamps"]["status"] == "PASS"
    assert checks["6_false_triangulation_violations"]["status"] == "PASS"
    assert checks["7_demo_contamination_in_prod"]["status"] == "PASS"
    assert checks["8_impossible_chronology_dates"]["status"] == "PASS"
    assert checks["9_geospatial_zero_as_null_violations"]["status"] == "PASS"
    assert checks["10_derived_sources_missing_parent"]["status"] == "PASS"
    assert checks["11_circular_derivation_dependencies"]["status"] == "PASS"
    assert checks["12_unhashed_transcripts"]["status"] == "PASS"
    assert checks["13_unanchored_controversial_claims"]["status"] in ("PASS", "WARNING")
