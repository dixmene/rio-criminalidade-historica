import pytest
from src.normalization.rules import normalize_nulls


def test_zero_preserved_as_zero():
    """
    REGRA 1: 0 comprovado NUNCA deve ser transformado em None/NULL.
    """
    assert normalize_nulls(0) == 0
    assert normalize_nulls(0.0) == 0.0
    assert normalize_nulls("0") == 0


def test_unknown_values_transformed_to_null():
    """
    REGRA 1: Valores desconhecidos, vazios ou marcadores sentinela NUNCA devem virar 0.
    Devem virar None (NULL no banco).
    """
    assert normalize_nulls(None) is None
    assert normalize_nulls("") is None
    assert normalize_nulls("   ") is None
    assert normalize_nulls("N/A") is None
    assert normalize_nulls("na") is None
    assert normalize_nulls("desconhecido") is None
    assert normalize_nulls("não informado") is None
    assert normalize_nulls("nao consta") is None
    assert normalize_nulls("-") is None
    assert normalize_nulls("s/d") is None
    assert normalize_nulls("indeterminado") is None


def test_real_positive_numbers_preserved():
    assert normalize_nulls(42) == 42
    assert normalize_nulls("42") == 42
    assert normalize_nulls(3.14) == 3.14
