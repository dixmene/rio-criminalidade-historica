"""
Serviço de Validação Epistemológica e Anti-Alucinação de Claims Historiográficas
================================================================================

Este módulo é a barreira anti-alucinação do projeto. Nenhuma afirmação histórica
extraída de fontes secundárias, vídeos do YouTube ou transcrições de áudio pode ser
promovida a claim sem atender a critérios estritos de fidelidade documental:

Regras Metodológicas:
1. Fidelidade Textual (Verbatim Excerpt):
   O trecho literal da citação ('excerpt') DEVE existir na transcrição do documento.
   Afirmações com trechos forjados ou ausentes são sumariamente REJEITADAS.
2. Limites Temporais (Timestamp Range):
   O timestamp indicado ('08:14', etc.) DEVE estar contido no intervalo [0, duração]
   do conteúdo audiovisual analisado.
3. Tipologia de Discurso Válida:
   O trecho deve ser categorizado segundo a taxonomia documental:
   - 'dado_documental'
   - 'fala_pesquisador'
   - 'narracao_documental'
   - 'fala_entrevistado'
   - 'opiniao_editorial'
4. Tipologia de Claim Válida:
   Fatos, datas, autorias, territórios, baixas letais, relações de poder/estado, etc.
5. Padrão Anti-Falsa Precisão:
   Não transformar especulação ou narrativa retórica em "fato confirmado".
"""

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Dict, Any, List, Optional, Tuple


VALID_DISCOURSE_TYPES = {
    "dado_documental",
    "fala_pesquisador",
    "narracao_documental",
    "fala_entrevistado",
    "opiniao_editorial"
}

VALID_CLAIM_TYPES = {
    "fato",
    "data",
    "autoria",
    "territorio",
    "baixa_letal",
    "motivacao",
    "presenca_armada",
    "relacao_estado",
    "disputa_territorial",
    "interpretacao",
    "opiniao",
    "alegacao",
    "testemunho",
    "descricao_narrativa"
}

VALID_CONFIDENCE_LEVELS = {
    "confirmado",
    "provavel",
    "conflitante",
    "nao_verificado"
}

VALID_STANCES = {
    "apoia",
    "contesta",
    "matiza",
    "menciona"
}


def normalize_text(text: str) -> str:
    """Normaliza texto removendo pontuação, diacríticos e múltiplos espaços."""
    if not text:
        return ""
    # Remove acentuação
    nfkd = unicodedata.normalize("NFKD", text)
    clean = "".join([c for c in nfkd if not unicodedata.combining(c)])
    # Caixa baixa e substitui pontuação por espaço
    clean = clean.lower()
    clean = re.sub(r"[^\w\s]", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def parse_timestamp_seconds(timestamp_str: str) -> Optional[float]:
    """Converte string de timestamp (ex: '08:14', '01:23:45', '494s') em segundos."""
    if not timestamp_str:
        return None
    
    clean = timestamp_str.strip().lower().replace("s", "").replace("timestamp", "").strip()
    parts = clean.split(":")
    
    try:
        if len(parts) == 1:
            return float(parts[0])
        elif len(parts) == 2:
            mins, secs = parts
            return float(mins) * 60.0 + float(secs)
        elif len(parts) == 3:
            hrs, mins, secs = parts
            return float(hrs) * 3600.0 + float(mins) * 60.0 + float(secs)
        return None
    except ValueError:
        return None


class ClaimValidator:
    """Validador central de afirmações históricas com detecção de inconsistências e alucinações."""

    @staticmethod
    def validate_verbatim_excerpt(
        excerpt: str,
        transcript_text: str,
        min_similarity: float = 0.75
    ) -> Dict[str, Any]:
        """
        Verifica se a citação literal (excerpt) consta no texto da transcrição.
        Usa correspondência exata normalizada e fallback por similaridade de sequência.
        """
        if not excerpt or not excerpt.strip():
            return {
                "valid": False,
                "match_type": "missing",
                "similarity": 0.0,
                "error": "Campo 'excerpt' está vazio ou ausente."
            }

        if not transcript_text or not transcript_text.strip():
            return {
                "valid": False,
                "match_type": "no_transcript",
                "similarity": 0.0,
                "error": "Transcrição do documento não fornecida para validação."
            }

        norm_excerpt = normalize_text(excerpt)
        norm_transcript = normalize_text(transcript_text)

        # 1. Correspondência exata de substring direta
        if norm_excerpt in norm_transcript:
            return {
                "valid": True,
                "match_type": "exact",
                "similarity": 1.0,
                "error": None
            }

        # 2. Se a citação contém elipses (... ou [...]), valida cada cláusula sequencialmente
        has_ellipsis = "..." in excerpt or "[...]" in excerpt
        if has_ellipsis:
            clauses = [re.sub(r"\[\.\.\.\]|\.\.\.", "", c).strip() for c in re.split(r"\[\.\.\.\]|\.\.\.", excerpt)]
            clauses = [c for c in clauses if len(normalize_text(c)) >= 8]
            
            if clauses:
                all_clauses_valid = True
                last_pos = -1
                clause_sims = []
                
                for clause in clauses:
                    norm_c = normalize_text(clause)
                    pos = norm_transcript.find(norm_c, max(0, last_pos))
                    if pos != -1:
                        last_pos = pos + len(norm_c)
                        clause_sims.append(1.0)
                    else:
                        # Busca por janela deslizante
                        c_words = norm_c.split()
                        w_size = len(c_words)
                        t_words = norm_transcript.split()
                        best_c_ratio = 0.0
                        step = max(1, w_size // 4)
                        for i in range(0, max(1, len(t_words) - w_size + 1), step):
                            w_str = " ".join(t_words[i : i + w_size])
                            r = SequenceMatcher(None, norm_c, w_str).ratio()
                            if r > best_c_ratio:
                                best_c_ratio = r
                                if best_c_ratio >= 0.95:
                                    break
                        if best_c_ratio >= min_similarity:
                            clause_sims.append(best_c_ratio)
                        else:
                            all_clauses_valid = False
                            break
                
                if all_clauses_valid and clause_sims:
                    avg_sim = round(sum(clause_sims) / len(clause_sims), 3)
                    return {
                        "valid": True,
                        "match_type": "multi_clause_ellipsis",
                        "similarity": avg_sim,
                        "error": None
                    }

        # 3. Busca aproximada por janelas deslizantes para tolerar pequenas variações da transcrição ASR
        excerpt_words = norm_excerpt.split()
        transcript_words = norm_transcript.split()
        window_size = len(excerpt_words)

        if window_size == 0 or len(transcript_words) == 0:
            return {
                "valid": False,
                "match_type": "none",
                "similarity": 0.0,
                "error": "Excerto não pôde ser tokenizado."
            }

        best_ratio = 0.0
        # Amostragem em janelas de tamanho similar
        step = max(1, window_size // 4)
        for i in range(0, max(1, len(transcript_words) - window_size + 1), step):
            window_str = " ".join(transcript_words[i : i + window_size])
            ratio = SequenceMatcher(None, norm_excerpt, window_str).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                if best_ratio >= 0.95:
                    break

        if best_ratio >= min_similarity:
            return {
                "valid": True,
                "match_type": "fuzzy",
                "similarity": round(best_ratio, 3),
                "error": None
            }

        return {
            "valid": False,
            "match_type": "none",
            "similarity": round(best_ratio, 3),
            "error": f"Citação literal não encontrada no documento original (similaridade máxima: {best_ratio:.2f} < {min_similarity:.2f})."
        }

    @staticmethod
    def validate_timestamp(
        timestamp_str: str,
        duration_seconds: Optional[float] = None
    ) -> Dict[str, Any]:
        """Valida formato do timestamp e se está dentro do limite da duração."""
        seconds = parse_timestamp_seconds(timestamp_str)
        if seconds is None:
            return {
                "valid": False,
                "seconds": None,
                "error": f"Formato de timestamp inválido: '{timestamp_str}'. Use 'MM:SS' ou 'HH:MM:SS'."
            }

        if seconds < 0:
            return {
                "valid": False,
                "seconds": seconds,
                "error": f"Timestamp negativo ({seconds}s) não é permitido."
            }

        if duration_seconds is not None and duration_seconds > 0:
            # Tolerância de 5 segundos para eventuais descompassos de fim de vídeo
            if seconds > (duration_seconds + 5.0):
                return {
                    "valid": False,
                    "seconds": seconds,
                    "error": f"Timestamp {timestamp_str} ({seconds:.1f}s) excede a duração total do vídeo ({duration_seconds:.1f}s)."
                }

        return {
            "valid": True,
            "seconds": seconds,
            "error": None
        }

    @classmethod
    def validate_claim(
        cls,
        claim_data: Dict[str, Any],
        transcript_text: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        require_transcript: bool = False
    ) -> Dict[str, Any]:
        """
        Executa validação completa de uma asserção (Claim).
        Retorna relatório detalhado com aceitação ou rejeição justificada.
        """
        errors: List[str] = []
        warnings: List[str] = []

        statement = claim_data.get("statement", "").strip()
        if not statement:
            errors.append("Declaração da claim ('statement') é obrigatória e está vazia.")
        elif len(statement) < 10:
            warnings.append(f"Declaração muito curta ('{statement}'), pode faltar contexto histórico.")

        # Validação do tipo de claim
        claim_type = claim_data.get("claim_type", "fato")
        if claim_type not in VALID_CLAIM_TYPES:
            errors.append(f"Tipo de claim inválido: '{claim_type}'. Válidos: {sorted(list(VALID_CLAIM_TYPES))}")

        # Validação da postura (stance)
        stance = claim_data.get("stance", "apoia")
        if stance not in VALID_STANCES:
            errors.append(f"Postura inválida: '{stance}'. Válidas: {sorted(list(VALID_STANCES))}")

        # Validação do nível de confiança
        confidence = claim_data.get("confidence_level", "provavel")
        if confidence not in VALID_CONFIDENCE_LEVELS:
            errors.append(f"Nível de confiança inválido: '{confidence}'. Válidos: {sorted(list(VALID_CONFIDENCE_LEVELS))}")

        # Validação da tipologia de discurso
        discourse = claim_data.get("tipo_discurso")
        if discourse and discourse not in VALID_DISCOURSE_TYPES:
            warnings.append(f"Tipo de discurso não padronizado: '{discourse}'. Recomendados: {sorted(list(VALID_DISCOURSE_TYPES))}")

        # Validação de timestamp
        timestamp_str = claim_data.get("timestamp")
        timestamp_res = None
        if timestamp_str:
            timestamp_res = cls.validate_timestamp(timestamp_str, duration_seconds=duration_seconds)
            if not timestamp_res["valid"]:
                errors.append(timestamp_res["error"])

        # Validação de fidelidade textual (Anti-Alucinação)
        excerpt = claim_data.get("excerpt", "")
        excerpt_res = None
        if transcript_text:
            excerpt_res = cls.validate_verbatim_excerpt(excerpt, transcript_text)
            if not excerpt_res["valid"]:
                errors.append(excerpt_res["error"])
            elif excerpt_res["match_type"] == "fuzzy":
                warnings.append(f"Citação confirmada por similaridade aproximada ({excerpt_res['similarity']:.1%}).")
        elif require_transcript:
            errors.append("Transcrição obrigatória não fornecida para validação anti-alucinação.")

        is_valid = len(errors) == 0

        return {
            "is_valid": is_valid,
            "status": "ACCEPTED" if is_valid else "REJECTED",
            "errors": errors,
            "warnings": warnings,
            "timestamp_validation": timestamp_res,
            "excerpt_validation": excerpt_res
        }
