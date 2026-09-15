import calendar
import re
from typing import Any, Dict, Optional, Tuple

from src.utils.unicode_normalization import normalize_string_unicode, create_dual_name_entry


UNKNOWN_SENTINEL_VALUES = {
    "", " ", "n/a", "na", "null", "none", "desconhecido",
    "nao informado", "não informado", "não consta", "nao consta",
    "-", "--", "s/d", "sem data", "indeterminado"
}

PT_MONTHS = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "março": 3,
    "abril": 4, "maio": 5, "junho": 6, "julho": 7,
    "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}


def normalize_nulls(value: Any) -> Optional[Any]:
    """
    Regra ZERO vs. DESCONHECIDO (NULL).

    Zero confirmado continua sendo 0; ausência, indeterminação ou sentinelas
    documentais equivalentes tornam-se None. Nenhuma ausência é convertida em zero.
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        if isinstance(value, float) and value != value:
            return None
        return value

    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned == "0":
            return 0
        if cleaned.lower() in UNKNOWN_SENTINEL_VALUES:
            return None
        if cleaned.isdigit():
            return int(cleaned)
        return cleaned

    return value


def normalize_name(name: Optional[str]) -> Dict[str, Optional[str]]:
    """Normaliza nome de pessoa preservando a grafia original."""
    if name is None:
        return {"original_name": None, "normalized_name": None}
    val = normalize_nulls(name)
    if val is None:
        return {"original_name": None, "normalized_name": None}
    return create_dual_name_entry(str(val))


def normalize_location(location: Optional[str]) -> Dict[str, Optional[str]]:
    """Normaliza topônimo, bairro ou município preservando a grafia original."""
    if location is None:
        return {"original_name": None, "normalized_name": None}
    val = normalize_nulls(location)
    if val is None:
        return {"original_name": None, "normalized_name": None}
    return create_dual_name_entry(str(val))


def normalize_organization(org_name: Optional[str]) -> Dict[str, Optional[str]]:
    """Normaliza nome de organização preservando a grafia original."""
    if org_name is None:
        return {"original_name": None, "normalized_name": None}
    val = normalize_nulls(org_name)
    if val is None:
        return {"original_name": None, "normalized_name": None}
    return create_dual_name_entry(str(val))


def _year_bounds(year: int) -> Tuple[str, str]:
    return f"{year:04d}-01-01", f"{year:04d}-12-31"


def _month_bounds(year: int, month: int) -> Tuple[str, str]:
    last_day = calendar.monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-{last_day:02d}"


def normalize_temporal_expression(value: Optional[str]) -> Dict[str, Any]:
    """
    Converte uma expressão temporal humana em um intervalo explícito sem
    fingir precisão documental.

    Retorna:
        date_start: limite inferior do intervalo (ISO ou None)
        date_end: limite superior do intervalo (ISO ou None)
        year: ano de referência, quando recuperável
        temporal_precision: dia | mes | ano | decada | aproximado | desconhecido
        exact_date: True apenas para dia/mês/ano explicitamente informados
        date_is_estimated: True quando o texto é aproximado (ex.: "c. 1982")
    """
    if value is None:
        return {
            "date_start": None,
            "date_end": None,
            "year": None,
            "temporal_precision": "desconhecido",
            "exact_date": False,
            "date_is_estimated": False,
        }

    cleaned = normalize_nulls(value)
    if cleaned is None:
        return {
            "date_start": None,
            "date_end": None,
            "year": None,
            "temporal_precision": "desconhecido",
            "exact_date": False,
            "date_is_estimated": False,
        }

    s = str(cleaned).strip().lower()

    # Dia exato: YYYY-MM-DD
    iso_match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if iso_match:
        y, m, d = map(int, iso_match.groups())
        # calendar.monthrange valida mês/dia indiretamente quando a data é usada.
        from datetime import date
        date(y, m, d)
        iso = f"{y:04d}-{m:02d}-{d:02d}"
        return {
            "date_start": iso,
            "date_end": iso,
            "year": y,
            "temporal_precision": "dia",
            "exact_date": True,
            "date_is_estimated": False,
        }

    br_match = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if br_match:
        d, m, y = map(int, br_match.groups())
        from datetime import date
        date(y, m, d)
        iso = f"{y:04d}-{m:02d}-{d:02d}"
        return {
            "date_start": iso,
            "date_end": iso,
            "year": y,
            "temporal_precision": "dia",
            "exact_date": True,
            "date_is_estimated": False,
        }

    extenso_match = re.fullmatch(
        r"(\d{1,2})\s+de\s+([a-zà-ÿ]+)\s+de\s+(\d{4})", s, re.IGNORECASE
    )
    if extenso_match:
        d = int(extenso_match.group(1))
        month_name = extenso_match.group(2)
        y = int(extenso_match.group(3))
        m = PT_MONTHS.get(month_name)
        if m:
            from datetime import date
            date(y, m, d)
            iso = f"{y:04d}-{m:02d}-{d:02d}"
            return {
                "date_start": iso,
                "date_end": iso,
                "year": y,
                "temporal_precision": "dia",
                "exact_date": True,
                "date_is_estimated": False,
            }

    month_year_match = re.fullmatch(r"([a-zà-ÿ]+)\s+de\s+(\d{4})", s, re.IGNORECASE)
    if month_year_match:
        m = PT_MONTHS.get(month_year_match.group(1))
        y = int(month_year_match.group(2))
        if m:
            start, end = _month_bounds(y, m)
            return {
                "date_start": start,
                "date_end": end,
                "year": y,
                "temporal_precision": "mes",
                "exact_date": False,
                "date_is_estimated": False,
            }

    ym_match = re.fullmatch(r"(\d{4})-(\d{2})", s)
    if ym_match:
        y, m = map(int, ym_match.groups())
        start, end = _month_bounds(y, m)
        return {
            "date_start": start,
            "date_end": end,
            "year": y,
            "temporal_precision": "mes",
            "exact_date": False,
            "date_is_estimated": False,
        }

    decade_match = re.fullmatch(r"d[ée]cada(?:\s+de)?\s+(?:19|20)(\d)0", s)
    if decade_match:
        decade_start = int(s[-4:])
        start, end = _year_bounds(decade_start)[0], _year_bounds(decade_start + 9)[1]
        return {
            "date_start": start,
            "date_end": end,
            "year": decade_start,
            "temporal_precision": "decada",
            "exact_date": False,
            "date_is_estimated": False,
        }

    approx_match = re.fullmatch(r"(?:c\.?|aprox\.?|aproximadamente)\s*(19\d{2}|20\d{2})", s)
    if approx_match:
        y = int(approx_match.group(1))
        start, end = _year_bounds(y)
        return {
            "date_start": start,
            "date_end": end,
            "year": y,
            "temporal_precision": "aproximado",
            "exact_date": False,
            "date_is_estimated": True,
        }

    year_match = re.fullmatch(r"(19\d{2}|20\d{2})", s)
    if year_match:
        y = int(year_match.group(1))
        start, end = _year_bounds(y)
        return {
            "date_start": start,
            "date_end": end,
            "year": y,
            "temporal_precision": "ano",
            "exact_date": False,
            "date_is_estimated": False,
        }

    # Conserva o comportamento legado de recuperar um ano embutido em expressões livres,
    # mas marca o resultado como aproximado em vez de apresentá-lo como preciso.
    any_year = re.search(r"\b(19\d{2}|20\d{2})\b", s)
    if any_year:
        y = int(any_year.group(1))
        start, end = _year_bounds(y)
        return {
            "date_start": start,
            "date_end": end,
            "year": y,
            "temporal_precision": "aproximado",
            "exact_date": False,
            "date_is_estimated": True,
        }

    return {
        "date_start": None,
        "date_end": None,
        "year": None,
        "temporal_precision": "desconhecido",
        "exact_date": False,
        "date_is_estimated": False,
    }


def normalize_date(date_str: Optional[str]) -> Tuple[Optional[str], Optional[int], bool]:
    """
    Compatibilidade retroativa para consumidores legados.

    Para novos fluxos, prefira normalize_temporal_expression(), que também
    retorna date_end e a precisão temporal explicitamente.
    """
    normalized = normalize_temporal_expression(date_str)
    return normalized["date_start"], normalized["year"], normalized["exact_date"]
