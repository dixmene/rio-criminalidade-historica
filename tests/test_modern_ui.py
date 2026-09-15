# -*- coding: utf-8 -*-
"""
Suíte de Testes Automatizados para o Módulo de Design e Componentes Modernos.
Valida:
1. `app.ui.styles.modern_theme`:
   - Geração de CSS Obsidian / Cyber-OSINT (fundo escuro #0B0F17, glassmorphism, badges com glow, scrollbars, fontes)
   - Injeção segura via `apply_modern_theme`
   - Paletas canônicas de facções, níveis de evidência e status
2. `app.ui.components.modern_ui`:
   - `render_hero_header`: Título, subtítulo de impacto e as 4 badges tecnológicas (WebGL 60 FPS, 100% Auditável, 69 Snapshots, Zero Alucinação)
   - `render_kpi_dashboard`: Grid moderno dos 5 indicadores obrigatórios com progress bars e deltas
   - `render_event_card`: Selos de evidência, facções com cores (#EF4444, #3B82F6, #10B981, #6B7280, #8B5CF6), datação, citação literal OSINT e SHA-256
   - Robustez e tratamento defensivo (objetos do banco, dicts e campos nulos)
"""

import pytest
from app.database import SessionLocal
from app.services import DataService
from app.ui.styles.modern_theme import (
    apply_modern_theme,
    get_modern_css,
    FACTION_COLORS_MODERN,
    EVIDENCE_LEVELS_MODERN,
    STATUS_COLORS_MODERN,
)
from app.ui.components.modern_ui import (
    render_hero_header,
    render_kpi_dashboard,
    render_event_card,
    _detect_faction_key,
    _infer_evidence_level_fallback,
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
# 1. TESTES DO TEMA E FOLHA DE ESTILOS CSS
# =============================================================================

def test_modern_theme_css_dark():
    """Valida especificações do Dark Mode Obsidian no CSS gerado."""
    css = get_modern_css(theme="dark")
    assert isinstance(css, str)
    assert len(css) > 1000

    # Cores Obsidian canônicas
    assert "#0B0F17" in css
    assert "#111827" in css
    assert "rgba(17, 24, 39, 0.85)" in css

    # Tipografia hierárquica
    assert "Libre Baskerville" in css
    assert "JetBrains Mono" in css
    assert "Inter" in css

    # Glassmorphism e Scrollbars
    assert "backdrop-filter" in css
    assert "::-webkit-scrollbar" in css
    assert "::-webkit-scrollbar-thumb" in css

    # Badges de facções com emissão de luz / glow
    assert "badge-cv" in css
    assert "#EF4444" in css  # CV Vermelho
    assert "badge-tcp" in css
    assert "#3B82F6" in css  # TCP Azul
    assert "badge-ada" in css
    assert "#10B981" in css  # ADA Verde
    assert "badge-mil" in css
    assert "#6B7280" in css or "#9CA3AF" in css  # Milícia Cinza
    assert "badge-oficial" in css
    assert "#8B5CF6" in css or "#A78BFA" in css  # Oficial Roxo


def test_modern_theme_css_light():
    """Valida que o gerador de CSS suporta modo claro sem exceções."""
    css_light = get_modern_css(theme="light")
    assert isinstance(css_light, str)
    assert "#F8FAFC" in css_light
    assert "#FFFFFF" in css_light


def test_apply_modern_theme_execution():
    """Garante que a função apply_modern_theme execute com sucesso."""
    apply_modern_theme("dark")
    apply_modern_theme("light")


def test_faction_palette_definitions():
    """Valida as especificações de cores das principais facções e forças estatais."""
    assert FACTION_COLORS_MODERN["CV"]["color"] == "#EF4444"
    assert FACTION_COLORS_MODERN["TCP"]["color"] == "#3B82F6"
    assert FACTION_COLORS_MODERN["ADA"]["color"] == "#10B981"
    assert FACTION_COLORS_MODERN["MIL"]["color"] == "#6B7280"
    assert FACTION_COLORS_MODERN["OFICIAL"]["color"] == "#8B5CF6"

    # Presença de glow e bg translúcido
    for f_key in ["CV", "TCP", "ADA", "MIL", "OFICIAL"]:
        assert "glow" in FACTION_COLORS_MODERN[f_key]
        assert "bg" in FACTION_COLORS_MODERN[f_key]
        assert "border" in FACTION_COLORS_MODERN[f_key]


# =============================================================================
# 2. TESTES DO HERO HEADER
# =============================================================================

def test_render_hero_header():
    """Valida a renderização e conteúdo do banner de topo investigativo."""
    html = render_hero_header()
    assert isinstance(html, str)

    # Título e subtítulo de impacto
    assert "Atlas Histórico da Criminalidade no Rio de Janeiro" in html
    assert "Plataforma científica de inteligência geoespacial" in html

    # As 4 badges tecnológicas obrigatórias
    assert "WebGL 60 FPS" in html
    assert "100% Auditável" in html
    assert "69 Snapshots Anuais" in html
    assert "Zero Alucinação" in html

    # Status operacional ativo
    assert "SISTEMA ATIVO" in html
    assert "radar-dot" in html


# =============================================================================
# 3. TESTES DO DASHBOARD DE KPIS
# =============================================================================

def test_render_kpi_dashboard_default():
    """Valida os 5 cartões de KPI modernos em grid com valores padrão."""
    html = render_kpi_dashboard()
    assert isinstance(html, str)

    # 1. Territórios Mapeados (1.671 polígonos)
    assert "Territórios Mapeados" in html
    assert "1.671" in html
    assert "Polígonos Vetoriais" in html

    # 2. Acontecimentos Históricos Catalogados (53+ eventos verificados)
    assert "Acontecimentos Históricos" in html
    assert "53+" in html
    assert "Eventos Verificados" in html

    # 3. Fontes e Documentos Auditados (291 fontes com citação literal)
    assert "Fontes e Documentos Auditados" in html
    assert "291" in html
    assert "Citação Literal 100%" in html

    # 4. Acervo Audiovisual (100+ documentários com minutagem e transcrição)
    assert "Acervo Audiovisual" in html
    assert "100+" in html
    assert "Minutagem e Transcrição" in html

    # 5. Integridade Cartográfica (14/14 checagens aprovadas - 100%)
    assert "Integridade Cartográfica" in html
    assert "100%" in html
    assert "14/14 Checagens" in html

    # Estrutura visual: Glassmorphism e barras de progresso
    assert "glass-card" in html
    assert "linear-gradient" in html


def test_render_kpi_dashboard_custom_stats():
    """Valida a injeção de estatísticas customizadas no painel de KPIs."""
    custom = {
        "territorios": "1.750",
        "eventos": "65",
        "fontes": "320",
        "audiovisual": "115",
        "integridade": "100%",
    }
    html = render_kpi_dashboard(custom)
    assert "1.750" in html
    assert "65" in html
    assert "320" in html
    assert "115" in html


# =============================================================================
# 4. TESTES DO EVENT CARD MODERNO
# =============================================================================

def test_detect_faction_key():
    """Valida o mapeamento heurístico de siglas e nomes para cores."""
    assert _detect_faction_key("Comando Vermelho") == "CV"
    assert _detect_faction_key("CV") == "CV"
    assert _detect_faction_key("Terceiro Comando Puro") == "TCP"
    assert _detect_faction_key("TCP") == "TCP"
    assert _detect_faction_key("Amigos dos Amigos") == "ADA"
    assert _detect_faction_key("Milícia da Zona Oeste") == "MIL"
    assert _detect_faction_key("Liga da Justiça (LJ)") == "LJ"
    assert _detect_faction_key("Milícia de Nova Iguaçu") == "MNI"
    assert _detect_faction_key("BOPE / PMERJ") == "OFICIAL"
    assert _detect_faction_key("Território Desconhecido") == "NEU"


def test_render_event_card_dict():
    """Valida renderização de cartão moderno a partir de dicionário."""
    mock_ev = {
        "id": 101,
        "title": "Apreensão Histórica e Conflito Territorial",
        "date_display": "14 de Julho de 1985",
        "temporal_precision": "dia",
        "confidence_level": "confirmado",
        "description": "Operação documentada com confronto armado.",
        "historical_context": "Transição democrática e reorganização policial.",
        "is_demo": False,
        "organizations": [{"original_name": "Comando Vermelho", "acronym": "CV"}],
        "regions": [{"original_name": "Morro do Alemão"}],
        "claims": [
            {
                "statement": "Houve apreensão de armamento de uso restrito.",
                "source_links": [
                    {
                        "stance": "apoia",
                        "excerpt": "A incursão policial apreendeu fuzis e munições em depósito clandestino.",
                        "section": "Boletim Interno nº 142",
                        "source": {
                            "title": "Inquérito Policial nº 32/85",
                            "author": "Polícia Civil do Estado do Rio de Janeiro",
                            "file_hash_sha256": "c0ffee1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                            "source_type": "oficial_inquerito",
                        },
                    }
                ],
            }
        ],
    }

    html = render_event_card(mock_ev)
    assert isinstance(html, str)

    # Identificação do evento
    assert "Apreensão Histórica e Conflito Territorial" in html
    assert "14 de Julho de 1985" in html
    assert "REGISTRO ID: #101" in html

    # Facção com badge luminoso CV
    assert "badge-cv" in html
    assert "Comando Vermelho" in html

    # Selo de Evidência Nível A
    assert "NÍVEL A" in html or "badge-nivel-a" in html

    # Citação literal OSINT
    assert "CITAÇÃO LITERAL COMPROBATÓRIA" in html
    assert "A incursão policial apreendeu fuzis" in html
    assert "Boletim Interno nº 142" in html
    assert "SHA-256: c0ffee1234567890" in html


def test_render_event_card_db_model(data_service):
    """Valida renderização de cartão a partir de instância real do SQLAlchemy Event."""
    events = data_service.list_events(is_demo=False)
    assert len(events) > 0

    first_event = events[0]
    html = render_event_card(first_event)
    assert isinstance(html, str)
    assert len(html) > 200
    assert first_event.title in html
    assert str(first_event.date_display) in html
    assert f"#{first_event.id}" in html


def test_render_event_card_edge_cases():
    """Valida comportamento defensivo para entradas nulas ou vazias."""
    # 1. Evento None
    assert render_event_card(None) == ""

    # 2. Evento mínimo com campos nulos
    empty_ev = {
        "id": 999,
        "title": None,
        "date_display": None,
        "description": None,
        "confidence_level": None,
        "historical_context": None,
        "organizations": [],
        "regions": [],
    }
    html = render_event_card(empty_ev)
    assert isinstance(html, str)
    assert "REGISTRO ID: #999" in html
    assert "badge-pill" in html
