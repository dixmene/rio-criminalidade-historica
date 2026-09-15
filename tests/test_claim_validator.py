# -*- coding: utf-8 -*-
"""
Testes Automatizados do Validador Epistemológico e Anti-Alucinação (ClaimValidator).
"""

import pytest
from app.services.claim_validator import (
    ClaimValidator,
    normalize_text,
    parse_timestamp_seconds,
)


def test_normalize_text():
    raw = "Às 08:30h, Fernandinho Beira-Mar (vulgo 'Dedo Nervoso') invadiu a ala!"
    clean = normalize_text(raw)
    assert "as 08 30h fernandinho beira mar" in clean
    assert "'" not in clean
    assert "!" not in clean


def test_parse_timestamp_seconds():
    assert parse_timestamp_seconds("08:14") == 494.0
    assert parse_timestamp_seconds("01:02:03") == 3723.0
    assert parse_timestamp_seconds("45s") == 45.0
    assert parse_timestamp_seconds("invalido") is None
    assert parse_timestamp_seconds("") is None


def test_validate_verbatim_excerpt_exact_match():
    transcript = "na manha de 12 de junho de 1994 ue atraiu orlando jogador ate o morro do adeus"
    excerpt = "Uê atraiu Orlando Jogador até o Morro do Adeus"
    
    res = ClaimValidator.validate_verbatim_excerpt(excerpt, transcript)
    assert res["valid"] is True
    assert res["match_type"] == "exact"
    assert res["similarity"] == 1.0
    assert res["error"] is None


def test_validate_verbatim_excerpt_multi_clause_ellipsis():
    transcript = (
        "homens de ue foram avisar orlando jogador que o bope estava no morro "
        "e apos muitas horas de negociacao quando orlando entregou o dinheiro "
        "os homens atiraram e tiraram a vida de orlando foi um banho de sangue"
    )
    excerpt = (
        "homens de ue foram avisar orlando jogador que o bope estava no morro ... "
        "quando orlando entregou o dinheiro os homens atiraram e tiraram a vida de orlando foi um banho de sangue"
    )
    
    res = ClaimValidator.validate_verbatim_excerpt(excerpt, transcript)
    assert res["valid"] is True
    assert res["match_type"] == "multi_clause_ellipsis"
    assert res["similarity"] >= 0.95
    assert res["error"] is None


def test_validate_verbatim_excerpt_rejects_hallucination():
    transcript = "a reuniao de cupula ocorreu em bangu com a presenca de advogados"
    fake_excerpt = "Uê sacou um revólver calibre 38 e disparou contra o coronel da PMERJ"
    
    res = ClaimValidator.validate_verbatim_excerpt(fake_excerpt, transcript)
    assert res["valid"] is False
    assert res["match_type"] == "none"
    assert "Citação literal não encontrada" in res["error"]


def test_validate_timestamp_within_bounds():
    res = ClaimValidator.validate_timestamp("13:30", duration_seconds=900.0)
    assert res["valid"] is True
    assert res["seconds"] == 810.0


def test_validate_timestamp_exceeding_duration():
    res = ClaimValidator.validate_timestamp("16:40", duration_seconds=816.0)
    assert res["valid"] is False
    assert "excede a duração total do vídeo" in res["error"]


def test_validate_claim_full_workflow():
    transcript = "beira mar se uniu a 30 homens comprou uma pistola e se adiantou ao plano de ue"
    duration = 1000.0

    valid_claim_data = {
        "statement": "Fernandinho Beira-Mar liderou a invasão da ala de Uê em Bangu 1.",
        "claim_type": "relacao_estado",
        "stance": "apoia",
        "confidence_level": "confirmado",
        "tipo_discurso": "narracao_documental",
        "timestamp": "11:00",
        "excerpt": "beira mar se uniu a 30 homens comprou uma pistola e se adiantou ao plano de ue"
    }

    report = ClaimValidator.validate_claim(
        valid_claim_data,
        transcript_text=transcript,
        duration_seconds=duration,
        require_transcript=True
    )

    assert report["is_valid"] is True
    assert report["status"] == "ACCEPTED"
    assert len(report["errors"]) == 0

    # Teste de Rejeição por tipo inválido e excerpt alucinado
    invalid_claim_data = {
        "statement": "Fato inventado sem base textual.",
        "claim_type": "tipo_inexistente",
        "stance": "postura_invalida",
        "confidence_level": "confirmado",
        "timestamp": "25:00",  # 1500s > 1000s
        "excerpt": "trecho completamente ficticio que nao consta no audio"
    }

    bad_report = ClaimValidator.validate_claim(
        invalid_claim_data,
        transcript_text=transcript,
        duration_seconds=duration,
        require_transcript=True
    )

    assert bad_report["is_valid"] is False
    assert bad_report["status"] == "REJECTED"
    assert len(bad_report["errors"]) >= 3  # tipo, timestamp e excerpt
