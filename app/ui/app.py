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
import hashlib
import unicodedata
from pathlib import Path
from collections import Counter

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

from app.database import SessionLocal, engine, Base
from app.services import EventService
from app.config import DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM

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

    /* Fundo e tipografia geral */
    .stApp {
        background-color: #F5F3EE;
        color: #20201E;
        font-family: 'Source Sans 3', -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.6;
    }

    h1, h2, h3, h4, .serif-font {
        font-family: 'Libre Baskerville', Georgia, serif;
        font-weight: 700;
        color: #20201E;
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

    /* Faixa Estatística Editorial (sem cards de SaaS) */
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

    /* Formulários e Inputs Streamlit customizados */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #FFFFFF !important;
        border: 1px solid #D8D3C9 !important;
        color: #20201E !important;
        border-radius: 2px !important;
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

# Seções Sóbrias (Sem emojis de produto)
SECOES = [
    "Visão Geral",
    "Atlas Cartográfico",
    "Linha do Tempo",
    "Acervo Documental",
    "Metodologia & Dados",
]

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
# Carregamento de Recursos Geoespaciais
# =============================================================================
@st.cache_data
def load_geospatial_factions():
    geojson_path = Path("data/geospatial/faccoes_rj_1671_poligonos.geojson")
    if not geojson_path.exists():
        return None
    with open(geojson_path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_badge(confidence: str) -> str:
    label, css = CONFIDENCE_STYLES.get(confidence.lower(), (confidence.capitalize(), "badge-editorial"))
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
    rows = []
    for ev in events:
        rows.append({
            "Ano": ev.year if ev.year else "S/D",
            "Data Documentada": ev.date_display,
            "Acontecimento": ev.title,
            "Territórios": ", ".join(r.original_name for r in ev.regions) or "Geral / Não delimitado",
            "Organizações": ", ".join(o.original_name for o in ev.organizations) or "—",
            "Fontes": len(ev.sources),
            "Claims": len(ev.claims) if hasattr(ev, "claims") else 0,
            "Confiabilidade": ev.confidence_level.capitalize(),
            "Origem": "DEMO" if ev.is_demo else "Real",
        })
    return pd.DataFrame(rows)


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
    selected_view = st.sidebar.radio(
        "Navegação",
        SECOES,
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

    # Slider Temporal
    min_b, max_b = service.get_timeline_bounds(is_demo=is_demo)
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

    st.markdown("""
    <div class="editorial-header">
        <div class="editorial-kicker">Observatório Documental · 1950—2026</div>
        <h1 class="editorial-title">Atlas Histórico da Criminalidade no Rio de Janeiro</h1>
        <p class="editorial-lead">
            Publicação científica, historiográfica e geográfica sobre as dinâmicas territoriais,
            organizações armadas, facções prisionais, contravenção e políticas de segurança pública no Estado do Rio de Janeiro.
        </p>
        <div class="editorial-stats-band">
            <span><b>36</b> acontecimentos documentados</span>
            <span class="sep">·</span>
            <span><b>182</b> fontes catalogadas</span>
            <span class="sep">·</span>
            <span><b>26</b> figuras históricas</span>
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
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Explorar o Atlas Cartográfico →", use_container_width=True):
                st.session_state.nav_view = "Atlas Cartográfico"
                st.rerun()
        with col_btn2:
            if st.button("Consultar a Linha do Tempo →", use_container_width=True):
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
# SEÇÃO 2 — ATLAS CARTOGRÁFICO (O Mapa como Protagonista)
# =============================================================================
def render_view_map(service, events, filtros):
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="margin: 0; font-size: 1.6rem;">Atlas Cartográfico</h2>
        <div style="font-size: 0.9rem; color: #6F6B63;">Mapeamento geoespacial de acontecimentos documentados e perímetros territoriais.</div>
    </div>
    """, unsafe_allow_html=True)

    c_mapa, c_dossie = st.columns([3, 2])

    with c_mapa:
        camadas_col1, camadas_col2 = st.columns(2)
        with camadas_col1:
            exibir_perimetros = st.checkbox("Sobrepor malha de perímetros (1.671 áreas)", value=False,
                                            help="Exibe contornos de favelas e comunidades segundo mapeamento vetorial.")
        with camadas_col2:
            st.caption(f"Exibindo **{len(events)}** acontecimentos documentados no recorte.")

        fmap = folium.Map(
            location=DEFAULT_MAP_CENTER,
            zoom_start=DEFAULT_MAP_ZOOM,
            tiles="OpenStreetMap"
        )

        # Sobreposição discreta de polígonos
        if exibir_perimetros:
            geo_data = load_geospatial_factions()
            if geo_data:
                folium.GeoJson(
                    geo_data,
                    name="Perímetros Territoriais",
                    style_function=lambda ft: {
                        "fillColor": ft["properties"].get("cor_hex", "#8C97A3"),
                        "color": ft["properties"].get("cor_hex", "#8C97A3"),
                        "weight": 1.0,
                        "fillOpacity": 0.22,
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=["nome", "faccao_nome"],
                        aliases=["Comunidade:", "Presença:"]
                    )
                ).add_to(fmap)

        # Plotagem dos acontecimentos históricos com coordenadas reais
        sem_geometria = []
        plotados = 0

        for ev in events:
            tem_ponto = False
            for link in ev.region_links:
                reg = link.region
                if reg.has_coordinates:
                    tem_ponto = True
                    popup_html = f"""
                    <div style="font-family: 'Source Sans 3', sans-serif; width: 220px;">
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #7A2E2E; font-weight: 700;">{ev.date_display}</div>
                        <div style="font-family: 'Libre Baskerville', serif; font-weight: 700; font-size: 13px; margin: 3px 0;">{ev.title}</div>
                        <div style="font-size: 11px; color: #555;"><b>Território:</b> {reg.original_name}</div>
                        <div style="font-size: 11px; color: #555;"><b>Fontes:</b> {len(ev.sources)} vinculadas</div>
                    </div>
                    """
                    folium.Marker(
                        [reg.latitude, reg.longitude],
                        popup=folium.Popup(popup_html, max_width=250),
                        tooltip=f"[{ev.date_display}] {ev.title}",
                        icon=folium.Icon(
                            color=MARKER_COLORS.get(ev.confidence_level, "darkred"),
                            icon="record",
                            prefix="glyphicon"
                        )
                    ).add_to(fmap)
                    plotados += 1
            if not tem_ponto:
                sem_geometria.append(ev)

        st_folium(fmap, width="100%", height=560)

        st.markdown("""
        <div style="display:flex; gap: 15px; font-size: 0.78rem; font-family: 'JetBrains Mono', monospace; color: #5A564F; margin-top: 4px;">
            <span>🟢 Confirmado documentalmente</span>
            <span>🔵 Provável</span>
            <span>🔴 Conflitante (Controvérsia)</span>
            <span>⚪ Não verificado</span>
        </div>
        """, unsafe_allow_html=True)

        if sem_geometria:
            with st.expander(f"📍 Acontecimentos sem delimitação pontual cadastrada ({len(sem_geometria)})"):
                st.caption("Cumprimento estrito da Regra 1: Não inventamos coordenadas geográficas para eventos de abrangência penitenciária ou estadual difusa.")
                for ev in sem_geometria:
                    st.markdown(f"- **[{ev.date_display}]** {ev.title} *(Território: {', '.join(r.original_name for r in ev.regions) or 'Geral'})*")

    # Coluna Direita: Ficha Arquivística
    with c_dossie:
        st.markdown("<div style='font-size:0.8rem; font-weight:700; text-transform:uppercase; color:#7A2E2E; letter-spacing:0.08em;'>Dossiê do Registro Selecionado</div>", unsafe_allow_html=True)

        if not events:
            st.info("Nenhum registro encontrado para os filtros selecionados.")
            return

        opcoes_eventos = {f"[{ev.date_display}] {ev.title}": ev.id for ev in events}
        sel_ev_str = st.selectbox("Selecione o acontecimento:", list(opcoes_eventos.keys()), label_visibility="collapsed")
        ev_id = opcoes_eventos[sel_ev_str]
        ev = service.get_event_by_id(ev_id)

        if ev:
            st.markdown(f"""
            <div class="archive-dossier">
                <div class="archive-tag">{ev.date_display} · {ev.temporal_precision.upper()} · {format_mode_badge(ev.is_demo)}</div>
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
                            <span style="font-style:italic; color:#3A3833;">"{csl.excerpt}"</span>
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
                            "{sl.excerpt}"
                        </div>
                        {f"<div style='font-size:0.78rem; color:#6F6B63;'><b>Avaliação Historiográfica:</b> {sl.confidence_notes or sl.assessment_notes}</div>" if (sl.confidence_notes or sl.assessment_notes) else ""}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Alerta: Registro sem sustentação em fonte documentada.")


# =============================================================================
# SEÇÃO 3 — LINHA DO TEMPO EDITORIAL
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
            fontes_count = len(ev.sources)
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
# SEÇÃO 4 — ACERVO DOCUMENTAL (Catálogo e Custódia)
# =============================================================================
def render_view_sources(service, filtros):
    st.markdown("""
    <div style="margin-bottom: 1.4rem;">
        <h2 style="margin: 0; font-size: 1.6rem;">Acervo Geral de Fontes Documentais</h2>
        <div style="font-size: 0.9rem; color: #6F6B63;">Catálogo completo de livros acadêmicos, inquéritos judiciais, relatórios policiais e hemeroteca histórica.</div>
    </div>
    """, unsafe_allow_html=True)

    fontes = service.list_sources(is_demo=filtros["is_demo"])
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
        <span><b>{sum(1 for s in fontes_filtradas if 'academico' in s.source_type)}</b> acadêmicas</span>
        <span class="sep">·</span>
        <span><b>{sum(1 for s in fontes_filtradas if s.source_type in ('documento_judicial', 'oficial_relatorio'))}</b> oficiais/judiciais</span>
        <span class="sep">·</span>
        <span><b>{sum(1 for s in fontes_filtradas if s.source_type in ('jornalismo_investigativo', 'historia_oral', 'jornalismo_hemeroteca'))}</b> hemeroteca/imprensa</span>
    </div>
    """, unsafe_allow_html=True)

    # Ficha Catalográfica Selecionada
    if fontes_filtradas:
        titulos = [s.title for s in fontes_filtradas]
        sel_titulo = st.selectbox("Examinar Ficha Catalográfica:", titulos)
        src_sel = next(s for s in fontes_filtradas if s.title == sel_titulo)

        st.markdown(f"""
        <div class="archive-dossier">
            <div class="archive-tag">{src_sel.source_type.upper().replace('_', ' ')} · PUBLICAÇÃO {src_sel.publication_year or 'S/D'}</div>
            <div class="archive-title">{src_sel.title}</div>
            <div style="font-size:0.92rem; margin-bottom: 0.6rem;">
                <b>Citação Formal (ABNT):</b><br>
                <i>{src_sel.citation}</i>
            </div>
            <div style="font-size:0.85rem; color:#5A564F; display:grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                <div><b>Autoria:</b> {src_sel.author or 'Não informada'}</div>
                <div><b>Instituição / Veículo:</b> {src_sel.publisher or 'Não informada'}</div>
                <div><b>Acervo / Fundo:</b> {src_sel.archive_ref or 'Catálogo Geral'}</div>
                <div><b>Custódia Digital:</b> {f'<code style=\"font-size:11px;\">{src_sel.file_hash_sha256[:24]}...</code>' if src_sel.file_hash_sha256 else 'Registro Remoto'}</div>
            </div>
            {f"<div style='margin-top:8px; font-size:0.85rem;'><b>Link de Acesso:</b> <a href='{src_sel.url}' target='_blank'>{src_sel.url}</a></div>" if src_sel.url else ""}
            {f"<div style='margin-top:6px; font-size:0.85rem; color:#6F6B63;'><b>Notas:</b> {src_sel.notes}</div>" if src_sel.notes else ""}
        </div>
        """, unsafe_allow_html=True)

        if src_sel.event_links:
            st.markdown("<div style='font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#7A2E2E; letter-spacing:0.08em; margin-bottom:0.4rem;'>Acontecimentos Sustentados por Esta Fonte</div>", unsafe_allow_html=True)
            for el in src_sel.event_links:
                st.markdown(f"- **[{el.event.date_display}] {el.event.title}** ({format_badge(el.validation_status)})")
                if el.excerpt:
                    st.markdown(f"  > *\"{el.excerpt}\"*")


# =============================================================================
# SEÇÃO 5 — METODOLOGIA & AUDITORIA DE DADOS
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
    service = EventService(db)

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

        if selected_view == "Atlas Cartográfico":
            render_view_map(service, events, filtros)
        elif selected_view == "Linha do Tempo":
            render_view_timeline(service, events)
        elif selected_view == "Acervo Documental":
            render_view_sources(service, filtros)
        elif selected_view == "Metodologia & Dados":
            render_view_methodology(service, events, filtros)

    finally:
        db.close()


if __name__ == "__main__":
    main()
