import sys
import os
from pathlib import Path

# -----------------------------------------------------------------------------
# Resolução de Namespace e sys.path
# Evita que o arquivo app.py faça shadowing do pacote raiz 'app/'
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
import json

from app.database import SessionLocal
from app.services import EventService
from app.config import DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM


@st.cache_data
def load_geospatial_factions():
    geojson_path = Path("data/geospatial/faccoes_rj_1671_poligonos.geojson")
    if not geojson_path.exists():
        return None
    with open(geojson_path, "r", encoding="utf-8") as f:
        return json.load(f)

st.set_page_config(
    page_title="Rio de Janeiro - Pesquisa Histórica & Territorial",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.2rem;
    }
    .badge-demo {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid #FCD34D;
    }
    .badge-real {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid #6EE7B7;
    }
    .badge-confirmado {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-provavel {
        background-color: #E1EFFE;
        color: #1E429F;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-conflitante {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-nao_verificado {
        background-color: #F3F4F6;
        color: #374151;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .source-box {
        background-color: #FFFFFF;
        border-left: 4px solid #3B82F6;
        border-radius: 4px;
        padding: 0.8rem 1rem;
        margin-top: 0.6rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .unmapped-box {
        background-color: #FFFBEB;
        border: 1px dashed #F59E0B;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        margin-top: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


def get_confidence_badge_html(level: str) -> str:
    labels = {
        "confirmado": ("Confirmado", "badge-confirmado"),
        "provavel": ("Provável", "badge-provavel"),
        "conflitante": ("Conflitante", "badge-conflitante"),
        "nao_verificado": ("Não Verificado", "badge-nao_verificado"),
    }
    label, css_class = labels.get(level.lower(), (level.capitalize(), "badge-nao_verificado"))
    return f'<span class="{css_class}">{label}</span>'


def get_marker_color(level: str) -> str:
    mapping = {
        "confirmado": "green",
        "provavel": "blue",
        "conflitante": "red",
        "nao_verificado": "gray",
    }
    return mapping.get(level.lower(), "blue")


def main():
    db = SessionLocal()
    service = EventService(db)

    try:
        # Cabeçalho
        col_title, col_status = st.columns([3, 1])
        with col_title:
            st.markdown('<div class="main-header">🏛️ Rio de Janeiro — Pesquisa Histórica e Territorial</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="sub-header">Base Histórica Documentada, Linha do Tempo e Proveniência de Fontes</div>',
                unsafe_allow_html=True
            )

        # ---------------------------------------------------------
        # BARRA LATERAL: CONTROLES E ISOLAMENTO DEMO
        # ---------------------------------------------------------
        st.sidebar.header("🔍 Controles e Filtros")

        # Modo de Isolamento DEMO vs Real (Regra: Não misturar silenciosamente!)
        demo_mode = st.sidebar.radio(
            "Origem dos Dados:",
            options=["Apenas Dados Históricos Reais", "Incluir Dados Técnicos [DEMO]", "Apenas Dados [DEMO]"],
            index=0,  # Default agora é o acervo de dados históricos reais
            help="Dados DEMO são identificados com [DEMO] e servem apenas para testes técnicos de interface."
        )

        if demo_mode == "Apenas Dados Históricos Reais":
            filter_is_demo = False
            badge_header = '<span class="badge-real">MODO HISTÓRICO REAL</span>'
        elif demo_mode == "Apenas Dados [DEMO]":
            filter_is_demo = True
            badge_header = '<span class="badge-demo">MODO TÉCNICO [DEMO]</span>'
        else:
            filter_is_demo = None
            badge_header = '<span class="badge-demo">MODO MISTO (AUDITORIA)</span>'

        with col_status:
            st.markdown(f'<div style="text-align: right; padding-top: 10px;">{badge_header}</div>', unsafe_allow_html=True)

        # Filtro Temporal
        min_bound, max_bound = service.get_timeline_bounds(is_demo=filter_is_demo)
        selected_years = st.sidebar.slider(
            "Recorte Temporal (Anos)",
            min_value=min_bound,
            max_value=max_bound,
            value=(min_bound, max_bound),
            step=1,
            help="Intervalo temporal para consulta na linha do tempo."
        )

        # Filtro por Região
        all_regions = service.list_regions(is_demo=filter_is_demo)
        region_options = {"Todas as Regiões": None}
        region_options.update({r.original_name: r.id for r in all_regions})
        selected_region_name = st.sidebar.selectbox("Filtrar por Território", list(region_options.keys()))
        selected_region_id = region_options[selected_region_name]

        # Filtro por Organização
        all_orgs = service.list_organizations(is_demo=filter_is_demo)
        org_options = {"Todas as Organizações": None}
        org_options.update({f"{o.original_name} ({o.acronym})" if o.acronym else o.original_name: o.id for o in all_orgs})
        selected_org_name = st.sidebar.selectbox("Filtrar por Organização", list(org_options.keys()))
        selected_org_id = org_options[selected_org_name]

        # Filtro por Confiabilidade
        confidence_options = {
            "Todos os Níveis": None,
            "Confirmado (Duas ou mais fontes)": "confirmado",
            "Provável (Fonte de referência consistente)": "provavel",
            "Conflitante (Divergência documentada)": "conflitante",
            "Não Verificado (Informe secundário)": "nao_verificado",
        }
        selected_conf_name = st.sidebar.selectbox("Status de Validação da Evidência", list(confidence_options.keys()))
        selected_conf_val = confidence_options[selected_conf_name]

        search_text = st.sidebar.text_input("Busca por Palavra-chave", placeholder="Ex: sindicato, passeata, OAB...")

        # Consulta
        filtered_events = service.list_events(
            year_min=selected_years[0],
            year_max=selected_years[1],
            region_id=selected_region_id,
            organization_id=selected_org_id,
            confidence_level=selected_conf_val,
            search_query=search_text if search_text else None,
            is_demo=filter_is_demo,
        )

        # Alerta se modo histórico estiver vazio
        if filter_is_demo is False and len(filtered_events) == 0:
            st.info(
                "ℹ️ **Nenhum registro histórico real cadastrado ainda.** "
                "Para testar tecnicamente a interface, mapa e relacionamentos com dados controlados, "
                "selecione **'Incluir Dados Técnicos [DEMO]'** no menu lateral."
            )

        # ---------------------------------------------------------
        # MÉTRICAS
        # ---------------------------------------------------------
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Período Ativo", f"{selected_years[0]} – {selected_years[1]}")
        m_col2.metric("Eventos Encontrados", len(filtered_events))
        
        unique_regions_count = len(set(r.id for ev in filtered_events for r in ev.regions))
        m_col3.metric("Territórios Relacionados", unique_regions_count)

        unique_sources_count = len(set(s.id for ev in filtered_events for s in ev.sources))
        m_col4.metric("Fontes Comprobatórias", unique_sources_count)

        st.divider()

        # ---------------------------------------------------------
        # ABAS PRINCIPAIS
        # ---------------------------------------------------------
        tab_map, tab_factions, tab_timeline, tab_sources = st.tabs([
            "🗺️ Mapa Territorial & Detalhes",
            "🏴 Mapeamento Territorial (1.671 Áreas)",
            "⏳ Linha do Tempo",
            "📚 Acervo Geral de Fontes"
        ])

        with tab_map:
            col_map, col_details = st.columns([3, 2])

            with col_map:
                st.subheader("📍 Mapa Territorial")

                col_sub_m1, col_sub_m2 = st.columns([1, 1])
                with col_sub_m1:
                    st.caption("Eventos históricos documentados com coordenadas.")
                with col_sub_m2:
                    show_faction_overlay = st.checkbox(
                        "🏴 Sobrepor Perímetros de Facções",
                        value=False,
                        help="Sobrepõe 1.671 polígonos de comunidades e favelas sob controle/presença de grupos armados (dadosderiscos)."
                    )

                map_obj = folium.Map(
                    location=DEFAULT_MAP_CENTER,
                    zoom_start=DEFAULT_MAP_ZOOM,
                    tiles="OpenStreetMap"
                )

                if show_faction_overlay:
                    factions_geo = load_geospatial_factions()
                    if factions_geo:
                        folium.GeoJson(
                            factions_geo,
                            name="Perímetros Facções RJ",
                            style_function=lambda feat: {
                                "fillColor": feat["properties"].get("cor_hex", "#8C97A3"),
                                "color": feat["properties"].get("cor_hex", "#8C97A3"),
                                "weight": 1.2,
                                "fillOpacity": 0.35,
                            },
                            tooltip=folium.GeoJsonTooltip(
                                fields=["nome", "faccao_nome"],
                                aliases=["Comunidade/Área:", "Presença Registrada:"]
                            )
                        ).add_to(map_obj)

                mapped_count = 0
                unmapped_events = []

                for ev in filtered_events:
                    has_any_coords = False
                    for ev_reg_link in ev.region_links:
                        reg = ev_reg_link.region
                        # REGRA DE GEOLOCALIZAÇÃO: Não inventar coordenadas!
                        # Só plota marcadores se latitude e longitude forem expressamente conhecidas
                        if reg.has_coordinates:
                            has_any_coords = True
                            color = get_marker_color(ev.confidence_level)
                            popup_html = f"""
                            <div style="font-family: sans-serif; width: 230px;">
                                <h4 style="margin: 0 0 5px 0; color: #1E293B;">{ev.title}</h4>
                                <p style="margin: 0 0 4px 0; font-size: 12px;"><b>Data:</b> {ev.date_display}</p>
                                <p style="margin: 0 0 4px 0; font-size: 12px;"><b>Território:</b> {reg.original_name}</p>
                                <p style="margin: 0 0 4px 0; font-size: 12px;"><b>Status:</b> {ev.confidence_level.capitalize()}</p>
                                <p style="margin: 0; font-size: 11px; color: #475569;">{ev.description[:110]}...</p>
                            </div>
                            """
                            folium.Marker(
                                location=[reg.latitude, reg.longitude],
                                popup=folium.Popup(popup_html, max_width=260),
                                tooltip=f"{ev.date_display}: {ev.title} ({reg.original_name})",
                                icon=folium.Icon(color=color, icon="info-sign"),
                            ).add_to(map_obj)
                            mapped_count += 1

                    if not has_any_coords:
                        unmapped_events.append(ev)

                st_folium(map_obj, width="100%", height=500)

                # Legenda das Cores
                st.markdown("""
                <div style="display: flex; gap: 15px; font-size: 12px; margin-top: 5px; color: #475569;">
                    <span>🟢 <b>Verde:</b> Confirmado</span>
                    <span>🔵 <b>Azul:</b> Provável</span>
                    <span>🔴 <b>Vermelho:</b> Conflitante</span>
                    <span>⚪ <b>Cinza:</b> Não Verificado</span>
                </div>
                """, unsafe_allow_html=True)

                # Seção de Eventos sem Coordenadas Documentadas (Respeito à incerteza geográfica)
                if unmapped_events:
                    st.markdown(f"""
                    <div class="unmapped-box">
                        <b>📍 Eventos em Territórios Sem Delimitação Cartográfica Exata ({len(unmapped_events)}):</b><br>
                        <small style="color: #92400E;">Estes eventos possuem documentação histórica válida, mas a localização física não possui coordenadas exatas cadastradas (não inventamos coordenadas).</small>
                        <ul style="margin-top: 5px; margin-bottom: 0; padding-left: 20px; font-size: 13px;">
                            {''.join([f"<li><b>[{ev.date_display}]</b> {ev.title} <i>({', '.join([r.original_name for r in ev.regions])})</i></li>" for ev in unmapped_events])}
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

            with col_details:
                st.subheader("📋 Inspecionar Evento e Proveniência")

                if not filtered_events:
                    st.info("Nenhum evento encontrado para os filtros selecionados.")
                else:
                    event_titles = {f"[{ev.date_display}] {ev.title}": ev.id for ev in filtered_events}
                    selected_key = st.selectbox("Selecione um evento para abrir:", list(event_titles.keys()))
                    selected_id = event_titles[selected_key]
                    selected_event = service.get_event_by_id(selected_id)

                    if selected_event:
                        st.markdown(f"### {selected_event.title}")
                        
                        b_html = get_confidence_badge_html(selected_event.confidence_level)
                        demo_tag = '<span class="badge-demo">DADO DEMO</span>' if selected_event.is_demo else '<span class="badge-real">HISTÓRICO REAL</span>'
                        
                        st.markdown(f"**Data Documentada:** `{selected_event.date_display}` &nbsp;|&nbsp; {b_html} &nbsp;|&nbsp; {demo_tag}", unsafe_allow_html=True)
                        st.markdown(f"**Precisão Temporal:** `{selected_event.temporal_precision}` &nbsp;|&nbsp; **Data Exata:** `{'Sim' if selected_event.exact_date else 'Não (Aproximada)'}`")

                        reg_names = [r.original_name for r in selected_event.regions]
                        st.markdown(f"**Território(s):** {', '.join(reg_names) if reg_names else 'Não especificado'}")

                        st.markdown("#### 📝 Descrição Documentada")
                        st.write(selected_event.description)

                        if selected_event.historical_context:
                            st.markdown("#### 🌐 Contexto Histórico")
                            st.write(selected_event.historical_context)

                        # Organizações e Pessoas
                        col_o, col_p = st.columns(2)
                        with col_o:
                            st.markdown("#### 🏢 Organizações")
                            if selected_event.organization_links:
                                for link in selected_event.organization_links:
                                    st.markdown(f"- **{link.organization.original_name}** *({link.role_in_event or 'participante'})*")
                            else:
                                st.caption("Nenhuma organização vinculada.")

                        with col_p:
                            st.markdown("#### 👤 Pessoas / Lideranças")
                            if selected_event.person_links:
                                for link in selected_event.person_links:
                                    st.markdown(f"- **{link.person.original_name}** *({link.role_in_event or 'envolvido'})*")
                            else:
                                st.caption("Nenhuma pessoa vinculada.")

                        # PROVENIÊNCIA ESTREITA (REGRA DE OURO)
                        st.markdown("#### 📚 Sustentação Documental (Fontes)")
                        if selected_event.source_links:
                            for s_link in selected_event.source_links:
                                src = s_link.source
                                status_badge = get_confidence_badge_html(s_link.validation_status)
                                
                                st.markdown(f"""
                                <div class="source-box">
                                    <b>{src.title}</b> ({src.publication_year or 'S/D'}) &nbsp; {status_badge}<br>
                                    <small><i>{src.citation}</i></small><br>
                                    <b>Tipo da Fonte:</b> <code>{src.source_type}</code> &nbsp;|&nbsp; <b>Página/Ref:</b> <code>{s_link.page_or_section or 'N/A'}</code><br>
                                    {f"<b>Acervo/Fundo:</b> {src.archive_ref}<br>" if src.archive_ref else ""}
                                    <div style="margin-top: 6px; padding: 6px; background-color: #F1F5F9; border-radius: 4px; font-style: italic; color: #1E293B;">
                                        "{s_link.excerpt}"
                                    </div>
                                    {f"<small style='color: #64748B;'><b>Nota Crítica:</b> {s_link.confidence_notes}</small>" if s_link.confidence_notes else ""}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.error("🚨 Erro Crítico: Evento sem proveniência documental registrada.")

        with tab_factions:
            st.subheader("🏴 Mapeamento Territorial de Facções e Milícias no Rio de Janeiro")
            st.markdown(
                "Visualização e análise vetorial de **1.671 perímetros territoriais** compilados com base em "
                "fontes públicas abertas (*dadosderiscos.com.br*), integrado à infraestrutura cartográfica do acervo."
            )

            factions_geo = load_geospatial_factions()
            if not factions_geo:
                st.warning("Arquivo GeoJSON vetorial não encontrado em `data/geospatial/faccoes_rj_1671_poligonos.geojson`.")
            else:
                features_list = factions_geo.get("features", [])

                # Métricas do Mapeamento
                f_m1, f_m2, f_m3, f_m4 = st.columns(4)
                f_m1.metric("Áreas Mapeadas", f"{len(features_list):,}".replace(",", "."))
                f_m2.metric("Comando Vermelho (CV)", "1.000 (59,8%)")
                f_m3.metric("Terceiro Comando Puro (TCP)", "295 (17,7%)")
                f_m4.metric("Milícias & LJ", "263 (15,7%)")

                st.markdown("""
                <div style="display: flex; gap: 12px; font-size: 12px; margin-top: 5px; margin-bottom: 15px; color: #334155; flex-wrap: wrap;">
                    <span>🔴 <b>CV:</b> 1.000 áreas</span>
                    <span>🟢 <b>TCP:</b> 295 áreas</span>
                    <span>🔵 <b>Liga da Justiça (CL220):</b> 130 áreas</span>
                    <span>🟡 <b>ADA:</b> 92 áreas</span>
                    <span>🌐 <b>Outras Milícias:</b> 91 áreas</span>
                    <span>🟣 <b>Milícia de Nova Iguaçu:</b> 42 áreas</span>
                    <span>⚪ <b>Neutro/Disputa:</b> 21 áreas</span>
                </div>
                """, unsafe_allow_html=True)

                col_fac_ctrl1, col_fac_ctrl2 = st.columns([2, 1])
                with col_fac_ctrl1:
                    faction_filter = st.multiselect(
                        "Filtrar por Grupo Armado / Organização:",
                        options=["CV", "TCP", "ADA", "MIL", "LJ", "MNI", "NEU"],
                        default=["CV", "TCP", "ADA", "MIL", "LJ", "MNI", "NEU"],
                        format_func=lambda x: {
                            "CV": "Comando Vermelho (CV)",
                            "TCP": "Terceiro Comando Puro (TCP)",
                            "ADA": "Amigos dos Amigos (ADA)",
                            "MIL": "Milícia (Geral)",
                            "LJ": "Liga da Justiça (CL220)",
                            "MNI": "Milícia de Nova Iguaçu",
                            "NEU": "Área Neutra / Disputada"
                        }.get(x, x)
                    )
                with col_fac_ctrl2:
                    community_names = sorted(list(set(f["properties"]["nome"] for f in features_list)))
                    community_search = st.selectbox(
                        "🔍 Localizar Comunidade no Mapa:",
                        options=["-- Nenhuma selecionada (Visão Geral) --"] + community_names
                    )

                # Filtragem dos polígonos
                filtered_features = [
                    f for f in features_list
                    if f["properties"].get("faccao_sigla") in faction_filter
                ]

                # Centro e zoom do mapa
                center_lat, center_lon, zoom_level = DEFAULT_MAP_CENTER[0], DEFAULT_MAP_CENTER[1], 10
                selected_feat = None

                if community_search != "-- Nenhuma selecionada (Visão Geral) --":
                    selected_feat = next((f for f in features_list if f["properties"]["nome"] == community_search), None)
                    if selected_feat:
                        c_lat = selected_feat["properties"].get("centroide_lat")
                        c_lon = selected_feat["properties"].get("centroide_lon")
                        if c_lat and c_lon:
                            center_lat, center_lon = c_lat, c_lon
                            zoom_level = 15

                fac_map = folium.Map(
                    location=[center_lat, center_lon],
                    zoom_start=zoom_level,
                    tiles="OpenStreetMap"
                )

                filtered_geojson = {
                    "type": "FeatureCollection",
                    "features": filtered_features
                }

                folium.GeoJson(
                    filtered_geojson,
                    name="Perímetros de Facções",
                    style_function=lambda feat: {
                        "fillColor": feat["properties"].get("cor_hex", "#8C97A3"),
                        "color": feat["properties"].get("cor_hex", "#8C97A3"),
                        "weight": 1.4,
                        "fillOpacity": 0.45,
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=["nome", "faccao_nome"],
                        aliases=["Comunidade/Área:", "Grupo Armado:"]
                    )
                ).add_to(fac_map)

                if selected_feat:
                    c_lat = selected_feat["properties"].get("centroide_lat")
                    c_lon = selected_feat["properties"].get("centroide_lon")
                    if c_lat and c_lon:
                        folium.Marker(
                            location=[c_lat, c_lon],
                            tooltip=f"📍 {selected_feat['properties']['nome']} ({selected_feat['properties']['faccao_nome']})",
                            icon=folium.Icon(color="red", icon="crosshairs", prefix="fa")
                        ).add_to(fac_map)

                st_folium(fac_map, width="100%", height=540)

                # Tabela de Exploração
                with st.expander("📋 Ver Tabela Completa das 1.671 Áreas e Centroides", expanded=False):
                    tbl_rows = []
                    for f in filtered_features:
                        p = f["properties"]
                        tbl_rows.append({
                            "Comunidade / Área": p.get("nome"),
                            "Sigla": p.get("faccao_sigla"),
                            "Grupo Armado": p.get("faccao_nome"),
                            "Latitude": p.get("centroide_lat"),
                            "Longitude": p.get("centroide_lon"),
                        })
                    df_fac = pd.DataFrame(tbl_rows)
                    st.dataframe(df_fac, use_container_width=True, hide_index=True)
                    csv_data = df_fac.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Baixar CSV das Áreas Filtradas",
                        data=csv_data,
                        file_name="areas_faccoes_rj.csv",
                        mime="text/csv"
                    )

                st.info(
                    "📌 **Nota Metodológica & Fontes Complementares:**\\n\\n"
                    "Este mapeamento representa uma compilação de perímetros favelares georreferenciados mantidos "
                    "pelo projeto aberto *dadosderiscos.com.br*. No acervo científico deste projeto, essa base se "
                    "articula com as pesquisas longitudinais do **GENI/UFF + Instituto Fogo Cruzado** (*Mapa dos Grupos Armados 2006–2024*), "
                    "com os perímetros municipais oficiais do **Data.Rio / Instituto Pereira Passos (Sabren)** "
                    "e com os dados abertos do **ISP-RJ** (Instituto de Segurança Pública)."
                )

        with tab_timeline:
            st.subheader("⏳ Linha do Tempo Cronológica")
            if filtered_events:
                t_rows = []
                for ev in filtered_events:
                    t_rows.append({
                        "Data Documentada": ev.date_display,
                        "Ano Ref.": str(ev.year) if ev.year is not None else "N/I",
                        "Precisão": ev.temporal_precision,
                        "Título do Evento": ev.title,
                        "Território": ", ".join([r.original_name for r in ev.regions]),
                        "Validação da Evidência": ev.confidence_level.capitalize(),
                        "Fontes": len(ev.sources),
                        "DEMO": "Sim" if ev.is_demo else "Não",
                    })
                df_t = pd.DataFrame(t_rows)
                st.dataframe(df_t, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum evento para exibir na linha do tempo.")

        with tab_sources:
            st.subheader("📚 Acervo Geral de Fontes Catalogadas")
            st.markdown(
                "Catálogo abrangente de fontes acadêmicas, relatórios oficiais, processos judiciais, "
                "reportagens investigativas e bases de dados bibliográficas."
            )
            all_s = service.list_sources(is_demo=filter_is_demo)
            if all_s:
                # Extrair eixos temáticos únicos
                axes_set = set()
                for s in all_s:
                    if s.archive_ref and "(" in s.archive_ref:
                        axis_cand = s.archive_ref.split("(")[0].strip()
                        if axis_cand and not axis_cand.startswith("Acervo"):
                            axes_set.add(axis_cand)
                    elif s.notes and "Eixo Temático:" in s.notes:
                        try:
                            axis_cand = s.notes.split("Eixo Temático:")[1].split("|")[0].strip()
                            if axis_cand:
                                axes_set.add(axis_cand)
                        except Exception:
                            pass
                
                sorted_axes = ["Todos os Eixos"] + sorted(list(axes_set))

                col_f1, col_f2, col_f3 = st.columns([2, 1, 2])
                with col_f1:
                    selected_src_axis = st.selectbox("Eixo Temático de Pesquisa:", sorted_axes)
                with col_f2:
                    typologies = ["Todas as Tipologias"] + sorted(list(set(s.source_type for s in all_s if s.source_type)))
                    selected_src_type = st.selectbox("Tipologia:", typologies)
                with col_f3:
                    src_search = st.text_input("Buscar no Acervo (Título, Autor, Veículo):", placeholder="Ex: Misse, Zaluar, ADPF, CPI...")

                # Filtragem
                filtered_s = []
                for s in all_s:
                    # Filtro por Eixo
                    if selected_src_axis != "Todos os Eixos":
                        s_axis = ""
                        if s.archive_ref and "(" in s.archive_ref:
                            s_axis = s.archive_ref.split("(")[0].strip()
                        elif s.notes and "Eixo Temático:" in s.notes:
                            s_axis = s.notes.split("Eixo Temático:")[1].split("|")[0].strip()
                        if selected_src_axis.lower() not in s_axis.lower():
                            continue

                    # Filtro por Tipologia
                    if selected_src_type != "Todas as Tipologias" and s.source_type != selected_src_type:
                        continue

                    # Filtro por Busca
                    if src_search:
                        q = src_search.lower()
                        blob = f"{s.title} {s.author or ''} {s.publisher or ''} {s.notes or ''}".lower()
                        if q not in blob:
                            continue

                    filtered_s.append(s)

                # Métricas do Acervo
                sm1, sm2, sm3, sm4 = st.columns(4)
                sm1.metric("Fontes Exibidas", len(filtered_s))
                sm2.metric("Acadêmicas", sum(1 for s in filtered_s if "academico" in s.source_type))
                sm3.metric("Judiciais / Oficiais", sum(1 for s in filtered_s if s.source_type in ("documento_judicial", "oficial_relatorio")))
                sm4.metric("Jornalismo / Mídia", sum(1 for s in filtered_s if s.source_type in ("jornalismo_investigativo", "historia_oral")))

                # Tabela Consolidada
                s_rows = []
                for s in filtered_s:
                    eixo_str = "Geral"
                    if s.archive_ref and "(" in s.archive_ref:
                        eixo_str = s.archive_ref.split("(")[0].strip()
                    elif s.notes and "Eixo Temático:" in s.notes:
                        eixo_str = s.notes.split("Eixo Temático:")[1].split("|")[0].strip()

                    s_rows.append({
                        "ID": s.id,
                        "Título": s.title,
                        "Eixo Temático": eixo_str,
                        "Instituição / Veículo": s.publisher or "N/I",
                        "Ano": str(s.publication_year) if s.publication_year is not None else "S/D",
                        "Tipologia": s.source_type,
                        "Eventos Vinculados": len(s.event_links),
                        "Custódia Local": "✅ SHA-256" if s.file_hash_sha256 else "🌐 Remoto / Catálogo",
                    })
                df_s = pd.DataFrame(s_rows)
                st.dataframe(df_s, use_container_width=True, hide_index=True)

                # Detalhes da Fonte Selecionada
                st.markdown("---")
                st.subheader("🔍 Ficha Catalográfica e Metadados da Fonte")
                if filtered_s:
                    selected_source_title = st.selectbox(
                        "Selecione uma fonte para examinar metadados completos:",
                        options=[s.title for s in filtered_s],
                        key="source_detail_selector"
                    )
                    target_source = next((s for s in filtered_s if s.title == selected_source_title), None)

                    if target_source:
                        c_info1, c_info2 = st.columns([3, 2])
                        with c_info1:
                            st.markdown(f"### {target_source.title}")
                            st.markdown(f"**Citação Formal (ABNT):** *{target_source.citation}*")
                            if target_source.author:
                                st.markdown(f"**Autoria:** {target_source.author}")
                            if target_source.publisher:
                                st.markdown(f"**Instituição / Veículo:** {target_source.publisher}")
                            st.markdown(f"**Ano:** {target_source.publication_year or 'Sem data informada'}")
                            st.markdown(f"**Tipologia:** `{target_source.source_type}`")

                        with c_info2:
                            st.markdown(f"**Acervo / Fundo:** `{target_source.archive_ref or 'Catálogo Geral'}`")
                            if target_source.file_hash_sha256:
                                st.markdown(f"**Hash SHA-256 (Custódia Digital):** `{target_source.file_hash_sha256[:16]}...`")
                            if target_source.url:
                                st.markdown(f"**Link Original:** [{target_source.url}]({target_source.url})")
                            if target_source.notes:
                                st.info(f"**Metadados / Notas:**\n\n{target_source.notes}")

                        # Eventos que utilizam esta fonte
                        if target_source.event_links:
                            st.markdown("#### 📌 Eventos Históricos Sustentados por Esta Fonte:")
                            for el in target_source.event_links:
                                badge = get_confidence_badge_html(el.validation_status)
                                st.markdown(f"- **{el.event.title}** ({el.event.date_display}) — {badge}")
                                if el.excerpt:
                                    st.markdown(f"  > *\"{el.excerpt}\"*")
                                if el.page_or_section:
                                    st.caption(f"  Página/Seção: {el.page_or_section}")
                        else:
                            st.caption("ℹ️ Esta fonte está catalogada no acervo bibliográfico e pronta para indexação em novos eventos.")
            else:
                st.info("Nenhuma fonte cadastrada.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
