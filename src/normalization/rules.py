import re
from typing import Any, Optional, Dict, Tuple
from src.utils.unicode_normalization import normalize_string_unicode, create_dual_name_entry


UNKNOWN_SENTINEL_VALUES = {
    "", " ", "n/a", "na", "null", "none", "desconhecido", 
    "nao informado", "não informado", "não consta", "nao consta", 
    "-", "--", "s/d", "sem data", "indeterminado"
}

PT_MONTHS = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "março": 3,
    "abril": 4, "maio": 5, "junho": 6, "julho": 7,
    "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
}


def normalize_nulls(value: Any) -> Optional[Any]:
    """
    REGRA 1 — ZERO vs. DESCONHECIDO (NULL)
    
    Regra absoluta:
    - 0 numérico (ou string "0") representa contagem real comprovada -> retorna 0.
    - Valores vazios, 'N/A', 'desconhecido', etc. -> retorna None (NULL no banco).
    - Não transforma desconhecido em 0, nem 0 em None.
    """
    if value is None:
        return None

    # Se for tipo numérico inteiro ou float (mesmo 0 ou 0.0)
    if isinstance(value, (int, float)):
        # Trata NaN de float
        if isinstance(value, float) and value != value:  # math.isnan
            return None
        return value

    # Se for string
    if isinstance(value, str):
        cleaned = value.strip()
        # Se for expressamente a string "0"
        if cleaned == "0":
            return 0
        
        if cleaned.lower() in UNKNOWN_SENTINEL_VALUES:
            return None
        
        # Tenta converter string numérica (ex: "42")
        if cleaned.isdigit():
            return int(cleaned)

        return cleaned

    return value


def normalize_name(name: Optional[str]) -> Dict[str, Optional[str]]:
    """Normaliza nome de pessoa preservando original."""
    if name is None:
        return {"original_name": None, "normalized_name": None}
    val = normalize_nulls(name)
    if val is None:
        return {"original_name": None, "normalized_name": None}
    return create_dual_name_entry(str(val))


def normalize_location(location: Optional[str]) -> Dict[str, Optional[str]]:
    """Normaliza topônimo, bairro ou município preservando original."""
    if location is None:
        return {"original_name": None, "normalized_name": None}
    val = normalize_nulls(location)
    if val is None:
        return {"original_name": None, "normalized_name": None}
    return create_dual_name_entry(str(val))


def normalize_organization(org_name: Optional[str]) -> Dict[str, Optional[str]]:
    """Normaliza nome de facção, milícia ou instituição preservando original."""
    if org_name is None:
        return {"original_name": None, "normalized_name": None}
    val = normalize_nulls(org_name)
    if val is None:
        return {"original_name": None, "normalized_name": None}
    return create_dual_name_entry(str(val))


def normalize_date(date_str: Optional[str]) -> Tuple[Optional[str], Optional[int], bool]:
    """
    Normaliza representações de datas históricas.
    Retorna: (date_start_str, year_int, exact_date_bool)
    
    Suporta:
    - ISO YYYY-MM-DD
    - BR DD/MM/YYYY
    - Português por extenso: '14 de novembro de 1982' -> ('1982-11-14', 1982, True)
    - Português mês/ano: 'maio de 1978' -> ('1978-05-01', 1978, False)
    - Apenas ano: '1975' -> ('1975-01-01', 1975, False)
    """
    if date_str is None:
        return (None, None, False)
    
    val = normalize_nulls(date_str)
    if val is None:
        return (None, None, False)
    
    s = str(val).strip()

    # Formato ISO YYYY-MM-DD
    iso_match = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', s)
    if iso_match:
        year = int(iso_match.group(1))
        return (s, year, True)

    # Formato Brasileiro DD/MM/YYYY
    br_match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', s)
    if br_match:
        day, month, year = br_match.groups()
        iso = f"{year}-{int(month):02d}-{int(day):02d}"
        return (iso, int(year), True)

    # Formato por extenso: '14 de novembro de 1982'
    extenso_match = re.match(r'^(\d{1,2})\s+de\s+([a-zA-ZçÇ]+)\s+de\s+(\d{4})$', s, re.IGNORECASE)
    if extenso_match:
        day = int(extenso_match.group(1))
        month_name = extenso_match.group(2).lower()
        year = int(extenso_match.group(3))
        if month_name in PT_MONTHS:
            month = PT_MONTHS[month_name]
            iso = f"{year}-{month:02d}-{day:02d}"
            return (iso, year, True)

    # Formato mês e ano por extenso: 'maio de 1978'
    mes_ano_match = re.match(r'^([a-zA-ZçÇ]+)\s+de\s+(\d{4})$', s, re.IGNORECASE)
    if mes_ano_match:
        month_name = mes_ano_match.group(1).lower()
        year = int(mes_ano_match.group(2))
        if month_name in PT_MONTHS:
            month = PT_MONTHS[month_name]
            iso = f"{year}-{month:02d}-01"
            return (iso, year, False)

    # Formato Mês/Ano numérico (YYYY-MM)
    my_match = re.match(r'^(\d{4})-(\d{2})$', s)
    if my_match:
        year = int(my_match.group(1))
        return (f"{s}-01", year, False)

    # Formato Apenas Ano (YYYY)
    y_match = re.match(r'^(\d{4})$', s)
    if y_match:
        year = int(y_match.group(1))
        return (f"{year}-01-01", year, False)

    # Tenta extrair qualquer ano de 4 dígitos (ex: "c. 1982", "década de 1970")
    any_year = re.search(r'\b(19\d{2}|20\d{2})\b', s)
    if any_year:
        year = int(any_year.group(1))
        return (f"{year}-01-01", year, False)

    return (s, None, False)
