"""
Testes automatizados para as camadas geoespaciais oficiais:
- 39 AISP (Batalhões da PMERJ - ISP-RJ)
- 166 Bairros Oficiais (PCRJ / IPP / Data.Rio)
- Arquivos GeoJSON, Parquet, metadados sidecar SHA-256 e Construtores de Mapa Dark / PyDeck.
"""

import json
from pathlib import Path
import pytest
import pandas as pd

from app.map.layers import (
    load_aisp_polygons,
    load_bairros_polygons,
    load_faction_polygons,
    load_aisp_dataframe,
    load_bairros_dataframe,
)
from app.map.builder import (
    build_historical_folium_map,
    build_pydeck_map,
    _infer_evidence_level,
)
from app.map.styles import MAP_TILES, EVIDENCE_LEVELS


def test_official_aisp_files_and_schema():
    """Valida presença e integridade da malha de 39 AISPs / Batalhões."""
    geojson_path = Path("data/geospatial/aisps_batalhoes_pmerj.geojson")
    parquet_path = Path("data/geospatial/aisps_batalhoes.parquet")
    meta_path = Path("data/geospatial/aisps_batalhoes_meta.json")

    assert geojson_path.exists(), "GeoJSON de AISPs deve existir"
    assert parquet_path.exists(), "Parquet de AISPs deve existir"
    assert meta_path.exists(), "Metadados SHA-256 de AISPs devem existir"

    data = load_aisp_polygons()
    assert data is not None
    assert data.get("type") == "FeatureCollection"
    features = data.get("features", [])
    assert len(features) == 39, f"Esperado 39 AISPs oficiais, encontrado: {len(features)}"

    # Checar propriedades canônicas
    sample = features[0]["properties"]
    assert "aisp" in sample
    assert "batalhao" in sample
    assert "sede" in sample
    assert "risp" in sample
    assert "cor_hex" in sample
    assert "centroide_lat" in sample and sample["centroide_lat"] is not None
    assert "centroide_lon" in sample and sample["centroide_lon"] is not None

    # Checar Parquet
    df = load_aisp_dataframe()
    assert df is not None
    assert len(df) == 39
    assert "batalhao" in df.columns
    assert "geometry_json" in df.columns

    # Checar Meta SHA-256
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["total_aisps"] == 39
    assert len(meta["sha256_geojson"]) == 64


def test_official_bairros_files_and_schema():
    """Valida presença e integridade dos 166 Bairros Oficiais do Rio."""
    geojson_path = Path("data/geospatial/bairros_rio_166_poligonos.geojson")
    parquet_path = Path("data/geospatial/bairros_rio.parquet")
    meta_path = Path("data/geospatial/bairros_rio_meta.json")

    assert geojson_path.exists(), "GeoJSON de Bairros deve existir"
    assert parquet_path.exists(), "Parquet de Bairros deve existir"
    assert meta_path.exists(), "Metadados SHA-256 de Bairros devem existir"

    data = load_bairros_polygons()
    assert data is not None
    assert data.get("type") == "FeatureCollection"
    features = data.get("features", [])
    assert len(features) == 166, f"Esperado 166 bairros oficiais, encontrado: {len(features)}"

    sample = features[0]["properties"]
    assert "nome" in sample
    assert "regiao_adm" in sample
    assert "area_planejamento" in sample

    df = load_bairros_dataframe()
    assert df is not None
    assert len(df) == 166

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    assert meta["total_bairros"] == 166
    assert len(meta["sha256_geojson"]) == 64


def test_build_historical_folium_map_dark_and_layers():
    """Valida geração do mapa Folium com tema Dark e todas as camadas ativadas."""
    class MockRegion:
        has_coordinates = True
        latitude = -22.90
        longitude = -43.20
        original_name = "Centro / Praça da Harmonia"

    class MockRegionLink:
        region = MockRegion()

    class MockSource:
        source_type = "documento_judicial"
        author = "STF"
        title = "ADPF 635 das Favelas"

    class MockSourceLink:
        source = MockSource()

    class MockEvent:
        id = 999
        title = "Acontecimento Histórico de Teste"
        date_display = "1979"
        confidence_level = "confirmado"
        is_demo = False
        sources = [MockSource()]
        source_links = [MockSourceLink()]
        region_links = [MockRegionLink()]

    mock_events = [MockEvent()]

    # 1. Modo Dark completo com AISP, Bairros e Facções
    fmap, sem_geo, plotados = build_historical_folium_map(
        mock_events,
        show_polygons=True,
        show_aisp=True,
        show_bairros=True,
        theme="dark"
    )
    assert fmap is not None
    assert plotados == 1
    assert len(sem_geo) == 0

    html = fmap.get_root().render()
    assert isinstance(html, str)
    assert len(html) > 5000
    assert "dark" in html.lower() or "carto" in html.lower()

    # 2. Modo Positron
    fmap_light, _, _ = build_historical_folium_map(mock_events, theme="light")
    html_light = fmap_light.get_root().render()
    assert len(html_light) > 1000


def test_build_pydeck_map_rendering():
    """Valida geração de visualização WebGL via PyDeck."""
    class MockRegion:
        has_coordinates = True
        latitude = -22.90
        longitude = -43.20
        original_name = "Centro"

    class MockRegionLink:
        region = MockRegion()

    class MockEvent:
        title = "Evento PyDeck"
        year = 2000
        date_display = "2000"
        region_links = [MockRegionLink()]

    deck = build_pydeck_map([MockEvent()], show_factions=True, show_aisp=True)
    assert deck is not None
    assert len(deck.layers) >= 1
    assert deck.map_style is not None
