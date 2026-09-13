"""
Testes para os pipelines de investigação especializada:
1. Base de Ocorrências e Desvios da Corregedoria (SHA-256 e Nível A)
2. Spatial Join Eleitoral (TSE x AISP) e Cálculo do HHI
3. Classificador Temático de Pautas Sensíveis (CMRJ/ALERJ)
"""

import json
from pathlib import Path
import pandas as pd
import pytest

from scripts.etl_tse_votacao import calculate_hhi, run_etl_tse
from scripts.classifier_pautas import classify_legislative_text, TAXONOMIA_PAUTAS_SENSIVEIS
from scripts.scraper_camara_rj import run_pipeline_legislativo


def test_corregedoria_occurrences_schema_and_custody():
    """Valida base auditada de ocorrências e denúncias da Corregedoria e GAECO."""
    corr_path = Path("database/ocorrencias_corregedoria.json")
    assert corr_path.exists(), "database/ocorrencias_corregedoria.json deve existir"

    with open(corr_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "metadados" in data
    assert "ocorrencias" in data
    ocorr = data["ocorrencias"]
    assert len(ocorr) >= 5

    for item in ocorr:
        assert "id" in item
        assert "nome_operacao" in item
        assert "processo_judicial" in item
        assert "aisp_afetadas" in item and len(item["aisp_afetadas"]) > 0
        assert "sha256_documento" in item
        assert len(item["sha256_documento"]) == 64, "Hash SHA-256 de custódia deve ter 64 caracteres"
        assert "batalhoes_envolvidos" in item


def test_hhi_calculation_and_electoral_pipeline(tmp_path):
    """Valida cálculo determinístico do HHI e execução do pipeline eleitoral do TSE."""
    # Cenário 1: Votação plural e competitiva (10 candidatos com 10% cada)
    # HHI = 10 * (10^2) = 1000
    plural_shares = [10.0] * 10
    hhi_plural = calculate_hhi(plural_shares)
    assert hhi_plural == 1000.0

    # Cenário 2: Votação com hegemonia atípica (Candidato tem 80%, outro 20%)
    # HHI = 80^2 + 20^2 = 6400 + 400 = 6800
    hegemonic_shares = [80.0, 20.0]
    hhi_hegemonic = calculate_hhi(hegemonic_shares)
    assert hhi_hegemonic == 6800.0
    assert hhi_hegemonic >= 6000.0

    # Teste de execução do ETL com arquivo Parquet
    test_out = tmp_path / "test_locais.parquet"
    df = run_etl_tse(output_path=test_out)
    assert len(df) >= 6
    assert "indice_hhi" in df.columns
    assert "aisp" in df.columns
    assert "batalhao" in df.columns
    assert "alerta_curral_eleitoral" in df.columns


def test_legislative_taxonomy_classification():
    """Valida a classificação dos 5 eixos temáticos de pautas sensíveis."""
    # Eixo 1: Transporte complementar / vans
    res_van = classify_legislative_text("Regulamenta o itinerário e permissão de vans e mototáxis na Zona Oeste")
    assert res_van["possui_convergencia_sensivel"] is True
    assert res_van["eixo_chave"] == "transporte_complementar"
    assert res_van["score_convergencia"] > 0.0

    # Eixo 2: Uso do solo e grilagem
    res_solo = classify_legislative_text("Dispõe sobre a desafetação de área e anistia a loteamento irregular")
    assert res_solo["possui_convergencia_sensivel"] is True
    assert res_solo["eixo_chave"] == "uso_solo_urbano"

    # Eixo 3: Monopólio de utilidades (gás/água/internet)
    res_gas = classify_legislative_text("Regras sobre distribuição de botijão de gás GLP e água mineral")
    assert res_gas["possui_convergencia_sensivel"] is True
    assert res_gas["eixo_chave"] == "monopolio_utilidades"

    # Eixo 4: Ferros-velhos e receptação de fios
    res_ferro = classify_legislative_text("Fiscalização de ferro-velho e combate ao comércio ilícito de fios de cobre")
    assert res_ferro["possui_convergencia_sensivel"] is True
    assert res_ferro["eixo_chave"] == "comercio_sucata"

    # Eixo 5: Moções de homenagem
    res_mocao = classify_legislative_text("Concede moção de aplauso e medalha tiradentes a policial militar")
    assert res_mocao["possui_convergencia_sensivel"] is True
    assert res_mocao["eixo_chave"] == "mocoes_homenagens"

    # Caso Neutro: Pauta orçamentária geral
    res_neutro = classify_legislative_text("Aprova a prestação de contas do exercício financeiro municipal")
    assert res_neutro["possui_convergencia_sensivel"] is False
    assert res_neutro["score_convergencia"] == 0.0


def test_legislative_pipeline_output():
    """Valida integridade do arquivo database/proposicoes_legislativas.csv gerado."""
    csv_path = Path("database/proposicoes_legislativas.csv")
    assert csv_path.exists()

    df = pd.read_csv(csv_path)
    assert len(df) >= 6
    assert "eixo_tematico" in df.columns
    assert "score_convergencia" in df.columns
    assert "autor" in df.columns
    assert "ementa" in df.columns
