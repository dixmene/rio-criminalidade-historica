# -*- coding: utf-8 -*-
"""
Atlas Histórico da Criminalidade no Rio de Janeiro (1950–2026)
Conceito: Atlas Editorial / Centro de Pesquisa Histórica / Publicação Digital

Direção Artística:
- Paleta clara inspirada em papel/acervo: Fundo #F5F3EE, Superfícies #FFFFFF, Texto #20201E.
- Cor de Destaque: Vinho histórico / Terracota #7A2E2E (substituindo o azul neon de SaaS).
- Tipografia: Serifada editorial (Libre Baskerville / Cormorant) para títulos e sans-serif neutra (Source Sans / Inter) para dados.
- O Mapa e o Tempo como protagonistas da investigação.
- Ficha Arquivística de proveniência com citações literais e controvérsias historiográficas (Claims).
- Regra inegociável ZERO ≠ NULL e isolamento estrito de dados técnicos [DEMO].
"""

import sys
import json
import math
import hashlib
import unicodedata
from pathlib import Path
from collections import Counter
from typing import Optional, List, Tuple, Any

# -----------------------------------------------------------------------------
# Resolução de Namespace e sys.path
# -----------------------------------------------------------------------------
_current_dir = str(Path(__file__).resolve().parent)
_root_dir = str(Path(__file__).resolve().parent.parent.parent)

while _current_dir in sys.path:
    sys.path.remove(_current_dir)

if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

if "app" in sys.modules and not hasattr(sys.modules["app"], "__path__"):
    del sys.modules["app"]

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import pydeck as pdk

from app.database import SessionLocal, engine, Base
from app.services import EventService, DataService
from app.config import DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM
from app.map import (
    build_historical_folium_map as app_map_build_historical_folium_map,
    build_pydeck_map,
    load_faction_polygons,
    load_aisp_polygons,
    load_bairros_polygons,
    load_aisp_dataframe,
    load_bairros_dataframe,
    MAP_TILES,
    EVIDENCE_LEVELS,
)
from scripts.classifier_pautas import classify_legislative_text, TAXONOMIA_PAUTAS_SENSIVEIS

# Garante criação de tabelas em ambientes efêmeros
Base.metadata.create_all(bind=engine)

st.set_page_config(
    page_title="Atlas Histórico da Criminalidade no Rio de Janeiro (1950–2026)",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# DESIGN SYSTEM — ATLAS EDITORIAL (Papel Claro & Vinho Histórico)
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Source+Sans+3:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg-canvas: #F5F3EE;
        --bg-surface: #FFFFFF;
        --bg-subtle: #EBE7DF;
        --border-subtle: #D8D3C9;
        --border-strong: #B5AEA0;
        --text-primary: #1C1B18;
        --text-secondary: #5A564F;
        --text-tertiary: #827D72;
        --accent-action: #7A2E2E;
        --accent-action-hover: #5C2222;
        --accent-subtle: #F7EBEB;
        --status-error-text: #9E2A2B;
        --status-error-bg: #FDF2F2;
        --status-success-text: #2D5A27;
        --status-success-bg: #F0F6F0;
        --status-warning-text: #8C580E;
        --status-warning-bg: #FEF9EE;
    }

    /* Travamento do contêiner principal para evitar espalhamento em monitores ultrawide */
    .main .block-container {
        max-width: 1280px;
        margin: 0 auto;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }

    /* Fundo e tipografia geral */
    .stApp {
        background-color: var(--bg-canvas);
        color: var(--text-primary);
        font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.6;
    }

    h1, h2, h3, h4, .serif-font {
        font-family: 'Libre Baskerville', Georgia, serif;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.01em;
    }

    /* Sidebar com estética de fichário de arquivo */
    section[data-testid="stSidebar"] {
        background-color: #EDEAE2;
        border-right: 1px solid #D8D3C9;
        padding-top: 1.5rem;
    }
    section[data-testid="stSidebar"] * {
        color: #20201E;
    }
    section[data-testid="stSidebar"] .stRadio label {
        font-size: 0.92rem;
        font-weight: 500;
        color: #3A3833;
    }

    /* Cabeçalho Editorial */
    .editorial-header {
        border-bottom: 2px solid #D8D3C9;
        padding-bottom: 1.4rem;
        margin-bottom: 1.6rem;
    }
    .editorial-kicker {
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: #7A2E2E;
        margin-bottom: 0.4rem;
    }
    .editorial-title {
        font-size: 2.2rem;
        color: #20201E;
        margin: 0 0 0.5rem 0;
        line-height: 1.2;
    }
    .editorial-lead {
        font-size: 1.05rem;
        color: #5A564F;
        max-width: 75ch;
        margin-bottom: 1rem;
    }

    /* Faixa Estatística Editorial */
    .editorial-stats-band {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 1.2rem;
        padding: 0.75rem 0;
        border-top: 1px solid #D8D3C9;
        border-bottom: 1px solid #D8D3C9;
        font-size: 0.92rem;
        color: #4A4740;
    }
    .editorial-stats-band b {
        color: #7A2E2E;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.05rem;
    }
    .editorial-stats-band .sep {
        color: #B5B0A4;
    }

    /* Ficha Arquivística (Painel de Evidência) */
    .archive-dossier {
        background-color: #FFFFFF;
        border: 1px solid #D8D3C9;
        border-top: 3px solid #7A2E2E;
        border-radius: 2px;
        padding: 1.4rem 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .archive-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #7A2E2E;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .archive-title {
        font-family: 'Libre Baskerville', Georgia, serif;
        font-size: 1.3rem;
        color: #20201E;
        margin-bottom: 0.6rem;
        line-height: 1.3;
    }

    /* Fontes e Citações Literais */
    .source-citation-block {
        background-color: #FAF9F5;
        border-left: 3px solid #7A2E2E;
        padding: 0.9rem 1.1rem;
        margin-top: 0.8rem;
        margin-bottom: 0.8rem;
        font-size: 0.9rem;
        color: #33312B;
    }
    .source-excerpt {
        font-family: 'Libre Baskerville', Georgia, serif;
        font-style: italic;
        color: #20201E;
        background: #FFFFFF;
        border-left: 2px solid #D8D3C9;
        padding: 0.6rem 0.9rem;
        margin: 0.6rem 0;
        font-size: 0.88rem;
        line-height: 1.55;
    }
    .source-meta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #6F6B63;
    }

    /* Claims e Posturas Historiográficas */
    .claim-box {
        background-color: #FAF8F5;
        border: 1px solid #E5E0D8;
        padding: 0.75rem 1rem;
        margin-top: 0.6rem;
        font-size: 0.88rem;
    }
    .stance-apoia {
        color: #2D5A27;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
    }
    .stance-contesta {
        color: #8C2D2D;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
    }
    .stance-matiza {
        color: #8C6A1E;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
    }

    /* Badges Sóbrias */
    .badge-editorial {
        display: inline-block;
        padding: 2px 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        border: 1px solid #D8D3C9;
        border-radius: 2px;
        background: #FFFFFF;
        color: #3A3833;
    }
    .badge-real {
        background-color: #EAF2E8;
        color: #1E4620;
        border-color: #C2DCC0;
    }
    .badge-demo {
        background-color: #FCF4E6;
        color: #7D4C0A;
        border-color: #EED4A8;
    }
    .badge-conflitante {
        background-color: #F8ECEC;
        color: #7A2E2E;
        border-color: #E6C2C2;
    }

    /* Linha do Tempo Editorial */
    .timeline-node {
        position: relative;
        padding-left: 1.8rem;
        margin-bottom: 1.8rem;
        border-left: 2px solid #D8D3C9;
    }
    .timeline-node::before {
        content: "";
        position: absolute;
        left: -6px;
        top: 4px;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #7A2E2E;
        border: 2px solid #F5F3EE;
    }
    .timeline-year {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        font-weight: 700;
        color: #7A2E2E;
    }
    .timeline-title {
        font-family: 'Libre Baskerville', Georgia, serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #20201E;
        margin: 0.2rem 0;
    }
    .timeline-meta {
        font-size: 0.85rem;
        color: #6F6B63;
    }

    /* Aviso Ético de Rodapé */
    .ethical-notice {
        background-color: #EDEAE2;
        border-left: 4px solid #7A2E2E;
        padding: 0.9rem 1.2rem;
        font-size: 0.85rem;
        color: #4A4740;
        margin-top: 2rem;
        line-height: 1.5;
    }

    /* Formulários e Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #D8D3C9 !important;
        color: #1C1B18 !important;
        border-radius: 3px !important;
    }
    .stSelectbox div[data-baseweb="select"] span {
        color: #1C1B18 !important;
    }
    .stSelectbox label, .stTextInput label, .stSlider label {
        color: #1C1B18 !important;
        font-family: 'Source Sans 3', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    /* Botões editoriais explícitos com alto contraste */
    .stButton > button {
        background-color: #FFFFFF !important;
        color: #1C1B18 !important;
        border: 1px solid #B5AEA0 !important;
        border-radius: 3px !important;
        font-family: 'Source Sans 3', sans-serif !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
        transition: all 0.15s ease-in-out !important;
    }
    .stButton > button:hover {
        background-color: #F7EBEB !important;
        border-color: #7A2E2E !important;
        color: #7A2E2E !important;
    }
    .stButton > button:active {
        background-color: #7A2E2E !important;
        color: #FFFFFF !important;
    }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #D8D3C9;
        border-radius: 2px;
        padding: 10px 14px;
    }
    div[data-testid="stMetric"] label {
        color: #6F6B63 !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        text-transform: uppercase;
    }
    div[data-testid="stMetric"] div {
        color: #20201E !important;
        font-family: 'Libre Baskerville', serif;
    }
</style>
""", unsafe_allow_html=True)

# As 6 Seções do Site
SECOES = [
    "Visão Geral",
    "Painel Analítico",
    "Mapa Histórico & Territórios",
    "Linha do Tempo",
    "Acervo de Fontes",
    "Metodologia Histórica",
]

VIEW_ALIASES = {
    "Atlas Cartográfico": "Mapa Histórico & Territórios",
    "Acervo Documental": "Acervo de Fontes",
    "Metodologia & Dados": "Metodologia Histórica",
}

CONFIDENCE_STYLES = {
    "confirmado": ("Confirmado", "badge-real"),
    "provavel": ("Provável", "badge-editorial"),
    "conflitante": ("Conflitante (Divergência)", "badge-conflitante"),
    "nao_verificado": ("Não Verificado", "badge-editorial"),
}

MARKER_COLORS = {
    "confirmado": "darkgreen",
    "provavel": "cadetblue",
    "conflitante": "darkred",
    "nao_verificado": "gray",
}

FACCAO_NOMES = {
    "CV": "Comando Vermelho (CV)",
    "TCP": "Terceiro Comando Puro (TCP)",
    "ADA": "Amigos dos Amigos (ADA)",
    "MIL": "Milícia Geral",
    "LJ": "Liga da Justiça / Campo Grande",
    "MNI": "Milícia de Nova Iguaçu",
    "NEU": "Área Neutra / Disputada",
}


# =============================================================================
# Carregamento de Recursos Geoespaciais e Funções de Suporte
# =============================================================================
@st.cache_data
def load_geospatial_factions(path: Optional[str] = None):
    return load_faction_polygons(path)


@st.cache_data
def load_corregedoria_data() -> Optional[dict]:
    p = Path("database/ocorrencias_corregedoria.json")
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


@st.cache_data
def load_locais_votacao_data() -> Optional[pd.DataFrame]:
    p = Path("database/locais_votacao_rio.parquet")
    if p.exists():
        return pd.read_parquet(p, engine="pyarrow")
    return None


@st.cache_data
def load_proposicoes_data() -> Optional[pd.DataFrame]:
    p = Path("database/proposicoes_legislativas.csv")
    if p.exists():
        return pd.read_csv(p)
    return None


def format_badge(confidence: str) -> str:
    label, css = CONFIDENCE_STYLES.get((confidence or "").lower(), ((confidence or "Indefinido").capitalize(), "badge-editorial"))
    return f'<span class="badge-editorial {css}">{label}</span>'


def format_mode_badge(is_demo: bool) -> str:
    if is_demo:
        return '<span class="badge-editorial badge-demo">Registro de Teste [DEMO]</span>'
    return '<span class="badge-editorial badge-real">Documentação Real</span>'


def normalize_string_search(text: str) -> str:
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acento.lower().strip()


def evaluate_zero_null(raw_val: str):
    """REGRA 1 — Zero Comprovado vs. Desconhecido (NULL)."""
    if raw_val is None or raw_val.strip() == "":
        return "NULL (Dado Desconhecido)", "Dado ausente na fonte documental. Deve persistir estritamente como NULL no banco.", "badge-editorial"
    try:
        num = float(raw_val.replace(",", "."))
    except ValueError:
        return "Inválido", "Valor alfanumérico não interpretável como contagem factual.", "badge-conflitante"
    if num == 0:
        return "0 (Zero Comprovado)", "A fonte atesta expressamente que o fenômeno não ocorreu ou contagem foi zero.", "badge-real"
    return f"{num} (Valor Numérico)", f"Contagem positiva documentada: {num}.", "badge-editorial"


def events_to_dataframe(events) -> pd.DataFrame:
    cols = ["Ano", "Data Documentada", "Acontecimento", "Territórios", "Organizações", "Fontes", "Claims", "Confiabilidade", "Origem"]
    if not events:
        return pd.DataFrame(columns=cols)

    rows = []
    for ev in events:
        rows.append({
            "Ano": ev.year if ev.year else "S/D",
            "Data Documentada": ev.date_display,
            "Acontecimento": ev.title,
            "Territórios": ", ".join(r.original_name for r in ev.regions) or "Geral / Não delimitado",
            "Organizações": ", ".join(o.original_name for o in ev.organizations) or "—",
            "Fontes": len(ev.sources) if hasattr(ev, "sources") else len(getattr(ev, "source_links", [])),
            "Claims": len(ev.claims) if hasattr(ev, "claims") else 0,
            "Confiabilidade": ev.confidence_level.capitalize() if ev.confidence_level else "—",
            "Origem": "DEMO" if ev.is_demo else "Real",
        })
    return pd.DataFrame(rows)


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
    Constrói o mapa Folium de forma determinística, isolada e testável programaticamente.
    Delega para app.map.builder mantendo 100% de retrocompatibilidade com a suíte de testes.
    """
    return app_map_build_historical_folium_map(
        events=events,
        show_polygons=show_polygons,
        show_aisp=show_aisp,
        show_bairros=show_bairros,
        theme=theme,
        geo_data=geo_data,
        aisp_data=aisp_data,
        bairros_data=bairros_data
    )


# =============================================================================
# Barra Lateral Sóbria de Pesquisa
# =============================================================================
def render_archival_sidebar(service, current_view):
    st.sidebar.markdown("""
    <div style="padding-bottom: 0.8rem; border-bottom: 1px solid #D8D3C9; margin-bottom: 1rem;">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #7A2E2E; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em;">Projeto de Pesquisa</div>
        <div style="font-family: 'Libre Baskerville', serif; font-size: 1.15rem; font-weight: 700; color: #20201E;">Atlas Histórico RJ</div>
        <div style="font-size: 0.8rem; color: #6F6B63;">Evolução Territorial & Criminalidade</div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<div style='font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#7A2E2E; letter-spacing:0.08em; margin-bottom:0.3rem;'>Seções do Acervo</div>", unsafe_allow_html=True)

    # Mapeia aliases legados para as 6 seções canônicas
    if current_view in VIEW_ALIASES:
        current_view = VIEW_ALIASES[current_view]

    default_idx = SECOES.index(current_view) if current_view in SECOES else 0

    selected_view = st.sidebar.radio(
        "Navegação",
        SECOES,
        index=default_idx,
        key="nav_view",
        label_visibility="collapsed"
    )

    st.sidebar.markdown("<div style='margin-top: 1.2rem; border-top: 1px solid #D8D3C9; padding-top: 1rem;'></div>", unsafe_allow_html=True)

    if selected_view == "Visão Geral":
        return selected_view, None

    # Filtros de Pesquisa Histórica
    st.sidebar.markdown("<div style='font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#7A2E2E; letter-spacing:0.08em; margin-bottom:0.6rem;'>Recorte Histórico</div>", unsafe_allow_html=True)

    # Modo de Isolamento
    modo_dados = st.sidebar.radio(
        "Acervo:",
        options=["Dados Históricos Reais", "Incluir Registros de Teste [DEMO]", "Apenas Testes [DEMO]"],
        index=0,
        help="Garante que dados técnicos de demonstração nunca se misturem silenciosamente com a documentação histórica real."
    )
    if modo_dados == "Dados Históricos Reais":
        is_demo = False
    elif modo_dados == "Apenas Testes [DEMO]":
        is_demo = True
    else:
        is_demo = None

    # Slider Temporal defensivo
    min_b, max_b = service.get_timeline_bounds(is_demo=is_demo)
    if min_b >= max_b:
        max_b = min_b + 1

    intervalo_anos = st.sidebar.slider(
        "Período de Análise:",
        min_value=min_b,
        max_value=max_b,
        value=(min_b, max_b),
        step=1
    )

    # Território
    regioes = service.list_regions(is_demo=is_demo)
    regiao_opcoes = {"Todos os Territórios": None}
    regiao_opcoes.update({r.original_name: r.id for r in regioes})
    sel_regiao = regiao_opcoes[st.sidebar.selectbox("Filtro Territorial:", list(regiao_opcoes.keys()))]

    # Organização
    orgs = service.list_organizations(is_demo=is_demo)
    org_opcoes = {"Todas as Organizações": None}
    org_opcoes.update({
        (f"{o.original_name} ({o.acronym})" if o.acronym else o.original_name): o.id
        for o in orgs
    })
    sel_org = org_opcoes[st.sidebar.selectbox("Organização / Força Policial:", list(org_opcoes.keys()))]

    # Nível de Validação da Evidência
    conf_opcoes = {
        "Todas as Validações": None,
        "Confirmado documentalmente": "confirmado",
        "Provável / Em apuração": "provavel",
        "Conflitante (Controvérsia)": "conflitante",
        "Não verificado": "nao_verificado",
    }
    sel_conf = conf_opcoes[st.sidebar.selectbox("Grau de Certeza:", list(conf_opcoes.keys()))]

    busca = st.sidebar.text_input("Busca Textual:", placeholder="Ex: Ilha Grande, BOPE, Le Cocq...")

    filtros = {
        "is_demo": is_demo,
        "years": intervalo_anos,
        "region_id": sel_regiao,
        "org_id": sel_org,
        "confidence": sel_conf,
        "search": busca.strip() if busca else None
    }
    return selected_view, filtros


# =============================================================================
# SEÇÃO 1 — VISÃO GERAL (Apresentação Editorial)
# =============================================================================
def render_view_overview(service):
    n_real = service.count_real_events()
    n_demo = service.count_demo_events()
    n_sources = len(service.list_sources(is_demo=False))
    n_regions = len(service.list_regions(is_demo=False))
    n_orgs = len(service.list_organizations(is_demo=False))
    n_people = len(service.list_people(is_demo=False))
    n_claims = len(service.list_claims()) if hasattr(service, "list_claims") else 0

    st.markdown(f"""
    <div class="editorial-header">
        <div class="editorial-kicker">Observatório Documental · 1950—2026</div>
        <h1 class="editorial-title">Atlas Histórico da Criminalidade no Rio de Janeiro</h1>
        <p class="editorial-lead">
            Publicação científica, historiográfica e geográfica sobre as dinâmicas territoriais,
            organizações armadas, facções prisionais, contravenção e políticas de segurança pública no Estado do Rio de Janeiro.
        </p>
        <div class="editorial-stats-band">
            <span><b>{n_real}</b> acontecimentos documentados</span>
            <span class="sep">·</span>
            <span><b>{n_sources}</b> fontes catalogadas</span>
            <span class="sep">·</span>
            <span><b>{n_people}</b> figuras históricas</span>
            <span class="sep">·</span>
            <span><b>1.671</b> perímetros cartográficos</span>
            <span class="sep">·</span>
            <span><b>100%</b> com citação literal</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_left, c_right = st.columns([3, 2])

    with c_left:
        st.markdown("### Escopo da Pesquisa Histórica")
        st.markdown("""
        Este atlas é estruturado como um **acervo de evidências primárias e secundárias**, no qual nenhum acontecimento
        entra na base sem sustentação em fonte verificável (inquérito judicial, relatório oficial de segurança pública,
        pesquisa acadêmica revisada por pares ou hemeroteca contemporânea).

        #### Pilares da Metodologia:
        1. **Rigor Epistemológico**: Não inferimos liderança, controle territorial nem casualidades sem referência expressa.
        2. **Intervalos de Conhecimento**: O tempo é tratado com rigor (datas exatas para dias conhecidos; limites de intervalo para anos e décadas).
        3. **Afirmações Atômicas e Controvérsias (Claims)**: Quando versões divergem (ex.: relatório policial versus hemeroteca investigativa),
           o atlas não escolhe um lado: registra ambas as versões com suas posturas (*apoia*, *contesta*, *matiza*).
        4. **Regra ZERO ≠ NULL**: Diferenciamos expressamente ausência de dado (*NULL*) de contagem zero (*0 comprovado*).
        """)

        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("Painel Analítico →", use_container_width=True):
                st.session_state.nav_view = "Painel Analítico"
                st.rerun()
        with col_btn2:
            if st.button("Mapa & Territórios →", use_container_width=True):
                st.session_state.nav_view = "Mapa Histórico & Territórios"
                st.rerun()
        with col_btn3:
            if st.button("Linha do Tempo →", use_container_width=True):
                st.session_state.nav_view = "Linha do Tempo"
                st.rerun()

    with c_right:
        st.markdown("### Síntese do Acervo")
        st.markdown(f"""
        <div class="archive-dossier">
            <div class="archive-tag">Indicadores do Corpus Ativo</div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 10px;">
                <div>
                    <div style="font-size:0.8rem; color:#6F6B63;">Acontecimentos Reais</div>
                    <div style="font-family:'Libre Baskerville',serif; font-size:1.4rem; color:#7A2E2E; font-weight:700;">{n_real}</div>
                </div>
                <div>
                    <div style="font-size:0.8rem; color:#6F6B63;">Claims Atomizados</div>
                    <div style="font-family:'Libre Baskerville',serif; font-size:1.4rem; color:#20201E; font-weight:700;">{n_claims}</div>
                </div>
                <div>
                    <div style="font-size:0.8rem; color:#6F6B63;">Fontes Bibliográficas</div>
                    <div style="font-family:'Libre Baskerville',serif; font-size:1.4rem; color:#20201E; font-weight:700;">{n_sources}</div>
                </div>
                <div>
                    <div style="font-size:0.8rem; color:#6F6B63;">Polígonos Vetoriais</div>
                    <div style="font-family:'Libre Baskerville',serif; font-size:1.4rem; color:#20201E; font-weight:700;">1.671</div>
                </div>
            </div>
            <div style="border-top: 1px solid #D8D3C9; margin-top: 14px; padding-top: 10px; font-size: 0.82rem; color: #5A564F;">
                Recorte cronológico coberto: <b>1958 — 2026</b> (68 anos de transformações institucionais documentadas).
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="ethical-notice">
            <b>Cláusula Ética de Responsabilidade</b><br>
            Projeto estritamente historiográfico, antropológico e de sociologia da violência.
            Não constitui ferramenta operacional, não realiza predição de incidentes futuros e não monitora ações em tempo real.
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# SEÇÃO 2 — PAINEL ANALÍTICO (Estatísticas Estruturadas e Controle Territorial)
# =============================================================================
def render_view_analytics(service, events, filtros):
    st.markdown("""
    <div style="margin-bottom: 1.4rem;">
        <h2 style="margin: 0; font-size: 1.6rem;">Painel Analítico Historiográfico</h2>
        <div style="font-size: 0.9rem; color: #6F6B63;">Análise quantitativa, distribuição espacial das facções e métricas de sustentação documental.</div>
    </div>
    """, unsafe_allow_html=True)

    data_service = service if hasattr(service, "get_analytics_summary") else DataService(service.db)
    analytics = data_service.get_analytics_summary(events)
    faction_dist = data_service.get_faction_distribution()

    # Faixa Resumo de Indicadores
    st.markdown(f"""
    <div class="editorial-stats-band" style="margin-bottom: 1.4rem;">
        <span><b>{analytics['total_events']}</b> acontecimentos no recorte</span>
        <span class="sep">·</span>
        <span><b>{len(analytics['events_by_region'])}</b> territórios documentados</span>
        <span class="sep">·</span>
        <span><b>{len(analytics['events_by_organization'])}</b> organizações mapeadas</span>
        <span class="sep">·</span>
        <span><b>{analytics['total_sources_referenced']}</b> fontes vinculadas</span>
        <span class="sep">·</span>
        <span><b>{analytics['total_claims']}</b> claims registrados</span>
    </div>
    """, unsafe_allow_html=True)

    if not events:
        st.info("Nenhum registro encontrado para os filtros selecionados. Ajuste os filtros na barra lateral para visualizar as métricas analíticas.")
        return

    tab_cronologia, tab_faccoes, tab_confianca, tab_territorios = st.tabs([
        "Evolução Cronológica",
        "Grupos Armados & Facções",
        "Grau de Certeza & Claims",
        "Topografia da Violência"
    ])

    with tab_cronologia:
        st.markdown("### Acontecimentos por Década")
        st.caption("Distribuição dos fatos catalogados ao longo do recorte histórico.")

        decades_data = analytics["events_by_decade"]
        if decades_data:
            df_dec = pd.DataFrame([
                {"Década": f"Anos {k}" if isinstance(k, (int, float)) else str(k), "Acontecimentos": v}
                for k, v in decades_data.items()
            ])
            st.bar_chart(df_dec.set_index("Década"), color="#7A2E2E")
            st.dataframe(df_dec, use_container_width=True, hide_index=True)

    with tab_faccoes:
        st.markdown("### Presença Territorial dos Grupos Armados")
        st.caption("Distribuição das 1.671 áreas e favelas mapeadas no Estado do Rio de Janeiro (base vetorial aberta).")

        if faction_dist["total_areas"] > 0:
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            cv_count = faction_dist["factions"].get("CV", 0)
            cv_pct = faction_dist["percentages"].get("CV", 0)
            tcp_count = faction_dist["factions"].get("TCP", 0)
            tcp_pct = faction_dist["percentages"].get("TCP", 0)
            lj_count = faction_dist["factions"].get("LJ", 0)
            lj_pct = faction_dist["percentages"].get("LJ", 0)
            ada_count = faction_dist["factions"].get("ADA", 0)
            ada_pct = faction_dist["percentages"].get("ADA", 0)

            col_f1.metric("Comando Vermelho (CV)", f"{cv_count}", f"{cv_pct}%")
            col_f2.metric("Terceiro Comando Puro (TCP)", f"{tcp_count}", f"{tcp_pct}%")
            col_f3.metric("Liga da Justiça (LJ)", f"{lj_count}", f"{lj_pct}%")
            col_f4.metric("Amigos dos Amigos (ADA)", f"{ada_count}", f"{ada_pct}%")

            df_faccoes = pd.DataFrame([
                {
                    "Grupo Armado": FACCAO_NOMES.get(k, k),
                    "Sigla": k,
                    "Áreas Mapeadas": v,
                    "Proporção": f"{faction_dist['percentages'].get(k, 0)}%"
                }
                for k, v in sorted(faction_dist["factions"].items(), key=lambda x: x[1], reverse=True)
            ])
            st.dataframe(df_faccoes, use_container_width=True, hide_index=True)

        st.markdown("#### Organizações mais Citadas nos Eventos do Recorte")
        orgs_data = analytics["events_by_organization"]
        if orgs_data:
            df_orgs = pd.DataFrame([
                {"Organização / Força Policial": k, "Acontecimentos Documentados": v}
                for k, v in orgs_data.items()
            ])
            st.dataframe(df_orgs, use_container_width=True, hide_index=True)

    with tab_confianca:
        st.markdown("### Avaliação Epistemológica de Confiabilidade")
        st.caption("Nível de sustentação probatória conforme critérios arquivísticos.")

        conf_data = analytics["events_by_confidence"]
        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        c_m1.metric("Confirmados", conf_data.get("confirmado", 0))
        c_m2.metric("Prováveis", conf_data.get("provavel", 0))
        c_m3.metric("Conflitantes", conf_data.get("conflitante", 0))
        c_m4.metric("Não Verificados", conf_data.get("nao_verificado", 0))

        st.markdown(f"""
        <div class="archive-dossier" style="margin-top: 15px;">
            <div class="archive-tag">Sustentação por Fontes Primárias e Secundárias</div>
            <p style="margin-top: 6px; font-size: 0.9rem; color: #33312B;">
                <b>{analytics['sources_coverage_pct']}%</b> dos eventos do recorte possuem sustentação em citação documental literal.<br>
                <b>{analytics['total_claims']}</b> proposições historiográficas registradas, sendo <b>{analytics['disputed_claims']}</b> com divergência explícita (controvérsia documental entre fontes).
            </p>
        </div>
        """, unsafe_allow_html=True)

    with tab_territorios:
        st.markdown("### Territórios mais Frequentes na Documentação")
        st.caption("Concentração espacial dos fatos históricos com base no acervo.")

        reg_data = analytics["events_by_region"]
        if reg_data:
            df_reg = pd.DataFrame([
                {"Território": k, "Acontecimentos": v}
                for k, v in reg_data.items()
            ])
            st.dataframe(df_reg, use_container_width=True, hide_index=True)

        st.markdown(f"""
        <div class="archive-dossier" style="margin-top: 15px;">
            <div class="archive-tag">Regra 1: Precisão Cartográfica vs Coordenadas Nulas</div>
            <p style="margin-top: 6px; font-size: 0.88rem; color: #4A4740;">
                Eventos com georreferenciamento pontual: <b>{analytics['events_with_coordinates']}</b><br>
                Eventos em territórios gerais/difusos (coordenadas estritamente NULL): <b>{analytics['events_without_coordinates']}</b><br>
                <i>Não inventamos coordenadas: ausência de demarcação física oficial é preservada como NULL.</i>
            </p>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# SEÇÃO 3 — MAPA HISTÓRICO & TERRITÓRIOS (O Mapa como Carro-Chefe)
# =============================================================================
def render_view_map(service, events, filtros):
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="margin: 0; font-size: 1.6rem;">Mapa Histórico & Territórios</h2>
        <div style="font-size: 0.9rem; color: #6F6B63;">Mapeamento geoespacial de acontecimentos documentados, inspeção territorial, malhas oficiais (AISP e Bairros) e perímetros faccionais.</div>
    </div>
    """, unsafe_allow_html=True)

    tab_mapa, tab_inspecao, tab_batalhoes, tab_corregedoria, tab_eleitoral, tab_legislativo = st.tabs([
        "🗺️ Atlas Cartográfico (Carro-Chefe)",
        "🔍 Inspeção Territorial (1.671 Áreas)",
        "🛡️ Batalhões PMERJ & AISP (39 Áreas)",
        "⚖️ Atos da Corregedoria & GAECO",
        "🗳️ Cruzamento Eleitoral (TSE x AISP)",
        "📜 Pautas Sensíveis no Legislativo"
    ])

    with tab_mapa:
        # Controles de Visualização no Topo do Mapa
        st.markdown("<div style='font-size:0.8rem; font-weight:700; text-transform:uppercase; color:#7A2E2E; letter-spacing:0.08em; margin-bottom:0.4rem;'>Painel de Controle Cartográfico</div>", unsafe_allow_html=True)
        c_ctrl1, c_ctrl2, c_ctrl3 = st.columns([1.5, 1.5, 2])

        with c_ctrl1:
            tema_mapa = st.selectbox(
                "Tema Visual (Basemap):",
                options=["dark", "light", "osm"],
                format_func=lambda x: "🌑 Dark Matter (Contraste Tático)" if x == "dark" else ("☀️ Positron (Claro Editorial)" if x == "light" else "🗺️ OpenStreetMap Clássico"),
                index=0,
                help="O mapa escuro (Dark Matter) realça os perímetros de facções e os selos de evidência."
            )

        with c_ctrl2:
            motor_mapa = st.selectbox(
                "Motor de Visualização:",
                options=["Folium (Interativo / Dossiê)", "PyDeck 3D (WebGL / Alta Performance)"],
                index=0,
                help="PyDeck utiliza aceleração por GPU no navegador para visualização vetorial ultrarrápida."
            )

        with c_ctrl3:
            camadas_sel = st.multiselect(
                "Camadas Vetoriais Oficiais:",
                options=["faccoes", "aisp", "bairros"],
                default=["faccoes", "aisp"],
                format_func=lambda x: {
                    "faccoes": "🏴 Perímetros de Controle (1.671 Áreas)",
                    "aisp": "🛡️ Áreas de Batalhões PMERJ (39 AISPs)",
                    "bairros": "🏙️ Malha de Bairros Oficiais (166 Bairros - PCRJ)"
                }.get(x, x)
            )

        # Barra de Playback Histórico
        c_play1, c_play2 = st.columns([3, 1])
        with c_play1:
            anos_disponiveis = [ev.year for ev in events if ev.year is not None]
            min_ano = min(anos_disponiveis) if anos_disponiveis else 1958
            max_ano = max(anos_disponiveis) if anos_disponiveis else 2026
            if min_ano >= max_ano:
                max_ano = min_ano + 1

            playback_teto = st.slider(
                "⏱️ Linha do Tempo Dinâmica (Acontecimentos até o ano selecionado):",
                min_value=min_ano,
                max_value=max_ano,
                value=max_ano,
                step=1,
                help="Mova o controle deslizante para inspecionar o surgimento progressivo de facções e acontecimentos históricos."
            )
        with c_play2:
            st.metric(
                label="Ano Limite",
                value=str(playback_teto),
                delta=f"{len([e for e in events if (e.year or 9999) <= playback_teto])} eventos"
            )

        # Filtrar eventos pelo playback
        events_filtrados_tempo = [e for e in events if (e.year is None or e.year <= playback_teto)]

        c_mapa, c_dossie = st.columns([3, 2])

        with c_mapa:
            exibir_perimetros = "faccoes" in camadas_sel
            exibir_aisp = "aisp" in camadas_sel
            exibir_bairros = "bairros" in camadas_sel

            if motor_mapa == "Folium (Interativo / Dossiê)":
                fmap, sem_geometria, plotados = build_historical_folium_map(
                    events_filtrados_tempo,
                    show_polygons=exibir_perimetros,
                    show_aisp=exibir_aisp,
                    show_bairros=exibir_bairros,
                    theme=tema_mapa
                )
                st_folium(fmap, width="100%", height=580)
            else:
                deck = build_pydeck_map(
                    events_filtrados_tempo,
                    show_factions=exibir_perimetros,
                    show_aisp=exibir_aisp
                )
                if deck:
                    st.pydeck_chart(deck, use_container_width=True)
                else:
                    st.warning("PyDeck não disponível neste ambiente.")
                sem_geometria = [e for e in events_filtrados_tempo if not any(getattr(r.region, "has_coordinates", False) for r in getattr(e, "region_links", []))]
                plotados = len(events_filtrados_tempo) - len(sem_geometria)

            # Legenda Editorial de Evidências e Facções
            st.markdown("""
            <div style="display:flex; flex-wrap:wrap; gap: 12px; font-size: 0.76rem; font-family: 'JetBrains Mono', monospace; background:#F0EDE6; padding:8px 12px; border:1px solid #D8D3C9; border-radius:3px; margin-top: 6px;">
                <span><b>Evidência:</b></span>
                <span style="color:#10B981; font-weight:700;">🟢 Nível A (Oficial/Judicial)</span>
                <span style="color:#3B82F6; font-weight:700;">🔵 Nível B (Acadêmico/ISP)</span>
                <span style="color:#F59E0B; font-weight:700;">🟡 Nível C (Imprensa Histórica)</span>
                <span style="color:#EF4444; font-weight:700;">🔴 Conflitante</span>
                <span style="color:#6F6B63;">|</span>
                <span><b>Domínio:</b></span>
                <span style="color:#E0342C; font-weight:700;">■ CV</span>
                <span style="color:#2FA46B; font-weight:700;">■ TCP</span>
                <span style="color:#EDB72B; font-weight:700;">■ ADA</span>
                <span style="color:#2B5BC7; font-weight:700;">■ Milícias</span>
                <span style="color:#00E5FF; font-weight:700;">- - AISP (PMERJ)</span>
            </div>
            """, unsafe_allow_html=True)

            # Botões de Exportação Direta
            c_exp1, c_exp2 = st.columns(2)
            with c_exp1:
                df_export = events_to_dataframe(events_filtrados_tempo)
                csv_data = df_export.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    "📥 Baixar Acontecimentos Filtrados (CSV)",
                    data=csv_data,
                    file_name=f"rio_historico_eventos_{playback_teto}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with c_exp2:
                # GeoJSON de pontos plotados
                features_pontos = []
                for ev in events_filtrados_tempo:
                    for link in getattr(ev, "region_links", []):
                        r = getattr(link, "region", None)
                        if r and getattr(r, "has_coordinates", False) and r.latitude and r.longitude:
                            features_pontos.append({
                                "type": "Feature",
                                "properties": {
                                    "id": ev.id,
                                    "titulo": ev.title,
                                    "ano": ev.year,
                                    "data": ev.date_display,
                                    "confiabilidade": ev.confidence_level,
                                    "territorio": r.original_name
                                },
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [float(r.longitude), float(r.latitude)]
                                }
                            })
                geo_export_str = json.dumps({"type": "FeatureCollection", "features": features_pontos}, ensure_ascii=False)
                st.download_button(
                    "📥 Baixar GeoJSON de Pontos",
                    data=geo_export_str.encode("utf-8"),
                    file_name=f"rio_historico_pontos_{playback_teto}.geojson",
                    mime="application/geo+json",
                    use_container_width=True
                )

            if sem_geometria:
                with st.expander(f"📍 Acontecimentos sem delimitação pontual cadastrada ({len(sem_geometria)})"):
                    st.caption("Cumprimento estrito da Regra 1: Não inventamos coordenadas geográficas para eventos de abrangência penitenciária ou estadual difusa.")
                    for ev in sem_geometria:
                        st.markdown(f"- **[{ev.date_display}]** {ev.title} *(Território: {', '.join(r.original_name for r in ev.regions) or 'Geral'})*")

        # Coluna Direita: Ficha Arquivística & Dossiê
        with c_dossie:
            st.markdown("<div style='font-size:0.8rem; font-weight:700; text-transform:uppercase; color:#7A2E2E; letter-spacing:0.08em;'>Dossiê do Registro Selecionado</div>", unsafe_allow_html=True)

            if not events_filtrados_tempo:
                st.info("Nenhum registro encontrado para os filtros selecionados.")
            else:
                opcoes_eventos = {f"[{ev.date_display}] {ev.title} (ID {ev.id})": ev.id for ev in events_filtrados_tempo}
                sel_ev_str = st.selectbox("Selecione o acontecimento:", list(opcoes_eventos.keys()), label_visibility="collapsed")
                ev_id = opcoes_eventos[sel_ev_str]
                ev = service.get_event_by_id(ev_id)

                if ev:
                    # Inferencia de Nível de Evidência
                    from app.map.builder import _infer_evidence_level
                    ev_lvl = _infer_evidence_level(ev)
                    ev_info = EVIDENCE_LEVELS.get(ev_lvl, EVIDENCE_LEVELS["C"])

                    st.markdown(f"""
                    <div class="archive-dossier">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <span class="badge-editorial" style="background:{ev_info['color']}; color:#fff; border:none;">{ev_info['label']}</span>
                            <span class="archive-tag">{ev.date_display} · {format_mode_badge(ev.is_demo)}</span>
                        </div>
                        <div class="archive-title">{ev.title}</div>
                        <div style="margin-bottom: 0.8rem;">
                            {format_badge(ev.confidence_level)}
                        </div>
                        <div style="font-size: 0.92rem; color: #20201E; line-height: 1.6; margin-bottom: 0.8rem;">
                            {ev.description}
                        </div>
                        {f"<div style='font-size: 0.85rem; color: #5A564F; font-style: italic; border-left: 2px solid #D8D3C9; padding-left: 8px; margin-bottom: 10px;'>Contexto Histórico: {ev.historical_context}</div>" if ev.historical_context else ""}
                        <div style="font-size: 0.82rem; color: #4A4740; border-top: 1px solid #E5E0D8; padding-top: 8px;">
                            <b>Território:</b> {', '.join(r.original_name for r in ev.regions) or 'Não delimitado'}<br>
                            <b>Organizações:</b> {', '.join(o.original_name for o in ev.organizations) or 'Nenhuma citada'}<br>
                            <b>Pessoas:</b> {', '.join(p.original_name for p in ev.people) or 'Nenhuma citada'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Controvérsias e Claims
                    if hasattr(ev, "claims") and ev.claims:
                        st.markdown("<div style='font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#7A2E2E; letter-spacing:0.08em; margin-top:0.8rem;'>Afirmações Históricas & Divergências (Claims)</div>", unsafe_allow_html=True)
                        for cl in ev.claims:
                            divergencia_aviso = '<span class="badge-editorial badge-conflitante">Divergência Registrada</span>' if cl.is_disputed else ''
                            st.markdown(f"""
                            <div class="claim-box">
                                <b>Proposição:</b> {cl.statement} {divergencia_aviso}<br>
                                {f"<small style='color:#6F6B63;'><i>Nota epistemológica: {cl.epistemological_notes}</i></small><br>" if cl.epistemological_notes else ""}
                            </div>
                            """, unsafe_allow_html=True)
                            for csl in cl.source_links:
                                st_css = f"stance-{csl.stance.lower()}"
                                st.markdown(f"""
                                <div style="margin-left: 14px; font-size: 0.82rem; margin-top: 4px;">
                                    <span class="{st_css}">[{csl.stance.upper()}]</span> <b>{csl.source.title}</b> (p. {csl.page or 'N/A'}):<br>
                                    <span style="font-style:italic; color:#3A3833;">\"{csl.excerpt}\"</span>
                                </div>
                                """, unsafe_allow_html=True)

                    # Fontes e Citações Literais
                    st.markdown("<div style='font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#7A2E2E; letter-spacing:0.08em; margin-top:1rem;'>Fontes Documentais Comprobatórias</div>", unsafe_allow_html=True)
                    if ev.source_links:
                        for idx, sl in enumerate(ev.source_links, start=1):
                            src = sl.source
                            st.markdown(f"""
                            <div class="source-citation-block">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <b>{idx:02d}. {src.title}</b>
                                    {format_badge(sl.validation_status)}
                                </div>
                                <div class="source-meta">
                                    {src.citation}<br>
                                    Tipo: {src.source_type} · Ref: {sl.page_or_section or sl.page or 'N/A'} {f'· Acervo: {src.archive_ref}' if src.archive_ref else ''}
                                </div>
                                <div class="source-excerpt">
                                    \"{sl.excerpt}\"
                                </div>
                                {f"<div style='font-size:0.78rem; color:#6F6B63;'><b>Avaliação Historiográfica:</b> {sl.confidence_notes or sl.assessment_notes}</div>" if (sl.confidence_notes or sl.assessment_notes) else ""}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.error("Alerta: Registro sem sustentação em fonte documentada.")

    with tab_inspecao:
        st.markdown("### Catálogo Territorial & Consulta Vetorial (1.671 Áreas)")
        st.caption("Pesquisa por comunidade, favela ou território histórico nas bases geoespaciais integradas.")

        geo_data = load_geospatial_factions()
        if geo_data:
            fts = geo_data.get("features", [])
            filtro_fac = st.multiselect(
                "Filtrar por Grupo Armado:",
                options=list(FACCAO_NOMES.keys()),
                default=list(FACCAO_NOMES.keys()),
                format_func=lambda x: FACCAO_NOMES.get(x, x)
            )
            busca_comunidade = st.text_input("Buscar Comunidade / Favela:", placeholder="Ex: Rocinha, Alemão, Maré...")

            areas_filtradas = []
            for f in fts:
                props = f.get("properties", {})
                fac = props.get("faccao_sigla") or props.get("faccao") or "NEU"
                nome = props.get("nome", "")
                if fac not in filtro_fac:
                    continue
                if busca_comunidade and normalize_string_search(busca_comunidade) not in normalize_string_search(nome):
                    continue
                areas_filtradas.append({
                    "Comunidade / Favela": nome,
                    "Grupo Armado": props.get("faccao_nome", fac),
                    "Sigla": fac,
                    "Cor": props.get("cor_hex", "#8C97A3"),
                    "Centroide Lat": props.get("centroide_lat", "—"),
                    "Centroide Lng": props.get("centroide_lng", "—"),
                })

            st.markdown(f"**{len(areas_filtradas)}** áreas encontradas.")
            if areas_filtradas:
                st.dataframe(pd.DataFrame(areas_filtradas), use_container_width=True, hide_index=True)

    with tab_batalhoes:
        st.markdown("### Áreas Integradas de Segurança Pública (39 AISPs / Batalhões PMERJ)")
        st.caption("Delimitação geográfica oficial dos batalhões territoriais da Polícia Militar do Estado do Rio de Janeiro.")

        df_aisp = load_aisp_dataframe()
        if df_aisp is not None and not df_aisp.empty:
            c_m1, c_m2, c_m3 = st.columns(3)
            with c_m1:
                st.metric("Total de AISPs Mapeadas", len(df_aisp))
            with c_m2:
                st.metric("RISPs (Regiões Integradas)", len(df_aisp["risp"].dropna().unique()))
            with c_m3:
                st.metric("Municípios Abrangidos", len(df_aisp["municipio"].dropna().unique()))

            busca_batalhao = st.text_input("Buscar por Batalhão, Sede ou Município:", placeholder="Ex: 14º BPM, Bangu, Baixada...")
            if busca_batalhao:
                term = normalize_string_search(busca_batalhao)
                df_aisp_view = df_aisp[
                    df_aisp["batalhao"].str.lower().str.contains(term, na=False) |
                    df_aisp["sede"].str.lower().str.contains(term, na=False) |
                    df_aisp["municipio"].str.lower().str.contains(term, na=False)
                ]
            else:
                df_aisp_view = df_aisp

            cols_view = ["aisp", "batalhao", "sede", "nome_completo", "risp", "municipio", "centroide_lat", "centroide_lon"]
            cols_exist = [c for c in cols_view if c in df_aisp_view.columns]
            st.dataframe(df_aisp_view[cols_exist].sort_values("aisp"), use_container_width=True, hide_index=True)
        else:
            st.info("Arquivo Parquet de AISPs não localizado em data/geospatial/aisps_batalhoes.parquet.")

    with tab_corregedoria:
        st.markdown("### Evidências Formais de Desvios de Conduta & 'Arrego'")
        st.caption("Registros auditados de operações da Corregedoria da PMERJ, GAECO/MPRJ e Polícia Federal com cadeia de custódia (SHA-256).")

        corr_data = load_corregedoria_data()
        if corr_data and "ocorrencias" in corr_data:
            ocorr_list = corr_data["ocorrencias"]
            st.markdown(f"**{len(ocorr_list)} operações e denúncias judicializadas catalogadas com hash de custódia.**")

            for oc in ocorr_list:
                st.markdown(f"""
                <div class="archive-dossier" style="margin-bottom:1rem;">
                    <div style="display:flex; justify-content:space-between;">
                        <span class="badge-editorial badge-real">{oc['id']} · {oc['ano']}</span>
                        <span class="archive-tag">{oc['orgao_investigador']}</span>
                    </div>
                    <div class="archive-title" style="margin:4px 0;">{oc['nome_operacao']}</div>
                    <div style="font-size:0.85rem; color:#7A2E2E; font-weight:700;">
                        Processo Judicial: {oc['processo_judicial']}
                    </div>
                    <div style="font-size:0.9rem; color:#20201E; margin:6px 0;">
                        {oc['descricao']}
                    </div>
                    <div style="font-size:0.82rem; color:#4A4740; background:#F0EDE6; padding:6px; border-radius:2px;">
                        <b>Batalhões/AISP Envolvidos:</b> {', '.join(oc['batalhoes_envolvidos'])}<br>
                        <b>Modalidade Ilícita:</b> {oc['modalidade_ilicita']}<br>
                        <b>Hash SHA-256 de Custódia:</b> <code>{oc['sha256_documento']}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Base de ocorrências da corregedoria não localizada em database/ocorrencias_corregedoria.json.")

    with tab_eleitoral:
        st.markdown("### Cruzamento Eleitoral: Locais de Votação x Batalhões (TSE)")
        st.caption("Spatial Join entre colégios eleitorais e as áreas dos batalhões com cálculo do Índice Herfindahl-Hirschman (HHI) de concentração.")

        df_tse = load_locais_votacao_data()
        if df_tse is not None and not df_tse.empty:
            c_e1, c_e2 = st.columns(2)
            with c_e1:
                currais_count = len(df_tse[df_tse["alerta_curral_eleitoral"] == True])
                st.metric("Locais com Alta Concentração (Suspeita de Curral)", currais_count, f"{round(currais_count/len(df_tse)*100, 1)}% dos locais")
            with c_e2:
                st.metric("Total de Locais Auditados", len(df_tse))

            st.markdown("""
            > [!NOTE]
            > **Cuidado Metodológico**: O índice HHI acima de 6.000 ou votações nominais superiores a 70% em colégios situados em áreas sob hegemonia armada indicam forte assimetria na circulação política, devendo ser interpretados como hipóteses de convergência e não condenações judiciais automáticas.
            """)

            st.dataframe(df_tse, use_container_width=True, hide_index=True)
        else:
            st.info("Base eleitoral do TSE não localizada em database/locais_votacao_rio.parquet.")

    with tab_legislativo:
        st.markdown("### Classificação Temática da Atividade Legislativa (CMRJ / ALERJ)")
        st.caption("Classificador de pautas sensíveis incidentes sobre os mercados de controle territorial armado no Rio de Janeiro.")

        # Testador interativo de classificação
        with st.expander("🧪 Testador Interativo de Pautas Sensíveis (NLP)"):
            st.caption("Cole a ementa de um Projeto de Lei para analisar sua incidência nos 5 eixos temáticos do crime organizado.")
            texto_teste = st.text_area(
                "Ementa ou texto da proposição:",
                value="Dispõe sobre a regularização de transporte alternativo por vans e mototáxis na Zona Oeste."
            )
            if st.button("Classificar Proposição"):
                res_class = classify_legislative_text(texto_teste)
                if res_class["possui_convergencia_sensivel"]:
                    st.success(f"Eixo Identificado: **{res_class['eixo_principal']}** (Score: {res_class['score_convergencia']})")
                    st.markdown(f"**Termos Identificados:** `{', '.join(res_class['termos_identificados'])}`")
                else:
                    st.info("Nenhuma convergência temática sensível identificada (Pauta Administrativa / Geral).")
                st.caption(res_class["cuidado_metodologico"])

        df_leg = load_proposicoes_data()
        if df_leg is not None and not df_leg.empty:
            st.markdown("#### Proposições Coletadas & Classificadas")
            st.dataframe(df_leg, use_container_width=True, hide_index=True)
        else:
            st.info("Base legislativa não localizada em database/proposicoes_legislativas.csv.")


# =============================================================================
# SEÇÃO 4 — LINHA DO TEMPO EDITORIAL
# =============================================================================
def render_view_timeline(service, events):
    st.markdown("""
    <div style="margin-bottom: 1.4rem;">
        <h2 style="margin: 0; font-size: 1.6rem;">Linha do Tempo Cronológica</h2>
        <div style="font-size: 0.9rem; color: #6F6B63;">Evolução contínua dos acontecimentos, rupturas institucionais e transformações territoriais.</div>
    </div>
    """, unsafe_allow_html=True)

    if not events:
        st.info("Nenhum registro para o período e filtros selecionados.")
        return

    # Agrupamento por década
    decadas = {}
    for ev in events:
        dec = (ev.year // 10) * 10 if ev.year else None
        decadas.setdefault(dec, []).append(ev)

    for dec in sorted(decadas.keys(), key=lambda d: (d is None, d)):
        label_dec = f"Década de {dec}" if dec else "Data Indeterminada"
        st.markdown(f"<h3 style='color:#7A2E2E; border-bottom: 1px solid #D8D3C9; padding-bottom: 4px; margin-top: 1.5rem;'>{label_dec}</h3>", unsafe_allow_html=True)

        for ev in decadas[dec]:
            terr_str = ", ".join(r.original_name for r in ev.regions) or "Território Difuso"
            fontes_count = len(ev.sources) if hasattr(ev, "sources") else len(getattr(ev, "source_links", []))
            st.markdown(f"""
            <div class="timeline-node">
                <div class="timeline-year">{ev.date_display} · {format_badge(ev.confidence_level)} {format_mode_badge(ev.is_demo)}</div>
                <div class="timeline-title">{ev.title}</div>
                <div class="timeline-meta">{terr_str} · {fontes_count} fonte(s) comprobatória(s)</div>
                <div style="font-size: 0.9rem; color: #33312B; margin-top: 4px; max-width: 80ch;">{ev.description}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    df_export = events_to_dataframe(events)
    st.download_button(
        "📥 Exportar Cronologia Filtrada (CSV)",
        df_export.to_csv(index=False).encode("utf-8"),
        "cronologia_historica_rj.csv",
        "text/csv"
    )


# =============================================================================
# SEÇÃO 5 — ACERVO DE FONTES (Catálogo e Custódia)
# =============================================================================
def render_view_sources(service, filtros):
    st.markdown("""
    <div style="margin-bottom: 1.4rem;">
        <h2 style="margin: 0; font-size: 1.6rem;">Acervo Geral de Fontes Documentais</h2>
        <div style="font-size: 0.9rem; color: #6F6B63;">Catálogo completo de livros acadêmicos, inquéritos judiciais, relatórios policiais e hemeroteca histórica.</div>
    </div>
    """, unsafe_allow_html=True)

    is_demo_val = filtros.get("is_demo") if isinstance(filtros, dict) else None
    fontes = service.list_sources(is_demo=is_demo_val)
    if not fontes:
        st.info("Nenhuma fonte cadastrada para a seleção atual.")
        return

    def extrair_eixo(src):
        if src.archive_ref and "(" in src.archive_ref:
            return src.archive_ref.split("(")[0].strip()
        if src.notes and "Eixo Temático:" in src.notes:
            return src.notes.split("Eixo Temático:")[1].split("|")[0].strip()
        return "Geral"

    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        todos_eixos = ["Todos os Eixos"] + sorted({extrair_eixo(s) for s in fontes})
        sel_eixo = st.selectbox("Eixo de Pesquisa:", todos_eixos)
    with c2:
        tipologias = ["Todas as Tipologias"] + sorted({s.source_type for s in fontes if s.source_type})
        sel_tipo = st.selectbox("Tipologia:", tipologias)
    with c3:
        termo_busca = st.text_input("Buscar por Título / Autor:", placeholder="Ex: Zaluar, Amorim, STF...")

    fontes_filtradas = []
    for s in fontes:
        if sel_eixo != "Todos os Eixos" and sel_eixo.lower() not in extrair_eixo(s).lower():
            continue
        if sel_tipo != "Todas as Tipologias" and s.source_type != sel_tipo:
            continue
        if termo_busca:
            bloco = f"{s.title} {s.author or ''} {s.publisher or ''} {s.notes or ''}".lower()
            if termo_busca.lower() not in bloco:
                continue
        fontes_filtradas.append(s)

    # Faixa Resumo das Fontes
    st.markdown(f"""
    <div class="editorial-stats-band" style="margin-bottom: 1.2rem;">
        <span><b>{len(fontes_filtradas)}</b> fontes exibidas</span>
        <span class="sep">·</span>
        <span><b>{sum(1 for s in fontes_filtradas if 'academico' in (s.source_type or ''))}</b> acadêmicas</span>
        <span class="sep">·</span>
        <span><b>{sum(1 for s in fontes_filtradas if s.source_type in ('documento_judicial', 'oficial_relatorio'))}</b> oficiais/judiciais</span>
        <span class="sep">·</span>
        <span><b>{sum(1 for s in fontes_filtradas if s.source_type in ('jornalismo_investigativo', 'historia_oral', 'jornalismo_hemeroteca'))}</b> hemeroteca/imprensa</span>
    </div>
    """, unsafe_allow_html=True)

    if not fontes_filtradas:
        st.info("Nenhuma fonte encontrada para os filtros selecionados.")
        return

    # Ficha Catalográfica Selecionada
    titulos = [f"{s.title} (ID {s.id})" for s in fontes_filtradas]
    sel_titulo = st.selectbox("Examinar Ficha Catalográfica:", titulos)
    sel_id = int(sel_titulo.split("(ID ")[-1].replace(")", ""))
    src_sel = next(s for s in fontes_filtradas if s.id == sel_id)

    url_html = f"<div style='margin-top:8px; font-size:0.85rem;'><b>Link de Acesso:</b> <a href='{src_sel.url}' target='_blank'>{src_sel.url}</a></div>" if src_sel.url else ""
    notes_html = f"<div style='margin-top:6px; font-size:0.85rem; color:#6F6B63;'><b>Notas:</b> {src_sel.notes}</div>" if src_sel.notes else ""
    hash_html = f"<code style='font-size:11px;'>{src_sel.file_hash_sha256[:24]}...</code>" if src_sel.file_hash_sha256 else "Registro Remoto"

    st.markdown(
        f"<div class='archive-dossier'>"
        f"<div class='archive-tag'>{(src_sel.source_type or 'INDEFINIDO').upper().replace('_', ' ')} · PUBLICAÇÃO {src_sel.publication_year or 'S/D'}</div>"
        f"<div class='archive-title'>{src_sel.title}</div>"
        f"<div style='font-size:0.92rem; margin-bottom: 0.6rem;'><b>Citação Formal (ABNT):</b><br><i>{src_sel.citation}</i></div>"
        f"<div style='font-size:0.85rem; color:#5A564F; display:grid; grid-template-columns: 1fr 1fr; gap: 8px;'>"
        f"<div><b>Autoria:</b> {src_sel.author or 'Não informada'}</div>"
        f"<div><b>Instituição / Veículo:</b> {src_sel.publisher or 'Não informada'}</div>"
        f"<div><b>Acervo / Fundo:</b> {src_sel.archive_ref or 'Catálogo Geral'}</div>"
        f"<div><b>Custódia Digital:</b> {hash_html}</div>"
        f"</div>"
        f"{url_html}"
        f"{notes_html}"
        f"</div>",
        unsafe_allow_html=True
    )

    if src_sel.event_links:
        st.markdown("<div style='font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#7A2E2E; letter-spacing:0.08em; margin-bottom:0.4rem;'>Acontecimentos Sustentados por Esta Fonte</div>", unsafe_allow_html=True)
        for el in src_sel.event_links:
            st.markdown(f"- **[{el.event.date_display}] {el.event.title}** ({format_badge(el.validation_status)})")
            if el.excerpt:
                st.markdown(f"  > *\"{el.excerpt}\"*")


# =============================================================================
# SEÇÃO 6 — METODOLOGIA HISTÓRICA (Auditoria de Dados e Epistemologia)
# =============================================================================
def render_view_methodology(service, events, filtros):
    st.markdown("""
    <div style="margin-bottom: 1.4rem;">
        <h2 style="margin: 0; font-size: 1.6rem;">Metodologia, Regras Epistemológicas & Auditoria</h2>
        <div style="font-size: 0.9rem; color: #6F6B63;">Princípios normativos que garantem a reproduzibilidade e a integridade da base documental.</div>
    </div>
    """, unsafe_allow_html=True)

    tab_regras, tab_zero, tab_normaliza, tab_custodia = st.tabs([
        "Regras Epistemológicas",
        "Regra 1: Zero vs. NULL",
        "Normalização Onomástica",
        "Auditoria Criptográfica (SHA-256)"
    ])

    with tab_regras:
        st.markdown("""
        ### Compromissos Inegociáveis do Projeto
        1. **Zero Alucinação de Fatos**: Nenhum evento é gerado ou inferido porque "parece plausível". Todo fato precisa de fonte primária ou secundária qualificada.
        2. **Não Invenção de Coordenadas**: Se um território não possui limites cartográficos delimitados nos órgãos oficiais (ex.: Rede Penitenciária Geral), a latitude e longitude permanecem estritamente `NULL`.
        3. **Isolamento de Testes**: Registros marcados como `[DEMO]` servem exclusivamente para testes técnicos e são filtrados por padrão do corpus historiográfico.
        4. **Proveniência Obrigatória**: Acontecimentos históricos reais rejeitam gravação se não acompanhados de trecho literal (`excerpt`) e localização dentro da fonte.
        5. **Registro de Divergências**: Historiografia não é consenso forçado. Versões divergentes são expostas como Claims com posturas opostas.
        """)

    with tab_zero:
        st.markdown("### Avaliador Interativo — Regra 1: Zero vs. NULL")
        st.caption("A confusão entre valor zero e valor ausente (NULL) é o erro mais comum em bancos de dados sobre violência. Teste a regra abaixo:")
        valor_teste = st.text_input("Insira o valor extraído da fonte (deixe vazio para testar dado ausente):", placeholder="Ex: 0, 14, ou vazio")
        rotulo, explicacao, css = evaluate_zero_null(valor_teste)
        st.markdown(f"""
        <div class="archive-dossier" style="margin-top: 10px;">
            <span class="badge-editorial {css}">{rotulo}</span>
            <p style="margin-top: 8px; color: #33312B;">{explicacao}</p>
        </div>
        """, unsafe_allow_html=True)

    with tab_normaliza:
        st.markdown("### Normalização Onomástica e Toponímica")
        st.caption("Preservamos a grafia original do documento histórico; a forma normalizada em caixa alta sem diacríticos é usada apenas para indexação relacional.")
        nome_teste = st.text_input("Nome histórico:", placeholder="Ex: Rogério Lemgruber — 'Bagulhão'")
        if nome_teste:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Grafia Documentada Original:**<br>`{nome_teste}`", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"**Chave Normalizada:**<br>`{normalize_string_search(nome_teste).upper()}`", unsafe_allow_html=True)

    with tab_custodia:
        st.markdown("### Verificação de Custódia Digital")
        st.caption("Permite verificar se um documento bruto em PDF ou imagem no acervo local confere exatamente com o hash SHA-256 catalogado.")
        arquivo_up = st.file_uploader("Selecione o arquivo local para verificação:", type=None)
        hash_esperado = st.text_input("Hash SHA-256 registrado no catálogo:")
        if arquivo_up and hash_esperado:
            digest_calculado = hashlib.sha256(arquivo_up.read()).hexdigest()
            if digest_calculado.lower() == hash_esperado.strip().lower():
                st.success(f"Autenticidade confirmada: O arquivo corresponde exatamente ao hash de custódia ({digest_calculado[:24]}...).")
            else:
                st.error(f"Divergência detectada:\nCalculado: {digest_calculado}\nEsperado: {hash_esperado}")


# =============================================================================
# FLUXO PRINCIPAL
# =============================================================================
def main():
    db = SessionLocal()
    service = DataService(db)

    try:
        current_view = st.session_state.get("nav_view", SECOES[0])
        selected_view, filtros = render_archival_sidebar(service, current_view)

        if selected_view == "Visão Geral":
            render_view_overview(service)
            return

        events = service.list_events(
            year_min=filtros["years"][0],
            year_max=filtros["years"][1],
            region_id=filtros["region_id"],
            organization_id=filtros["org_id"],
            confidence_level=filtros["confidence"],
            search_query=filtros["search"],
            is_demo=filtros["is_demo"]
        )

        if selected_view == "Painel Analítico":
            render_view_analytics(service, events, filtros)
        elif selected_view in ("Mapa Histórico & Territórios", "Atlas Cartográfico"):
            render_view_map(service, events, filtros)
        elif selected_view == "Linha do Tempo":
            render_view_timeline(service, events)
        elif selected_view in ("Acervo de Fontes", "Acervo Documental"):
            render_view_sources(service, filtros)
        elif selected_view in ("Metodologia Histórica", "Metodologia & Dados"):
            render_view_methodology(service, events, filtros)

    finally:
        db.close()


if __name__ == "__main__":
    main()
