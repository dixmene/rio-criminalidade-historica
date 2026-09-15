from src.normalization.rules import normalize_temporal_expression


def test_exact_day_has_same_start_and_end():
    result = normalize_temporal_expression("15/03/1983")
    assert result["date_start"] == "1983-03-15"
    assert result["date_end"] == "1983-03-15"
    assert result["temporal_precision"] == "dia"
    assert result["exact_date"] is True
    assert result["date_is_estimated"] is False


def test_month_does_not_become_first_day_only():
    result = normalize_temporal_expression("maio de 1978")
    assert result["date_start"] == "1978-05-01"
    assert result["date_end"] == "1978-05-31"
    assert result["temporal_precision"] == "mes"
    assert result["exact_date"] is False


def test_year_represents_full_year():
    result = normalize_temporal_expression("1975")
    assert result["date_start"] == "1975-01-01"
    assert result["date_end"] == "1975-12-31"
    assert result["temporal_precision"] == "ano"
    assert result["exact_date"] is False


def test_approximate_year_is_marked_as_estimated():
    result = normalize_temporal_expression("c. 1982")
    assert result["year"] == 1982
    assert result["temporal_precision"] == "aproximado"
    assert result["date_is_estimated"] is True


def test_unknown_date_is_not_fabricated():
    result = normalize_temporal_expression("não informado")
    assert result["date_start"] is None
    assert result["date_end"] is None
    assert result["year"] is None
    assert result["temporal_precision"] == "desconhecido"
