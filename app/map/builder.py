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


CANONICAL_FACTION_COLORS: Dict[str, str] = {
    "CV": "#EF4444",      # Vermelho vibrante (Comando Vermelho)
    "TCP": "#3B82F6",     # Azul vibrante (Terceiro Comando Puro)
    "ADA": "#10B981",     # Verde esmeralda (Amigos dos Amigos)
    "MIL": "#4B5563",     # Cinza escuro / Grafite (Milícia Geral)
    "LJ": "#374151",      # Grafite escuro (Liga da Justiça / CL220)
    "MNI": "#4B5563",     # Cinza escuro (Milícia de Nova Iguaçu)
    "NEU": "#9CA3AF",     # Cinza neutro (Área Neutra / Disputada)
}


def get_canonical_faction_color(props: Dict[str, Any]) -> str:
    """Retorna cor vibrante e de alto contraste conforme a facção controladora."""
    sigla = (props.get("faccao_sigla") or props.get("organization_acronym") or "").strip().upper()
    if sigla in CANONICAL_FACTION_COLORS:
        return CANONICAL_FACTION_COLORS[sigla]

    nome = (props.get("faccao_nome") or props.get("organization_name") or "").strip().upper()
    if "COMANDO VERMELHO" in nome or "FALANGE" in nome:
        return "#EF4444"
    if "TERCEIRO" in nome or "TCP" in nome:
        return "#3B82F6"
    if "AMIGOS" in nome or "ADA" in nome:
        return "#10B981"
    if "MIL" in nome or "LIGA" in nome or "JUSTICA" in nome:
        return "#374151"

    return props.get("cor_hex") or props.get("color_hex") or "#8C97A3"


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
        subdomains=tile_config.get("subdomains", "abc"),
        control_scale=True,
        prefer_canvas=True
    )

    # Plugin de Tela Cheia
    plugins.Fullscreen(
        position="topright",
        title="Expandir Mapa para Tela Cheia",
        title_cancel="Sair da Tela Cheia",
        force_separate_button=True
    ).add_to(fmap)

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
            sample_props = geo_data.get("features", [{}])[0].get("properties", {}) if geo_data.get("features") else {}
            tooltip_fields = ["nome", "faccao_nome"]
            tooltip_aliases = ["Comunidade:", "Domínio Territorial:"]
            if "faccao_sigla" in sample_props:
                tooltip_fields.append("faccao_sigla")
                tooltip_aliases.append("Sigla:")

            folium.GeoJson(
                geo_data,
                name="Controle Territorial (1.671 Áreas)",
                style_function=lambda ft: {
                    "fillColor": get_canonical_faction_color(ft.get("properties", {})),
                    "color": get_canonical_faction_color(ft.get("properties", {})),
                    "weight": STYLE_FACTION_POLYGON_DARK.get("weight", 1.2),
                    "fillOpacity": 0.40,
                    "opacity": STYLE_FACTION_POLYGON_DARK.get("opacity", 0.85)
                },
                highlight_function=lambda ft: {
                    "weight": 2.5,
                    "fillOpacity": 0.70,
                    "color": "#FFFFFF"
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=tooltip_fields,
                    aliases=tooltip_aliases
                )
            ).add_to(fmap)

    # Controle de Camadas Interativo
    folium.LayerControl(collapsed=True).add_to(fmap)

    sem_geometria = []
    plotados = 0

    # 4. Marcadores de Acontecimentos Históricos com Selo de Evidência
    for ev in events:
        tem_ponto = False
        
        # Suporta tanto region_links quanto regions diretamente
        target_regions = []
        region_links = getattr(ev, "region_links", [])
        if region_links:
            for link in region_links:
                reg = getattr(link, "region", None)
                if reg:
                    target_regions.append(reg)
        elif hasattr(ev, "regions") and ev.regions:
            target_regions = list(ev.regions)

        for reg in target_regions:
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
                    date_display_safe = (getattr(ev, "date_display", "") or str(getattr(ev, "year", "") or "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    fontes_count = len(ev.sources) if hasattr(ev, "sources") else len(getattr(ev, "source_links", []))
                    
                    desc = getattr(ev, "description", "") or ""
                    desc_snippet = ""
                    if desc:
                        clean_desc = desc[:130].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        if len(desc) > 130:
                            clean_desc += "..."
                        desc_snippet = f'<div style="font-size: 10px; color: #555; border-top: 1px solid #EEE; padding-top: 4px; margin-top: 4px;">{clean_desc}</div>'

                    popup_html = f"""
                    <div style="font-family: 'Source Sans 3', sans-serif; width: 250px; color: #111; line-height: 1.35;">
                        <div style="display:flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                            <span style="display:inline-block; padding: 2px 6px; font-size: 10px; font-weight: 700; border-radius: 3px; background-color: {ev_meta['color']}; color: #fff;">
                                {ev_meta['label']}
                            </span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #7A2E2E; font-weight: 700;">{date_display_safe}</span>
                        </div>
                        <div style="font-family: 'Libre Baskerville', Georgia, serif; font-weight: 700; font-size: 13px; margin: 3px 0 5px 0; color: #111;">{ev_title_safe}</div>
                        <div style="font-size: 11px; color: #333;"><b>📍 Território:</b> {reg_name_safe}</div>
                        <div style="font-size: 11px; color: #333;"><b>📜 Custódia:</b> {fontes_count} fonte(s) catalogada(s)</div>
                        {desc_snippet}
                    </div>
                    """

                    folium.Marker(
                        [lat_f, lng_f],
                        popup=folium.Popup(popup_html, max_width=270),
                        tooltip=f"[{ev_meta['label'][:7]}] [{date_display_safe}] {ev_title_safe}",
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
