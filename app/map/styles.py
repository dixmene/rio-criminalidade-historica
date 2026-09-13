"""
Módulo de Estilos e Configurações Cartográficas (Tema Escuro & Alta Legibilidade).
Suporte a mapas-base táticos (Dark Matter, Positron, OSM) e esquemas de cores
para Facções Armadas, AISPs (Batalhões PMERJ) e Níveis de Evidência Historiográfica.
"""

from typing import Dict, Any

# Mapas-base suportados
MAP_TILES = {
    "dark": {
        "name": "CartoDB Dark Matter",
        "tiles": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        "attr": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        "subdomains": "abcd",
        "max_zoom": 19,
    },
    "light": {
        "name": "CartoDB Positron",
        "tiles": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        "attr": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        "subdomains": "abcd",
        "max_zoom": 19,
    },
    "osm": {
        "name": "OpenStreetMap Editorial",
        "tiles": "OpenStreetMap",
        "attr": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        "max_zoom": 19,
    }
}

# Paleta canônica de cores para Facções e Grupos Armados no Rio de Janeiro
FACTION_COLORS: Dict[str, str] = {
    "CV": "#E0342C",      # Vermelho vivo (Comando Vermelho)
    "TCP": "#2FA46B",     # Verde esmeralda (Terceiro Comando Puro)
    "ADA": "#EDB72B",     # Amarelo/Dourado (Amigos dos Amigos)
    "MIL": "#4E9DE0",     # Azul tático (Milícia Geral)
    "LJ": "#2B5BC7",      # Azul escuro/aço (Liga da Justiça / CL220)
    "MNI": "#9B6BD6",     # Roxo (Milícia de Nova Iguaçu)
    "NEU": "#8C97A3",     # Cinza neutro (Área Neutra / Disputada)
}

FACTION_NAMES: Dict[str, str] = {
    "CV": "Comando Vermelho",
    "TCP": "Terceiro Comando Puro",
    "ADA": "Amigos dos Amigos",
    "MIL": "Milícia (Geral)",
    "LJ": "Liga da Justiça (CL220)",
    "MNI": "Milícia de Nova Iguaçu",
    "NEU": "Área Neutra / Disputada"
}

# Selos de Nível de Evidência (Metodologia de Custódia e Veracidade)
EVIDENCE_LEVELS: Dict[str, Dict[str, Any]] = {
    "A": {
        "label": "Nível A — Oficial / Judicial",
        "descricao": "Decisões judiciais transitadas em julgado, denúncias do GAECO/MPRJ, relatórios de CPIs e Diário Oficial.",
        "color": "#10B981",  # Verde esmeralda brilhante
        "marker_color": "green",
        "badge_css": "badge-nivel-a",
        "icon": "shield"
    },
    "B": {
        "label": "Nível B — Acadêmico / Estatístico",
        "descricao": "Artigos de centros de pesquisa (UFRJ, UERJ, UFF, ISP-RJ, GENI/UFF, Fogo Cruzado) com metodologia aberta.",
        "color": "#3B82F6",  # Azul institucional
        "marker_color": "blue",
        "badge_css": "badge-nivel-b",
        "icon": "education"
    },
    "C": {
        "label": "Nível C — Imprensa Histórica Checada",
        "descricao": "Arquivos da Hemeroteca Digital da Biblioteca Nacional e reportagens investigativas corroboradas.",
        "color": "#F59E0B",  # Âmbar tático
        "marker_color": "orange",
        "badge_css": "badge-nivel-c",
        "icon": "bullhorn"
    },
    "conflitante": {
        "label": "Controvérsia Documentada",
        "descricao": "Divergência expressa entre fontes oficiais ou históricas catalogadas no banco.",
        "color": "#EF4444",  # Vermelho alerta
        "marker_color": "red",
        "badge_css": "badge-conflitante",
        "icon": "warning-sign"
    }
}

# Estilos CSS e parâmetros de exibição vetorial
STYLE_FACTION_POLYGON_DARK = {
    "weight": 1.2,
    "fillOpacity": 0.35,
    "opacity": 0.85
}

STYLE_AISP_POLYGON_DARK = {
    "color": "#00E5FF",      # Ciano brilhante tático
    "fillColor": "#00E5FF",
    "weight": 1.5,
    "dashArray": "4, 4",
    "fillOpacity": 0.08,
    "opacity": 0.75
}

STYLE_BAIRROS_POLYGON_DARK = {
    "color": "#A0AEC0",      # Cinza claro sutil
    "fillColor": "#4A5568",
    "weight": 0.8,
    "fillOpacity": 0.05,
    "opacity": 0.45
}
