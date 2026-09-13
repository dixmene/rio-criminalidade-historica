# -*- coding: utf-8 -*-
"""
Rio de Janeiro — Pesquisa Histórica & Territorial
Interface unificada: Landing Page + Painéis Analíticos + Ferramentas.

Substituição completa de app/ui/app.py — mesma camada de serviços (EventService),
mesmo isolamento DEMO vs Real, mesmo GeoJSON de perímetros, mesma proveniência e claims.
Nenhuma dependência nova é necessária.
"""

import sys
import json
import hashlib
import unicodedata
from pathlib import Path
from collections import Counter

# -----------------------------------------------------------------------------
# Resolução de Namespace e sys.path (evita shadowing do pacote raiz 'app/')
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

# Garante a criação de tabelas em ambientes efêmeros como Streamlit Cloud
Base.metadata.create_all(bind=engine)

st.set_page_config(
    page_title="Mapa Histórico do Rio | Pesquisa Territorial & Antropológica",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# DESIGN SYSTEM — Tema escuro acadêmico
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');

    .stApp {
        background: radial-gradient(1100px 500px at 85% -10%, rgba(56,130,246,.14), transparent 60%),
                    radial-gradient(900px 500px at -10% 20%, rgba(16,185,129,.08), transparent 55%),
                    #0B1120;
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4 { font-family: 'Sora', sans-serif; }
    section[data-testid="stSidebar"] {
        background: #0F172A;
        border-right: 1px solid #1E293B;
    }
    section[data-testid="stSidebar"] * { color: #CBD5E1; }
    div[data-testid="stMetric"] {
        background: #111C33;
        border: 1px solid #243352;
        border-radius: 14px;
        padding: 14px 16px;
    }
    div[data-testid="stMetric"] label { color: #94A3B8 !important; }
    div[data-testid="stMetric"] div { color: #F1F5F9 !important; }

    /* ---------- HERO (landing) ---------- */
    .hero {
        background: linear-gradient(135deg, rgba(30,58,138,.55) 0%, rgba(11,17,32,.9) 55%),
                    linear-gradient(0deg, rgba(11,17,32,.35), rgba(11,17,32,.35));
        border: 1px solid #243352;
        border-radius: 22px;
        padding: 3.2rem 3rem 2.6rem 3rem;
        margin-bottom: 1.6rem;
    }
    .hero-kicker {
        color: #38BDF8; font-size: .8rem; font-weight: 700;
        letter-spacing: .22em; text-transform: uppercase; margin-bottom: .9rem;
    }
    .hero-title {
        color: #F8FAFC; font-family: 'Sora', sans-serif;
        font-size: 2.6rem; font-weight: 800; line-height: 1.12; margin-bottom: .8rem;
    }
    .hero-title span { color: #38BDF8; }
    .hero-sub { color: #A5B4CB; font-size: 1.05rem; max-width: 62ch; line-height: 1.65; }

    /* ---------- Cards ---------- */
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; }
    .card {
        background: #111C33; border: 1px solid #243352; border-radius: 16px;
        padding: 1.3rem 1.4rem; transition: border-color .2s ease, transform .2s ease;
    }
    .card:hover { border-color: #38BDF8; transform: translateY(-2px); }
    .card h3 { color: #F1F5F9; font-size: 1.05rem; margin: .35rem 0 .5rem 0; }
    .card p { color: #94A3B8; font-size: .88rem; line-height: 1.55; margin: 0; }
    .card .ico { font-size: 1.5rem; }
    .card .cta { color: #38BDF8; font-weight: 600; font-size: .85rem; }

    .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: .9rem; margin: 1.2rem 0; }
    .kpi {
        background: linear-gradient(180deg, #13203C 0%, #101A30 100%);
        border: 1px solid #243352; border-radius: 14px; padding: 1rem 1.2rem;
    }
    .kpi .v { color: #F8FAFC; font-family: 'Sora', sans-serif; font-size: 1.7rem; font-weight: 800; }
    .kpi .l { color: #7C8DAF; font-size: .78rem; text-transform: uppercase; letter-spacing: .08em; }

    /* ---------- Caixas de aviso ---------- */
    .ethic-box {
        background: rgba(245,158,11,.08); border: 1px solid rgba(245,158,11,.35);
        border-radius: 14px; padding: 1.1rem 1.3rem; color: #FCD34D; font-size: .92rem;
        line-height: 1.6; margin-top: 1.2rem;
    }
    .info-box {
        background: rgba(56,189,248,.07); border: 1px solid rgba(56,189,248,.3);
        border-radius: 14px; padding: 1rem 1.2rem; color: #BAE6FD; font-size: .9rem;
        line-height: 1.6; margin: .8rem 0;
    }
    .unmapped-box {
        background: rgba(245,158,11,.07); border: 1px dashed rgba(245,158,11,.5);
        border-radius: 12px; padding: .9rem 1.1rem; color: #FDE68A; font-size: .88rem; margin-top: .8rem;
    }

    /* ---------- Badges ---------- */
    .badge {
        display: inline-block; padding: 3px 10px; border-radius: 999px;
        font-weight: 600; font-size: .78rem; border: 1px solid transparent;
    }
    .badge-real   { background: rgba(16,185,129,.15); color: #34D399; border-color: rgba(16,185,129,.4); }
    .badge-demo   { background: rgba(245,158,11,.15); color: #FBBF24; border-color: rgba(245,158,11,.4); }
    .badge-conf   { background: rgba(16,185,129,.15); color: #34D399; border-color: rgba(16,185,129,.35); }
    .badge-prov   { background: rgba(59,130,246,.15); color: #60A5FA; border-color: rgba(59,130,246,.35); }
    .badge-confli { background: rgba(239,68,68,.15);  color: #F87171; border-color: rgba(239,68,68,.35); }
    .badge-nao    { background: rgba(148,163,184,.12);color: #94A3B8; border-color: rgba(148,163,184,.3); }

    /* ---------- Proveniência ---------- */
    .source-box {
        background: #101A30; border-left: 4px solid #38BDF8;
        border-radius: 10px; padding: .9rem 1.1rem; margin-top: .6rem;
        border-top: 1px solid #243352; border-right: 1px solid #243352; border-bottom: 1px solid #243352;
        color: #CBD5E1;
    }
    .source-box .excerpt {
        margin-top: 8px; padding: 8px 10px; background: #0B1428;
        border-radius: 6px; font-style: italic; color: #E2E8F0; font-size: .9rem;
    }
    .source-box small { color: #7C8DAF; }

    /* ---------- Timeline ---------- */
    .tl-item {
        border-left: 3px solid #38BDF8; padding: .35rem 0 .35rem 1rem;
        margin-bottom: .9rem;
    }
    .tl-item .d { color: #38BDF8; font-weight: 700; font-size: .82rem; letter-spacing: .05em; }
    .tl-item .t { color: #F1F5F9; font-weight: 600; font-size: .95rem; }
    .tl-item .m { color: #7C8DAF; font-size: .83rem; }

    hr { border-color: #243352; }
    footer { color: #64748B; font-size: .8rem; text-align: center; padding: 2rem 0 1rem 0; }
</style>
""", unsafe_allow_html=True)

VIEWS = [
    "🏠 Início",
    "📊 Painel Analítico",
    "🗺️ Mapa & Território",
    "⏳ Linha do Tempo",
    "📚 Acervo de Fontes",
    "🛠️ Ferramentas de Pesquisa",
]

CONFIDENCE_LABELS = {
    "confirmado": ("Confirmado", "badge-conf"),
    "provavel": ("Provável", "badge-prov"),
    "conflitante": ("Conflitante", "badge-confli"),
    "nao_verificado": ("Não Verificado", "badge-nao"),
}

MARKER_COLORS = {
    "confirmado": "green",
    "provavel": "blue",
    "conflitante": "red",
    "nao_verificado": "gray",
}

FACCAO_NAMES = {
    "CV": "Comando Vermelho (CV)",
    "TCP": "Terceiro Comando Puro (TCP)",
    "ADA": "Amigos dos Amigos (ADA)",
    "MIL": "Milícia (Geral)",
    "LJ": "Liga da Justiça (CL220)",
    "MNI": "Milícia de Nova Iguaçu",
    "NEU": "Área Neutra / Disputada",
}


# =============================================================================
# Helpers
# =============================================================================
@st.cache_data
def load_geospatial_factions():
    geojson_path = Path("data/geospatial/faccoes_rj_1671_poligonos.geojson")
    if not geojson_path.exists():
        return None
    with open(geojson_path, "r", encoding="utf-8") as f:
        return json.load(f)


def badge_html(level: str) -> str:
    label, css = CONFIDENCE_LABELS.get(level.lower(), (level.capitalize(), "badge-nao"))
    return f'<span class="badge {css}">{label}</span>'


def mode_badge(is_demo: bool) -> str:
    if is_demo:
        return '<span class="badge badge-demo">DADO TÉCNICO [DEMO]</span>'
    return '<span class="badge badge-real">HISTÓRICO REAL</span>'


def normalize_name_demo(text: str) -> str:
    """Replica as regras de normalização do projeto (docs/metodologia/02)."""
    if text is None:
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    without_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    lowered = without_accents.lower().strip()
    cleaned = re_sub_nonalnum(lowered)
    return " ".join(cleaned.split())


def re_sub_nonalnum(s: str) -> str:
    out = []
    for ch in s:
        out.append(ch if (ch.isalnum() or ch.isspace()) else " ")
    return "".join(out)


def classify_zero_vs_null(raw: str):
    """REGRA 1 — ZERO vs. DESCONHECIDO (NULL)."""
    if raw is None or raw.strip() == "":
        return ("NULL", "Dado ausente/desconhecido. Armazenar como NULL — nunca como 0.",
                "badge-nao")
    try:
        val = float(raw.replace(",", "."))
    except ValueError:
        return ("INVÁLIDO", "Entrada não numérica. Verifique a tipagem da coluna.",
                "badge-confli")
    if val == 0:
        return ("ZERO", "Contagem confirmada como zero por fonte documentada.",
                "badge-conf")
    return ("VALOR", f"Contagem informada: {val}. Registrar o valor com sua fonte.",
            "badge-prov")


def events_to_df(events) -> pd.DataFrame:
    rows = []
    for ev in events:
        rows.append({
            "ID": ev.id,
            "Data": ev.date_display,
            "Ano": ev.year,
            "Título": ev.title,
            "Territórios": ", ".join(r.original_name for r in ev.regions),
            "Organizações": ", ".join(l.organization.original_name for l in ev.organization_links),
            "Pessoas": ", ".join(l.person.original_name for l in ev.person_links),
            "Confiabilidade": ev.confidence_level,
            "Precisão Temporal": ev.temporal_precision,
            "Fontes": len(ev.sources),
            "Claims": len(ev.claims) if hasattr(ev, "claims") else 0,
            "DEMO": "Sim" if ev.is_demo else "Não",
        })
    return pd.DataFrame(rows)


# =============================================================================
# Sidebar — navegação + filtros globais
# =============================================================================
def render_sidebar(service, view):
    st.sidebar.markdown("### 🧭 Navegação")
    nav = st.sidebar.radio(
        "Seções do atlas",
        VIEWS,
        key="nav_view",
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Pesquisa científica, histórica e antropológica sobre a evolução "
        "da criminalidade organizada no Rio de Janeiro."
    )

    if view == VIEWS[0]:
        return nav, None

    # ---------- Filtros globais (valem para Painel, Mapa, Timeline, Fontes) ----------
    st.sidebar.header("🔍 Controles e Filtros")

    demo_mode = st.sidebar.radio(
        "Origem dos Dados:",
        options=["Apenas Dados Históricos Reais", "Incluir Dados Técnicos [DEMO]", "Apenas Dados [DEMO]"],
        index=0,
        help="Dados [DEMO] são identificados e servem apenas para testes técnicos de interface.",
    )
    if demo_mode == "Apenas Dados Históricos Reais":
        is_demo = False
    elif demo_mode == "Apenas Dados [DEMO]":
        is_demo = True
    else:
        is_demo = None

    min_bound, max_bound = service.get_timeline_bounds(is_demo=is_demo)
    years = st.sidebar.slider("Recorte Temporal (Anos)", min_bound, max_bound, (min_bound, max_bound), 1)

    regions = service.list_regions(is_demo=is_demo)
    region_opts = {"Todas as Regiões": None}
    region_opts.update({r.original_name: r.id for r in regions})
    region_id = region_opts[st.sidebar.selectbox("Território", list(region_opts.keys()))]

    orgs = service.list_organizations(is_demo=is_demo)
    org_opts = {"Todas as Organizações": None}
    org_opts.update({
        (f"{o.original_name} ({o.acronym})" if o.acronym else o.original_name): o.id
        for o in orgs
    })
    org_id = org_opts[st.sidebar.selectbox("Organização", list(org_opts.keys()))]

    conf_opts = {
        "Todos os Níveis": None,
        "Confirmado": "confirmado",
        "Provável": "provavel",
        "Conflitante": "conflitante",
        "Não Verificado": "nao_verificado",
    }
    conf = conf_opts[st.sidebar.selectbox("Validação da Evidência", list(conf_opts.keys()))]

    search = st.sidebar.text_input("Busca por Palavra-chave", placeholder="Ex: sindicato, OAB, ADPF...")

    filters = dict(
        is_demo=is_demo, years=years, region_id=region_id,
        org_id=org_id, confidence=conf, search=search or None,
    )
    return nav, filters


def apply_filters(service, f):
    return service.list_events(
        year_min=f["years"][0],
        year_max=f["years"][1],
        region_id=f["region_id"],
        organization_id=f["org_id"],
        confidence_level=f["confidence"],
        search_query=f["search"],
        is_demo=f["is_demo"],
    )


# =============================================================================
# VIEW 1 — INÍCIO (Landing Page)
# =============================================================================
def view_home(service):
    n_real = service.count_real_events()
    n_demo = service.count_demo_events()
    n_regions = len(service.list_regions())
    n_orgs = len(service.list_organizations())
    n_people = len(service.list_people())
    n_sources = len(service.list_sources())
    n_claims = len(service.list_claims()) if hasattr(service, "list_claims") else 0

    st.markdown(f"""
    <div class="hero">
        <div class="hero-kicker">Atlas Histórico · Territorial · Antropológico</div>
        <div class="hero-title">A criminalidade no Rio de Janeiro,<br><span>documentada como ciência.</span></div>
        <div class="hero-sub">
            Base histórica auditável e reproduzível sobre a evolução de facções, milícias,
            disputas territoriais e intervenções estatais — cada fato vinculado a fonte
            primária com citação literal, página, afirmações atômicas e referência arquivística.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Eventos Históricos Reais", n_real)
    c2.metric("Afirmações Atomizadas (Claims)", n_claims)
    c3.metric("Fontes Catalogadas", n_sources)
    c4.metric("Organizações Mapeadas", n_orgs)

    st.markdown("#### Explore o atlas")

    cards = [
        ("📊", "Painel Analítico", "Dashboards: distribuição temporal, territorial e por confiabilidade da evidência.", VIEWS[1]),
        ("🗺️", "Mapa & Território", "Mapa de eventos documentados + 1.671 perímetros de grupos armados georreferenciados.", VIEWS[2]),
        ("⏳", "Linha do Tempo", "Cronologia filtrável com precisão temporal e vínculo às fontes de cada registro.", VIEWS[3]),
        ("📚", "Acervo de Fontes", "Catálogo bibliográfico com eixos temáticos, tipologias e custódia SHA-256.", VIEWS[4]),
        ("🛠️", "Ferramentas de Pesquisa", "Normalizador de nomes, verificador Zero vs. NULL, exportação e checagem de hash.", VIEWS[5]),
    ]

    for row_start in range(0, len(cards), 3):
        cols = st.columns(3)
        for col, (ico, title, desc, target) in zip(cols, cards[row_start:row_start + 3]):
            with col:
                st.markdown(f"""
                <div class="card">
                    <div class="ico">{ico}</div>
                    <h3>{title}</h3>
                    <p>{desc}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Acessar →", key=f"cta_{target}", use_container_width=True):
                    st.session_state.nav_view = target
                    st.rerun()

    st.markdown(f"""
    <div class="ethic-box">
        ⚠️ <b>AVISO ÉTICO E LIMITAÇÃO DE ESCOPO.</b> Projeto de finalidade exclusivamente acadêmica,
        historiográfica e sociológica. <b>NÃO</b> é ferramenta de inteligência operacional policial,
        <b>NÃO</b> realiza predições, <b>NÃO</b> indica alvos e <b>NÃO</b> auxilia qualquer atividade ilícita.
        Nenhum fato entra na base sem fonte documentada; narrativas conflitantes são preservadas lado a lado.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <footer>
        Mapa Histórico, Territorial e Antropológico da Criminalidade no Rio de Janeiro ·
        Metodologia: proveniência estrita · grafias preservadas · Regra ZERO ≠ NULL
    </footer>
    """, unsafe_allow_html=True)


# =============================================================================
# VIEW 2 — PAINEL ANALÍTICO
# =============================================================================
def view_dashboard(service, events, f):
    st.markdown("### 📊 Painel Analítico")
    st.caption(f"Recorte: **{f['years'][0]} – {f['years'][1]}** · Modo: "
               + ("Real" if f["is_demo"] is False else "[DEMO]" if f["is_demo"] is True else "Misto (Auditoria)"))

    if not events:
        st.info("Nenhum registro para os filtros atuais. Ajuste a barra lateral ou inclua dados [DEMO].")
        return

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Eventos no Recorte", len(events))
    k2.metric("Territórios Relacionados", len({r.id for ev in events for r in ev.regions}))
    k3.metric("Fontes Comprobatórias", len({s.id for ev in events for s in ev.sources}))
    k4.metric("Organizações Presentes", len({l.organization_id for ev in events for l in ev.organization_links}))

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Eventos por Ano")
        per_year = pd.DataFrame(
            sorted(Counter(ev.year for ev in events if ev.year is not None).items()),
            columns=["Ano", "Eventos"],
        )
        if per_year.empty:
            st.caption("Sem datas informadas no recorte.")
        else:
            st.bar_chart(per_year.set_index("Ano")["Eventos"], color="#38BDF8")

        st.markdown("#### Split Real vs. [DEMO]")
        split = pd.DataFrame(
            Counter("Histórico Real" if not ev.is_demo else "Técnico [DEMO]" for ev in events).items(),
            columns=["Origem", "Eventos"],
        )
        st.bar_chart(split.set_index("Origem")["Eventos"], color="#34D399")

    with col_b:
        st.markdown("#### Validação da Evidência")
        per_conf = pd.DataFrame(
            Counter(ev.confidence_level for ev in events).items(),
            columns=["Nível", "Eventos"],
        )
        st.bar_chart(per_conf.set_index("Nível")["Eventos"], color="#F59E0B")

        st.markdown("#### Top Territórios no Recorte")
        per_reg = Counter()
        for ev in events:
            for r in ev.regions:
                per_reg[r.original_name] += 1
        top_reg = pd.DataFrame(per_reg.most_common(12), columns=["Território", "Eventos"])
        st.bar_chart(top_reg.set_index("Território")["Eventos"], color="#818CF8")

    st.markdown("#### Tabela do Recorte")
    st.dataframe(events_to_df(events), use_container_width=True, hide_index=True)


# =============================================================================
# VIEW 3 — MAPA & TERRITÓRIO
# =============================================================================
def view_map(service, events, f):
    st.markdown("### 🗺️ Mapa & Território")
    tab_ev, tab_fac = st.tabs(["📍 Eventos Históricos Documentados", "🏴 Perímetros de Grupos Armados (1.671 áreas)"])

    # ---------------- Aba 1: eventos ----------------
    with tab_ev:
        c_map, c_det = st.columns([3, 2])

        with c_map:
            overlay = st.checkbox(
                "Sobrepor perímetros de facções",
                value=False,
                help="Sobrepõe 1.671 polígonos de comunidades sob controle/presença de grupos armados.",
            )
            fmap = folium.Map(location=DEFAULT_MAP_CENTER, zoom_start=DEFAULT_MAP_ZOOM, tiles="OpenStreetMap")

            if overlay:
                geo = load_geospatial_factions()
                if geo:
                    folium.GeoJson(
                        geo,
                        name="Perímetros",
                        style_function=lambda ft: {
                            "fillColor": ft["properties"].get("cor_hex", "#8C97A3"),
                            "color": ft["properties"].get("cor_hex", "#8C97A3"),
                            "weight": 1.1, "fillOpacity": 0.3,
                        },
                        tooltip=folium.GeoJsonTooltip(fields=["nome", "faccao_nome"],
                                                      aliases=["Área:", "Presença:"]),
                    ).add_to(fmap)

            mapped, unmapped = 0, []
            for ev in events:
                plotted = False
                for link in ev.region_links:
                    reg = link.region
                    if reg.has_coordinates:  # nunca inventar coordenadas
                        plotted = True
                        popup = f"""
                        <div style="width:230px">
                          <h4 style="margin:0 0 5px 0">{ev.title}</h4>
                          <b>Data:</b> {ev.date_display}<br>
                          <b>Território:</b> {reg.original_name}<br>
                          <b>Status:</b> {ev.confidence_level.capitalize()}<br>
                          <small>{(ev.description or "")[:110]}...</small>
                        </div>"""
                        folium.Marker(
                            [reg.latitude, reg.longitude],
                            popup=folium.Popup(popup, max_width=260),
                            tooltip=f"{ev.date_display}: {ev.title}",
                            icon=folium.Icon(color=MARKER_COLORS.get(ev.confidence_level, "blue"), icon="info-sign"),
                        ).add_to(fmap)
                        mapped += 1
                if not plotted:
                    unmapped.append(ev)

            st_folium(fmap, width="100%", height=500)
            st.markdown(
                '<div style="font-size:12px;color:#7C8DAF">🟢 Confirmado · 🔵 Provável · '
                '🔴 Conflitante · ⚪ Não Verificado</div>', unsafe_allow_html=True)

            if unmapped:
                items = "".join(
                    f"<li><b>[{ev.date_display}]</b> {ev.title} <i>({', '.join(r.original_name for r in ev.regions)})</i></li>"
                    for ev in unmapped
                )
                st.markdown(f"""
                <div class="unmapped-box">
                    <b>📍 Sem delimitação cartográfica exata ({len(unmapped)})</b><br>
                    <small>Eventos documentados cujos territórios não possuem coordenadas cadastradas — não inventamos coordenadas.</small>
                    <ul style="margin:6px 0 0 0;padding-left:18px">{items}</ul>
                </div>""", unsafe_allow_html=True)

        with c_det:
            st.markdown("#### 🔎 Inspecionar Evento e Proveniência")
            if not events:
                st.info("Nenhum evento nos filtros atuais.")
            else:
                opts = {f"[{ev.date_display}] {ev.title}": ev.id for ev in events}
                sel = st.selectbox("Selecione um evento:", list(opts.keys()))
                ev = service.get_event_by_id(opts[sel])
                if ev:
                    st.markdown(f"**{ev.title}**")
                    st.markdown(
                        f"`{ev.date_display}` · Precisão: `{ev.temporal_precision}` · "
                        f"{'Data exata' if ev.exact_date else 'Data aproximada'}",
                        unsafe_allow_html=True)
                    st.markdown(f"{badge_html(ev.confidence_level)} &nbsp; {mode_badge(ev.is_demo)}",
                                unsafe_allow_html=True)
                    st.markdown(f"**Território(s):** {', '.join(r.original_name for r in ev.regions) or 'N/I'}")

                    with st.expander("📝 Descrição documentada", expanded=True):
                        st.write(ev.description or "—")
                        if ev.historical_context:
                            st.caption(f"Contexto histórico: {ev.historical_context}")

                    co, cp = st.columns(2)
                    with co:
                        st.markdown("**🏢 Organizações**")
                        if ev.organization_links:
                            for l in ev.organization_links:
                                st.markdown(f"- {l.organization.original_name} *({l.role_in_event or 'participante'})*")
                        else:
                            st.caption("Nenhuma vinculada.")
                    with cp:
                        st.markdown("**👤 Pessoas**")
                        if ev.person_links:
                            for l in ev.person_links:
                                st.markdown(f"- {l.person.original_name} *({l.role_in_event or 'envolvida'})*")
                        else:
                            st.caption("Nenhuma vinculada.")

                    # Afirmações atômicas e divergências historiográficas (Claims)
                    if hasattr(ev, "claims") and ev.claims:
                        st.markdown("**⚖️ Afirmações Factuais & Controvérsias (Claims)**")
                        for cl in ev.claims:
                            disputed_badge = '<span class="badge badge-confli">Divergência Historiográfica</span>' if cl.is_disputed else ''
                            st.markdown(f"• **{cl.statement}** {disputed_badge}", unsafe_allow_html=True)
                            for csl in cl.source_links:
                                stance_color = "#34D399" if csl.stance == "apoia" else "#F87171" if csl.stance == "contesta" else "#FBBF24"
                                st.markdown(f"""<div style="margin-left: 15px; font-size: 0.85rem; color: #CBD5E1; margin-bottom: 4px;">
                                <span style="color: {stance_color}; font-weight: 600;">[{csl.stance.upper()}]</span> {csl.source.title} (p. {csl.page or 'N/A'}): <i>"{csl.excerpt}"</i>
                                </div>""", unsafe_allow_html=True)

                    st.markdown("**📚 Sustentação Documental**")
                    if ev.source_links:
                        for sl in ev.source_links:
                            src = sl.source
                            st.markdown(f"""
                            <div class="source-box">
                                <b>{src.title}</b> ({src.publication_year or 'S/D'}) &nbsp;{badge_html(sl.validation_status)}<br>
                                <small><i>{src.citation}</i></small><br>
                                <small>Tipo: <code>{src.source_type}</code> · Pág./Ref: <code>{sl.page_or_section or sl.page or 'N/A'}</code>
                                {f" · Acervo: {src.archive_ref}" if src.archive_ref else ""}</small>
                                <div class="excerpt">"{sl.excerpt}"</div>
                                {f"<small><b>Nota crítica:</b> {sl.confidence_notes or sl.assessment_notes}</small>" if (sl.confidence_notes or sl.assessment_notes) else ""}
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.error("🚨 Evento sem proveniência documental registrada.")

    # ---------------- Aba 2: perímetros ----------------
    with tab_fac:
        st.markdown("#### Mapeamento Territorial de Facções e Milícias no Rio de Janeiro")
        st.caption("Compilação vetorial de 1.671 perímetros (fonte aberta: dadosderiscos.com.br), "
                   "articulada com GENI/UFF + Fogo Cruzado, Data.Rio/IPP e ISP-RJ.")

        geo = load_geospatial_factions()
        if not geo:
            st.warning("GeoJSON não encontrado em `data/geospatial/faccoes_rj_1671_poligonos.geojson`.")
            return

        feats = geo.get("features", [])
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Áreas Mapeadas", f"{len(feats):,}".replace(",", "."))
        m2.metric("Comando Vermelho", "1.000 (59,8%)")
        m3.metric("Terceiro Comando Puro", "295 (17,7%)")
        m4.metric("Milícias & LJ", "263 (15,7%)")

        cf1, cf2 = st.columns([2, 1])
        with cf1:
            sel_siglas = st.multiselect("Filtrar por grupo armado:", options=list(FACCAO_NAMES.keys()),
                                        default=list(FACCAO_NAMES.keys()), format_func=lambda x: FACCAO_NAMES[x])
        with cf2:
            nomes = sorted({ft["properties"]["nome"] for ft in feats})
            alvo = st.selectbox("Localizar comunidade:", ["— Visão geral —"] + nomes)

        center, zoom = list(DEFAULT_MAP_CENTER), 10
        alvo_feat = None
        if alvo != "— Visão geral —":
            alvo_feat = next((ft for ft in feats if ft["properties"]["nome"] == alvo), None)
            if alvo_feat:
                la, lo = alvo_feat["properties"].get("centroide_lat"), alvo_feat["properties"].get("centroide_lon")
                if la and lo:
                    center, zoom = [la, lo], 15

        fmap2 = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")
        sub = {"type": "FeatureCollection",
               "features": [ft for ft in feats if ft["properties"].get("faccao_sigla") in sel_siglas]}
        folium.GeoJson(
            sub,
            style_function=lambda ft: {
                "fillColor": ft["properties"].get("cor_hex", "#8C97A3"),
                "color": ft["properties"].get("cor_hex", "#8C97A3"),
                "weight": 1.3, "fillOpacity": 0.45,
            },
            tooltip=folium.GeoJsonTooltip(fields=["nome", "faccao_nome"],
                                          aliases=["Comunidade/Área:", "Grupo Armado:"]),
        ).add_to(fmap2)
        if alvo_feat:
            la, lo = alvo_feat["properties"].get("centroide_lat"), alvo_feat["properties"].get("centroide_lon")
            if la and lo:
                folium.Marker([la, lo], tooltip=f"📍 {alvo}",
                              icon=folium.Icon(color="red", icon="crosshairs", prefix="fa")).add_to(fmap2)

        st_folium(fmap2, width="100%", height=540)

        with st.expander("📋 Tabela das áreas filtradas"):
            rows = [{
                "Comunidade / Área": ft["properties"].get("nome"),
                "Sigla": ft["properties"].get("faccao_sigla"),
                "Grupo Armado": ft["properties"].get("faccao_nome"),
                "Latitude": ft["properties"].get("centroide_lat"),
                "Longitude": ft["properties"].get("centroide_lon"),
            } for ft in sub["features"]]
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button("📥 Baixar CSV", df.to_csv(index=False).encode("utf-8"),
                               "areas_faccoes_rj.csv", "text/csv")


# =============================================================================
# VIEW 4 — LINHA DO TEMPO
# =============================================================================
def view_timeline(service, events):
    st.markdown("### ⏳ Linha do Tempo Cronológica")

    if not events:
        st.info("Nenhum evento para os filtros atuais.")
        return

    # Visual em cartões (agrupado por década)
    decadas = {}
    for ev in events:
        dec = (ev.year // 10) * 10 if ev.year else None
        decadas.setdefault(dec, []).append(ev)

    for dec in sorted(decadas, key=lambda d: (d is None, d)):
        label = f"{dec}s" if dec else "Sem ano informado"
        with st.expander(f"🗓️ {label} — {len(decadas[dec])} registro(s)", expanded=(dec == max(d for d in decadas if d))):
            for ev in decadas[dec]:
                regs = ", ".join(r.original_name for r in ev.regions) or "Território N/I"
                st.markdown(f"""
                <div class="tl-item">
                    <div class="d">{ev.date_display} · {ev.confidence_level.upper().replace('_', ' ')}{' · [DEMO]' if ev.is_demo else ''}</div>
                    <div class="t">{ev.title}</div>
                    <div class="m">{regs} · {len(ev.sources)} fonte(s)</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("#### Tabela completa")
    st.dataframe(events_to_df(events), use_container_width=True, hide_index=True)
    st.download_button("📥 Exportar recorte (CSV)", events_to_df(events).to_csv(index=False).encode("utf-8"),
                       "linha_do_tempo.csv", "text/csv")


# =============================================================================
# VIEW 5 — ACERVO DE FONTES
# =============================================================================
def view_sources(service, f):
    st.markdown("### 📚 Acervo Geral de Fontes Catalogadas")
    st.caption("Fontes acadêmicas, relatórios oficiais, processos judiciais, reportagens investigativas e bases bibliográficas.")

    sources = service.list_sources(is_demo=f["is_demo"])
    if not sources:
        st.info("Nenhuma fonte cadastrada para o modo atual.")
        return

    def eixo_of(s):
        if s.archive_ref and "(" in s.archive_ref:
            return s.archive_ref.split("(")[0].strip()
        if s.notes and "Eixo Temático:" in s.notes:
            return s.notes.split("Eixo Temático:")[1].split("|")[0].strip()
        return "Geral"

    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        eixos = ["Todos os Eixos"] + sorted({eixo_of(s) for s in sources})
        sel_eixo = st.selectbox("Eixo Temático:", eixos)
    with c2:
        tipos = ["Todas as Tipologias"] + sorted({s.source_type for s in sources if s.source_type})
        sel_tipo = st.selectbox("Tipologia:", tipos)
    with c3:
        q = st.text_input("Buscar (título, autor, veículo):", placeholder="Ex: Misse, Zaluar, ADPF, CPI...")

    filtradas = []
    for s in sources:
        if sel_eixo != "Todos os Eixos" and sel_eixo.lower() not in eixo_of(s).lower():
            continue
        if sel_tipo != "Todas as Tipologias" and s.source_type != sel_tipo:
            continue
        if q:
            blob = f"{s.title} {s.author or ''} {s.publisher or ''} {s.notes or ''}".lower()
            if q.lower() not in blob:
                continue
        filtradas.append(s)

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Fontes Exibidas", len(filtradas))
    s2.metric("Acadêmicas", sum(1 for s in filtradas if "academico" in s.source_type))
    s3.metric("Judiciais / Oficiais", sum(1 for s in filtradas if s.source_type in ("documento_judicial", "oficial_relatorio")))
    s4.metric("Jornalismo / Mídia", sum(1 for s in filtradas if s.source_type in ("jornalismo_investigativo", "historia_oral", "jornalismo_hemeroteca")))

    st.markdown("#### Distribuição por Tipologia")
    per_tipo = pd.DataFrame(Counter(s.source_type for s in filtradas).most_common(),
                            columns=["Tipologia", "Fontes"])
    st.bar_chart(per_tipo.set_index("Tipologia")["Fontes"], color="#34D399")

    rows = [{
        "ID": s.id,
        "Título": s.title,
        "Eixo Temático": eixo_of(s),
        "Instituição / Veículo": s.publisher or "N/I",
        "Ano": str(s.publication_year) if s.publication_year is not None else "S/D",
        "Tipologia": s.source_type,
        "Eventos Vinculados": len(s.event_links),
        "Custódia": "✅ SHA-256" if s.file_hash_sha256 else "🌐 Remoto / Catálogo",
    } for s in filtradas]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### 🔍 Ficha Catalográfica")
    if filtradas:
        alvo_t = st.selectbox("Examinar fonte:", [s.title for s in filtradas], key="ficha_fonte")
        src = next(s for s in filtradas if s.title == alvo_t)
        ci, cm = st.columns([3, 2])
        with ci:
            st.markdown(f"**{src.title}**")
            st.markdown(f"*Citação (ABNT):* {src.citation}")
            if src.author:
                st.markdown(f"**Autoria:** {src.author}")
            if src.publisher:
                st.markdown(f"**Instituição / Veículo:** {src.publisher}")
            st.markdown(f"**Ano:** {src.publication_year or 'S/D'} · **Tipologia:** `{src.source_type}`")
        with cm:
            st.markdown(f"**Acervo / Fundo:** `{src.archive_ref or 'Catálogo Geral'}`")
            if src.file_hash_sha256:
                st.markdown(f"**SHA-256:** `{src.file_hash_sha256[:20]}...`")
            if src.url:
                st.markdown(f"[Link original]({src.url})")
            if src.notes:
                st.caption(f"Notas: {src.notes}")

        if src.event_links:
            st.markdown("**📌 Eventos sustentados por esta fonte**")
            for el in src.event_links:
                st.markdown(f"- **{el.event.title}** ({el.event.date_display}) — {badge_html(el.validation_status)}")
                if el.excerpt:
                    st.markdown(f"  > *\"{el.excerpt}\"*")
                if el.page_or_section:
                    st.caption(f"  Pág./Seção: {el.page_or_section}")
        else:
            st.caption("ℹ️ Fonte catalogada e pronta para indexação em novos eventos.")


# =============================================================================
# VIEW 6 — FERRAMENTAS DE PESQUISA
# =============================================================================
def view_tools(service, events, f):
    st.markdown("### 🛠️ Ferramentas de Pesquisa")
    st.caption("Utilitários fiéis à metodologia do projeto (docs/metodologia/02, 03 e 07).")

    t_norm, t_zero, t_export, t_hash = st.tabs([
        "🔤 Normalizador de Nomes",
        "0️⃣ Zero vs. NULL",
        "📤 Exportar Recorte",
        "🔐 Verificação SHA-256",
    ])

    with t_norm:
        st.markdown("#### Normalização de nomes para buscas")
        st.caption("Preserva-se a grafia original no banco; a forma normalizada serve apenas para indexação e busca.")
        raw = st.text_input("Nome original:", placeholder="Ex: Comando Vermelho — 'CV' do Morro do Dendê")
        if raw:
            c_a, c_b = st.columns(2)
            with c_a:
                st.markdown(f'<div class="card"><div class="l">GRAFIA ORIGINAL</div>'
                            f'<div class="v" style="font-size:1.1rem">{raw}</div></div>', unsafe_allow_html=True)
            with c_b:
                st.markdown(f'<div class="card"><div class="l">FORMA NORMALIZADA</div>'
                            f'<div class="v" style="font-size:1.1rem">{normalize_name_demo(raw)}</div></div>',
                            unsafe_allow_html=True)
            st.info("Regras aplicadas: NFKD (remove acentos) → minúsculas → remove pontuação → colapsa espaços.")

    with t_zero:
        st.markdown("#### REGRA 1 — ZERO é diferente de DESCONHECIDO (NULL)")
        st.caption("`0` = contagem confirmada como zero por fonte. `NULL` = dado ausente. Misturá-los corrompe análises.")
        entrada = st.text_input("Valor encontrado na fonte (deixe vazio para testar NULL):",
                                placeholder="Ex.: 0, 12, ou vazio")
        cls, msg, css = classify_zero_vs_null(entrada)
        st.markdown(f'<div class="card"><span class="badge {css}">{cls}</span>'
                    f'<p style="margin-top:8px">{msg}</p></div>', unsafe_allow_html=True)

    with t_export:
        st.markdown("#### Exportação do recorte atual")
        st.caption(f"Recorte: {f['years'][0]}–{f['years'][1]} · {len(events)} evento(s) · "
                   f"modo {'Real' if f['is_demo'] is False else '[DEMO]' if f['is_demo'] else 'Misto'}")
        if events:
            df_ev = events_to_df(events)
            st.dataframe(df_ev, use_container_width=True, hide_index=True)
            st.download_button("📥 Baixar recorte (CSV)", df_ev.to_csv(index=False).encode("utf-8"),
                               "recorte_pesquisa.csv", "text/csv")
        else:
            st.info("Sem eventos no recorte atual para exportar.")

    with t_hash:
        st.markdown("#### Verificação de custódia digital (SHA-256)")
        st.caption("Confira a integridade de um arquivo baixado contra o hash registrado no catálogo de fontes.")
        up = st.file_uploader("Arquivo para verificação:", type=None)
        informado = st.text_input("Hash SHA-256 esperado (do catálogo):", placeholder="64 caracteres hex")
        if up and informado:
            digest = hashlib.sha256(up.read()).hexdigest()
            ok = digest.lower() == informado.strip().lower()
            if ok:
                st.success(f"✅ Integridade confirmada. SHA-256: `{digest[:32]}...`")
            else:
                st.error(f"❌ Hash divergente.\n\nArquivo: `{digest}`\n\nCatálogo: `{informado.strip()}`")


# =============================================================================
# MAIN
# =============================================================================
def main():
    db = SessionLocal()
    service = EventService(db)

    try:
        current = st.session_state.get("nav_view", VIEWS[0])
        view, filters = render_sidebar(service, current)

        if view == VIEWS[0]:
            view_home(service)
            return

        events = apply_filters(service, filters)

        if filters["is_demo"] is False and not events and view not in (VIEWS[5],):
            st.info(
                "ℹ️ Nenhum registro histórico real para os filtros atuais. "
                "Para testes técnicos, selecione **'Incluir Dados Técnicos [DEMO]'** na barra lateral."
            )

        header = {
            VIEWS[1]: ("📊 Painel Analítico", "Distribuição temporal, territorial e por confiabilidade"),
            VIEWS[2]: ("🗺️ Mapa & Território", "Eventos documentados + perímetros de grupos armados"),
            VIEWS[3]: ("⏳ Linha do Tempo", "Cronologia com precisão temporal e proveniência"),
            VIEWS[4]: ("📚 Acervo de Fontes", "Catálogo bibliográfico auditável"),
            VIEWS[5]: ("🛠️ Ferramentas de Pesquisa", "Utilitários metodológicos"),
        }[view]

        st.markdown(
            f'<div style="margin-bottom:4px;color:#F1F5F9;font-family:Sora;font-size:1.5rem;font-weight:700">'
            f'{header[0]}</div>'
            f'<div style="color:#7C8DAF;font-size:.9rem;margin-bottom:1rem">{header[1]}</div>',
            unsafe_allow_html=True)

        if view == VIEWS[1]:
            view_dashboard(service, events, filters)
        elif view == VIEWS[2]:
            view_map(service, events, filters)
        elif view == VIEWS[3]:
            view_timeline(service, events)
        elif view == VIEWS[4]:
            view_sources(service, filters)
        elif view == VIEWS[5]:
            view_tools(service, events, filters)

    finally:
        db.close()


if __name__ == "__main__":
    main()
