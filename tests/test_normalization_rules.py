import pytest
from src.utils.unicode_normalization import normalize_string_unicode, create_dual_name_entry
from src.normalization.rules import (
    normalize_name,
    normalize_location,
    normalize_organization,
    normalize_date,
)


def test_unicode_normalization_accents():
    assert normalize_string_unicode("São Gonçalo") == "SAO GONCALO"
    assert normalize_string_unicode("João da Silva") == "JOAO DA SILVA"
    assert normalize_string_unicode("Niterói") == "NITEROI"
    assert normalize_string_unicode("Praça Seca - Jacarepaguá") == "PRACA SECA - JACAREPAGUA"
    assert normalize_string_unicode("Élcio de Queiroz") == "ELCIO DE QUEIROZ"


def test_dual_name_preservation():
    dual = create_dual_name_entry("São Gonçalo")
    assert dual["original_name"] == "São Gonçalo"
    assert dual["normalized_name"] == "SAO GONCALO"

    dual_empty = create_dual_name_entry("")
    assert dual_empty["original_name"] is None
    assert dual_empty["normalized_name"] is None


def test_entity_normalization_helpers():
    # Pessoa
    pers = normalize_name("Rogério Lemgruber")
    assert pers["original_name"] == "Rogério Lemgruber"
    assert pers["normalized_name"] == "ROGERIO LEMGRUBER"

    # Localização
    loc = normalize_location("Complexo da Maré")
    assert loc["original_name"] == "Complexo da Maré"
    assert loc["normalized_name"] == "COMPLEXO DA MARE"

    # Organização
    org = normalize_organization("Comando Vermelho")
    assert org["original_name"] == "Comando Vermelho"
    assert org["normalized_name"] == "COMANDO VERMELHO"


def test_date_normalization_formats():
    # ISO YYYY-MM-DD
    dt, yr, exact = normalize_date("1981-04-30")
    assert dt == "1981-04-30"
    assert yr == 1981
    assert exact is True

    # BR DD/MM/YYYY
    dt, yr, exact = normalize_date("15/03/1983")
    assert dt == "1983-03-15"
    assert yr == 1983
    assert exact is True

    # Apenas Ano
    dt, yr, exact = normalize_date("1975")
    assert dt == "1975-01-01"
    assert yr == 1975
    assert exact is False

    # Aproximado
    dt, yr, exact = normalize_date("década de 1970")
    assert yr == 1970
    assert exact is False

    # Desconhecido
    dt, yr, exact = normalize_date("s/d")
    assert dt is None
    assert yr is None
    assert exact is False
