import calendar
from datetime import date
import re
from typing import Any, Dict, Optional, Tuple

from src.utils.unicode_normalization import create_dual_name_entry, normalize_string_unicode

UNKNOWN_SENTINEL_VALUES = frozenset({
    "",
    " ",
    "n/a",
    "na",
    "null",
    "none",
    "desconhecido",
    "nao informado",
    "não informado",
    "não consta",
    "nao consta",
    "-",
    "--",
    "s/d",
    "sem data",
    "indeterminado",
})

PT_MONTHS: Dict[str, int] = {
    "janeiro": 1,
    "fevereiro": 2,
    "marco": 3,
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}

# Precompiled temporal parsing regexes
_ISO_DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
_BR_DATE_RE = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
_EXTENSO_DATE_RE = re.compile(r"(\d{1,2})\s+de\s+([a-zà-ÿ]+)\s+de\s+(\d{4})", re.IGNORECASE)
_MONTH_YEAR_RE = re.compile(r"([a-zà-ÿ]+)\s+de\s+(\d{4})", re.IGNORECASE)
_YM_RE = re.compile(r"(\d{4})-(\d{2})")
_DECADE_RE = re.compile(r"d[ée]cada(?:\s+de)?\s+((?:19|20)\d0)")
_APPROX_YEAR_RE = re.compile(r"(?:c\.?|aprox\.?|aproximadamente)\s*(19\d{2}|20\d{2})")
_YEAR_RE = re.compile(r"(19\d{2}|20\d{2})")
_ANY_YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")


def normalize_nulls(value: Any) -> Optional[Any]:
    """
    Regra ZERO vs. DESCONHECIDO (NULL).

    Zero confirmado continua sendo 0; ausência, indeterminação ou sentinelas
    documentais equivalentes tornam-se None. Nenhuma ausência é convertida em zero.
    """
    if value is None:
        return None

    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned == "0":
            return 0
        if cleaned.lower() in UNKNOWN_SENTINEL_VALUES:
            return None
        if cleaned.isdigit():
            return int(cleaned)
        return cleaned

    if isinstance(value, (int, float)):
        if isinstance(value, float) and value != value:
            return None
        return value

    return value


def _normalize_dual_entity(raw_value: Optional[str]) -> Dict[str, Optional[str]]:
    if raw_value is None:
        return {"original_name": None, "normalized_name": None}
    val = normalize_nulls(raw_value)
    if val is None:
        return {"original_name": None, "normalized_name": None}
    return create_dual_name_entry(val if isinstance(val, str) else str(val))


def normalize_name(name: Optional[str]) -> Dict[str, Optional[str]]:
    """Normaliza nome de pessoa preservando a grafia original."""
    return _normalize_dual_entity(name)


def normalize_location(location: Optional[str]) -> Dict[str, Optional[str]]:
    """Normaliza topônimo, bairro ou município preservando a grafia original."""
    return _normalize_dual_entity(location)


def normalize_organization(org_name: Optional[str]) -> Dict[str, Optional[str]]:
    """Normaliza nome de organização preservando a grafia original."""
    return _normalize_dual_entity(org_name)


def _year_bounds(year: int) -> Tuple[str, str]:
    return f"{year:04d}-01-01", f"{year:04d}-12-31"


def _month_bounds(year: int, month: int) -> Tuple[str, str]:
    last_day = calendar.monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-{last_day:02d}"


def _temporal_result(
    date_start: Optional[str],
    date_end: Optional[str],
    year: Optional[int],
    temporal_precision: str,
    exact_date: bool,
    date_is_estimated: bool,
) -> Dict[str, Any]:
    return {
        "date_start": date_start,
        "date_end": date_end,
        "year": year,
        "temporal_precision": temporal_precision,
        "exact_date": exact_date,
        "date_is_estimated": date_is_estimated,
    }


def _unknown_temporal() -> Dict[str, Any]:
    return _temporal_result(None, None, None, "desconhecido", False, False)


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
        return _unknown_temporal()

    cleaned = normalize_nulls(value)
    if cleaned is None:
        return _unknown_temporal()

    # Fast path for plain integer year (normalize_nulls converts "1975" -> 1975)
    if isinstance(cleaned, int):
        if 1900 <= cleaned <= 2099:
            start, end = _year_bounds(cleaned)
            return _temporal_result(start, end, cleaned, "ano", False, False)
        return _unknown_temporal()

    s = str(cleaned).strip().lower()
    slen = len(s)

    # Fast-path structural dispatch before general regexes
    if slen == 10 and s[4] == "-" and s[7] == "-":
        iso_match = _ISO_DATE_RE.fullmatch(s)
        if iso_match:
            y, m, d = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
            date(y, m, d)
            iso = f"{y:04d}-{m:02d}-{d:02d}"
            return _temporal_result(iso, iso, y, "dia", True, False)

    if "/" in s:
        br_match = _BR_DATE_RE.fullmatch(s)
        if br_match:
            d, m, y = int(br_match.group(1)), int(br_match.group(2)), int(br_match.group(3))
            date(y, m, d)
            iso = f"{y:04d}-{m:02d}-{d:02d}"
            return _temporal_result(iso, iso, y, "dia", True, False)

    if slen == 7 and s[4] == "-":
        ym_match = _YM_RE.fullmatch(s)
        if ym_match:
            y, m = int(ym_match.group(1)), int(ym_match.group(2))
            start, end = _month_bounds(y, m)
            return _temporal_result(start, end, y, "mes", False, False)

    if slen == 4:
        year_match = _YEAR_RE.fullmatch(s)
        if year_match:
            y = int(year_match.group(1))
            start, end = _year_bounds(y)
            return _temporal_result(start, end, y, "ano", False, False)

    if " de " in s:
        extenso_match = _EXTENSO_DATE_RE.fullmatch(s)
        if extenso_match:
            m = PT_MONTHS.get(extenso_match.group(2))
            if m:
                d = int(extenso_match.group(1))
                y = int(extenso_match.group(3))
                date(y, m, d)
                iso = f"{y:04d}-{m:02d}-{d:02d}"
                return _temporal_result(iso, iso, y, "dia", True, False)

        month_year_match = _MONTH_YEAR_RE.fullmatch(s)
        if month_year_match:
            m = PT_MONTHS.get(month_year_match.group(1))
            if m:
                y = int(month_year_match.group(2))
                start, end = _month_bounds(y, m)
                return _temporal_result(start, end, y, "mes", False, False)

    if s.startswith("d"):
        decade_match = _DECADE_RE.fullmatch(s)
        if decade_match:
            decade_start = int(decade_match.group(1))
            start, end = _year_bounds(decade_start)[0], _year_bounds(decade_start + 9)[1]
            return _temporal_result(start, end, decade_start, "decada", False, False)

    if s.startswith(("c", "a")):
        approx_match = _APPROX_YEAR_RE.fullmatch(s)
        if approx_match:
            y = int(approx_match.group(1))
            start, end = _year_bounds(y)
            return _temporal_result(start, end, y, "aproximado", False, True)

    # Conserva o comportamento legado de recuperar um ano embutido em expressões livres,
    # mas marca o resultado como aproximado em vez de apresentá-lo como preciso.
    any_year = _ANY_YEAR_RE.search(s)
    if any_year:
        y = int(any_year.group(1))
        start, end = _year_bounds(y)
        return _temporal_result(start, end, y, "aproximado", False, True)

    return _unknown_temporal()


def normalize_date(date_str: Optional[str]) -> Tuple[Optional[str], Optional[int], bool]:
    """
    Compatibilidade retroativa para consumidores legados.

    Para novos fluxos, prefira normalize_temporal_expression(), que também
    retorna date_end e a precisão temporal explicitamente.
    """
    normalized = normalize_temporal_expression(date_str)
    return normalized["date_start"], normalized["year"], normalized["exact_date"]
