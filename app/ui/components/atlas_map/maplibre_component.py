# -*- coding: utf-8 -*-
"""
Componente Cartográfico MapLibre GL JS — Atlas Histórico Espaço-Temporal
========================================================================

Substitui o Folium estático por MapLibre GL 4.x com aceleração WebGL,
renderização vetorial fluida (60 FPS), suporte nativo às 1.671 áreas de facções,
malha de 39 AISPs (Batalhões PMERJ), 166 Bairros Oficiais (PCRJ) e camadas auditáveis.
Garante que containers em iframes Streamlit NUNCA colapsem com altura zero.
"""

import json
from typing import Dict, List, Optional, Any
import streamlit.components.v1 as components

from app.services.atlas_service import WorldState
from app.map.layers import (
    load_faction_polygons,
    load_aisp_polygons,
    load_bairros_polygons,
)

# Cache em memória para strings JSON serializadas (otimiza renderizações subsequentes)
_JSON_CACHE: Dict[str, str] = {}


def _get_cached_json(cache_key: str, data: Optional[Dict[str, Any]]) -> str:
    if not data:
        return "null"
    if cache_key not in _JSON_CACHE:
        _JSON_CACHE[cache_key] = json.dumps(data, ensure_ascii=False)
    return _JSON_CACHE[cache_key]


def generate_maplibre_html(
    world_state: WorldState,
    comparison_world_state: Optional[WorldState] = None,
    theme: str = "dark",
    mode: str = "tempo",
    height: int = 650,
    selected_feature_id: Optional[str] = None,
    factions_geojson: Optional[Dict[str, Any]] = None,
    aisps_geojson: Optional[Dict[str, Any]] = None,
    bairros_geojson: Optional[Dict[str, Any]] = None,
    show_factions: bool = True,
    show_aisps: bool = False,
    show_bairros: bool = False,
) -> str:
    """
    Gera o HTML/CSS/JavaScript autônomo com MapLibre GL JS 4.x.
    Suporta renderização de polígonos, anacronismo (hachurado cinza),
    instalações públicas, eventos com buffers de incerteza, fluxos de deslocamento
    e camadas opcionais de controle territorial (1.671 áreas), AISPs e Bairros.
    """
    # 1. GeoJSON principal do WorldState
    geojson_main = world_state.to_geojson()
    geojson_main_json = json.dumps(geojson_main, ensure_ascii=False)

    # 2. GeoJSON de Comparação
    geojson_comp_json = "null"
    if comparison_world_state:
        geojson_comp_json = json.dumps(comparison_world_state.to_geojson(), ensure_ascii=False)

    # 3. Camada de Facções (1.671 Polígonos de comunidades e domínio territorial)
    factions_json = "null"
    if show_factions:
        if factions_geojson is None:
            factions_geojson = load_faction_polygons()
        if factions_geojson:
            factions_json = _get_cached_json("factions_1671", factions_geojson)

    # 4. Camada de AISPs (39 Batalhões PMERJ)
    aisps_json = "null"
    if show_aisps:
        if aisps_geojson is None:
            aisps_geojson = load_aisp_polygons()
        if aisps_geojson:
            aisps_json = _get_cached_json("aisps_39", aisps_geojson)

    # 5. Camada de Bairros Oficiais (166 Bairros PCRJ/IPP)
    bairros_json = "null"
    if show_bairros:
        if bairros_geojson is None:
            bairros_geojson = load_bairros_polygons()
        if bairros_geojson:
            bairros_json = _get_cached_json("bairros_166", bairros_geojson)

    # Basemap style URLs e paleta temática
    if theme == "light":
        bg_color = "#F8F7F4"
        text_color = "#20201E"
        card_bg = "rgba(255, 255, 255, 0.95)"
        card_border = "#E2DDD5"
        carto_tile_url = "https://a.basemaps.cartocdn.com/rastertiles/light_all/{z}/{x}/{y}.png"
    else:
        bg_color = "#121212"
        text_color = "#E0DCD3"
        card_bg = "rgba(24, 24, 27, 0.95)"
        card_border = "#3F3F46"
        carto_tile_url = "https://a.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png"

    year = world_state.year
    warning_text = world_state.metadata.get("epistemological_warning") or ""

    factions_count_display = len(factions_geojson.get("features", [])) if (show_factions and factions_geojson) else 0
    aisps_count_display = len(aisps_geojson.get("features", [])) if (show_aisps and aisps_geojson) else 0
    bairros_count_display = len(bairros_geojson.get("features", [])) if (show_bairros and bairros_geojson) else 0

    html_code = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Atlas Histórico do Rio de Janeiro — MapLibre GL</title>
    <!-- MapLibre GL JS 4.7.1 -->
    <script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
    <link href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css" rel="stylesheet" />
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: {bg_color};
            color: {text_color};
        }}
        #map {{
            width: 100%;
            height: 100%;
            min-height: 600px;
            position: absolute;
            top: 0;
            bottom: 0;
            left: 0;
            right: 0;
        }}
        /* Overlay de Controles e Legenda */
        .atlas-panel {{
            position: absolute;
            background: {card_bg};
            border: 1px solid {card_border};
            border-radius: 6px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
            backdrop-filter: blur(8px);
            z-index: 10;
            padding: 12px 14px;
            font-size: 13px;
        }}
        .atlas-header {{
            top: 14px;
            left: 14px;
            max-width: 420px;
        }}
        .atlas-header h1 {{
            font-family: 'Libre Baskerville', Georgia, serif;
            font-size: 16px;
            margin: 0 0 4px 0;
            color: {text_color};
            font-weight: 700;
        }}
        .atlas-badge {{
            display: inline-block;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 3px;
            background: #7A2E2E;
            color: #FFFFFF;
            margin-bottom: 6px;
        }}
        .atlas-warning {{
            background: rgba(245, 158, 11, 0.15);
            border-left: 3px solid #F59E0B;
            padding: 6px 8px;
            font-size: 11px;
            margin-top: 8px;
            color: #D97706;
            line-height: 1.35;
        }}
        /* Legenda Cartográfica */
        .atlas-legend {{
            bottom: 24px;
            right: 14px;
            max-width: 270px;
        }}
        .atlas-legend-title {{
            font-weight: 700;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
            color: #7A2E2E;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
            font-size: 12px;
        }}
        .legend-color {{
            width: 14px;
            height: 14px;
            border-radius: 2px;
            margin-right: 8px;
            flex-shrink: 0;
            border: 1px solid rgba(0, 0, 0, 0.25);
        }}
        .legend-hatch {{
            background: repeating-linear-gradient(
                45deg,
                #6B7280,
                #6B7280 2px,
                transparent 2px,
                transparent 6px
            );
        }}
        /* Popups */
        .maplibregl-popup-content {{
            background: {card_bg};
            color: {text_color};
            border: 1px solid {card_border};
            border-radius: 6px;
            padding: 14px;
            font-size: 12px;
            line-height: 1.4;
            max-width: 320px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.45);
        }}
        .maplibregl-popup-close-button {{
            color: {text_color};
            font-size: 16px;
            padding: 4px 8px;
        }}
        .popup-tag {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            text-transform: uppercase;
            font-weight: 700;
            color: #7A2E2E;
        }}
        .popup-title {{
            font-family: 'Libre Baskerville', Georgia, serif;
            font-size: 14px;
            font-weight: 700;
            margin: 4px 0 8px 0;
            color: {text_color};
        }}
        .popup-meta {{
            font-size: 11px;
            color: #888;
            margin-bottom: 4px;
        }}
        .popup-evidence-badge {{
            display: inline-block;
            padding: 1px 5px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            color: #FFFFFF;
            background: #3B82F6;
        }}
        .popup-anach {{
            background: rgba(107, 114, 128, 0.15);
            border-left: 2px solid #6B7280;
            padding: 4px 6px;
            font-size: 10px;
            margin-top: 6px;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div id="map"></div>

    <!-- Painel de Controle Superior -->
    <div class="atlas-panel atlas-header">
        <span class="atlas-badge">ANO {year}</span>
        <h1>Atlas Espaço-Temporal</h1>
        <div style="font-size: 12px; color: #888;">
            Total no Atlas: <strong>{world_state.metadata.get("total_features", 0)}</strong> |
            Territórios: <strong>{world_state.metadata.get("territories_count", 0)}</strong> |
            Instalações: <strong>{world_state.metadata.get("facilities_count", 0)}</strong>
            {" | Facções: <strong>1.671</strong>" if factions_count_display else ""}
            {" | AISP: <strong>39</strong>" if aisps_count_display else ""}
            {" | Bairros: <strong>166</strong>" if bairros_count_display else ""}
        </div>
        {"<div class='atlas-warning'>" + warning_text + "</div>" if warning_text else ""}
    </div>

    <!-- Legenda Cartográfica -->
    <div class="atlas-panel atlas-legend">
        <div class="atlas-legend-title">Convenções Cartográficas</div>
        <div class="legend-item">
            <span class="legend-color" style="background: #EF4444;"></span>
            <span>Comando Vermelho (CV)</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #3B82F6;"></span>
            <span>Terceiro Comando / TCP</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #10B981;"></span>
            <span>Amigos dos Amigos (ADA)</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #374151;"></span>
            <span>Milícia / Grupos Paramilitares</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #D97706;"></span>
            <span>Área em Disputa / Conflito</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="border: 2px dashed #00E5FF; background: rgba(0, 229, 255, 0.2);"></span>
            <span>AISP / Batalhão PMERJ</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="border: 1px solid #A0AEC0; background: rgba(160, 174, 192, 0.15);"></span>
            <span>Bairro Oficial (PCRJ)</span>
        </div>
        <div class="legend-item">
            <span class="legend-color legend-hatch"></span>
            <span>Malha Ilustrativa (Anacrônica)</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #991B1B; border-radius: 50%;"></span>
            <span>Equipamento Prisional</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #1D4ED8; border-radius: 50%;"></span>
            <span>Instalação Policial / NuCOE</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #10B981; border-radius: 50%;"></span>
            <span>Acontecimento Documentado</span>
        </div>
    </div>

    <script>
        const geojsonMain = {geojson_main_json};
        const geojsonComp = {geojson_comp_json};
        const factionsGeoJSON = {factions_json};
        const aispsGeoJSON = {aisps_json};
        const bairrosGeoJSON = {bairros_json};
        const selectedFeatureId = "{selected_feature_id or ''}";

        // Estilo com tiles raster CartoDB Dark/Positron
        const mapStyle = {{
            "version": 8,
            "sources": {{
                "carto-tiles": {{
                    "type": "raster",
                    "tiles": [
                        "{carto_tile_url}"
                    ],
                    "tileSize": 256,
                    "attribution": "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a>, &copy; <a href='https://carto.com/attributions'>CARTO</a>"
                }}
            }},
            "layers": [
                {{
                    "id": "carto-base-layer",
                    "type": "raster",
                    "source": "carto-tiles",
                    "minzoom": 0,
                    "maxzoom": 19
                }}
            ]
        }};

        // Inicialização do Mapa MapLibre GL
        const map = new maplibregl.Map({{
            container: 'map',
            style: mapStyle,
            center: [-43.25, -22.90],
            zoom: 10.5,
            pitch: 0,
            bearing: 0
        }});

        // Controles de Navegação, Tela Cheia e Escala
        map.addControl(new maplibregl.NavigationControl({{ showCompass: true, showZoom: true }}), 'top-right');
        map.addControl(new maplibregl.FullscreenControl(), 'top-right');
        map.addControl(new maplibregl.ScaleControl({{ maxWidth: 120, unit: 'metric' }}), 'bottom-left');

        // Criação de padrão de hachura para áreas anacrônicas no Canvas
        function createHatchPattern(color1, color2) {{
            const canvas = document.createElement('canvas');
            canvas.width = 16;
            canvas.height = 16;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = color1;
            ctx.fillRect(0, 0, 16, 16);
            ctx.strokeStyle = color2;
            ctx.lineWidth = 2.5;
            ctx.beginPath();
            ctx.moveTo(0, 16);
            ctx.lineTo(16, 0);
            ctx.stroke();
            return ctx.getImageData(0, 0, 16, 16);
        }}

        window.addEventListener('resize', () => {{
            map.resize();
        }});

        map.on('load', () => {{
            // Força recálculo do viewport para nunca colapsar dentro de iframes
            map.resize();
            setTimeout(() => {{ map.resize(); }}, 250);
            setTimeout(() => {{ map.resize(); }}, 800);

            // Adiciona imagens de padrão hachurado
            try {{
                map.addImage('hatch-anach', createHatchPattern('rgba(0,0,0,0)', 'rgba(107, 114, 128, 0.45)'));
                map.addImage('hatch-disputa', createHatchPattern('rgba(217, 119, 6, 0.2)', 'rgba(220, 38, 38, 0.6)'));
            }} catch (e) {{
                console.warn('Canvas pattern error', e);
            }}

            // 1. Camada de Bairros Oficiais (PCRJ / IPP)
            if (bairrosGeoJSON && bairrosGeoJSON.features && bairrosGeoJSON.features.length > 0) {{
                map.addSource('bairros-data', {{
                    type: 'geojson',
                    data: bairrosGeoJSON
                }});

                map.addLayer({{
                    id: 'bairros-fill',
                    type: 'fill',
                    source: 'bairros-data',
                    paint: {{
                        'fill-color': '#718096',
                        'fill-opacity': 0.05
                    }}
                }});

                map.addLayer({{
                    id: 'bairros-stroke',
                    type: 'line',
                    source: 'bairros-data',
                    paint: {{
                        'line-color': '#A0AEC0',
                        'line-width': 0.9,
                        'line-opacity': 0.5
                    }}
                }});
            }}

            // 2. Camada de AISP (Batalhões da PMERJ)
            if (aispsGeoJSON && aispsGeoJSON.features && aispsGeoJSON.features.length > 0) {{
                map.addSource('aisps-data', {{
                    type: 'geojson',
                    data: aispsGeoJSON
                }});

                map.addLayer({{
                    id: 'aisps-fill',
                    type: 'fill',
                    source: 'aisps-data',
                    paint: {{
                        'fill-color': '#00E5FF',
                        'fill-opacity': 0.08
                    }}
                }});

                map.addLayer({{
                    id: 'aisps-stroke',
                    type: 'line',
                    source: 'aisps-data',
                    paint: {{
                        'line-color': '#00E5FF',
                        'line-width': 1.6,
                        'line-dasharray': [3, 2],
                        'line-opacity': 0.85
                    }}
                }});
            }}

            // 3. Camada de Perímetros Territoriais de Facções (1.671 Polígonos)
            if (factionsGeoJSON && factionsGeoJSON.features && factionsGeoJSON.features.length > 0) {{
                map.addSource('factions-data', {{
                    type: 'geojson',
                    data: factionsGeoJSON
                }});

                map.addLayer({{
                    id: 'factions-fill',
                    type: 'fill',
                    source: 'factions-data',
                    filter: ['in', ['geometry-type'], ['literal', ['Polygon', 'MultiPolygon']]],
                    paint: {{
                        'fill-color': [
                            'match',
                            ['get', 'faccao_sigla'],
                            'CV', '#EF4444',
                            'TCP', '#3B82F6',
                            'ADA', '#10B981',
                            ['MIL', 'LJ', 'MNI'], '#374151',
                            'NEU', '#9CA3AF',
                            ['coalesce', ['get', 'cor_hex'], ['get', 'faccao_cor'], '#6B7280']
                        ],
                        'fill-opacity': 0.42
                    }}
                }});

                map.addLayer({{
                    id: 'factions-stroke',
                    type: 'line',
                    source: 'factions-data',
                    filter: ['in', ['geometry-type'], ['literal', ['Polygon', 'MultiPolygon']]],
                    paint: {{
                        'line-color': [
                            'match',
                            ['get', 'faccao_sigla'],
                            'CV', '#EF4444',
                            'TCP', '#3B82F6',
                            'ADA', '#10B981',
                            ['MIL', 'LJ', 'MNI'], '#374151',
                            'NEU', '#9CA3AF',
                            ['coalesce', ['get', 'cor_hex'], ['get', 'faccao_cor'], '#6B7280']
                        ],
                        'line-width': 1.2,
                        'line-opacity': 0.85
                    }}
                }});
            }}

            // 4. Fonte Principal GeoJSON (WorldState)
            map.addSource('atlas-data', {{
                type: 'geojson',
                data: geojsonMain
            }});

            // 4.1 Polígonos de Territórios (Preenchimento) — APENAS Polygon / MultiPolygon
            map.addLayer({{
                id: 'territories-fill',
                type: 'fill',
                source: 'atlas-data',
                filter: [
                    'all',
                    ['==', ['get', 'layer'], 'territories'],
                    ['in', ['geometry-type'], ['literal', ['Polygon', 'MultiPolygon']]]
                ],
                paint: {{
                    'fill-color': ['coalesce', ['get', 'color_hex'], '#6B7280'],
                    'fill-opacity': [
                        'case',
                        ['==', ['get', 'relation_type'], 'controle'], 0.50,
                        ['==', ['get', 'relation_type'], 'disputa'], 0.40,
                        ['==', ['get', 'relation_type'], 'presenca_estatal'], 0.35,
                        0.25
                    ]
                }}
            }});

            // 4.2 Linhas de Borda de Territórios Poligonais
            map.addLayer({{
                id: 'territories-stroke',
                type: 'line',
                source: 'atlas-data',
                filter: [
                    'all',
                    ['==', ['get', 'layer'], 'territories'],
                    ['in', ['geometry-type'], ['literal', ['Polygon', 'MultiPolygon']]]
                ],
                paint: {{
                    'line-color': ['coalesce', ['get', 'color_hex'], '#6B7280'],
                    'line-width': 2.0,
                    'line-opacity': 0.90
                }}
            }});

            // 4.3 Territórios Pontuais (quando o território é modelado como Ponto)
            map.addLayer({{
                id: 'territories-point',
                type: 'circle',
                source: 'atlas-data',
                filter: [
                    'all',
                    ['==', ['get', 'layer'], 'territories'],
                    ['in', ['geometry-type'], ['literal', ['Point', 'MultiPoint']]]
                ],
                paint: {{
                    'circle-radius': 8.5,
                    'circle-color': ['coalesce', ['get', 'color_hex'], '#EF4444'],
                    'circle-stroke-width': 2.5,
                    'circle-stroke-color': '#FFFFFF',
                    'circle-opacity': 0.95
                }}
            }});

            // 4.4 Fluxos de Movimento (LineString)
            map.addLayer({{
                id: 'flows-line',
                type: 'line',
                source: 'atlas-data',
                filter: [
                    'all',
                    ['==', ['get', 'layer'], 'flows'],
                    ['in', ['geometry-type'], ['literal', ['LineString', 'MultiLineString']]]
                ],
                paint: {{
                    'line-color': '#F59E0B',
                    'line-width': 3,
                    'line-dasharray': [2, 2],
                    'line-opacity': 0.9
                }}
            }});

            // 4.5 Instalações Institucionais (Círculos)
            map.addLayer({{
                id: 'facilities-circle',
                type: 'circle',
                source: 'atlas-data',
                filter: [
                    'all',
                    ['==', ['get', 'layer'], 'facilities'],
                    ['in', ['geometry-type'], ['literal', ['Point', 'MultiPoint']]]
                ],
                paint: {{
                    'circle-radius': 7,
                    'circle-color': [
                        'case',
                        ['==', ['get', 'facility_type'], 'presidio'], '#991B1B',
                        ['==', ['get', 'facility_type'], 'presidio_seguranca_maxima'], '#7F1D1D',
                        ['==', ['get', 'facility_type'], 'complexo_penitenciario'], '#B91C1C',
                        ['==', ['get', 'facility_type'], 'batalhao_pmerj'], '#1D4ED8',
                        '#4B5563'
                    ],
                    'circle-stroke-width': 2,
                    'circle-stroke-color': '#FFFFFF'
                }}
            }});

            // 4.6 Acontecimentos Históricos (Pontos com Nível de Confiança)
            map.addLayer({{
                id: 'events-circle',
                type: 'circle',
                source: 'atlas-data',
                filter: [
                    'all',
                    ['==', ['get', 'layer'], 'events'],
                    ['in', ['geometry-type'], ['literal', ['Point', 'MultiPoint']]]
                ],
                paint: {{
                    'circle-radius': 6.5,
                    'circle-color': [
                        'case',
                        ['==', ['get', 'confidence_level'], 'confirmado'], '#10B981',
                        ['==', ['get', 'confidence_level'], 'provavel'], '#F59E0B',
                        '#EF4444'
                    ],
                    'circle-stroke-width': 1.8,
                    'circle-stroke-color': '#FFFFFF'
                }}
            }});

            // 5. Camada de Comparação (se houver)
            if (geojsonComp && geojsonComp.features && geojsonComp.features.length > 0) {{
                map.addSource('atlas-comp-data', {{
                    type: 'geojson',
                    data: geojsonComp
                }});
                map.addLayer({{
                    id: 'comp-territories-fill',
                    type: 'fill',
                    source: 'atlas-comp-data',
                    filter: [
                        'all',
                        ['==', ['get', 'layer'], 'territories'],
                        ['in', ['geometry-type'], ['literal', ['Polygon', 'MultiPolygon']]]
                    ],
                    paint: {{
                        'fill-color': '#9CA3AF',
                        'fill-opacity': 0.25
                    }}
                }});
                map.addLayer({{
                    id: 'comp-territories-stroke',
                    type: 'line',
                    source: 'atlas-comp-data',
                    filter: [
                        'all',
                        ['==', ['get', 'layer'], 'territories'],
                        ['in', ['geometry-type'], ['literal', ['Polygon', 'MultiPolygon']]]
                    ],
                    paint: {{
                        'line-color': '#9CA3AF',
                        'line-width': 1.5,
                        'line-dasharray': [2, 2],
                        'line-opacity': 0.7
                    }}
                }});
            }}

            // Interação: Popups ao Clicar
            const popup = new maplibregl.Popup({{
                closeButton: true,
                closeOnClick: true,
                maxWidth: '340px'
            }});

            const clickLayers = [
                'factions-fill',
                'aisps-fill',
                'bairros-fill',
                'territories-fill',
                'territories-point',
                'facilities-circle',
                'events-circle',
                'flows-line'
            ];

            clickLayers.forEach(layerId => {{
                if (!map.getLayer(layerId)) return;

                map.on('mouseenter', layerId, () => {{
                    map.getCanvas().style.cursor = 'pointer';
                }});
                map.on('mouseleave', layerId, () => {{
                    map.getCanvas().style.cursor = '';
                }});

                map.on('click', layerId, (e) => {{
                    if (!e.features || !e.features[0]) return;
                    const props = e.features[0].properties;
                    const coords = e.lngLat;

                    let content = '';

                    if (layerId === 'factions-fill') {{
                        const faccaoNome = props.faccao_nome || props.faccao_sigla || 'Facção Desconhecida';
                        const sigla = props.faccao_sigla || '';
                        const cor = props.cor_hex || '#EF4444';
                        content = `
                            <div class="popup-tag" style="color: ${{cor}};">CONTROLE TERRITORIAL &bull; ${{sigla}}</div>
                            <div class="popup-title">${{props.nome || 'Comunidade'}}</div>
                            <div class="popup-meta"><strong>Domínio:</strong> <span style="color: ${{cor}}; font-weight:700;">${{faccaoNome}}</span></div>
                            ${{props.centroide_lat ? `<div class="popup-meta"><strong>Coordenadas:</strong> ${{Number(props.centroide_lat).toFixed(4)}}, ${{Number(props.centroide_lon).toFixed(4)}}</div>` : ''}}
                            <div class="popup-meta"><strong>Base de Dados:</strong> ${{props.fonte_origem || 'Base Consolidada (1.671 Polígonos)'}}</div>
                        `;
                    }} else if (layerId === 'aisps-fill') {{
                        content = `
                            <div class="popup-tag" style="color: #00E5FF;">AISP &bull; SEGURANÇA PÚBLICA</div>
                            <div class="popup-title">${{props.batalhao || ('AISP ' + props.aisp)}}</div>
                            <div class="popup-meta"><strong>Sede do Batalhão:</strong> ${{props.sede || 'N/D'}}</div>
                            <div class="popup-meta"><strong>Município:</strong> ${{props.municipio || 'Rio de Janeiro'}} &bull; <strong>RISP:</strong> ${{props.risp || 'N/D'}}</div>
                            <div class="popup-meta"><strong>Fonte Oficial:</strong> ISP-RJ / PMERJ</div>
                        `;
                    }} else if (layerId === 'bairros-fill') {{
                        content = `
                            <div class="popup-tag" style="color: #A0AEC0;">BAIRRO OFICIAL</div>
                            <div class="popup-title">${{props.nome || 'Bairro'}}</div>
                            <div class="popup-meta"><strong>Região Administrativa:</strong> ${{props.regiao_adm || 'N/D'}}</div>
                            <div class="popup-meta"><strong>Área de Planejamento (AP):</strong> ${{props.area_planejamento || 'N/D'}}</div>
                            <div class="popup-meta"><strong>Fonte Oficial:</strong> PCRJ / IPP (Data.Rio)</div>
                        `;
                    }} else if (layerId === 'territories-fill' || layerId === 'territories-point') {{
                        const isPoint = (layerId === 'territories-point');
                        const relType = (props.relation_type || 'presença').toUpperCase();
                        const evStr = props.evidence_strength || 'alegada';
                        content = `
                            <div class="popup-tag">TERRITÓRIO HISTÓRICO &bull; ${{relType}} ${{isPoint ? '(PONTO)' : ''}}</div>
                            <div class="popup-title">${{props.region_name || 'Território'}}</div>
                            <div class="popup-meta"><strong>Organização:</strong> ${{props.organization_name || 'Desconhecida'}} (${{props.organization_acronym || 'N/D'}})</div>
                            <div class="popup-meta"><strong>Força da Evidência:</strong> <span class="popup-evidence-badge">${{evStr.toUpperCase()}}</span></div>
                            <div class="popup-meta"><strong>Fontes Independentes:</strong> ${{props.independent_root_count || 1}}</div>
                            <div class="popup-meta"><strong>Dataset / Custódia:</strong> ${{props.dataset_name || 'Acervo Histórico'}}</div>
                            ${{props.notes ? `<div style="font-size:11px; margin-top:4px; color:#A1A1AA;">${{props.notes}}</div>` : ''}}
                            ${{props.is_anachronistic ? `<div class="popup-anach">⚠️ ${{props.anachronism_note || 'Malha contemporânea aplicada como referência ilustrativa.'}}</div>` : ''}}
                        `;
                    }} else if (layerId === 'facilities-circle') {{
                        content = `
                            <div class="popup-tag">INSTITUIÇÃO PÚBLICA &bull; ${{props.facility_type ? props.facility_type.toUpperCase() : ''}}</div>
                            <div class="popup-title">${{props.name || 'Instalação'}}</div>
                            <div class="popup-meta"><strong>Abertura:</strong> ${{props.opened_at || 'Desconhecida'}} &bull; <strong>Fechamento:</strong> ${{props.closed_at || 'Em operação'}}</div>
                            ${{props.capacity ? `<div class="popup-meta"><strong>Capacidade:</strong> ${{props.capacity}} vagas</div>` : ''}}
                            <div style="font-size: 11px; margin-top: 6px;">${{props.notes || ''}}</div>
                        `;
                    }} else if (layerId === 'events-circle') {{
                        const conf = (props.confidence_level || 'confirmado').toUpperCase();
                        content = `
                            <div class="popup-tag">ACONTECIMENTO HISTÓRICO &bull; ${{conf}}</div>
                            <div class="popup-title">${{props.title || 'Evento'}}</div>
                            <div class="popup-meta"><strong>Data:</strong> ${{props.date_display || props.date_start || 'Data não informada'}}</div>
                            <div class="popup-meta"><strong>Fonte Primária:</strong> ${{props.primary_source || 'Catalogada no Acervo'}}</div>
                            <div class="popup-meta"><strong>Precisão Espacial:</strong> ${{props.coordinate_source || 'Referencial'}}</div>
                        `;
                    }} else if (layerId === 'flows-line') {{
                        content = `
                            <div class="popup-tag">FLUXO ESPAÇO-TEMPORAL</div>
                            <div class="popup-title">${{props.flow_type ? props.flow_type.replace('_', ' ').toUpperCase() : 'Fluxo'}}</div>
                            <div class="popup-meta"><strong>Data:</strong> ${{props.date_start || ''}}</div>
                            <div style="font-size: 11px; margin-top: 6px;">${{props.notes || ''}}</div>
                        `;
                    }}

                    popup.setLngLat(coords).setHTML(content).addTo(map);
                }});
            }});
        }});
    </script>
</body>
</html>
"""
    return html_code


def render_maplibre_atlas(
    world_state: WorldState,
    comparison_world_state: Optional[WorldState] = None,
    theme: str = "dark",
    mode: str = "tempo",
    height: int = 650,
    selected_feature_id: Optional[str] = None,
    factions_geojson: Optional[Dict[str, Any]] = None,
    aisps_geojson: Optional[Dict[str, Any]] = None,
    bairros_geojson: Optional[Dict[str, Any]] = None,
    show_factions: bool = True,
    show_aisps: bool = False,
    show_bairros: bool = False,
):
    """
    Renderiza o componente MapLibre GL JS integrado no Streamlit.
    """
    html = generate_maplibre_html(
        world_state=world_state,
        comparison_world_state=comparison_world_state,
        theme=theme,
        mode=mode,
        height=height,
        selected_feature_id=selected_feature_id,
        factions_geojson=factions_geojson,
        aisps_geojson=aisps_geojson,
        bairros_geojson=bairros_geojson,
        show_factions=show_factions,
        show_aisps=show_aisps,
        show_bairros=show_bairros,
    )
    components.html(html, height=height, scrolling=False)
