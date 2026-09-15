# -*- coding: utf-8 -*-
"""Componentes de interface do Atlas Histórico da Criminalidade RJ."""

from app.ui.components.modern_ui import (
    render_hero_header,
    render_kpi_dashboard,
    render_event_card,
)

# Exportações condicionais para módulos auxiliares
try:
    from app.ui.components.atlas_map import render_maplibre_atlas, generate_maplibre_html
except ImportError:
    render_maplibre_atlas = None
    generate_maplibre_html = None

try:
    from app.ui.components.video_corpus_explorer import (
        render_video_corpus_explorer,
        get_video_corpus_analytics,
        load_video_catalog,
    )
except ImportError:
    render_video_corpus_explorer = None
    get_video_corpus_analytics = None
    load_video_catalog = None

__all__ = [
    "render_hero_header",
    "render_kpi_dashboard",
    "render_event_card",
    "render_maplibre_atlas",
    "generate_maplibre_html",
    "render_video_corpus_explorer",
    "get_video_corpus_analytics",
    "load_video_catalog",
]
