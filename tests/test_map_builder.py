# -*- coding: utf-8 -*-
"""
Suíte de Testes Automatizados para Construtores de Mapa e Camadas Cartográficas
=============================================================================
Testa:
1. build_historical_folium_map (Folium Dark Matter, 1.671 polígonos, cores vibrantes, popups ricos, badges).
2. generate_maplibre_html / render_maplibre_atlas (CSS anti-colapso, separação Point/Polygon, controles, popups, 3 camadas vetoriais).
3. Resiliência a dados nulos, NaN, listas vazias e conformidade visual com convenções cartográficas.
"""

import json
import pytest
from app.map.builder import (
    build_historical_folium_map,
    build_pydeck_map,
    get_canonical_faction_color,
    CANONICAL_FACTION_COLORS,
    _infer_evidence_level,
)
from app.map.styles import FACTION_COLORS, MAP_TILES, EVIDENCE_LEVELS
from app.map.layers import (
    load_faction_polygons,
    load_aisp_polygons,
    load_bairros_polygons,
)
from app.services.atlas_service import WorldState
from app.ui.components.atlas_map.maplibre_component import (
    generate_maplibre_html,
)


class MockRegion:
    def __init__(self, name="Morro do Alemão", lat=-22.86, lng=-43.27, has_coords=True):
        self.original_name = name
        self.latitude = lat
        self.longitude = lng
        self.has_coordinates = has_coords


class MockRegionLink:
    def __init__(self, region):
        self.region = region


class MockSource:
    def __init__(self, source_type="documento_judicial", author="MPRJ", title="Denúncia GAECO"):
        self.source_type = source_type
        self.author = author
        self.title = title


class MockSourceLink:
    def __init__(self, source):
        self.source = source


class MockEvent:
    def __init__(
        self,
        id=101,
        title="Ocupação Territorial de Teste",
        date_display="1982",
        year=1982,
        confidence="confirmado",
        description="Descrição detalhada para teste cartográfico de dossiê.",
        region=None,
        source=None
    ):
        self.id = id
        self.title = title
        self.date_display = date_display
        self.year = year
        self.confidence_level = confidence
        self.description = description
        reg = region or MockRegion()
        self.region_links = [MockRegionLink(reg)]
        self.regions = [reg]
        src = source or MockSource()
        self.source_links = [MockSourceLink(src)]
        self.sources = [src]


# =============================================================================
# 1. TESTES DO CONSTRUTOR FOLIUM
# =============================================================================

def test_canonical_faction_colors():
    """Valida as cores contrastantes e vibrantes das facções principais."""
    assert CANONICAL_FACTION_COLORS["CV"] == "#EF4444"
    assert CANONICAL_FACTION_COLORS["TCP"] == "#3B82F6"
    assert CANONICAL_FACTION_COLORS["ADA"] == "#10B981"
    assert CANONICAL_FACTION_COLORS["MIL"] == "#4B5563"
    assert CANONICAL_FACTION_COLORS["LJ"] == "#374151"

    # Função de inferência
    assert get_canonical_faction_color({"faccao_sigla": "CV"}) == "#EF4444"
    assert get_canonical_faction_color({"faccao_sigla": "TCP"}) == "#3B82F6"
    assert get_canonical_faction_color({"faccao_sigla": "ADA"}) == "#10B981"
    assert get_canonical_faction_color({"faccao_sigla": "MIL"}) == "#4B5563"
    assert get_canonical_faction_color({"faccao_sigla": "LJ"}) == "#374151"
    assert get_canonical_faction_color({"faccao_nome": "Comando Vermelho"}) == "#EF4444"
    assert get_canonical_faction_color({"faccao_nome": "Terceiro Comando Puro"}) == "#3B82F6"
    assert get_canonical_faction_color({"faccao_nome": "Amigos dos Amigos"}) == "#10B981"
    assert get_canonical_faction_color({"faccao_nome": "Milícia Liga da Justiça"}) == "#374151"


def test_build_historical_folium_map_full_layers():
    """Garante que Folium Dark Matter renderiza com todas as 3 camadas oficiais e marcadores ricos."""
    ev = MockEvent()
    fmap, sem_geo, plotados = build_historical_folium_map(
        [ev],
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

    # Validação do basemap Dark Matter
    assert "dark_all" in html or "cartocdn" in html

    # Validação da presença do controle de tela cheia e layer control
    assert "fullscreen" in html.lower() or "leaflet-control" in html.lower()

    # Validação de popup rico do evento
    assert "Ocupação Territorial de Teste" in html
    assert "Morro do Alemão" in html
    assert "Nível A" in html or "Oficial" in html


def test_build_historical_folium_map_edge_cases():
    """Testa eventos sem coordenadas, com NaN e listas vazias."""
    ev_nan = MockEvent(region=MockRegion(lat=float("nan"), lng=float("nan")))
    ev_null = MockEvent(region=MockRegion(lat=None, lng=None, has_coords=False))
    ev_ok = MockEvent()

    fmap, sem_geo, plotados = build_historical_folium_map([ev_nan, ev_null, ev_ok])
    assert plotados == 1
    assert len(sem_geo) == 2

    html = fmap.get_root().render()
    assert isinstance(html, str)
    assert len(html) > 1000

    # Lista vazia
    fmap_empty, sem_geo_empty, plotados_empty = build_historical_folium_map([])
    assert plotados_empty == 0
    assert len(sem_geo_empty) == 0


# =============================================================================
# 2. TESTES DO COMPONENTE MAPLIBRE GL JS
# =============================================================================

def test_maplibre_html_anti_collapse_css():
    """Garante que o CSS estrito anti-colapso está presente para evitar mapa em branco."""
    ws = WorldState(
        year=1979,
        month=None,
        metadata={"total_features": 2, "territories_count": 1, "facilities_count": 1}
    )

    html = generate_maplibre_html(ws, height=650)
    assert isinstance(html, str)

    # CSS Obrigatório: html, body e #map devem ter dimensões estritas
    assert "html, body {" in html
    assert "width: 100%;" in html
    assert "height: 100%;" in html
    assert "overflow: hidden;" in html

    assert "#map {" in html
    assert "min-height: 600px;" in html
    assert "position: absolute;" in html
    assert "top: 0;" in html
    assert "bottom: 0;" in html
    assert "left: 0;" in html
    assert "right: 0;" in html


def test_maplibre_point_polygon_separation():
    """
    Garante que territórios do tipo Point NUNCA são passados para a camada fill
    e são renderizados com segurança na camada circle 'territories-point'.
    """
    point_territory = {
        "type": "Feature",
        "id": "territory_pt_1",
        "geometry": {
            "type": "Point",
            "coordinates": [-43.20, -22.90]
        },
        "properties": {
            "feature_id": "territory_pt_1",
            "layer": "territories",
            "region_name": "Ponto de Controle Histórico",
            "relation_type": "controle",
            "color_hex": "#EF4444",
            "evidence_strength": "alta"
        }
    }

    poly_territory = {
        "type": "Feature",
        "id": "territory_poly_1",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[-43.25, -22.95], [-43.24, -22.95], [-43.24, -22.94], [-43.25, -22.95]]]
        },
        "properties": {
            "feature_id": "territory_poly_1",
            "layer": "territories",
            "region_name": "Área de Controle Ampla",
            "relation_type": "controle",
            "color_hex": "#EF4444"
        }
    }

    ws = WorldState(
        year=1979,
        month=None,
        territories=[point_territory, poly_territory],
        metadata={"total_features": 2, "territories_count": 2}
    )

    html = generate_maplibre_html(ws, show_factions=False)

    # 1. Verifica camada fill filtrada estritamente para Polygon / MultiPolygon
    assert "id: 'territories-fill'" in html
    assert "['in', ['geometry-type'], ['literal', ['Polygon', 'MultiPolygon']]]" in html

    # 2. Verifica camada circle para Point / MultiPoint
    assert "id: 'territories-point'" in html
    assert "['in', ['geometry-type'], ['literal', ['Point', 'MultiPoint']]]" in html


def test_maplibre_vector_layers_injection():
    """Garante que as 1.671 facções, 39 AISPs e 166 Bairros são injetadas quando ativadas."""
    ws = WorldState(
        year=2020,
        month=None,
        metadata={"total_features": 1, "territories_count": 1}
    )

    # Ativação das 3 camadas vetoriais
    html = generate_maplibre_html(
        ws,
        show_factions=True,
        show_aisps=True,
        show_bairros=True,
        theme="dark"
    )

    # Fontes GeoJSON presentes
    assert "bairros-data" in html
    assert "aisps-data" in html
    assert "factions-data" in html

    # Camadas MapLibre adicionadas
    assert "id: 'bairros-fill'" in html
    assert "id: 'bairros-stroke'" in html
    assert "id: 'aisps-stroke'" in html
    assert "id: 'factions-fill'" in html
    assert "id: 'factions-stroke'" in html

    # Validação de cores contrastantes no MapLibre para as facções
    assert "#EF4444" in html  # CV
    assert "#3B82F6" in html  # TCP
    assert "#10B981" in html  # ADA
    assert "#374151" in html  # Milícia

    # Validação de controles
    assert "NavigationControl" in html
    assert "FullscreenControl" in html
    assert "ScaleControl" in html


def test_maplibre_popups_and_interactivity():
    """Valida registro de popups para feições de facções, AISP, bairros e acontecimentos."""
    ws = WorldState(
        year=1980,
        month=None,
        metadata={"total_features": 1, "territories_count": 1}
    )

    html = generate_maplibre_html(ws, show_factions=True, show_aisps=True, show_bairros=True)

    # Popups de facções
    assert "CONTROLE TERRITORIAL" in html
    # Popups de AISP
    assert "SEGURANÇA PÚBLICA" in html
    # Popups de Bairros
    assert "BAIRRO OFICIAL" in html
    # Popups de Território Histórico
    assert "TERRITÓRIO HISTÓRICO" in html
    # Popups de Acontecimento
    assert "ACONTECIMENTO HISTÓRICO" in html


# =============================================================================
# 3. TESTES DE CARREGAMENTO DAS CAMADAS
# =============================================================================

def test_map_layers_loading():
    """Valida integridade do carregamento das malhas vetoriais."""
    factions = load_faction_polygons()
    assert factions is not None
    assert len(factions["features"]) == 1671

    aisps = load_aisp_polygons()
    assert aisps is not None
    assert len(aisps["features"]) == 39

    bairros = load_bairros_polygons()
    assert bairros is not None
    assert len(bairros["features"]) == 166
