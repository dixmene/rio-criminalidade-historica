"""
Testes de integridade para a base geoespacial vetorial de polígonos de facções do RJ.
"""

import json
from pathlib import Path


GEOJSON_PATH = Path("data/geospatial/faccoes_rj_1671_poligonos.geojson")
META_PATH = Path("data/geospatial/faccoes_rj_1671_meta.json")


def test_geospatial_files_exist():
    assert GEOJSON_PATH.exists(), "Arquivo GeoJSON de polígonos deve existir em data/geospatial/"
    assert META_PATH.exists(), "Arquivo de metadados sidecar deve existir em data/geospatial/"


def test_geospatial_geojson_validity():
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data.get("type") == "FeatureCollection"
    features = data.get("features", [])
    assert len(features) == 1671, f"Esperado 1.671 polígonos mapeados, encontrado: {len(features)}"

    expected_factions = {"CV", "TCP", "ADA", "MIL", "LJ", "MNI", "NEU"}
    found_factions = set()

    for feat in features:
        assert feat.get("type") == "Feature"
        props = feat.get("properties", {})
        assert "nome" in props and len(props["nome"]) > 0
        assert "faccao_sigla" in props
        assert "cor_hex" in props and props["cor_hex"].startswith("#")
        found_factions.add(props["faccao_sigla"])

        # Validação geográfica: coordenadas devem estar dentro do Estado do RJ aproximado
        # Longitude: -45 a -40 | Latitude: -24 a -20
        c_lat = props.get("centroide_lat")
        c_lon = props.get("centroide_lon")
        if c_lat is not None and c_lon is not None:
            assert -24.5 <= c_lat <= -20.5, f"Latitude fora dos limites do RJ: {c_lat} em {props['nome']}"
            assert -45.5 <= c_lon <= -40.5, f"Longitude fora dos limites do RJ: {c_lon} em {props['nome']}"

    assert expected_factions.issubset(found_factions), f"Todas as facções devem estar presentes: {found_factions}"


def test_geospatial_metadata_consistency():
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["total_poligonos"] == 1671
    assert "sha256_geojson" in meta
    assert len(meta["sha256_geojson"]) == 64
    assert "distribuicao_faccoes" in meta
    assert "CV (Comando Vermelho)" in meta["distribuicao_faccoes"]
