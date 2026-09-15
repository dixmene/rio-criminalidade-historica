# -*- coding: utf-8 -*-
"""
Testes Unitários do Serviço do Atlas e Snapshots Temporais (FASE 2)
==================================================================

Testa:
1. AtlasService.get_world_state (agregação temporal rigorosa, filtros e metadados).
2. AtlasService.get_epistemological_record (rastreabilidade do pixel à citação documental).
3. AtlasService.get_territorial_timeline (linha do tempo histórica do território).
4. Integridade dos snapshots pré-computados (1958-2026) e do manifest.json criptográfico.
"""

import json
import hashlib
from pathlib import Path
from app.services.atlas_service import AtlasService, WorldState, EpistemologicalRecord


def test_atlas_service_world_state_1979():
    """Testa a geração do estado do mundo para o ano crucial de 1979 (gênese da Falange Vermelha)."""
    service = AtlasService()
    ws = service.get_world_state(year=1979, is_demo=False)

    assert isinstance(ws, WorldState)
    assert ws.year == 1979
    assert ws.metadata["total_features"] > 0
    assert ws.metadata["anachronistic_features_count"] >= 1
    assert "Atenção historiográfica" in ws.metadata["epistemological_warning"]

    # Verificação de equipamentos do Estado ativos em 1979
    facility_names = [f["properties"]["name"] for f in ws.facilities]
    assert any("Cândido Mendes" in name or "Dois Rios" in name for name in facility_names), "Ilha Grande deve estar ativa em 1979."
    assert any("Frei Caneca" in name for name in facility_names), "Frei Caneca deve estar ativa em 1979."
    assert any("NuCOE" in name for name in facility_names), "NuCOE (fundado em 1978) deve estar ativo em 1979."

    # Verificação de territórios sob controle em 1979
    cv_territories = [t for t in ws.territories if t["properties"]["organization_acronym"] == "CV"]
    assert len(cv_territories) >= 1

    # Exportação para GeoJSON válido
    gj = ws.to_geojson()
    assert gj["type"] == "FeatureCollection"
    assert len(gj["features"]) == ws.metadata["total_features"]


def test_atlas_service_epistemological_record():
    """Verifica a ficha epistemológica: pixel ao trecho literal."""
    service = AtlasService()
    ws = service.get_world_state(year=1979, is_demo=False)
    assert len(ws.territories) > 0

    first_terr_id = ws.territories[0]["properties"]["feature_id"]
    rec = service.get_epistemological_record(first_terr_id)

    assert isinstance(rec, EpistemologicalRecord)
    assert rec.feature_id == first_terr_id
    assert rec.relation_type in ("controle", "presenca", "disputa", "presenca_estatal")
    assert rec.dataset_provenance is not None
    assert "dataset_name" in rec.dataset_provenance

    # Testa ficha epistemológica de instalação pública
    assert len(ws.facilities) > 0
    fac_id = ws.facilities[0]["properties"]["feature_id"]
    rec_fac = service.get_epistemological_record(fac_id)
    assert rec_fac is not None
    assert rec_fac.feature_type == "equipamento_institucional"


def test_atlas_service_territorial_timeline():
    """Testa a reconstrução cronológica das transições territoriais de uma região."""
    service = AtlasService()
    # Região 73: Ilha Grande
    timeline = service.get_territorial_timeline(region_id=73)
    assert len(timeline) >= 1
    assert timeline[0]["relation_type"] == "controle"
    assert timeline[0]["organization_acronym"] == "CV"


def test_precomputed_snapshots_and_manifest():
    """Testa a integridade de todos os 69 snapshots anuais pré-computados e do manifest."""
    root_dir = Path(__file__).resolve().parent.parent
    snapshots_dir = root_dir / "data" / "exports" / "snapshots"
    manifest_path = snapshots_dir / "manifest.json"

    assert manifest_path.exists(), "manifest.json deve existir na pasta de snapshots."

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["year_range"] == [1958, 2026]
    assert manifest["total_years"] == 69
    assert len(manifest["snapshots"]) == 69

    # Testa amostragem de snapshots (1958, 1979, 1988, 2026)
    for sample_year in (1958, 1979, 1988, 2026):
        year_str = str(sample_year)
        assert year_str in manifest["snapshots"]
        meta = manifest["snapshots"][year_str]

        snap_file = snapshots_dir / meta["filename"]
        assert snap_file.exists(), f"Arquivo {meta['filename']} deve existir."

        # Validação do hash SHA-256
        with open(snap_file, "rb") as f:
            content = f.read()
            computed_hash = hashlib.sha256(content).hexdigest()
            assert computed_hash == meta["sha256"], f"Hash SHA-256 incorreto para {snap_file.name}."

        # Validação do GeoJSON
        snap_data = json.loads(content.decode("utf-8"))
        assert snap_data["type"] == "FeatureCollection"
        assert len(snap_data["features"]) == meta["total_features"]
