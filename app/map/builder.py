"""
Módulo de Construção Cartográfica Histórica (Folium & PyDeck).
Implementa Tema Dark (CartoDB Dark Matter), sobreposição vetorial de AISPs,
Bairros e Facções Armadas, e pins com Selo de Nível de Evidência Historiográfica.
"""

import math
from typing import Tuple, List, Optional, Any, Dict
import folium
from folium import plugins

from app.map.styles import (
    MAP_TILES,
    FACTION_COLORS,
    EVIDENCE_LEVELS,
    STYLE_FACTION_POLYGON_DARK,
    STYLE_AISP_POLYGON_DARK,
    STYLE_BAIRROS_POLYGON_DARK,
)
from app.map.layers import (
    load_faction_polygons,
    load_aisp_polygons,
    load_bairros_polygons
)

DEFAULT_MAP_CENTER = [-22.9068, -43.1729]
DEFAULT_MAP_ZOOM = 11


def _infer_evidence_level(ev) -> str:
    """Classifica o evento em Nível A (Oficial/Judicial), B (Acadêmico) ou C (Imprensa)."""
    # 1. Checar se há controvérsia
    conf = getattr(ev, "confidence_level", "").lower()
    if conf in ("conflitante", "disputed"):
        return "conflitante"

    # 2. Analisar fontes vinculadas
    sources = getattr(ev, "sources", [])
    if not sources and hasattr(ev, "source_links"):
        sources = [sl.source for sl in ev.source_links if hasattr(sl, "source")]

    has_official = False
    has_academic = False

    for s in sources:
        tipo = getattr(s, "source_type", "").lower()
        autor = getattr(s, "author", "").lower()
        titulo = getattr(s, "title", "").lower()
        if any(k in tipo for k in ["judicial", "oficial", "sentenca", "inquerito", "boletim", "lei"]):
            has_official = True
        elif any(k in autor for k in ["stf", "tjrj", "mp-rj", "mprj", "pmerj", "polícia", "alerj", "isp"]):
            has_official = True
        elif any(k in tipo for k in ["academico", "artigo", "tese", "dissertacao", "livro"]):
            has_academic = True

    if has_official or conf in ("alta", "confirmado"):
        return "A"
    elif has_academic or conf in ("media", "provavel"):
        return "B"
    return "C"


def build_historical_folium_map(
    events,
    show_polygons: bool = False,
    show_aisp: bool = False,
    show_bairros: bool = False,
    theme: str = "dark",
    geo_data: Optional[dict] = None,
    aisp_data: Optional[dict] = None,
    bairros_data: Optional[dict] = None
) -> Tuple[folium.Map, List[Any], int]:
    """
    Constrói o mapa Folium com tema Dark e camadas auditáveis.
    Preserva assinatura retrocompatível com a suíte de testes.
    """
    # Configuração de Basemap (Dark Matter por padrão)
    tile_config = MAP_TILES.get(theme, MAP_TILES["dark"])
    
    fmap = folium.Map(
        location=DEFAULT_MAP_CENTER,
        zoom_start=DEFAULT_MAP_ZOOM,
        tiles=tile_config["tiles"],
        attr=tile_config.get("attr"),
        subdomains=tile_config.get("subdomains", "abc")
    )

    # 1. Camada de Bairros Oficiais (Prefeitura do Rio / IPP)
    if show_bairros:
        if bairros_data is None:
            bairros_data = load_bairros_polygons()
        if bairros_data:
            folium.GeoJson(
                bairros_data,
                name="Malha de Bairros (PCRJ/IPP)",
                style_function=lambda ft: STYLE_BAIRROS_POLYGON_DARK,
                highlight_function=lambda ft: {
                    "color": "#FFFFFF",
                    "weight": 2.0,
                    "fillOpacity": 0.2
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=["nome", "regiao_adm", "area_planejamento"],
                    aliases=["Bairro:", "R.A.:", "Área Planejamento (AP):"]
                )
            ).add_to(fmap)

    # 2. Camada de AISP (Batalhões da PMERJ - ISP-RJ)
    if show_aisp:
        if aisp_data is None:
            aisp_data = load_aisp_polygons()
        if aisp_data:
            folium.GeoJson(
                aisp_data,
                name="Áreas de Batalhões (AISP / PMERJ)",
                style_function=lambda ft: {
                    "color": ft.get("properties", {}).get("cor_hex", "#00E5FF"),
                    "fillColor": ft.get("properties", {}).get("cor_hex", "#00E5FF"),
                    "weight": 1.5,
                    "dashArray": "5, 5",
                    "fillOpacity": 0.12,
                    "opacity": 0.8
                },
                highlight_function=lambda ft: {
                    "weight": 3.0,
                    "fillOpacity": 0.3,
                    "dashArray": ""
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=["batalhao", "sede", "aisp", "risp"],
                    aliases=["Batalhão:", "Sede/Bairro:", "AISP:", "RISP:"]
                )
            ).add_to(fmap)

    # 3. Camada de Perímetros Territoriais de Facções e Grupos Armados (1.671 áreas)
    if show_polygons:
        if geo_data is None:
            geo_data = load_faction_polygons()
        if geo_data:
            folium.GeoJson(
                geo_data,
                name="Controle Territorial (1.671 Áreas)",
                style_function=lambda ft: {
                    "fillColor": ft.get("properties", {}).get("cor_hex", "#8C97A3"),
                    "color": ft.get("properties", {}).get("cor_hex", "#8C97A3"),
                    "weight": STYLE_FACTION_POLYGON_DARK["weight"],
                    "fillOpacity": STYLE_FACTION_POLYGON_DARK["fillOpacity"],
                    "opacity": STYLE_FACTION_POLYGON_DARK["opacity"]
                },
                highlight_function=lambda ft: {
                    "weight": 2.5,
                    "fillOpacity": 0.6
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=["nome", "faccao_nome"],
                    aliases=["Comunidade:", "Domínio Territorial:"]
                )
            ).add_to(fmap)

    sem_geometria = []
    plotados = 0

    # 4. Marcadores de Acontecimentos Históricos com Selo de Evidência
    for ev in events:
        tem_ponto = False
        region_links = getattr(ev, "region_links", [])
        for link in region_links:
            reg = getattr(link, "region", None)
            if reg and getattr(reg, "has_coordinates", False):
                lat = getattr(reg, "latitude", None)
                lng = getattr(reg, "longitude", None)
                if lat is not None and lng is not None:
                    try:
                        lat_f = float(lat)
                        lng_f = float(lng)
                        if math.isnan(lat_f) or math.isnan(lng_f):
                            continue
                    except (ValueError, TypeError):
                        continue

                    tem_ponto = True
                    ev_level_key = _infer_evidence_level(ev)
                    ev_meta = EVIDENCE_LEVELS.get(ev_level_key, EVIDENCE_LEVELS["C"])

                    ev_title_safe = (ev.title or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    reg_name_safe = (reg.original_name or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    fontes_count = len(ev.sources) if hasattr(ev, "sources") else len(getattr(ev, "source_links", []))

                    popup_html = f"""
                    <div style="font-family: 'Source Sans 3', sans-serif; width: 240px; color: #111;">
                        <div style="display:inline-block; padding: 2px 6px; font-size: 10px; font-weight: bold; border-radius: 3px; background-color: {ev_meta['color']}; color: #fff; margin-bottom: 4px;">
                            {ev_meta['label']}
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #7A2E2E; font-weight: 700;">{ev.date_display}</div>
                        <div style="font-family: 'Libre Baskerville', serif; font-weight: 700; font-size: 13px; margin: 3px 0;">{ev_title_safe}</div>
                        <div style="font-size: 11px; color: #444;"><b>Território:</b> {reg_name_safe}</div>
                        <div style="font-size: 11px; color: #444;"><b>Custódia:</b> {fontes_count} fontes documentadas</div>
                    </div>
                    """

                    folium.Marker(
                        [lat_f, lng_f],
                        popup=folium.Popup(popup_html, max_width=260),
                        tooltip=f"[{ev_meta['label'][:7]}] [{ev.date_display}] {ev_title_safe}",
                        icon=folium.Icon(
                            color=ev_meta["marker_color"],
                            icon=ev_meta.get("icon", "record"),
                            prefix="glyphicon"
                        )
                    ).add_to(fmap)
                    plotados += 1

        if not tem_ponto:
            sem_geometria.append(ev)

    return fmap, sem_geometria, plotados


def build_pydeck_map(events, show_factions: bool = True, show_aisp: bool = True) -> Any:
    """
    Construtor de mapa interativo de alta performance via PyDeck (WebGL).
    Renderiza polígonos e pontos com aceleração de hardware.
    """
    try:
        import pydeck as pdk
    except ImportError:
        return None

    layers = []

    # 1. Camada de Facções em PyDeck
    if show_factions:
        factions_geo = load_faction_polygons()
        if factions_geo and "features" in factions_geo:
            layers.append(
                pdk.Layer(
                    "GeoJsonLayer",
                    data=factions_geo,
                    opacity=0.35,
                    stroked=True,
                    filled=True,
                    get_line_color=[255, 255, 255, 120],
                    line_width_min_pixels=1,
                    get_fill_color="properties.cor_hex ? [220, 50, 50, 140] : [140, 150, 160, 100]",
                    pickable=True,
                    auto_highlight=True,
                )
            )

    # 2. Camada de AISP em PyDeck
    if show_aisp:
        aisp_geo = load_aisp_polygons()
        if aisp_geo and "features" in aisp_geo:
            layers.append(
                pdk.Layer(
                    "GeoJsonLayer",
                    data=aisp_geo,
                    opacity=0.2,
                    stroked=True,
                    filled=True,
                    get_line_color=[0, 229, 255, 200],
                    line_width_min_pixels=2,
                    get_fill_color=[0, 229, 255, 30],
                    pickable=True,
                    auto_highlight=True,
                )
            )

    # 3. Pontos de Acontecimentos
    point_records = []
    for ev in events:
        for link in getattr(ev, "region_links", []):
            reg = getattr(link, "region", None)
            if reg and getattr(reg, "has_coordinates", False):
                lat = getattr(reg, "latitude", None)
                lng = getattr(reg, "longitude", None)
                if lat and lng:
                    point_records.append({
                        "title": ev.title,
                        "year": getattr(ev, "year", None),
                        "date": ev.date_display,
                        "territory": reg.original_name,
                        "coordinates": [float(lng), float(lat)],
                    })

    if point_records:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=point_records,
                get_position="coordinates",
                get_color=[255, 75, 75, 220],
                get_radius=300,
                radius_min_pixels=5,
                radius_max_pixels=15,
                pickable=True,
                auto_highlight=True,
            )
        )

    view_state = pdk.ViewState(
        latitude=DEFAULT_MAP_CENTER[0],
        longitude=DEFAULT_MAP_CENTER[1],
        zoom=10.5,
        pitch=30,
    )

    return pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style=pdk.map_styles.CARTO_DARK,
        tooltip={"text": "{title}\nTerritório: {territory}\nData: {date}"}
    )
