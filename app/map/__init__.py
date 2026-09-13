"""
Pacote Cartográfico Integrado do Rio de Janeiro Histórico.
Suporte a Dark Basemaps, AISP/Batalhões PMERJ, Bairros e Perímetros Faccionais.
"""

from app.map.styles import (
    MAP_TILES,
    FACTION_COLORS,
    FACTION_NAMES,
    EVIDENCE_LEVELS,
    STYLE_FACTION_POLYGON_DARK,
    STYLE_AISP_POLYGON_DARK,
    STYLE_BAIRROS_POLYGON_DARK,
)
from app.map.layers import (
    load_faction_polygons,
    load_aisp_polygons,
    load_bairros_polygons,
    load_aisp_dataframe,
    load_bairros_dataframe,
)
from app.map.builder import (
    build_historical_folium_map,
    build_pydeck_map,
    DEFAULT_MAP_CENTER,
    DEFAULT_MAP_ZOOM,
)

__all__ = [
    "MAP_TILES",
    "FACTION_COLORS",
    "FACTION_NAMES",
    "EVIDENCE_LEVELS",
    "STYLE_FACTION_POLYGON_DARK",
    "STYLE_AISP_POLYGON_DARK",
    "STYLE_BAIRROS_POLYGON_DARK",
    "load_faction_polygons",
    "load_aisp_polygons",
    "load_bairros_polygons",
    "load_aisp_dataframe",
    "load_bairros_dataframe",
    "build_historical_folium_map",
    "build_pydeck_map",
    "DEFAULT_MAP_CENTER",
    "DEFAULT_MAP_ZOOM",
]
