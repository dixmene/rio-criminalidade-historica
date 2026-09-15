# -*- coding: utf-8 -*-
"""
Suíte de Testes Automatizados para o Módulo de Exploração do Corpus Audiovisual
Componente: app/ui/components/video_corpus_explorer.py
"""

import json
import pytest
from pathlib import Path
from streamlit.testing.v1 import AppTest

from app.ui.components.video_corpus_explorer import (
    load_video_catalog,
    load_transcript_file,
    get_available_transcripts_map,
    enrich_video_entry,
    get_video_corpus_analytics,
    normalize_string,
    parse_duration_to_seconds,
    format_seconds_display,
    render_video_corpus_explorer,
)


def test_normalize_string():
    """Valida normalização onomástica e remoção de acentos."""
    assert normalize_string("Rogério Lemgruber") == "rogerio lemgruber"
    assert normalize_string("Uê - Racha do Crime") == "ue - racha do crime"
    assert normalize_string("Milícias da Zona Oeste") == "milicias da zona oeste"
    assert normalize_string("") == ""
    assert normalize_string(None) == ""


def test_parse_duration_to_seconds():
    """Valida parsing de durações em formatos MM:SS e HH:MM:SS."""
    assert parse_duration_to_seconds("10:35") == 635
    assert parse_duration_to_seconds("01:10:00") == 4200
    assert parse_duration_to_seconds("00:45") == 45
    assert parse_duration_to_seconds("inválido") == 0
    assert parse_duration_to_seconds(None) == 0


def test_format_seconds_display():
    """Valida formatação amigável de durações."""
    assert format_seconds_display(635) == "10:35"
    assert format_seconds_display(3665) == "1h 01m"
    assert format_seconds_display(0) == "S/D"


def test_load_video_catalog_success():
    """Valida o carregamento dos 100 documentários do catálogo oficial."""
    cat = load_video_catalog()
    assert cat is not None
    assert cat.get("_error") is None
    assert cat.get("playlist_title") == "Histórias do Rio de Janeiro"
    assert cat.get("channel_name") == "Iconografia da História"
    videos = cat.get("videos", [])
    assert len(videos) == 100

    first = videos[0]
    assert first.get("id") == "YTRIO-0001"
    assert "XXRL8Kj_dTE" in first.get("youtube_url")
    assert "BRASILEIRINHO" in first.get("title").upper()


def test_load_video_catalog_missing_resilience():
    """Garante tratamento gracioso e retorno estruturado sem exceções para arquivo ausente."""
    cat = load_video_catalog(custom_path="caminho/absolutamente/inexistente_123.json")
    # Deve fallback para o padrão ou retornar dicionário estruturado com _error
    assert isinstance(cat, dict)
    assert "videos" in cat


def test_load_transcript_file():
    """Valida carregamento de transcrições individuais e tolerância a IDs ausentes."""
    # Teste de vídeo com transcrição existente
    tdata = load_transcript_file("XXRL8Kj_dTE")
    assert tdata is not None
    assert tdata.get("video_id") == "XXRL8Kj_dTE"
    assert len(tdata.get("snippets", [])) > 0
    assert tdata.get("duration_seconds", 0) > 600

    # Teste de vídeo inexistente (deve retornar None sem erro)
    none_data = load_transcript_file("VIDEO_INEXISTENTE_999")
    assert none_data is None


def test_get_available_transcripts_map():
    """Valida indexação das 10 transcrições brutas auditadas."""
    tmap = get_available_transcripts_map()
    assert isinstance(tmap, dict)
    assert len(tmap) >= 10
    assert "XXRL8Kj_dTE" in tmap
    assert "IAndFXthQ0E" in tmap
    assert "axe6V7UzxO0" in tmap


def test_enrich_video_entry():
    """Valida classificação entitária, matrizes, territórios e citação formal ABNT."""
    tmap = get_available_transcripts_map()

    # 1. Caso Brasileirinho (YTRIO-0001)
    v1 = {
        "id": "YTRIO-0001",
        "video_id": "XXRL8Kj_dTE",
        "youtube_url": "https://www.youtube.com/watch?v=XXRL8Kj_dTE",
        "channel_name": "Iconografia da História",
        "title": "A HISTÓRIA DE BRASILEIRINHO, O \"MASCOTE\" DOS CHEFES DA ROCINHA",
        "duration": "10:35",
        "transcript_status": "generated",
        "transcript_hash": "24a9db2142de3bdac4c43e2c652375f056be206ad99307b754cd1930c7b94c62"
    }
    enriched1 = enrich_video_entry(v1, tmap)
    assert "Brasileirinho" in enriched1["detected_characters"]
    assert "Comando Vermelho (CV)" in enriched1["detected_factions"]
    assert "Rocinha" in enriched1["detected_territories"]
    assert enriched1["duration_seconds"] == 635
    assert enriched1["is_transcribed"] is True
    assert "ICONOGRAFIA DA HISTÓRIA" in enriched1["abnt_citation"]
    assert "24a9db21" in enriched1["abnt_citation"]

    # 2. Caso Jogo do Bicho (YTRIO-0005)
    v5 = {
        "id": "YTRIO-0005",
        "video_id": "axe6V7UzxO0",
        "title": "JOGO DO BICHO: THE COMPLETE AND DETAILED STORY #history #riodejaneiro #crime",
        "duration": "19:29",
        "transcript_hash": "ed5eee3cf8f8223a3e6911c7ab429ae104b314c8a28d8f240b0775459197f835"
    }
    enriched5 = enrich_video_entry(v5, tmap)
    assert "Jogo do Bicho & Contravenção" in enriched5["detected_factions"]
    assert enriched5["duration_bucket"] == "Longa (>18 min)"


def test_get_video_corpus_analytics():
    """Valida métricas analíticas consolidadas do acervo audiovisual."""
    cat = load_video_catalog()
    tmap = get_available_transcripts_map()
    enriched_videos = [enrich_video_entry(v, tmap) for v in cat.get("videos", [])]

    analytics = get_video_corpus_analytics(enriched_videos)
    assert analytics["total_videos"] == 100
    assert analytics["total_with_hash"] >= 10
    assert analytics["unique_characters_count"] >= 50
    assert "Comando Vermelho (CV)" in analytics["factions_coverage"]
    assert "Milícias & Paramilitares" in analytics["factions_coverage"]
    assert "Rocinha" in analytics["territories_coverage"]
    assert "horas" in analytics["estimated_total_hours_str"]


def test_apptest_video_corpus_explorer_integration():
    """Valida execução Streamlit sem exceções ao renderizar o explorador."""
    code = """
import streamlit as st
from app.ui.components.video_corpus_explorer import render_video_corpus_explorer

render_video_corpus_explorer()
"""
    at = AppTest.from_string(code)
    at.run(timeout=15)
    assert len(at.exception) == 0
    assert len(at.metric) >= 5
    assert len(at.selectbox) >= 4
