"""
Testes automatizados para validação da integridade das séries temporais
e dos coeficientes de correlação do ISP-RJ.

Arquivo testado: scripts/geospatial/process_isp_timeseries.py
Artefatos validados:
- database/series_historica_isp.parquet
- data/geospatial/isp_correlacoes.json
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from scripts.geospatial.process_isp_timeseries import (
    compute_bivariate_correlation,
    aggregate_isp_timeseries,
    METRIC_COLUMNS,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PARQUET_PATH = PROJECT_ROOT / "database" / "series_historica_isp.parquet"
JSON_PATH = PROJECT_ROOT / "data" / "geospatial" / "isp_correlacoes.json"


@pytest.fixture(scope="module")
def df_timeseries():
    """Carrega o dataset consolidado Parquet."""
    assert PARQUET_PATH.exists(), f"Arquivo Parquet não encontrado em {PARQUET_PATH}"
    df = pd.read_parquet(PARQUET_PATH, engine="pyarrow")
    return df


@pytest.fixture(scope="module")
def correlacoes_json():
    """Carrega o arquivo de correlações estatísticas."""
    assert JSON_PATH.exists(), f"Arquivo JSON não encontrado em {JSON_PATH}"
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# ==============================================================================
# 1. TESTES DE ESTRUTURA E INTEGRIDADE DO PARQUET
# ==============================================================================

def test_parquet_file_exists_and_non_empty(df_timeseries):
    """Verifica se o dataset Parquet existe e contém registros."""
    assert len(df_timeseries) > 10_000, f"Esperado > 10.000 registros, obtido: {len(df_timeseries)}"
    assert PARQUET_PATH.stat().st_size > 50_000, "Arquivo Parquet anormalmente pequeno"


def test_required_columns_present(df_timeseries):
    """Valida a presença de todas as variáveis centrais exigidas."""
    required_metrics = [
        "hom_doloso",
        "hom_por_interv_policial",
        "letalidade_violenta",
        "roubo_veiculo",
        "roubo_carga",
        "roubo_transeunte",
        "armas_apreendidas",
        "fuzil_apreendido",
    ]
    required_dimensions = [
        "nivel_geografico",
        "periodicidade",
        "aisp",
        "batalhao",
        "ano",
        "mes",
        "data_referencia",
        "ano_completo",
    ]

    for col in required_metrics + required_dimensions:
        assert col in df_timeseries.columns, f"Coluna obrigatória '{col}' ausente no Parquet."


def test_geographic_and_temporal_granularity(df_timeseries):
    """Verifica se as quatro combinações canônicas de granularidade estão presentes."""
    granularidades = df_timeseries.groupby(["nivel_geografico", "periodicidade"]).size().to_dict()

    assert ("aisp", "mensal") in granularidades, "Granularidade AISP Mensal ausente"
    assert ("aisp", "anual") in granularidades, "Granularidade AISP Anual ausente"
    assert ("estado", "mensal") in granularidades, "Granularidade Estado Mensal ausente"
    assert ("estado", "anual") in granularidades, "Granularidade Estado Anual ausente"

    assert granularidades[("estado", "mensal")] >= 250, "Série mensal do estado deve ter >= 250 meses (2003+)"
    assert granularidades[("estado", "anual")] >= 22, "Série anual do estado deve ter >= 22 anos (2003-2024+)"


def test_temporal_span_2003_to_2024_plus(df_timeseries):
    """Garante que a cobertura temporal inicie em 2003 e alcance pelo menos 2024+."""
    assert int(df_timeseries["ano"].min()) == 2003, "A série histórica deve iniciar em 2003"
    assert int(df_timeseries["ano"].max()) >= 2024, "A série histórica deve contemplar 2024 ou superior"


def test_non_negative_crime_metrics(df_timeseries):
    """Assegura que contagens criminais sejam estritamente não-negativas."""
    crime_cols = [
        "hom_doloso",
        "hom_por_interv_policial",
        "letalidade_violenta",
        "roubo_veiculo",
        "roubo_carga",
        "roubo_transeunte",
    ]
    for col in crime_cols:
        min_val = df_timeseries[col].min()
        assert min_val >= 0, f"Valor negativo encontrado na coluna {col}: {min_val}"


# ==============================================================================
# 2. TESTE DA REGRA ZERO VS NULL (PRESERVAÇÃO METODOLÓGICA)
# ==============================================================================

def test_zero_vs_null_rule_for_weapons(df_timeseries):
    """
    REGRA 1 DO PROJETO:
    - Armas/Fuzis antes de 2007 NÃO eram mensurados no microdado por CISP,
      portanto DEVEM ser NULL/NaN (não inventar 0).
    - De 2007 em diante, foram coletados e devem ser não-nulos e >= 0.
    """
    pre_2007 = df_timeseries[df_timeseries["ano"] < 2007]
    assert pre_2007["armas_apreendidas"].isnull().all(), "Armas antes de 2007 devem ser estritamente NULL/NaN"
    assert pre_2007["fuzil_apreendido"].isnull().all(), "Fuzis antes de 2007 devem ser estritamente NULL/NaN"

    pos_2007 = df_timeseries[df_timeseries["ano"] >= 2007]
    assert pos_2007["armas_apreendidas"].isnull().sum() == 0, "Armas de 2007+ não devem conter NULL"
    assert pos_2007["fuzil_apreendido"].isnull().sum() == 0, "Fuzis de 2007+ não devem conter NULL"
    assert (pos_2007["armas_apreendidas"] >= 0).all(), "Armas apreendidas devem ser >= 0"
    assert (pos_2007["fuzil_apreendido"] >= 0).all(), "Fuzis apreendidos devem ser >= 0"


# ==============================================================================
# 3. TESTES DE CONSISTÊNCIA MATEMÁTICA E AGREGAÇÃO
# ==============================================================================

def test_aisp_sums_equal_state_totals(df_timeseries):
    """
    Valida a integridade da agregação:
    A soma das AISPs em qualquer mês/ano deve ser exatamente igual ao total do Estado.
    """
    aisp_m = df_timeseries[(df_timeseries["nivel_geografico"] == "aisp") & (df_timeseries["periodicidade"] == "mensal")]
    est_m = df_timeseries[(df_timeseries["nivel_geografico"] == "estado") & (df_timeseries["periodicidade"] == "mensal")]

    for col in ["hom_doloso", "hom_por_interv_policial", "roubo_veiculo", "roubo_carga"]:
        aisp_sum = aisp_m.groupby(["ano", "mes"])[col].sum().reset_index()
        merged = pd.merge(est_m[["ano", "mes", col]], aisp_sum, on=["ano", "mes"], suffixes=("_est", "_aisp"))
        diff = (merged[f"{col}_est"] - merged[f"{col}_aisp"]).abs().max()
        assert diff == 0, f"Inconsistência na agregação da coluna {col}: diferença máxima = {diff}"


def test_annual_sums_equal_monthly_sums(df_timeseries):
    """
    Valida que a série anual do Estado é exatamente a soma dos seus meses.
    """
    est_m = df_timeseries[(df_timeseries["nivel_geografico"] == "estado") & (df_timeseries["periodicidade"] == "mensal")]
    est_a = df_timeseries[(df_timeseries["nivel_geografico"] == "estado") & (df_timeseries["periodicidade"] == "anual")]

    for col in ["hom_doloso", "letalidade_violenta", "roubo_rua"]:
        m_sum = est_m.groupby("ano")[col].sum().reset_index()
        merged = pd.merge(est_a[["ano", col]], m_sum, on="ano", suffixes=("_anual", "_mensal_sum"))
        diff = (merged[f"{col}_anual"] - merged[f"{col}_mensal_sum"]).abs().max()
        assert diff == 0, f"Inconsistência anual x mensal em {col}: diferença = {diff}"


# ==============================================================================
# 4. TESTES DAS CORRELAÇÕES E TESTES DE HIPÓTESE (JSON)
# ==============================================================================

def test_correlations_json_structure(correlacoes_json):
    """Verifica se o JSON possui a estrutura de nós obrigatória."""
    assert "metadata" in correlacoes_json
    assert "testes_de_hipotese" in correlacoes_json
    assert "matrizes_correlacao" in correlacoes_json
    assert "amostra_por_batalhao" in correlacoes_json

    hipoteses = correlacoes_json["testes_de_hipotese"]
    assert "hipotese_1_letalidade_policial_vs_homicidio_doloso" in hipoteses
    assert "hipotese_2_letalidade_policial_vs_roubos" in hipoteses
    assert "hipotese_3_apreensao_armas_vs_letalidade_violenta" in hipoteses


def test_correlation_coefficients_bounds(correlacoes_json):
    """Valida se todos os coeficientes de correlação estão no intervalo [-1, 1] e p-valores em [0, 1]."""
    h1 = correlacoes_json["testes_de_hipotese"]["hipotese_1_letalidade_policial_vs_homicidio_doloso"]

    for period_key in ["mesmo_periodo_t", "defasagem_t_mais_1", "reacao_policial_hom_t_letalidade_t_mais_1"]:
        node = h1[period_key]
        r = node["pearson"]["r"]
        p = node["pearson"]["p_value"]
        rho = node["spearman"]["rho"]
        p_rho = node["spearman"]["p_value"]

        assert -1.0 <= r <= 1.0, f"Coeficiente de Pearson fora dos limites: {r}"
        assert -1.0 <= rho <= 1.0, f"Coeficiente de Spearman fora dos limites: {rho}"
        assert 0.0 <= p <= 1.0, f"P-valor fora dos limites: {p}"
        assert 0.0 <= p_rho <= 1.0, f"P-valor fora dos limites: {p_rho}"
        assert node["n_observacoes"] > 200, f"Amostra insuficiente: {node['n_observacoes']}"


def test_hypothesis_1_statistical_integrity(correlacoes_json):
    """
    Testa a Hipótese 1: Letalidade Policial x Homicídio Doloso.
    Em criminologia no RJ, a correlação contemporânea é positiva (r ~ +0.15)
    e não demonstra redução desfasada em t+1.
    """
    h1 = correlacoes_json["testes_de_hipotese"]["hipotese_1_letalidade_policial_vs_homicidio_doloso"]
    r_t = h1["mesmo_periodo_t"]["pearson"]["r"]
    r_lag1 = h1["defasagem_t_mais_1"]["pearson"]["r"]

    assert r_t > 0, "A correlação contemporânea entre letalidade policial e homicídio doloso é positiva"
    assert "conclusao_estatistica" in h1
    assert len(h1["conclusao_estatistica"]) > 30


def test_hypothesis_2_robberies_correlation(correlacoes_json):
    """
    Testa a Hipótese 2: Letalidade Policial x Crimes Patrimoniais (Roubos).
    Roubo de veículos e carga correlacionam-se positivamente com letalidade policial.
    """
    h2 = correlacoes_json["testes_de_hipotese"]["hipotese_2_letalidade_policial_vs_roubos"]
    for crime_type in ["roubo_carga", "roubo_veiculo", "roubo_transeunte", "roubo_rua"]:
        assert crime_type in h2, f"Tipo de roubo {crime_type} ausente na hipótese 2"
        r_t = h2[crime_type]["mesmo_periodo_t"]["pearson"]["r"]
        r_lag = h2[crime_type]["defasagem_t_mais_1"]["pearson"]["r"]
        assert -1.0 <= r_t <= 1.0
        assert -1.0 <= r_lag <= 1.0
        # No RJ, veículos e carga têm forte correlação positiva com letalidade policial (ambos concentrados em conflagrações)
        if crime_type in ["roubo_carga", "roubo_veiculo"]:
            assert r_t > 0.20, f"Correlação esperada > 0.20 para {crime_type}, obtido {r_t}"


def test_hypothesis_3_weapons_and_lethality(correlacoes_json):
    """
    Testa a Hipótese 3: Apreensão de Armas/Fuzis x Letalidade Violenta.
    """
    h3 = correlacoes_json["testes_de_hipotese"]["hipotese_3_apreensao_armas_vs_letalidade_violenta"]
    assert "armas_apreendidas_total" in h3
    assert "fuzil_apreendido" in h3

    r_armas = h3["armas_apreendidas_total"]["mesmo_periodo_t"]["pearson"]["r"]
    # Armas totais correlacionam fortemente de forma positiva com letalidade violenta
    assert r_armas > 0.60, f"Esperado r > 0.60 para armas totais, obtido {r_armas}"


def test_correlation_matrices_symmetry_and_diagonal(correlacoes_json):
    """
    Valida as propriedades matemáticas fundamentais das matrizes de correlação:
    - Diagonal principal deve ser 1.0
    - Matriz deve ser simétrica (M[i][j] == M[j][i])
    """
    matrizes = correlacoes_json["matrizes_correlacao"]
    for mat_name in ["estado_mensal_pearson", "estado_mensal_spearman", "aisp_painel_pooled_pearson"]:
        mat = matrizes[mat_name]
        variables = list(mat.keys())
        for var1 in variables:
            assert abs(mat[var1][var1] - 1.0) < 1e-4, f"Diagonal principal de {var1} deve ser 1.0 em {mat_name}"
            for var2 in variables:
                val12 = mat[var1][var2]
                val21 = mat[var2][var1]
                assert abs(val12 - val21) < 1e-4, f"Assimetria em {mat_name} entre {var1} e {var2}: {val12} != {val21}"


# ==============================================================================
# 5. TESTES UNITÁRIOS DA FUNÇÃO DE CORRELAÇÃO BIVARIADA
# ==============================================================================

def test_compute_bivariate_correlation_unit_cases():
    """Valida a função matemática compute_bivariate_correlation sob diferentes cenários sintéticos."""
    # 1. Correlação linear positiva perfeita
    x = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])
    y = pd.Series([2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0])
    res_pos = compute_bivariate_correlation(x, y)
    assert res_pos["pearson"]["r"] == 1.0
    assert res_pos["spearman"]["rho"] == 1.0
    assert res_pos["pearson"]["significativo_p05"] is True

    # 2. Correlação linear negativa perfeita
    y_neg = pd.Series([14.0, 12.0, 10.0, 8.0, 6.0, 4.0, 2.0])
    res_neg = compute_bivariate_correlation(x, y_neg)
    assert res_neg["pearson"]["r"] == -1.0
    assert res_neg["spearman"]["rho"] == -1.0

    # 3. Tratamento de NaNs intercalados
    x_nan = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0, 6.0, 7.0])
    y_nan = pd.Series([2.0, 4.0, 6.0, np.nan, 10.0, 12.0, 14.0])
    res_nan = compute_bivariate_correlation(x_nan, y_nan)
    assert res_nan["n_observacoes"] == 5

    # 4. Amostra com menos de 5 observações
    x_small = pd.Series([1.0, 2.0, 3.0])
    y_small = pd.Series([2.0, 4.0, 6.0])
    res_small = compute_bivariate_correlation(x_small, y_small)
    assert res_small["pearson"]["r"] is None
    assert res_small["n_observacoes"] == 3
