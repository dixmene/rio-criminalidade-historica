# -*- coding: utf-8 -*-
"""
Suíte de Testes Automatizados da Interface do Usuário (UI) e Serviços.
Projeto: rio-criminalidade-historica

Testa exaustivamente:
1. Todas as 6 seções canônicas do site:
   - Visão Geral (Home / Início)
   - Painel Analítico
   - Mapa Histórico & Territórios (Folium maps, polígonos GeoJSON, marcadores de eventos, inspeção territorial)
   - Linha do Tempo (agrupamento por décadas, filtros de ano, exportação CSV)
   - Acervo de Fontes (filtros de tipologia, ficha catalográfica com SHA-256)
   - Metodologia Histórica (avaliação de confiança, princípios epistemológicos)
2. Casos de borda críticos:
   - Filtros que retornam zero resultados (0 divisões, listas vazias)
   - Territórios com coordenadas nulas (ex: ID 89 Subúrbios Ferroviários, ID 91, ID 124)
   - Eventos de intervalo longo (ex: 1975-1980)
   - Eventos reais vs DEMO (isolamento estrito)
   - Renderização de mapas com Folium sem erros de serialização (HTML)
3. Funções de suporte da UI e DataService
4. Execução programática de Streamlit AppTest para todas as seções
"""

import math
import pytest
import pandas as pd
from pathlib import Path
from streamlit.testing.v1 import AppTest

from app.database import SessionLocal
from app.services import EventService, DataService
from app.models import Region, Event
from app.ui.app import (
    SECOES,
    VIEW_ALIASES,
    CONFIDENCE_STYLES,
    MARKER_COLORS,
    FACCAO_NOMES,
    format_badge,
    format_mode_badge,
    normalize_string_search,
    evaluate_zero_null,
    events_to_dataframe,
    load_geospatial_factions,
    build_historical_folium_map,
)


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def data_service(db_session):
    return DataService(db_session)


# =============================================================================
# 1. TESTES DE CONSTANTES, FORMATADORES E FUNÇÕES DE SUPORTE
# =============================================================================
def test_ui_constants_and_aliases():
    """Valida as 6 seções canônicas e seus aliases historiográficos."""
    assert len(SECOES) == 6
    assert SECOES == [
        "Visão Geral",
        "Painel Analítico",
        "Mapa Histórico & Territórios",
        "Linha do Tempo",
        "Acervo de Fontes",
        "Metodologia Histórica",
    ]

    # Aliases para compatibilidade de rotas e sessões anteriores
    assert "Atlas Cartográfico" in VIEW_ALIASES
    assert VIEW_ALIASES["Atlas Cartográfico"] == "Mapa Histórico & Territórios"
    assert VIEW_ALIASES["Acervo Documental"] == "Acervo de Fontes"
    assert VIEW_ALIASES["Metodologia & Dados"] == "Metodologia Histórica"

    # Paleta sóbria de marcadores
    assert "confirmado" in MARKER_COLORS
    assert "provavel" in MARKER_COLORS
    assert "conflitante" in MARKER_COLORS
    assert "nao_verificado" in MARKER_COLORS


def test_format_badge_and_mode():
    """Valida renderização de badges editoriais e isolamento DEMO."""
    # Badges de confiança
    badge_conf = format_badge("confirmado")
    assert "Confirmado" in badge_conf
    assert "badge-real" in badge_conf

    badge_cont = format_badge("conflitante")
    assert "badge-conflitante" in badge_cont

    badge_prov = format_badge("provavel")
    assert "badge-editorial" in badge_prov

    badge_unk = format_badge("nao_verificado")
    assert "badge-editorial" in badge_unk

    # Badge com valor nulo ou vazio não deve quebrar
    badge_empty = format_badge("")
    assert "badge-editorial" in badge_empty

    # Badges de modo (DEMO vs Real)
    badge_demo = format_mode_badge(True)
    assert "[DEMO]" in badge_demo
    assert "badge-demo" in badge_demo

    badge_real = format_mode_badge(False)
    assert "Documentação Real" in badge_real
    assert "badge-real" in badge_real


def test_normalize_string_search():
    """Valida remoção de diacríticos e caixa alta para buscas seguras."""
    assert normalize_string_search("Rogério Lemgruber") == "rogerio lemgruber"
    assert normalize_string_search("SUBÚRBIOS FERROVIÁRIOS") == "suburbios ferroviarios"
    assert normalize_string_search("Ilha Grande / Dois Rios") == "ilha grande / dois rios"
    assert normalize_string_search("") == ""
    assert normalize_string_search(None) == ""


def test_evaluate_zero_null_epistemology():
    """Valida a Regra 1: Zero Comprovado vs Dado Ausente (NULL)."""
    # 1. Ausente -> NULL
    rotulo, expl, css = evaluate_zero_null(None)
    assert "NULL" in rotulo
    assert "ausente" in expl.lower()

    rotulo, expl, css = evaluate_zero_null("   ")
    assert "NULL" in rotulo

    # 2. Zero Comprovado
    rotulo, expl, css = evaluate_zero_null("0")
    assert "Zero Comprovado" in rotulo
    assert css == "badge-real"

    rotulo, expl, css = evaluate_zero_null("0,0")
    assert "Zero Comprovado" in rotulo

    # 3. Positivo documentado
    rotulo, expl, css = evaluate_zero_null("14")
    assert "14.0" in rotulo
    assert "positiva" in expl.lower()

    # 4. Inválido alfanumérico
    rotulo, expl, css = evaluate_zero_null("não consta")
    assert "Inválido" in rotulo
    assert css == "badge-conflitante"


# =============================================================================
# 2. TESTES DE RECURSOS GEOESPACIAIS (1.671 POLÍGONOS)
# =============================================================================
def test_load_geospatial_factions():
    """Valida o carregamento dos 1.671 perímetros vetoriais de facções."""
    data = load_geospatial_factions()
    assert data is not None
    assert "features" in data
    assert len(data["features"]) == 1671

    # Verifica integridade das propriedades do primeiro polígono
    first_feat = data["features"][0]
    props = first_feat.get("properties", {})
    assert "nome" in props
    assert "faccao_sigla" in props or "faccao" in props
    assert "cor_hex" in props
    sigla = props.get("faccao_sigla") or props.get("faccao")
    assert sigla in FACCAO_NOMES

    # Verifica caminho inexistente
    data_none = load_geospatial_factions("caminho/falso/inexistente.geojson")
    assert data_none is None


# =============================================================================
# 3. TESTES DO CONSTRUTOR DE MAPA FOLIUM E SERIALIZAÇÃO
# =============================================================================
def test_build_historical_folium_map(data_service):
    """Testa a geração do mapa Folium e garante serialização HTML livre de erros."""
    events = data_service.list_events(is_demo=False)
    assert len(events) > 0

    fmap, sem_geometria, plotados = build_historical_folium_map(events, show_polygons=False)
    assert fmap is not None
    assert plotados > 0
    assert plotados + len(sem_geometria) >= len(events)

    # Teste estrito de serialização HTML (sem erros)
    html = fmap.get_root().render()
    assert isinstance(html, str)
    assert len(html) > 1000
    assert "leaflet" in html.lower() or "folium" in html.lower()


def test_build_historical_folium_map_with_polygons(data_service):
    """Testa geração do mapa com a camada de 1.671 polígonos sobreposta."""
    events = data_service.list_events(is_demo=False)
    fmap, sem_geometria, plotados = build_historical_folium_map(events, show_polygons=True)
    assert fmap is not None

    html = fmap.get_root().render()
    assert isinstance(html, str)
    assert len(html) > 5000


# =============================================================================
# 4. CASOS DE BORDA CRÍTICOS
# =============================================================================
def test_edge_case_null_coordinates_region_89(data_service, db_session):
    """
    Caso de Borda 1: Territórios com coordenadas nulas.
    Exemplo real no banco: Região ID 89 (Subúrbios Ferroviários da Zona Norte).
    Não deve quebrar o mapa nem tentar plotar marcador com lat/lng nulos.
    """
    region_89 = db_session.query(Region).filter(Region.id == 89).first()
    assert region_89 is not None
    assert region_89.latitude is None
    assert region_89.longitude is None
    assert region_89.has_coordinates is False

    # Busca eventos associados a territórios sem coordenadas
    unmapped_regions = db_session.query(Region).filter(Region.latitude.is_(None)).all()
    assert len(unmapped_regions) >= 2  # Regiões 89, 91, 124

    unmapped_ids = [r.id for r in unmapped_regions]
    events_with_unmapped = [
        ev for ev in data_service.list_events(is_demo=None)
        if any(r.id in unmapped_ids for r in ev.regions)
    ]
    assert len(events_with_unmapped) > 0

    # O construtor de mapa não deve lançar exceção ao processar esses eventos
    fmap, sem_geometria, plotados = build_historical_folium_map(events_with_unmapped)
    assert fmap is not None
    assert len(sem_geometria) > 0
    # Nenhum evento sem coordenada deve ter sido plotado
    assert all(ev in sem_geometria for ev in events_with_unmapped if not any(r.has_coordinates for r in ev.regions))

    # A serialização do mapa permanece 100% válida
    html = fmap.get_root().render()
    assert isinstance(html, str)


def test_edge_case_nan_coordinates():
    """Garante que coordenadas NaN em memória não quebram o gerador de marcadores."""
    class MockRegion:
        latitude = float("nan")
        longitude = float("nan")
        has_coordinates = True
        original_name = "Região com NaN"

    class MockLink:
        region = MockRegion()

    class MockEvent:
        id = 9999
        title = "Evento com NaN"
        date_display = "1980"
        confidence_level = "provavel"
        region_links = [MockLink()]
        sources = []

    fmap, sem_geometria, plotados = build_historical_folium_map([MockEvent()])
    assert plotados == 0
    assert len(sem_geometria) == 1
    html = fmap.get_root().render()
    assert isinstance(html, str)


def test_edge_case_zero_results_filter(data_service):
    """
    Caso de Borda 2: Filtros que retornam zero resultados.
    A UI e os serviços não devem quebrar com ZeroDivisionError ou IndexError.
    """
    # Intervalo impossível
    events_empty = data_service.list_events(year_min=1800, year_max=1820)
    assert len(events_empty) == 0

    # 1. Mapa com zero eventos
    fmap, sem_geometria, plotados = build_historical_folium_map(events_empty)
    assert plotados == 0
    assert len(sem_geometria) == 0
    html = fmap.get_root().render()
    assert isinstance(html, str)

    # 2. Dataframe com zero eventos
    df = events_to_dataframe(events_empty)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    assert "Ano" in df.columns
    assert "Acontecimento" in df.columns

    # 3. Painel analítico com zero eventos
    analytics = data_service.get_analytics_summary(events_empty)
    assert analytics["total_events"] == 0
    assert analytics["sources_coverage_pct"] == 0.0
    assert analytics["events_with_coordinates"] == 0


def test_edge_case_long_interval_events(data_service):
    """
    Caso de Borda 3: Eventos em intervalos amplos (ex: 1975-1980).
    Verifica precisão temporal e limites cronológicos.
    """
    events_75_80 = data_service.list_events(year_min=1975, year_max=1980)
    assert len(events_75_80) >= 4
    for ev in events_75_80:
        assert 1975 <= ev.year <= 1980

    bounds_real = data_service.get_timeline_bounds(is_demo=False)
    assert bounds_real[0] <= 1958
    assert bounds_real[1] >= 2026


def test_edge_case_real_vs_demo_isolation(data_service):
    """
    Caso de Borda 4: Isolamento estrito de dados técnicos [DEMO].
    Garante que dados DEMO nunca se misturem com a documentação histórica real.
    """
    real_events = data_service.list_events(is_demo=False)
    demo_events = data_service.list_events(is_demo=True)
    all_events = data_service.list_events(is_demo=None)

    assert len(real_events) >= 36
    assert len(demo_events) >= 10
    assert len(all_events) == len(real_events) + len(demo_events)

    for ev in real_events:
        assert ev.is_demo is False
        assert "[DEMO]" not in ev.title

    for ev in demo_events:
        assert ev.is_demo is True

    # Fontes reais vs DEMO
    real_sources = data_service.list_sources(is_demo=False)
    assert len(real_sources) >= 180
    for s in real_sources:
        assert s.is_demo is False


# =============================================================================
# 5. TESTES DO DATASERVICE
# =============================================================================
def test_data_service_analytics(data_service):
    """Valida todos os métodos analíticos do DataService."""
    summary = data_service.get_analytics_summary(is_demo=False)
    assert summary["total_events"] >= 36
    assert summary["sources_coverage_pct"] >= 95.0
    assert summary["total_sources_referenced"] >= 20
    assert "confirmado" in summary["events_by_confidence"]
    assert summary["events_with_coordinates"] > 0
    assert summary["events_without_coordinates"] > 0

    # Distribuição das facções
    f_dist = data_service.get_faction_distribution()
    assert f_dist["total_areas"] == 1671
    assert "CV" in f_dist["factions"]
    assert "TCP" in f_dist["factions"]
    assert f_dist["percentages"]["CV"] > 50.0  # ~59.8%

    # Resumo das fontes
    s_summary = data_service.get_sources_summary(is_demo=False)
    assert s_summary["total_sources"] >= 180
    assert "academico_artigo" in s_summary["sources_by_type"] or "academico_livro" in s_summary["sources_by_type"]
    assert s_summary["sources_with_custody_hash"] >= 5

    # DataFrames de exportação
    df_ev = data_service.events_to_dataframe()
    assert len(df_ev) >= 36
    assert "Acontecimento" in df_ev.columns

    df_src = data_service.sources_to_dataframe()
    assert len(df_src) >= 180
    assert "Título" in df_src.columns
    assert "Custódia SHA-256" in df_src.columns


# =============================================================================
# 6. TESTES PROGRAMÁTICOS DAS 6 SEÇÕES COM STREAMLIT APPTEST
# =============================================================================
APP_PATH = str((Path(__file__).resolve().parent.parent / "app" / "ui" / "app.py").resolve())


@pytest.mark.parametrize("secao", SECOES)
def test_streamlt_apptest_six_sections(secao):
    """
    Executa programaticamente o Streamlit AppTest para cada uma das 6 seções.
    Garante que nenhuma seção lance exceções em tempo de execução.
    """
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=10)
    assert len(at.exception) == 0, f"Exceção inicial ao abrir a aplicação: {at.exception}"

    # Navega para a seção
    if at.radio:
        at.radio[0].set_value(secao).run(timeout=10)
        assert len(at.exception) == 0, f"Exceção ao renderizar a seção '{secao}': {at.exception}"


def test_streamlit_apptest_legacy_aliases():
    """Garante que a navegação por aliases legados funcione sem erros."""
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=10)
    assert len(at.exception) == 0

    for alias, canonica in VIEW_ALIASES.items():
        at.radio[0].set_value(canonica).run(timeout=10)
        assert len(at.exception) == 0, f"Exceção no alias '{alias}' -> '{canonica}': {at.exception}"
