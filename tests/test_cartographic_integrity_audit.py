# -*- coding: utf-8 -*-
"""
Teste Automatizado da Auditoria Cartográfica (14/14 Checagens) (FASE 7)
======================================================================
"""

from scripts.audit_cartographic_integrity import CartographicAuditor


def test_cartographic_integrity_audit_passes_all_14_checks():
    """Garante conformidade estrita de todos os 14 pilares cartográficos do Atlas."""
    auditor = CartographicAuditor()
    report = auditor.run_all_checks()

    assert report["total_checks"] == 14
    assert report["failed_checks"] == 0
    assert report["passed_checks"] == 14
    assert report["integrity_score"] == 100.0
    assert report["is_fully_compliant"] is True

    # Validação pontual dos pilares mais críticos
    checks = report["checks"]
    assert checks["check_01_no_invented_coordinates"]["status"] == "PASS"
    assert checks["check_02_strict_null_preservation"]["status"] == "PASS"
    assert checks["check_07_anachronism_explicit_flagging"]["status"] == "PASS"
    assert checks["check_08_strict_territorial_semantics"]["status"] == "PASS"
    assert checks["check_12_snapshots_and_manifest_integrity"]["status"] == "PASS"
    assert checks["check_13_ethics_embargo_24_months"]["status"] == "PASS"
    assert checks["check_14_anti_operational_intelligence_filter"]["status"] == "PASS"
