# -*- coding: utf-8 -*-
"""
Design System Moderno: Obsidian / Cyber-OSINT
=============================================
Interface de alta resolução inspirada em plataformas de inteligência investigativa
e jornalismo geoespacial (Bellingcat, NYT Visual Investigations, Palantir).

Características:
- Paleta profunda Dark Mode Obsidian (#0B0F17 / #111827)
- Superfícies em Glassmorphism translúcido com desfoque de fundo (backdrop-filter)
- Bordas sutis (#1F2937 / #374151) com realces dinâmicos de luz e hover
- Tipografia hierárquica híbrida: Títulos editoriais serifados (Libre Baskerville / Merriweather)
  e métricas de alta densidade em JetBrains Mono / Inter
- Badges de grupos armados e status com emissão luminosa suave (glow effect):
  * CV: Vermelho #EF4444
  * TCP: Azul #3B82F6
  * ADA: Verde #10B981
  * Milícia: Cinza #6B7280
  * Oficial / Estado: Roxo #8B5CF6
- Scrollbars táticas customizadas e microinterações com transições suaves (0.2s cubic-bezier)
"""

from typing import Dict, Any, Optional

try:
    import streamlit as st
except ImportError:
    st = None  # Permite importação e inspeção de CSS fora de ambiente Streamlit


# =============================================================================
# PALETA CANÔNICA MODERNA
# =============================================================================

FACTION_COLORS_MODERN: Dict[str, Dict[str, str]] = {
    "CV": {
        "name": "Comando Vermelho",
        "color": "#EF4444",
        "bg": "rgba(239, 68, 68, 0.14)",
        "border": "rgba(239, 68, 68, 0.45)",
        "glow": "rgba(239, 68, 68, 0.35)",
    },
    "TCP": {
        "name": "Terceiro Comando Puro",
        "color": "#3B82F6",
        "bg": "rgba(59, 130, 246, 0.14)",
        "border": "rgba(59, 130, 246, 0.45)",
        "glow": "rgba(59, 130, 246, 0.35)",
    },
    "ADA": {
        "name": "Amigos dos Amigos",
        "color": "#10B981",
        "bg": "rgba(16, 185, 129, 0.14)",
        "border": "rgba(16, 185, 129, 0.45)",
        "glow": "rgba(16, 185, 129, 0.35)",
    },
    "MIL": {
        "name": "Milícia Geral",
        "color": "#6B7280",
        "bg": "rgba(107, 114, 128, 0.16)",
        "border": "rgba(107, 114, 128, 0.45)",
        "glow": "rgba(107, 114, 128, 0.25)",
    },
    "LJ": {
        "name": "Liga da Justiça / Campo Grande",
        "color": "#64748B",
        "bg": "rgba(100, 116, 139, 0.16)",
        "border": "rgba(100, 116, 139, 0.45)",
        "glow": "rgba(100, 116, 139, 0.25)",
    },
    "MNI": {
        "name": "Milícia de Nova Iguaçu",
        "color": "#78716C",
        "bg": "rgba(120, 113, 108, 0.16)",
        "border": "rgba(120, 113, 108, 0.45)",
        "glow": "rgba(120, 113, 108, 0.25)",
    },
    "OFICIAL": {
        "name": "Forças de Segurança / Estado",
        "color": "#8B5CF6",
        "bg": "rgba(139, 92, 246, 0.14)",
        "border": "rgba(139, 92, 246, 0.45)",
        "glow": "rgba(139, 92, 246, 0.35)",
    },
    "NEU": {
        "name": "Área Neutra / Disputada",
        "color": "#94A3B8",
        "bg": "rgba(148, 163, 184, 0.12)",
        "border": "rgba(148, 163, 184, 0.35)",
        "glow": "rgba(148, 163, 184, 0.20)",
    },
}

EVIDENCE_LEVELS_MODERN: Dict[str, Dict[str, str]] = {
    "A": {
        "label": "Nível A · Oficial / Judicial",
        "short_label": "NÍVEL A",
        "color": "#10B981",
        "bg": "rgba(16, 185, 129, 0.15)",
        "border": "#10B981",
        "glow": "rgba(16, 185, 129, 0.30)",
        "description": "Peças judiciais transitadas, inquéritos e denúncias do GAECO/MPRJ.",
    },
    "B": {
        "label": "Nível B · Acadêmico / Estatístico",
        "short_label": "NÍVEL B",
        "color": "#3B82F6",
        "bg": "rgba(59, 130, 246, 0.15)",
        "border": "#3B82F6",
        "glow": "rgba(59, 130, 246, 0.30)",
        "description": "Pesquisas acadêmicas revisadas por pares, GENI/UFF, ISP-RJ.",
    },
    "C": {
        "label": "Nível C · Imprensa Investigativa",
        "short_label": "NÍVEL C",
        "color": "#F59E0B",
        "bg": "rgba(245, 158, 11, 0.15)",
        "border": "#F59E0B",
        "glow": "rgba(245, 158, 11, 0.30)",
        "description": "Hemeroteca histórica checada e fontes jornalísticas corroboradas.",
    },
    "conflitante": {
        "label": "Controvérsia Historiográfica",
        "short_label": "DIVERGÊNCIA",
        "color": "#EF4444",
        "bg": "rgba(239, 68, 68, 0.15)",
        "border": "#EF4444",
        "glow": "rgba(239, 68, 68, 0.30)",
        "description": "Versões contraditórias registradas de modo explícito.",
    },
}

STATUS_COLORS_MODERN: Dict[str, Dict[str, str]] = {
    "confirmado": {"color": "#10B981", "bg": "rgba(16, 185, 129, 0.12)", "border": "#10B981"},
    "provavel": {"color": "#3B82F6", "bg": "rgba(59, 130, 246, 0.12)", "border": "#3B82F6"},
    "conflitante": {"color": "#EF4444", "bg": "rgba(239, 68, 68, 0.12)", "border": "#EF4444"},
    "nao_verificado": {"color": "#6B7280", "bg": "rgba(107, 114, 128, 0.12)", "border": "#6B7280"},
}


# =============================================================================
# GERADOR DE FOLHA DE ESTILOS CSS
# =============================================================================

def get_modern_css(theme: str = "dark") -> str:
    """
    Retorna o CSS compilado do tema Obsidian / Cyber-OSINT de alta resolução.
    Suporta 'dark' (padrão de inteligência investigativa) e 'light' (modo claro contemporâneo).
    """
    is_dark = (theme.lower() != "light")

    if is_dark:
        bg_canvas = "#0B0F17"
        bg_surface = "#111827"
        bg_surface_elevated = "#1F2937"
        bg_glass = "rgba(17, 24, 39, 0.85)"
        bg_glass_hover = "rgba(31, 41, 55, 0.90)"
        bg_card_inner = "rgba(11, 15, 23, 0.65)"
        border_subtle = "#1F2937"
        border_medium = "#374151"
        border_highlight = "rgba(255, 255, 255, 0.12)"
        text_primary = "#F9FAFB"
        text_secondary = "#9CA3AF"
        text_tertiary = "#6B7280"
        sidebar_bg = "#0D131F"
        sidebar_border = "#1E293B"
        scrollbar_track = "#0B0F17"
        scrollbar_thumb = "#1F2937"
        scrollbar_hover = "#374151"
        accent_action = "#3B82F6"
        accent_action_hover = "#2563EB"
        glow_primary = "rgba(59, 130, 246, 0.25)"
    else:
        bg_canvas = "#F8FAFC"
        bg_surface = "#FFFFFF"
        bg_surface_elevated = "#F1F5F9"
        bg_glass = "rgba(255, 255, 255, 0.90)"
        bg_glass_hover = "rgba(248, 250, 252, 0.95)"
        bg_card_inner = "rgba(241, 245, 249, 0.70)"
        border_subtle = "#E2E8F0"
        border_medium = "#CBD5E1"
        border_highlight = "rgba(0, 0, 0, 0.08)"
        text_primary = "#0F172A"
        text_secondary = "#475569"
        text_tertiary = "#94A3B8"
        sidebar_bg = "#F1F5F9"
        sidebar_border = "#E2E8F0"
        scrollbar_track = "#F8FAFC"
        scrollbar_thumb = "#CBD5E1"
        scrollbar_hover = "#94A3B8"
        accent_action = "#2563EB"
        accent_action_hover = "#1D4ED8"
        glow_primary = "rgba(37, 99, 235, 0.15)"

    return f"""
/* ==========================================================================
   ATLAS HISTÓRICO — DESIGN SYSTEM OBSIDIAN / CYBER-OSINT MODERNO
   ========================================================================== */

@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300;1,400&family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');

:root {{
    --bg-canvas: {bg_canvas};
    --bg-surface: {bg_surface};
    --bg-surface-elevated: {bg_surface_elevated};
    --bg-glass: {bg_glass};
    --bg-glass-hover: {bg_glass_hover};
    --bg-card-inner: {bg_card_inner};
    --border-subtle: {border_subtle};
    --border-medium: {border_medium};
    --border-highlight: {border_highlight};
    --text-primary: {text_primary};
    --text-secondary: {text_secondary};
    --text-tertiary: {text_tertiary};
    --accent-blue: #3B82F6;
    --accent-cyan: #06B6D4;
    --accent-red: #EF4444;
    --accent-emerald: #10B981;
    --accent-purple: #8B5CF6;
    --accent-amber: #F59E0B;
    --accent-action: {accent_action};
    --accent-action-hover: {accent_action_hover};
    --glow-primary: {glow_primary};
}}

/* ==========================================================================
   CONTAINER PRINCIPAL E ESTRUTURA GERAL
   ========================================================================== */

.stApp {{
    background-color: var(--bg-canvas) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    line-height: 1.6 !important;
    -webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
}}

.main .block-container {{
    max-width: 1440px !important;
    margin: 0 auto !important;
    padding-top: 1.25rem !important;
    padding-bottom: 3.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}}

/* Tipografia Hierárquica */
h1, h2, h3, h4, .serif-font {{
    font-family: 'Libre Baskerville', 'Merriweather', Georgia, serif !important;
    letter-spacing: -0.015em !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
}}

.mono-font {{
    font-family: 'JetBrains Mono', monospace !important;
}}

p, li, span {{
    color: var(--text-secondary);
}}

b, strong {{
    color: var(--text-primary);
    font-weight: 600;
}}

/* ==========================================================================
   SCROLLBARS TÁTICAS MODERNAS
   ========================================================================== */

::-webkit-scrollbar {{
    width: 7px;
    height: 7px;
}}

::-webkit-scrollbar-track {{
    background: {scrollbar_track};
}}

::-webkit-scrollbar-thumb {{
    background: {scrollbar_thumb};
    border-radius: 4px;
    border: 1px solid var(--border-subtle);
}}

::-webkit-scrollbar-thumb:hover {{
    background: {scrollbar_hover};
}}

/* ==========================================================================
   SIDEBAR OBSIDIAN
   ========================================================================== */

section[data-testid="stSidebar"] {{
    background-color: {sidebar_bg} !important;
    border-right: 1px solid {sidebar_border} !important;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.45) !important;
}}

section[data-testid="stSidebar"] * {{
    color: var(--text-primary) !important;
}}

section[data-testid="stSidebar"] .stRadio label {{
    font-size: 0.90rem !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    transition: color 0.15s ease-in-out;
}}

section[data-testid="stSidebar"] .stRadio label:hover {{
    color: #FFFFFF !important;
}}

/* ==========================================================================
   GLASSMORPHISM & CARTÕES MODERNOS
   ========================================================================== */

.glass-card {{
    background: var(--bg-glass);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 1.35rem 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 24px -2px rgba(0, 0, 0, 0.55), inset 0 1px 0 var(--border-highlight);
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}}

.glass-card:hover {{
    border-color: var(--border-medium);
    box-shadow: 0 10px 32px -4px rgba(0, 0, 0, 0.70), inset 0 1px 0 rgba(255, 255, 255, 0.15);
    transform: translateY(-2px);
}}

.glass-card-glow-blue:hover {{
    border-color: rgba(59, 130, 246, 0.6);
    box-shadow: 0 8px 30px -4px rgba(59, 130, 246, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15);
}}

.glass-card-glow-emerald:hover {{
    border-color: rgba(16, 185, 129, 0.6);
    box-shadow: 0 8px 30px -4px rgba(16, 185, 129, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15);
}}

.glass-card-glow-red:hover {{
    border-color: rgba(239, 68, 68, 0.6);
    box-shadow: 0 8px 30px -4px rgba(239, 68, 68, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15);
}}

/* ==========================================================================
   BADGES COM GLOW LUMINOSO (FACÇÕES E STATUS)
   ========================================================================== */

.badge-pill {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-radius: 9999px;
    transition: all 0.2s ease-in-out;
}}

/* Facções */
.badge-cv {{
    background: rgba(239, 68, 68, 0.14);
    color: #EF4444 !important;
    border: 1px solid rgba(239, 68, 68, 0.45);
    box-shadow: 0 0 10px rgba(239, 68, 68, 0.25);
}}

.badge-tcp {{
    background: rgba(59, 130, 246, 0.14);
    color: #3B82F6 !important;
    border: 1px solid rgba(59, 130, 246, 0.45);
    box-shadow: 0 0 10px rgba(59, 130, 246, 0.25);
}}

.badge-ada {{
    background: rgba(16, 185, 129, 0.14);
    color: #10B981 !important;
    border: 1px solid rgba(16, 185, 129, 0.45);
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.25);
}}

.badge-mil {{
    background: rgba(107, 114, 128, 0.16);
    color: #9CA3AF !important;
    border: 1px solid rgba(156, 163, 175, 0.45);
    box-shadow: 0 0 8px rgba(107, 114, 128, 0.20);
}}

.badge-oficial {{
    background: rgba(139, 92, 246, 0.14);
    color: #A78BFA !important;
    border: 1px solid rgba(139, 92, 246, 0.45);
    box-shadow: 0 0 10px rgba(139, 92, 246, 0.25);
}}

.badge-neu {{
    background: rgba(148, 163, 184, 0.12);
    color: #94A3B8 !important;
    border: 1px solid rgba(148, 163, 184, 0.35);
}}

/* Níveis de Evidência */
.badge-nivel-a {{
    background: rgba(16, 185, 129, 0.15);
    color: #34D399 !important;
    border: 1px solid rgba(16, 185, 129, 0.50);
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.25);
}}

.badge-nivel-b {{
    background: rgba(59, 130, 246, 0.15);
    color: #60A5FA !important;
    border: 1px solid rgba(59, 130, 246, 0.50);
    box-shadow: 0 0 10px rgba(59, 130, 246, 0.25);
}}

.badge-nivel-c {{
    background: rgba(245, 158, 11, 0.15);
    color: #FBBF24 !important;
    border: 1px solid rgba(245, 158, 11, 0.50);
    box-shadow: 0 0 10px rgba(245, 158, 11, 0.25);
}}

.badge-conflito {{
    background: rgba(239, 68, 68, 0.16);
    color: #F87171 !important;
    border: 1px solid rgba(239, 68, 68, 0.50);
    box-shadow: 0 0 10px rgba(239, 68, 68, 0.25);
}}

/* Status de Postura (Claims) */
.stance-apoia-modern {{
    color: #10B981 !important;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
}}

.stance-contesta-modern {{
    color: #EF4444 !important;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
}}

.stance-matiza-modern {{
    color: #F59E0B !important;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
}}

/* ==========================================================================
   CONTROLES E ELEMENTOS DO STREAMLIT (OVERRIDE ELEGANTE)
   ========================================================================== */

/* Métricas Nativas */
div[data-testid="stMetric"] {{
    background: var(--bg-glass) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    padding: 14px 18px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
    transition: all 0.2s ease-in-out !important;
}}

div[data-testid="stMetric"]:hover {{
    border-color: var(--border-medium) !important;
    transform: translateY(-1px) !important;
}}

div[data-testid="stMetric"] label {{
    color: var(--text-tertiary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
    color: #FFFFFF !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 1.6rem !important;
}}

/* Botões Modernos */
.stButton > button {{
    background: linear-gradient(180deg, rgba(31, 41, 55, 0.9) 0%, rgba(17, 24, 39, 0.95) 100%) !important;
    color: #F9FAFB !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 8px 20px !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.35) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}}

.stButton > button:hover {{
    border-color: var(--accent-blue) !important;
    color: #FFFFFF !important;
    box-shadow: 0 0 16px var(--glow-primary), 0 4px 14px rgba(0, 0, 0, 0.5) !important;
    transform: translateY(-1px) !important;
}}

.stButton > button:active {{
    background: var(--accent-action) !important;
    transform: translateY(0px) !important;
}}

/* Inputs, Selectbox e Multiselect */
.stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stMultiSelect div[data-baseweb="select"] > div {{
    background-color: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.90rem !important;
}}

.stTextInput input:focus, .stSelectbox div[data-baseweb="select"] > div:focus-within {{
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 12px var(--glow-primary) !important;
}}

.stSelectbox div[data-baseweb="select"] span {{
    color: var(--text-primary) !important;
}}

.stSelectbox label, .stTextInput label, .stSlider label, .stMultiSelect label {{
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
}}

/* Expanders */
div[data-testid="stExpander"] {{
    background: var(--bg-glass) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    margin-bottom: 0.75rem !important;
}}

div[data-testid="stExpander"]:hover {{
    border-color: var(--border-medium) !important;
}}

/* Tabs Modernas */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    border-bottom: 1px solid var(--border-subtle) !important;
    background: transparent !important;
    padding-bottom: 2px;
}}

.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    border: none !important;
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    border-radius: 6px 6px 0 0 !important;
    transition: all 0.15s ease-in-out !important;
}}

.stTabs [data-baseweb="tab"]:hover {{
    color: #FFFFFF !important;
    background: rgba(255, 255, 255, 0.03) !important;
}}

.stTabs [aria-selected="true"] {{
    color: var(--accent-cyan) !important;
    border-bottom: 2px solid var(--accent-cyan) !important;
    font-weight: 600 !important;
}}

/* Alertas & Infos */
.stAlert {{
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
}}

/* Radar Pulse Animation */
@keyframes radar-pulse {{
    0% {{
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }}
    70% {{
        transform: scale(1);
        box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
    }}
    100% {{
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }}
}}

.radar-dot {{
    width: 8px;
    height: 8px;
    background-color: #10B981;
    border-radius: 50%;
    display: inline-block;
    animation: radar-pulse 2s infinite cubic-bezier(0.4, 0, 0.6, 1);
}}

/* ==========================================================================
   COMPATIBILIDADE COM SELETORES HISTÓRICOS / DOSSIÊS EXISTENTES
   ========================================================================== */

.editorial-header {{
    border-bottom: 1px solid rgba(255, 255, 255, 0.10);
    padding-bottom: 1.4rem;
    margin-bottom: 1.6rem;
}}

.editorial-kicker {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: #60A5FA;
    margin-bottom: 0.4rem;
}}

.editorial-title {{
    font-size: 2.2rem;
    color: #FFFFFF;
    margin: 0 0 0.5rem 0;
    line-height: 1.2;
}}

.editorial-lead {{
    font-size: 1.02rem;
    color: #94A3B8;
    max-width: 85ch;
    margin-bottom: 1rem;
}}

.editorial-stats-band {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 1.2rem;
    padding: 0.75rem 0;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    font-size: 0.90rem;
    color: #CBD5E1;
}}

.editorial-stats-band b {{
    color: #38BDF8;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.05rem;
}}

.editorial-stats-band .sep {{
    color: #475569;
}}

.archive-dossier {{
    background-color: var(--bg-glass);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--border-subtle);
    border-top: 3px solid #3B82F6;
    border-radius: 10px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}}

.archive-tag {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #60A5FA;
    font-weight: 600;
    margin-bottom: 0.3rem;
}}

.archive-title {{
    font-family: 'Libre Baskerville', Georgia, serif;
    font-size: 1.3rem;
    color: #FFFFFF;
    margin-bottom: 0.6rem;
    line-height: 1.3;
}}

.source-citation-block {{
    background-color: rgba(11, 15, 23, 0.75);
    border-left: 3px solid #3B82F6;
    border-radius: 0 8px 8px 0;
    padding: 0.9rem 1.1rem;
    margin-top: 0.8rem;
    margin-bottom: 0.8rem;
    font-size: 0.9rem;
    color: #CBD5E1;
}}

.source-excerpt {{
    font-family: 'Merriweather', 'Libre Baskerville', Georgia, serif;
    font-style: italic;
    color: #E2E8F0;
    background: rgba(17, 24, 39, 0.6);
    border-left: 2px solid #374151;
    padding: 0.6rem 0.9rem;
    margin: 0.6rem 0;
    font-size: 0.88rem;
    line-height: 1.55;
}}

.source-meta {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem;
    color: #94A3B8;
}}

.claim-box {{
    background-color: rgba(17, 24, 39, 0.75);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-top: 0.6rem;
    font-size: 0.88rem;
}}

.badge-editorial {{
    display: inline-block;
    padding: 2px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border: 1px solid #374151;
    border-radius: 4px;
    background: rgba(31, 41, 55, 0.8);
    color: #E5E7EB;
}}

.badge-real {{
    background-color: rgba(16, 185, 129, 0.15) !important;
    color: #34D399 !important;
    border-color: rgba(16, 185, 129, 0.45) !important;
    box-shadow: 0 0 8px rgba(16, 185, 129, 0.2);
}}

.badge-demo {{
    background-color: rgba(245, 158, 11, 0.15) !important;
    color: #FBBF24 !important;
    border-color: rgba(245, 158, 11, 0.45) !important;
}}

.badge-conflitante {{
    background-color: rgba(239, 68, 68, 0.15) !important;
    color: #F87171 !important;
    border-color: rgba(239, 68, 68, 0.45) !important;
    box-shadow: 0 0 8px rgba(239, 68, 68, 0.2);
}}

.timeline-node {{
    position: relative;
    padding-left: 1.8rem;
    margin-bottom: 1.8rem;
    border-left: 2px solid #374151;
}}

.timeline-node::before {{
    content: "";
    position: absolute;
    left: -6px;
    top: 4px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: #3B82F6;
    border: 2px solid #0B0F17;
    box-shadow: 0 0 8px rgba(59, 130, 246, 0.6);
}}

.timeline-year {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    color: #60A5FA;
}}

.timeline-title {{
    font-family: 'Libre Baskerville', Georgia, serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0.2rem 0;
}}

.timeline-meta {{
    font-size: 0.85rem;
    color: #94A3B8;
}}

.ethical-notice {{
    background-color: rgba(17, 24, 39, 0.85);
    border-left: 4px solid #3B82F6;
    border-radius: 0 8px 8px 0;
    padding: 0.9rem 1.2rem;
    font-size: 0.85rem;
    color: #94A3B8;
    margin-top: 2rem;
    line-height: 1.5;
}}
"""


# =============================================================================
# INJETOR DE TEMA
# =============================================================================

def apply_modern_theme(theme: str = "dark") -> None:
    """
    Injeta a folha de estilos CSS de alto impacto na aplicação Streamlit.

    Args:
        theme: 'dark' (Modo Obsidian / Cyber-OSINT, recomendado) ou 'light'.
    """
    css = get_modern_css(theme=theme)
    if st is not None and hasattr(st, "markdown"):
        st.markdown(f"<style>\n{css}\n</style>", unsafe_allow_html=True)
