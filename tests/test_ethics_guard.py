# -*- coding: utf-8 -*-
"""
Testes Unitários da Guarda Ética e Filtros Cartográficos (FASE 5 — BLOQUEANTE)
=============================================================================
"""

from app.services.ethics_guard import EthicsGuard, MUNICIPALITY_CENTROID
from app.services.atlas_service import AtlasService, WorldState


def test_ethics_guard_temporal_embargo_check():
    """Valida a detecção da janela de embargo de 24 meses."""
    # Ano corrente: 2026
    assert EthicsGuard.is_under_temporal_embargo(2026) is True
    assert EthicsGuard.is_under_temporal_embargo(2025) is True
    assert EthicsGuard.is_under_temporal_embargo(2024) is False
    assert EthicsGuard.is_under_temporal_embargo(1979) is False
    assert EthicsGuard.is_under_temporal_embargo(1958) is False


def test_ethics_guard_apply_embargo_to_recent_world_state():
    """Verifica que acontecimentos recentes têm coordenadas agregadas por segurança."""
    atlas = AtlasService()
    # 2026: Ano sob embargo
    ws_2026 = atlas.get_world_state(year=2026, is_demo=False)
    embargoed_ws = EthicsGuard.apply_embargo(ws_2026, current_year=2026)

    assert embargoed_ws.metadata.get("ethics_embargo_active") is True
    assert "Embargo Ético de 24 Meses" in embargoed_ws.metadata.get("ethics_embargo_reason", "")

    # Eventos em 2026 devem ter pontos agregados ao centroide municipal
    for ev in embargoed_ws.events:
        if ev["geometry"]["type"] == "Point":
            assert ev["geometry"]["coordinates"] == MUNICIPALITY_CENTROID
            assert ev["properties"]["location_precision"] == "agregado_municipal_embargo_etico"
            assert ev["properties"]["is_embargoed"] is True


def test_ethics_guard_no_embargo_on_historical_world_state():
    """Garante que a história consolidada (> 24 meses) não sofre agregação de embargo."""
    atlas = AtlasService()
    # 1979: Fato histórico consolidado
    ws_1979 = atlas.get_world_state(year=1979, is_demo=False)
    original_coords = [e["geometry"]["coordinates"] for e in ws_1979.events if e["geometry"]["type"] == "Point"]

    embargoed_ws = EthicsGuard.apply_embargo(ws_1979, current_year=2026)
    assert embargoed_ws.metadata.get("ethics_embargo_active") is not True

    result_coords = [e["geometry"]["coordinates"] for e in embargoed_ws.events if e["geometry"]["type"] == "Point"]
    assert original_coords == result_coords


def test_ethics_guard_anti_operational_intelligence_filter():
    """Testa a rejeição e higienização de termos de inteligência tático-operacional."""
    text_with_violation = (
        "Operação localizou nova boca de fumo e identificou rota de fuga ativa "
        "nos fundos do beco, próximo à residência particular de familiares."
    )

    has_violation, terms = EthicsGuard.scan_operational_intelligence(text_with_violation)
    assert has_violation is True
    assert "boca de fumo" in terms
    assert "rota de fuga ativa" in terms
    assert "residência particular" in terms

    # Teste de higienização
    sanitized = EthicsGuard.sanitize_metadata_text(text_with_violation)
    assert "boca de fumo" not in sanitized
    assert "rota de fuga ativa" not in sanitized
    assert "[REDUZIDO POR DIRETRIZ ÉTICA]" in sanitized


def test_ethics_guard_audit_cartographic_feature():
    """Testa a higienização de uma feição cartográfica completa."""
    fake_feature = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [-43.2, -22.9]},
        "properties": {
            "title": "Apreensão em ponto de venda de drogas",
            "notes": "Suspeitos utilizavam rota de fuga ativa pelos telhados."
        }
    }

    audited = EthicsGuard.audit_cartographic_feature(fake_feature)
    assert "[REDUZIDO POR DIRETRIZ ÉTICA]" in audited["properties"]["title"]
    assert "[REDUZIDO POR DIRETRIZ ÉTICA]" in audited["properties"]["notes"]
    assert audited["properties"].get("ethics_sanitized") is True
