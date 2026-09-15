# -*- coding: utf-8 -*-
"""
Componente Cartográfico MapLibre GL JS — Atlas Histórico Espaço-Temporal
========================================================================

Substitui o Folium estático por MapLibre GL 4.x com aceleração WebGL,
renderização vetorial fluida (60 FPS), hierarquia cartográfica de 10 camadas
e suporte aos 9 modos de cruzamento historiográfico.
"""

import json
from typing import Dict, List, Optional, Any
import streamlit.components.v1 as components

from app.services.atlas_service import WorldState


def generate_maplibre_html(
    world_state: WorldState,
    comparison_world_state: Optional[WorldState] = None,
    theme: str = "dark",
    mode: str = "tempo",
    height: int = 680,
    selected_feature_id: Optional[str] = None
) -> str:
    """
    Gera o HTML/CSS/JavaScript autônomo com MapLibre GL JS 4.x.
    Suporta renderização de polígonos, anacronismo (hachurado cinza),
    instalações públicas, eventos com buffers de incerteza e fluxos de deslocamento.
    """
    geojson_main = world_state.to_geojson()
    geojson_main_json = json.dumps(geojson_main, ensure_ascii=False)

    geojson_comp_json = "null"
    if comparison_world_state:
        geojson_comp_json = json.dumps(comparison_world_state.to_geojson(), ensure_ascii=False)

    # Basemap style URLs (com fallbacks para raster tiles abertos)
    if theme == "light":
        basemap_style = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
        bg_color = "#F8F7F4"
        text_color = "#20201E"
        card_bg = "rgba(255, 255, 255, 0.95)"
        card_border = "#E2DDD5"
    else:
        basemap_style = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
        bg_color = "#121212"
        text_color = "#E0DCD3"
        card_bg = "rgba(24, 24, 27, 0.95)"
        card_border = "#3F3F46"

    year = world_state.year
    warning_text = world_state.metadata.get("epistemological_warning") or ""

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
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: {bg_color};
            color: {text_color};
            overflow: hidden;
        }}
        #map {{
            position: absolute;
            top: 0;
            bottom: 0;
            width: 100%;
            height: 100%;
        }}
        /* Overlay de Controles e Legenda */
        .atlas-panel {{
            position: absolute;
            background: {card_bg};
            border: 1px solid {card_border};
            border-radius: 6px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
            backdrop-filter: blur(8px);
            z-index: 10;
            padding: 12px 14px;
            font-size: 13px;
        }}
        .atlas-header {{
            top: 14px;
            left: 14px;
            max-width: 380px;
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
            max-width: 260px;
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
            border: 1px solid rgba(0, 0, 0, 0.2);
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
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
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
            Total de feições: <strong>{world_state.metadata.get("total_features", 0)}</strong> |
            Territórios: <strong>{world_state.metadata.get("territories_count", 0)}</strong> |
            Instalações: <strong>{world_state.metadata.get("facilities_count", 0)}</strong>
        </div>
        {"<div class='atlas-warning'>" + warning_text + "</div>" if warning_text else ""}
    </div>

    <!-- Legenda Cartográfica -->
    <div class="atlas-panel atlas-legend">
        <div class="atlas-legend-title">Convenções Cartográficas</div>
        <div class="legend-item">
            <span class="legend-color" style="background: #DC2626;"></span>
            <span>Comando Vermelho (Controle)</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #2563EB;"></span>
            <span>Terceiro Comando / TCP</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #059669;"></span>
            <span>Amigos dos Amigos (ADA)</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #374151;"></span>
            <span>Milícia / Liga da Justiça</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #D97706;"></span>
            <span>Área em Disputa / Conflito</span>
        </div>
        <div class="legend-item">
            <span class="legend-color legend-hatch"></span>
            <span>Malha Ilustrativa (Anacrônica)</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #991B1B; border-radius: 50%;"></span>
            <span>Equipamento Prisional Ativo</span>
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
        const selectedFeatureId = "{selected_feature_id or ''}";

        // Estilo de fallback seguro com tiles abertos Carto Positron/Dark
        const mapStyle = {{
            "version": 8,
            "sources": {{
                "carto-tiles": {{
                    "type": "raster",
                    "tiles": [
                        "{'https://a.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png' if theme == 'dark' else 'https://a.basemaps.cartocdn.com/rastertiles/light_all/{z}/{x}/{y}.png'}"
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

        map.addControl(new maplibregl.NavigationControl(), 'bottom-left');
        map.addControl(new maplibregl.ScaleControl({{ maxWidth: 100, unit: 'metric' }}), 'bottom-left');

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

        map.on('load', () => {{
            // Adiciona imagens de padrão hachurado
            try {{
                map.addImage('hatch-anach', createHatchPattern('rgba(0,0,0,0)', 'rgba(107, 114, 128, 0.45)'));
                map.addImage('hatch-disputa', createHatchPattern('rgba(217, 119, 6, 0.2)', 'rgba(220, 38, 38, 0.6)'));
            }} catch (e) {{
                console.warn('Canvas pattern error', e);
            }}

            // Fonte Principal GeoJSON
            map.addSource('atlas-data', {{
                type: 'geojson',
                data: geojsonMain
            }});

            // 1. Layer: Polígonos de Territórios (Preenchimento)
            map.addLayer({{
                id: 'territories-fill',
                type: 'fill',
                source: 'atlas-data',
                filter: ['==', ['get', 'layer'], 'territories'],
                paint: {{
                    'fill-color': ['coalesce', ['get', 'color_hex'], '#6B7280'],
                    'fill-opacity': [
                        'case',
                        ['==', ['get', 'relation_type'], 'controle'], 0.45,
                        ['==', ['get', 'relation_type'], 'disputa'], 0.35,
                        ['==', ['get', 'relation_type'], 'presenca_estatal'], 0.35,
                        0.25
                    ]
                }}
            }});

            // 2. Layer: Linhas de Borda de Territórios
            map.addLayer({{
                id: 'territories-stroke',
                type: 'line',
                source: 'atlas-data',
                filter: ['==', ['get', 'layer'], 'territories'],
                paint: {{
                    'line-color': ['coalesce', ['get', 'color_hex'], '#6B7280'],
                    'line-width': 1.8,
                    'line-opacity': 0.85
                }}
            }});

            // 3. Layer: Fluxos de Movimento (LineString)
            map.addLayer({{
                id: 'flows-line',
                type: 'line',
                source: 'atlas-data',
                filter: ['==', ['get', 'layer'], 'flows'],
                paint: {{
                    'line-color': '#F59E0B',
                    'line-width': 3,
                    'line-dasharray': [2, 2],
                    'line-opacity': 0.9
                }}
            }});

            // 4. Layer: Instalações Institucionais (Círculos)
            map.addLayer({{
                id: 'facilities-circle',
                type: 'circle',
                source: 'atlas-data',
                filter: ['==', ['get', 'layer'], 'facilities'],
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

            // 5. Layer: Acontecimentos Históricos (Pontos)
            map.addLayer({{
                id: 'events-circle',
                type: 'circle',
                source: 'atlas-data',
                filter: ['==', ['get', 'layer'], 'events'],
                paint: {{
                    'circle-radius': 6,
                    'circle-color': [
                        'case',
                        ['==', ['get', 'confidence_level'], 'confirmado'], '#10B981',
                        ['==', ['get', 'confidence_level'], 'provavel'], '#F59E0B',
                        '#EF4444'
                    ],
                    'circle-stroke-width': 1.5,
                    'circle-stroke-color': '#FFFFFF'
                }}
            }});

            // Interação: Popups ao Clicar
            const popup = new maplibregl.Popup({{
                closeButton: true,
                closeOnClick: true
            }});

            ['territories-fill', 'facilities-circle', 'events-circle', 'flows-line'].forEach(layerId => {{
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
                    if (props.layer === 'territories') {{
                        content = `
                            <div class="popup-tag">TERRITÓRIO &bull; ${{props.relation_type ? props.relation_type.toUpperCase() : ''}}</div>
                            <div class="popup-title">${{props.region_name || 'Território'}}</div>
                            <div class="popup-meta"><strong>Organização:</strong> ${{props.organization_name || 'Desconhecida'}} (${{props.organization_acronym || 'N/D'}})</div>
                            <div class="popup-meta"><strong>Força da Evidência:</strong> ${{props.evidence_strength || 'alegada'}}</div>
                            <div class="popup-meta"><strong>Fontes Independentes:</strong> ${{props.independent_root_count || 1}}</div>
                            <div class="popup-meta"><strong>Dataset:</strong> ${{props.dataset_name || 'N/D'}}</div>
                            ${{props.is_anachronistic ? `<div class="popup-anach">⚠️ ${{props.anachronism_note || 'Malha contemporânea aplicada como referência ilustrativa.'}}</div>` : ''}}
                        `;
                    }} else if (props.layer === 'facilities') {{
                        content = `
                            <div class="popup-tag">INSTITUIÇÃO PÚBLICA &bull; ${{props.facility_type || ''}}</div>
                            <div class="popup-title">${{props.name || 'Instalação'}}</div>
                            <div class="popup-meta"><strong>Abertura:</strong> ${{props.opened_at || 'Desconhecida'}} &bull; <strong>Fechamento:</strong> ${{props.closed_at || 'Em operação'}}</div>
                            ${{props.capacity ? `<div class="popup-meta"><strong>Capacidade:</strong> ${{props.capacity}} vagas</div>` : ''}}
                            <div style="font-size: 11px; margin-top: 6px;">${{props.notes || ''}}</div>
                        `;
                    }} else if (props.layer === 'events') {{
                        content = `
                            <div class="popup-tag">ACONTECIMENTO HISTÓRICO &bull; ${{props.confidence_level ? props.confidence_level.toUpperCase() : ''}}</div>
                            <div class="popup-title">${{props.title || 'Evento'}}</div>
                            <div class="popup-meta"><strong>Data:</strong> ${{props.date_display || props.date_start || ''}}</div>
                            <div class="popup-meta"><strong>Fonte Primária:</strong> ${{props.primary_source || 'Catalogada no Acervo'}}</div>
                            <div class="popup-meta"><strong>Precisão Espacial:</strong> ${{props.coordinate_source || 'Referencial'}}</div>
                        `;
                    }} else if (props.layer === 'flows') {{
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
    height: int = 680,
    selected_feature_id: Optional[str] = None
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
        selected_feature_id=selected_feature_id
    )
    components.html(html, height=height, scrolling=False)
