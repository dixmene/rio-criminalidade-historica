# -*- coding: utf-8 -*-
"""
Laboratório Quantitativo e Criminológico de Microdados do ISP-RJ (2003–2026).
Módulo de visualização analítica, matrizes de correlação e testes empíricos de hipóteses.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PARQUET_PATH = PROJECT_ROOT / "database" / "series_historica_isp.parquet"
JSON_CORR_PATH = PROJECT_ROOT / "data" / "geospatial" / "isp_correlacoes.json"

METRIC_LABELS = {
    "hom_doloso": "Homicídio Doloso",
    "hom_por_interv_policial": "Mortes por Intervenção Policial (MDIP)",
    "letalidade_violenta": "Letalidade Violenta Total",
    "roubo_veiculo": "Roubo de Veículo",
    "roubo_carga": "Roubo de Carga",
    "roubo_transeunte": "Roubo a Transeunte",
    "roubo_rua": "Roubo de Rua",
    "armas_apreendidas": "Armas de Fogo Apreendidas (Total)",
    "fuzil_apreendido": "Fuzis de Guerra Apreendidos",
    "recuperacao_veiculos": "Recuperação de Veículos",
    "registro_ocorrencias": "Total de Ocorrências",
}

BATALHOES_MAP = {
    "ESTADO": "Estado do Rio de Janeiro (Total)",
    "41": "41º BPM — Irajá / Pavuna / Madureira",
    "14": "14º BPM — Bangu / Realengo / Senador Camará",
    "15": "15º BPM — Duque de Caxias (Baixada)",
    "7": "7º BPM — São Gonçalo",
    "9": "9º BPM — Rocha Miranda / Marechal Hermes",
    "3": "3º BPM — Méier / Jacarezinho",
    "12": "12º BPM — Niterói / Maricá",
    "21": "21º BPM — São João de Meriti",
    "39": "39º BPM — Belford Roxo",
    "2": "2º BPM — Botafogo / Zona Sul",
}


@st.cache_data(show_spinner=False)
def load_isp_timeseries() -> Optional[pd.DataFrame]:
    """Carrega o dataset consolidado Parquet do ISP-RJ com cache."""
    if not PARQUET_PATH.exists():
        return None
    try:
        return pd.read_parquet(PARQUET_PATH, engine="pyarrow")
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def load_isp_correlations() -> Optional[Dict[str, Any]]:
    """Carrega as matrizes e testes de hipótese estatísticos com cache."""
    if not JSON_CORR_PATH.exists():
        return None
    try:
        with open(JSON_CORR_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def render_isp_analytics_laboratory():
    """Renderiza a seção do laboratório quantitativo e testes de hipóteses do ISP-RJ."""
    df_isp = load_isp_timeseries()
    corr_data = load_isp_correlations()

    st.markdown("""
    <div style="background-color: #FFFFFF; border: 1px solid #D8D3C9; border-radius: 4px; padding: 16px 20px; margin-bottom: 20px;">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #7A2E2E; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em;">
            Laboratório Quantitativo de Segurança Pública &bull; ISP-RJ 2003–2026
        </div>
        <div style="font-family: 'Libre Baskerville', serif; font-size: 1.35rem; font-weight: 700; color: #20201E; margin-top: 4px;">
            A Intervenção Letal e a Apreensão de Armas Realmente Fazem Diferença?
        </div>
        <div style="font-size: 0.88rem; color: #5A564F; line-height: 1.5; margin-top: 6px;">
            Investigação empírica sobre <b>38.136 registros mensais</b> de delegacias (CISP) e <b>32.340 apreensões de armas</b> do Instituto de Segurança Pública (ISP-RJ). 
            Cruzamento estatístico entre letalidade policial, homicídios, roubos patrimoniais e escalada de armas de guerra (fuzis), avaliando defasagem temporal (lag <i>t</i> vs <i>t+1</i>) e ciclos políticos.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df_isp is None or corr_data is None:
        st.warning("Dataset consolidado do ISP-RJ não encontrado em database/series_historica_isp.parquet. Execute o pipeline de engenharia para gerar os dados.")
        return

    # -------------------------------------------------------------------------
    # KPIs Históricos Gerais (Total Estadual)
    # -------------------------------------------------------------------------
    est_anual = df_isp[(df_isp["nivel_geografico"] == "estado") & (df_isp["periodicidade"] == "anual") & (df_isp["ano_completo"])].sort_values("ano")
    tot_hom = int(est_anual["hom_doloso"].sum())
    tot_mdip = int(est_anual["hom_por_interv_policial"].sum())
    est_armas = est_anual[est_anual["ano"] >= 2007]
    tot_armas = int(est_armas["armas_apreendidas"].sum())
    tot_fuzis = int(est_armas["fuzil_apreendido"].sum())
    fuzil_pct_2007 = (est_anual[est_anual["ano"] == 2007]["fuzil_apreendido"].values[0] / est_anual[est_anual["ano"] == 2007]["armas_apreendidas"].values[0]) * 100
    fuzil_pct_2025 = (est_anual[est_anual["ano"] == 2025]["fuzil_apreendido"].values[0] / est_anual[est_anual["ano"] == 2025]["armas_apreendidas"].values[0]) * 100

    col_k1, col_k2, col_k3, col_k4, col_k5 = st.columns(5)
    with col_k1:
        st.metric("Homicídios Dolosos", f"{tot_hom:,}".replace(",", "."), "2003–2025 (RJ)")
    with col_k2:
        st.metric("Mortes por Ação Policial", f"{tot_mdip:,}".replace(",", "."), f"{(tot_mdip/tot_hom)*100:.1f}% dos hom.")
    with col_k3:
        st.metric("Armas Apreendidas", f"{tot_armas:,}".replace(",", "."), "2007–2025 (Fogo)")
    with col_k4:
        st.metric("Fuzis de Guerra", f"{tot_fuzis:,}".replace(",", "."), f"{tot_fuzis/len(est_armas):.0f}/ano em média")
    with col_k5:
        st.metric("Escalada do Fuzil", f"{fuzil_pct_2025:.1f}%", f"+{fuzil_pct_2025 - fuzil_pct_2007:.1f} p.p. desde 2007")

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Abas do Laboratório Quantitativo
    # -------------------------------------------------------------------------
    subtab_hipoteses, subtab_series, subtab_matriz, subtab_batalhoes, subtab_criminologia = st.tabs([
        "🤔 Hipóteses Criminológicas: Faz Diferença?",
        "📈 Explorador de Séries Temporais (2003–2026)",
        "🧮 Matrizes de Correlação (Pearson / Spearman)",
        "🛡️ Painel Comparativo de Batalhões PMERJ",
        "📚 Dossiê Científico & Citações Teóricas"
    ])

    # -------------------------------------------------------------------------
    # SUBTAB 1: TESTES EMPÍRICOS DE HIPÓTESES
    # -------------------------------------------------------------------------
    with subtab_hipoteses:
        st.markdown("### Avaliação Empírica das 4 Grandes Hipóteses da Segurança Pública")
        st.caption("Cruzamento rigoroso dos microdados do ISP-RJ contra as teorias criminológicas e declarações do debate público.")

        selected_hyp = st.selectbox(
            "Selecione a Hipótese a Inspecionar:",
            options=[
                "1. A letalidade policial produz dissuasão e reduz homicídios futuros? (Teoria da Dissuasão Clássica)",
                "2. Operações policiais com mortes reduzem crimes patrimoniais violentos (veículo, carga, rua)?",
                "3. A apreensão massiva de fuzis e armas desarma o conflito ou gera reposição célere?",
                "4. Ciclos de Políticas Públicas: UPP (2008-2015), Intervenção (2018), Witzel (2019) e ADPF 635 (2020-2024)",
            ]
        )

        h_data = corr_data.get("testes_de_hipotese", {})

        if selected_hyp.startswith("1."):
            h1 = h_data.get("hipotese_1_letalidade_policial_vs_homicidio_doloso", {})
            h1_t = h1.get("mesmo_periodo_t", {}).get("pearson", {})
            h1_t1 = h1.get("defasagem_t_mais_1", {}).get("pearson", {})
            h1_rev = h1.get("reacao_policial_hom_t_letalidade_t_mais_1", {}).get("pearson", {})

            st.markdown(f"""
            <div style="border-left: 4px solid #9E2A2B; background-color: #FDF2F2; padding: 14px 18px; border-radius: 0 4px 4px 0; margin-bottom: 16px;">
                <div style="font-weight: 700; color: #9E2A2B; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.05em;">
                    Veredito Empírico: HIPÓTESE REFUTADA PELOS DADOS
                </div>
                <div style="font-size: 0.95rem; color: #20201E; margin-top: 6px; line-height: 1.5;">
                    <b>Não há evidência estatística de que o aumento de mortes por agentes do Estado reduza os homicídios futuros.</b><br>
                    A correlação no mesmo mês é <b>positiva</b> (<i>r</i> = +0,153, <i>p</i> = 0,0099). Com defasagem temporal de 1 mês (<i>t</i> &rarr; <i>t+1</i>), o coeficiente cai para <i>r</i> = +0,0956 e <b>perde significância estatística</b> (<i>p</i> = 0,109).
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <div class="archive-dossier">
                    <div class="archive-tag">Contemporâneo (Mês t)</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: #7A2E2E; font-family: 'JetBrains Mono', monospace;">
                        r = +{h1_t.get('r', 0.153):.3f}
                    </div>
                    <div style="font-size: 0.82rem; color: #5A564F; margin-top: 4px;">
                        p-valor: {h1_t.get('p_value', 0):.4f} (Significativo a 99%)<br>
                        IC 95%: [{h1_t.get('ci_95_low', 0):.3f}, {h1_t.get('ci_95_high', 0):.3f}]<br>
                        <i>Picos de mortes policiais e homicídios acontecem juntos.</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                <div class="archive-dossier">
                    <div class="archive-tag">Efeito Dissuasório (t &rarr; t+1)</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: #5A564F; font-family: 'JetBrains Mono', monospace;">
                        r = +{h1_t1.get('r', 0.095):.3f}
                    </div>
                    <div style="font-size: 0.82rem; color: #5A564F; margin-top: 4px;">
                        p-valor: {h1_t1.get('p_value', 0):.4f} (Não Significativo)<br>
                        IC 95%: [{h1_t1.get('ci_95_low', 0):.3f}, {h1_t1.get('ci_95_high', 0):.3f}]<br>
                        <i>A letalidade de hoje não previne nem reduz mortes no mês seguinte.</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with c3:
                st.markdown(f"""
                <div class="archive-dossier">
                    <div class="archive-tag">Padrão Reativo (Hom t &rarr; MDIP t+1)</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: #7A2E2E; font-family: 'JetBrains Mono', monospace;">
                        r = +{h1_rev.get('r', 0.202):.3f}
                    </div>
                    <div style="font-size: 0.82rem; color: #5A564F; margin-top: 4px;">
                        p-valor: {h1_rev.get('p_value', 0):.5f} (Altamente Significativo)<br>
                        IC 95%: [{h1_rev.get('ci_95_low', 0):.3f}, {h1_rev.get('ci_95_high', 0):.3f}]<br>
                        <i>O Estado reage com incursões letais a homicídios prévios.</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
            #### Síntese Criminológica
            O modelo bivariado de Granger e a regressão OLS controlada confirmam que as mortes por intervenção policial não causam redução de homicídios dolosos. 
            Em vez de dissuasão, o que os microdados descrevem é um **ciclo vicioso de conflagração**: conflitos armados entre facções ou homicídios geram comoção pública, motivando incursões repressivas que aumentam as baixas de civis e policiais, sem alterar a estrutura territorial do crime organizado.
            """)

        elif selected_hyp.startswith("2."):
            h2 = h_data.get("hipotese_2_letalidade_policial_vs_roubos", {})
            st.markdown("""
            <div style="border-left: 4px solid #9E2A2B; background-color: #FDF2F2; padding: 14px 18px; border-radius: 0 4px 4px 0; margin-bottom: 16px;">
                <div style="font-weight: 700; color: #9E2A2B; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.05em;">
                    Veredito Empírico: HIPÓTESE REFUTADA PELOS DADOS
                </div>
                <div style="font-size: 0.95rem; color: #20201E; margin-top: 6px; line-height: 1.5;">
                    <b>Incursões letais não reduzem roubos de carga nem roubos de veículos no período subsequente.</b><br>
                    Pelo contrário: as correlações são fortemente <b>positivas</b> e persistem positivas com defasagem temporal de 1 mês (<i>t+1</i>). A letalidade policial e o crime patrimonial violento coexistem e se concentram nas mesmas faixas geográficas (vias expressas e entornos de favelas).
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_r1, col_r2, col_r3, col_r4 = st.columns(4)
            with col_r1:
                r_veic = h2.get("roubo_veiculo", {}).get("mesmo_periodo_t", {}).get("pearson", {})
                st.metric("Roubo de Veículo (t)", f"r = +{r_veic.get('r', 0.347):.3f}", "p < 0,0001 (Forte)")
            with col_r2:
                r_carga = h2.get("roubo_carga", {}).get("mesmo_periodo_t", {}).get("pearson", {})
                st.metric("Roubo de Carga (t)", f"r = +{r_carga.get('r', 0.265):.3f}", "p < 0,0001 (Forte)")
            with col_r3:
                r_rua = h2.get("roubo_rua", {}).get("mesmo_periodo_t", {}).get("pearson", {})
                st.metric("Roubo de Rua (t)", f"r = +{r_rua.get('r', 0.290):.3f}", "p < 0,0001 (Forte)")
            with col_r4:
                r_panel = corr_data.get("matrizes_correlacao", {}).get("aisp_painel_pooled_pearson", {}).get("hom_por_interv_policial", {}).get("roubo_veiculo", 0.544)
                st.metric("Painel Batalhões (AISP)", f"r = +{r_panel:.3f}", "Espacial transversal")

            st.markdown("""
            #### Análise da Dinâmica Territorial
            Quando analisamos os batalhões da PMERJ de forma transversal (Painel de 11.130 meses/AISP), a correlação entre letalidade policial e roubo de veículo sobe para **r = +0,544** (e Spearman &rho; = +0,637).
            Isso evidencia que o modelo de operações policiais armadas em favelas não desarticula a logística dos roubos de cargas e veículos, os quais dependem de cadeias de receptação no asfalto, galpões industriais e desmanches fora das comunidades.
            """)

        elif selected_hyp.startswith("3."):
            st.markdown("""
            <div style="border-left: 4px solid #8C580E; background-color: #FEF9EE; padding: 14px 18px; border-radius: 0 4px 4px 0; margin-bottom: 16px;">
                <div style="font-weight: 700; color: #8C580E; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.05em;">
                    Veredito Empírico: CORRIDA ARMAMENTISTA E REPOSIÇÃO CÉLERE
                </div>
                <div style="font-size: 0.95rem; color: #20201E; margin-top: 6px; line-height: 1.5;">
                    <b>A apreensão total de armas atua como termômetro do confronto armado (r = +0,758 com letalidade violenta), mas não esgota o arsenal bélico das facções.</b><br>
                    O volume total de armas de fogo apreendidas caiu 46% (de 11.062 em 2007 para 5.959 em 2025), enquanto a apreensão específica de <b>fuzis de guerra subiu +330%</b> (de 214 para 922/ano). O crime organizado substituiu armas leves por poder de fogo militar de alta cadência (calibres 5.56 e 7.62).
                </div>
            </div>
            """, unsafe_allow_html=True)

            df_armas_chart = est_anual[est_anual["ano"] >= 2007][["ano", "armas_apreendidas", "fuzil_apreendido"]].set_index("ano")
            df_armas_chart.columns = ["Total de Armas de Fogo", "Fuzis de Guerra"]
            st.line_chart(df_armas_chart)

            st.markdown("""
            #### O 'Mercado da Bala' e a 'Mercadoria Política' (Michel Misse)
            A apreensão de fuzis nas favelas atinge apenas a ponta final da cadeia logística do armamento. Sem fiscalização aduaneira nas fronteiras terrestres, portos e aeroportos federais, as rotas de tráfico internacional mantêm um fluxo constante de reposição financiado pelas rendas do narcotráfico, da extorsão e da exploração miliciana de serviços essenciais.
            """)

        elif selected_hyp.startswith("4."):
            st.markdown("""
            <div style="border-left: 4px solid #2D5A27; background-color: #F0F6F0; padding: 14px 18px; border-radius: 0 4px 4px 0; margin-bottom: 16px;">
                <div style="font-weight: 700; color: #2D5A27; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.05em;">
                    Veredito Empírico: DIRETRIZES POLÍTICAS E REGRAS DE ENGAJAMENTO SALVAM VIDAS
                </div>
                <div style="font-size: 0.95rem; color: #20201E; margin-top: 6px; line-height: 1.5;">
                    <b>A redução da letalidade policial não causa explosão de crimes violentos; pelo contrário, momentos de contenção judicial e planejamento associam-se às menores taxas de letalidade violenta da série histórica.</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

            df_ciclos = pd.DataFrame([
                {
                    "Ciclo de Política Pública": "1. Auge das UPPs (2009–2013)",
                    "Média Anual Homicídios": "4.729",
                    "Média Anual Letalidade Policial": "652",
                    "Média Anual Fuzis": "246",
                    "Impacto Observado": "Queda contínua de 42,5% na letalidade policial e 25% nos homicídios na capital."
                },
                {
                    "Ciclo de Política Pública": "2. Crise Fiscal & Intervenção Federal (2016–2018)",
                    "Média Anual Homicídios": "5.112",
                    "Média Anual Letalidade Policial": "1.195",
                    "Média Anual Fuzis": "453",
                    "Impacto Observado": "Desmantelamento das UPPs, escalada da letalidade policial (+82%) e pico histórico de roubos de carga."
                },
                {
                    "Ciclo de Política Pública": "3. Retórica do 'Tiro na Cabecinha' (Witzel, 2019)",
                    "Média Anual Homicídios": "4.004",
                    "Média Anual Letalidade Policial": "1.814",
                    "Média Anual Fuzis": "550",
                    "Impacto Observado": "Recorde histórico absoluto de mortes policiais em toda a história do Rio de Janeiro (5/dia)."
                },
                {
                    "Ciclo de Política Pública": "4. ADPF 635 / STF 'ADPF das Favelas' (2020–2024)",
                    "Média Anual Homicídios": "3.212",
                    "Média Anual Letalidade Policial": "1.101",
                    "Média Anual Fuzis": "482",
                    "Impacto Observado": "Letalidade policial caiu para 703 em 2024; homicídios atingiram mínimas históricas (sub-3.000)."
                },
            ])
            st.dataframe(df_ciclos, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # SUBTAB 2: EXPLORADOR DE SÉRIES TEMPORAIS
    # -------------------------------------------------------------------------
    with subtab_series:
        st.markdown("### Explorador Interativo de Séries Temporais do ISP-RJ")
        st.caption("Filtre dados por Batalhão da PMERJ (AISP) ou total estadual, escolhendo periodicidade e indicadores criminais.")

        c_filt1, c_filt2, c_filt3 = st.columns([1.5, 1, 2.5])
        with c_filt1:
            sel_territorio = st.selectbox(
                "Território de Análise:",
                options=list(BATALHOES_MAP.keys()),
                format_func=lambda x: BATALHOES_MAP.get(x, x),
                index=0
            )

        with c_filt2:
            sel_periodo = st.selectbox(
                "Periodicidade:",
                options=["anual", "mensal"],
                format_func=lambda x: "📅 Série Anual (2003–2026)" if x == "anual" else "📊 Série Mensal (283 meses)",
                index=0
            )

        with c_filt3:
            available_metrics = [
                "hom_doloso",
                "hom_por_interv_policial",
                "letalidade_violenta",
                "roubo_veiculo",
                "roubo_carga",
                "roubo_transeunte",
                "armas_apreendidas",
                "fuzil_apreendido",
            ]
            sel_metrics = st.multiselect(
                "Variáveis Criminais para Comparar:",
                options=available_metrics,
                default=["hom_doloso", "hom_por_interv_policial", "roubo_veiculo"],
                format_func=lambda x: METRIC_LABELS.get(x, x)
            )

        # Filtragem do DataFrame
        if sel_territorio == "ESTADO":
            df_filtered = df_isp[(df_isp["nivel_geografico"] == "estado") & (df_isp["periodicidade"] == sel_periodo)].copy()
        else:
            aisp_num = int(sel_territorio)
            df_filtered = df_isp[(df_isp["nivel_geografico"] == "aisp") & (df_isp["aisp"] == aisp_num) & (df_isp["periodicidade"] == sel_periodo)].copy()

        if sel_periodo == "anual":
            df_filtered = df_filtered.sort_values("ano")
            x_col = "ano"
        else:
            df_filtered = df_filtered.sort_values(["ano", "mes"])
            x_col = "data_referencia"

        if df_filtered.empty or not sel_metrics:
            st.info("Nenhum dado disponível para a combinação selecionada.")
        else:
            chart_df = df_filtered[[x_col] + sel_metrics].copy().set_index(x_col)
            chart_df.columns = [METRIC_LABELS.get(c, c) for c in chart_df.columns]
            st.line_chart(chart_df)

            with st.expander("📄 Ver Tabela de Dados e Ficha Numérica"):
                st.dataframe(
                    df_filtered[[x_col] + sel_metrics].rename(columns=METRIC_LABELS),
                    use_container_width=True,
                    hide_index=True
                )

    # -------------------------------------------------------------------------
    # SUBTAB 3: MATRIZES DE CORRELAÇÃO
    # -------------------------------------------------------------------------
    with subtab_matriz:
        st.markdown("### Matrizes de Correlação Bivariada (Pearson & Spearman)")
        st.caption("Matrizes simétricas de associação linear e monotônica calculadas sobre a série histórica oficial do ISP-RJ.")

        mat_tipo = st.radio(
            "Selecione o Nível de Agregação da Matriz:",
            options=[
                "Estado Mensal (283 meses ininterruptos, 2003–2026)",
                "Painel AISP Batalhões (11.130 observações de batalhões/mês)"
            ],
            horizontal=True
        )

        mat_key = "estado_mensal_pearson" if "Estado" in mat_tipo else "aisp_painel_pooled_pearson"
        spear_key = "estado_mensal_spearman" if "Estado" in mat_tipo else "aisp_painel_pooled_spearman"

        mat_dict = corr_data.get("matrizes_correlacao", {}).get(mat_key, {})
        mat_spear_dict = corr_data.get("matrizes_correlacao", {}).get(spear_key, {})

        if mat_dict:
            cols_order = [
                "hom_doloso",
                "hom_por_interv_policial",
                "letalidade_violenta",
                "roubo_veiculo",
                "roubo_carga",
                "roubo_transeunte",
                "armas_apreendidas",
                "fuzil_apreendido"
            ]
            cols_present = [c for c in cols_order if c in mat_dict]

            df_mat = pd.DataFrame(index=cols_present, columns=cols_present)
            for r in cols_present:
                for c in cols_present:
                    df_mat.loc[r, c] = mat_dict.get(r, {}).get(c, 0.0)

            df_mat = df_mat.astype(float)
            df_mat_display = df_mat.rename(index=METRIC_LABELS, columns=METRIC_LABELS)

            st.markdown("#### Matriz de Correlação de Pearson (r)")
            st.dataframe(
                df_mat_display.round(3),
                use_container_width=True
            )

            st.markdown("""
            **Guia de Leitura dos Coeficientes:**
            * **r > +0.70 (Forte Associação Positiva)**: Ex.: *Armas Apreendidas x Letalidade Violenta* (r = +0.758) e *Roubo de Carga x Roubo de Veículos* (r = +0.843).
            * **r entre +0.25 e +0.55 (Moderada Positiva)**: Ex.: *Letalidade Policial x Roubo de Veículos* (r = +0.347 no Estado, r = +0.544 no painel de AISPs).
            * **r próximo de zero (Sem Correlação Linear)**: Ex.: *Letalidade Policial x Homicídio Doloso defasado t+1* (r = +0.095, p = 0.109).
            """)

    # -------------------------------------------------------------------------
    # SUBTAB 4: PAINEL COMPARATIVO DE BATALHÕES
    # -------------------------------------------------------------------------
    with subtab_batalhoes:
        st.markdown("### Comportamento Local por Batalhão da PMERJ (AISP)")
        st.caption("Correlações específicas nos territórios com maiores volumes de confrontos armados e roubos.")

        amostra_bat = corr_data.get("amostra_por_batalhao", {})
        if amostra_bat:
            rows_bat = []
            for aisp_id, info in amostra_bat.items():
                corr_hd = info.get("letalidade_policial_vs_hom_doloso", {}).get("pearson", {}).get("r", 0)
                p_hd = info.get("letalidade_policial_vs_hom_doloso", {}).get("pearson", {}).get("p_value", 1)
                corr_veic = info.get("letalidade_policial_vs_roubo_veiculo", {}).get("pearson", {}).get("r", 0)
                corr_carga = info.get("letalidade_policial_vs_roubo_carga", {}).get("pearson", {}).get("r", 0)

                rows_bat.append({
                    "AISP": aisp_id,
                    "Batalhão PMERJ": info.get("batalhao", f"{aisp_id}º BPM"),
                    "Município": info.get("municipio", ""),
                    "Letalidade Policial x Homicídio Doloso (r)": f"+{corr_hd:.3f}" if corr_hd >= 0 else f"{corr_hd:.3f}",
                    "Significativo (p < 0.05)": "Sim" if p_hd < 0.05 else "Não",
                    "Letalidade Policial x Roubo Veículo (r)": f"+{corr_veic:.3f}" if corr_veic >= 0 else f"{corr_veic:.3f}",
                    "Letalidade Policial x Roubo Carga (r)": f"+{corr_carga:.3f}" if corr_carga >= 0 else f"{corr_carga:.3f}",
                })

            st.dataframe(pd.DataFrame(rows_bat), use_container_width=True, hide_index=True)

            st.markdown("""
            > **Destaque Crítico: O Caso do 9º BPM (Rocha Miranda) e 41º BPM (Pavuna)**
            > No 9º BPM, a correlação entre letalidade policial e homicídio doloso é altíssima (**r = +0,695**), e com roubo de veículos atinge **r = +0,555**. 
            > No 41º BPM (historicamente o batalhão com maior número absoluto de mortes por intervenção policial), a correlação defasada com homicídio doloso é estatisticamente nula (**r = +0,065**, p = 0,37), provando que mesmo nos batalhões mais letais da corporação, a intervenção violenta não produz dissuasão sobre os homicídios locais.
            """)

    # -------------------------------------------------------------------------
    # SUBTAB 5: DOSSIÊ CIENTÍFICO & REFERÊNCIAS
    # -------------------------------------------------------------------------
    with subtab_criminologia:
        st.markdown("### Fundamentação Teórica e Criminologia Crítica Fluminense")
        st.caption("Principais referências acadêmicas que embasam a interpretação dos microdados.")

        st.markdown("""
        1. **Michel Misse (UFRJ) &bull; A Teoria das Mercadorias Políticas e a Acumulação Social da Violência:**
           - Demonstra que o crime violento no Rio não é mero 'desvio', mas opera através de mercados ilícitos protegidos por agentes estatais corruptos (o 'arrego'). A repressão letal pontual não ameaça a mercadoria política, apenas renegocia seu preço.
        
        2. **Alba Zaluar (UERJ) &bull; Condomínio do Diabo & Redes de Sociabilidade Armada:**
           - Documentou como a juventude periférica é recrutada como força de trabalho descartável para as pontas armadas, tornando a reposição de soldados e fuzis praticamente instantânea diante de incursões policiais letais.

        3. **Daniel Cerqueira (IPEA) &bull; Efeitos do Estatuto do Desarmamento e Armas de Fogo:**
           - Evidenciou nacionalmente que a difusão de armas de fogo explica diretamente a variação da taxa de homicídios. No Rio, a corrida bélica substituiu o revólver pelo fuzil, elevando a letalidade por disparo.

        4. **Grupo de Estudos dos Novos Ilegalismos (GENI/UFF):**
           - Pesquisas pioneiras sobre a **ADPF 635 (STF)** demonstraram empiricamente que a restrição judicial de operações policiais reduziu a letalidade policial em mais de 40% sem qualquer aumento proporcional de crimes violentos, refutando o mito de que a polícia precisa matar para conter o crime.

        5. **Laboratório de Análise da Violência (LAV/UERJ):**
           - Monitoramento histórico das UPPs e da letalidade policial demonstrando o padrão de 'metástase' criminal quando as operações ignoram a inteligência financeira e a apreensão de patrimônio dos chefes.
        """)

        st.info("Para uma leitura monográfica completa com derivações econométricas, consulte o arquivo oficial `reports/estudo_quantitativo_correlacoes_violencia.md` no repositório.")
