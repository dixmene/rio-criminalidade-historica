import unicodedata
import re
from typing import Optional, Dict


def normalize_string_unicode(text: Optional[str]) -> Optional[str]:
    """
    Remove acentos, converte para maiúsculas e remove espaços sobressalentes.
    Exemplo: 'São Gonçalo' -> 'SAO GONCALO'
             'João da Silva' -> 'JOAO DA SILVA'
    """
    if text is None:
        return None

    # Decomposição canônica (NFD) para isolar marcas diacríticas
    nfkd_form = unicodedata.normalize('NFD', text)
    # Remove marcas diacríticas (acentos)
    without_accents = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    # Limpa múltiplos espaços e converte para maiúsculo
    cleaned = re.sub(r'\s+', ' ', without_accents).strip().upper()
    return cleaned


def create_dual_name_entry(original_name: str) -> Dict[str, Optional[str]]:
    """
    Gera representação dual para preservar o dado histórico original e facilitar buscas.
    """
    if not original_name or not original_name.strip():
        return {
            "original_name": None,
            "normalized_name": None
        }
    
    cleaned_orig = original_name.strip()
    return {
        "original_name": cleaned_orig,
        "normalized_name": normalize_string_unicode(cleaned_orig)
    }
