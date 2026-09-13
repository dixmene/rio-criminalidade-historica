import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

from app.database import SessionLocal
from app.services import EventService
from app.config import DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM

st.set_page_config(
    page_title="Daniel Systems - MVP Histórico & Territorial",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
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
    .badge-confirmado {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-provavel {
        background-color: #E1EFFE;
        color: #1E429F;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-conflitante {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-nao_verificado {
        background-color: #F3F4F6;
        color: #374151;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .card-detail {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .source-box {
        background-color: #FFFFFF;
        border-left: 4px solid #3B82F6;
        border-radius: 4px;
        padding: 0.8rem 1rem;
        margin-top: 0.6rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
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
            st.markdown('<div class="main-header">🏛️ Daniel Systems</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="sub-header">Mapeamento Histórico, Territorialidade e Proveniência de Fontes — Rio de Janeiro</div>',
                unsafe_allow_html=True
            )
        with col_status:
            st.markdown(
                '<div style="text-align: right; padding-top: 10px;"><span class="badge-demo">MODO MVP (PILOTO)</span></div>',
                unsafe_allow_html=True
            )

        # ---------------------------------------------------------
        # BARRA LATERAL: FILTROS
        # ---------------------------------------------------------
        st.sidebar.header("🔍 Controles e Filtros")

        min_bound, max_bound = service.get_timeline_bounds()
        selected_years = st.sidebar.slider(
            "Recorte Temporal (Anos)",
            min_value=min_bound,
            max_value=max_bound,
            value=(min_bound, max_bound),
            step=1,
            help="Selecione o intervalo de anos para filtrar os eventos históricos."
        )

        all_regions = service.list_regions()
        region_options = {"Todas as Regiões": None}
        region_options.update({r.name: r.id for r in all_regions})
        selected_region_name = st.sidebar.selectbox("Filtrar por Território / Região", list(region_options.keys()))
        selected_region_id = region_options[selected_region_name]

        all_orgs = service.list_organizations()
        org_options = {"Todas as Organizações": None}
        org_options.update({f"{o.name} ({o.acronym})" if o.acronym else o.name: o.id for o in all_orgs})
        selected_org_name = st.sidebar.selectbox("Filtrar por Organização", list(org_options.keys()))
        selected_org_id = org_options[selected_org_name]

        confidence_options = {
            "Todos os Níveis": None,
            "Confirmado": "confirmado",
            "Provável": "provavel",
            "Conflitante (Divergência entre fontes)": "conflitante",
            "Não Verificado": "nao_verificado",
        }
        selected_conf_name = st.sidebar.selectbox("Status de Validação", list(confidence_options.keys()))
        selected_conf_val = confidence_options[selected_conf_name]

        search_text = st.sidebar.text_input("Busca por Palavra-chave", placeholder="Ex: sindicato, passeata, OAB...")

        # Consulta os eventos filtrados
        filtered_events = service.list_events(
            year_min=selected_years[0],
            year_max=selected_years[1],
            region_id=selected_region_id,
            organization_id=selected_org_id,
            confidence_level=selected_conf_val,
            search_query=search_text if search_text else None,
        )

        # ---------------------------------------------------------
        # MÉTRICAS DO RECORTE
        # ---------------------------------------------------------
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Período Ativo", f"{selected_years[0]} – {selected_years[1]}")
        m_col2.metric("Eventos Documentados", len(filtered_events))
        
        unique_regions_count = len(set(r.id for ev in filtered_events for r in ev.regions))
        m_col3.metric("Territórios com Registro", unique_regions_count)

        unique_sources_count = len(set(s.id for ev in filtered_events for s in ev.sources))
        m_col4.metric("Fontes Vinculadas", unique_sources_count)

        st.divider()

        # ---------------------------------------------------------
        # LAYOUT PRINCIPAL: MAPA + DETALHES
        # ---------------------------------------------------------
        tab_map, tab_timeline, tab_sources = st.tabs(["🗺️ Mapa Territorial & Detalhes", "⏳ Linha do Tempo Comparativa", "📚 Catálogo Geral de Fontes"])

        with tab_map:
            col_map, col_details = st.columns([3, 2])

            with col_map:
                st.subheader(f"📍 Mapa Territorial ({len(filtered_events)} eventos)")

                # Cria o mapa centralizado no Rio
                map_obj = folium.Map(
                    location=DEFAULT_MAP_CENTER,
                    zoom_start=DEFAULT_MAP_ZOOM,
                    tiles="CartoDB positron"
                )

                # Adiciona marcadores de eventos
                for ev in filtered_events:
                    for ev_reg_link in ev.region_links:
                        reg = ev_reg_link.region
                        color = get_marker_color(ev.confidence_level)
                        
                        popup_html = f"""
                        <div style="font-family: sans-serif; width: 220px;">
                            <h4 style="margin: 0 0 5px 0; color: #1E293B;">{ev.title}</h4>
                            <p style="margin: 0 0 4px 0; font-size: 12px;"><b>Ano:</b> {ev.year} | <b>Local:</b> {reg.name}</p>
                            <p style="margin: 0 0 4px 0; font-size: 12px;"><b>Status:</b> {ev.confidence_level.capitalize()}</p>
                            <p style="margin: 0; font-size: 11px; color: #475569;">{ev.description[:100]}...</p>
                        </div>
                        """

                        folium.Marker(
                            location=[reg.latitude, reg.longitude],
                            popup=folium.Popup(popup_html, max_width=250),
                            tooltip=f"{ev.year}: {ev.title} ({reg.name})",
                            icon=folium.Icon(color=color, icon="info-sign"),
                        ).add_to(map_obj)

                st_folium(map_obj, width="100%", height=520)

                # Legenda das Cores do Mapa
                st.markdown("""
                <div style="display: flex; gap: 15px; font-size: 12px; margin-top: 5px; color: #475569;">
                    <span>🟢 <b>Verde:</b> Confirmado</span>
                    <span>🔵 <b>Azul:</b> Provável</span>
                    <span>🔴 <b>Vermelho:</b> Conflitante / Divergente</span>
                    <span>⚪ <b>Cinza:</b> Não Verificado</span>
                </div>
                """, unsafe_allow_html=True)

            with col_details:
                st.subheader("📋 Detalhes do Evento e Fontes")

                if not filtered_events:
                    st.info("Nenhum evento histórico encontrado para os filtros selecionados.")
                else:
                    event_titles = {f"[{ev.year}] {ev.title}": ev.id for ev in filtered_events}
                    selected_event_key = st.selectbox(
                        "Selecione um evento para inspecionar:",
                        list(event_titles.keys())
                    )
                    selected_event_id = event_titles[selected_event_key]
                    selected_event = service.get_event_by_id(selected_event_id)

                    if selected_event:
                        with st.container():
                            st.markdown(f"### {selected_event.title}")
                            
                            b_html = get_confidence_badge_html(selected_event.confidence_level)
                            st.markdown(f"**Data:** `{selected_event.date_start}` &nbsp;|&nbsp; **Nível de Confiança:** {b_html}", unsafe_allow_html=True)

                            # Localização / Territórios
                            reg_names = [r.name for r in selected_event.regions]
                            st.markdown(f"**Território(s):** {', '.join(reg_names) if reg_names else 'Não especificado'}")

                            st.markdown("#### 📝 Descrição dos Fatos")
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
                                        st.markdown(f"- **{link.organization.name}** *({link.role_in_event or 'participante'})*")
                                else:
                                    st.caption("Nenhuma organização vinculada.")

                            with col_p:
                                st.markdown("#### 👤 Pessoas / Lideranças")
                                if selected_event.person_links:
                                    for link in selected_event.person_links:
                                        st.markdown(f"- **{link.person.name}** *({link.role_in_event or 'envolvido'})*")
                                else:
                                    st.caption("Nenhuma pessoa vinculada.")

                            # PROVENIÊNCIA DE FONTES (REGRA DE OURO)
                            st.markdown("#### 📚 Fontes e Proveniência Documental")
                            if selected_event.source_links:
                                for s_link in selected_event.source_links:
                                    src = s_link.source
                                    status_badge = get_confidence_badge_html(s_link.validation_status)
                                    
                                    st.markdown(f"""
                                    <div class="source-box">
                                        <b>{src.title}</b> ({src.publication_year or 'S/D'}) &nbsp; {status_badge}<br>
                                        <small><i>{src.citation}</i></small><br>
                                        <b>Referência/Página:</b> <code>{s_link.page_or_section or 'N/A'}</code><br>
                                        {f"<b>Acervo:</b> {src.archive_ref}<br>" if src.archive_ref else ""}
                                        <div style="margin-top: 6px; padding: 6px; background-color: #F1F5F9; border-radius: 4px; font-style: italic; color: #1E293B;">
                                            "{s_link.excerpt}"
                                        </div>
                                        {f"<small style='color: #64748B;'><b>Nota Crítica:</b> {s_link.confidence_notes}</small>" if s_link.confidence_notes else ""}
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.warning("⚠️ Alerta: Evento sem comprovação de fontes vinculadas.")

        with tab_timeline:
            st.subheader("⏳ Cronologia dos Eventos no Período Selecionado")
            if filtered_events:
                timeline_rows = []
                for ev in filtered_events:
                    timeline_rows.append({
                        "Ano": ev.year,
                        "Data": ev.date_start,
                        "Título do Evento": ev.title,
                        "Território": ", ".join([r.name for r in ev.regions]),
                        "Validação": ev.confidence_level.capitalize(),
                        "Fontes": len(ev.sources),
                        "Organizações": ", ".join([o.acronym or o.name for o in ev.organizations]),
                    })
                df_timeline = pd.DataFrame(timeline_rows)
                st.dataframe(df_timeline, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum registro para exibir na linha do tempo.")

        with tab_sources:
            st.subheader("📚 Catálogo Geral de Fontes Documentadas")
            all_sources = service.list_sources()
            if all_sources:
                sources_rows = []
                for s in all_sources:
                    sources_rows.append({
                        "ID": s.id,
                        "Título": s.title,
                        "Autor": s.author or "N/A",
                        "Ano": s.publication_year or "N/A",
                        "Tipo": s.source_type,
                        "Fundo / Arquivo": s.archive_ref or "N/A",
                        "Grau de Confiabilidade": f"{'★' * s.reliability_rating}{'☆' * (5 - s.reliability_rating)}",
                        "Eventos Vinculados": len(s.event_links),
                    })
                df_sources = pd.DataFrame(sources_rows)
                st.dataframe(df_sources, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma fonte catalogada.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
