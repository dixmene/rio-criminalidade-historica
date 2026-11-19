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

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import lru_cache
import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


VALID_DISCOURSE_TYPES = frozenset({
    "dado_documental",
    "fala_pesquisador",
    "narracao_documental",
    "fala_entrevistado",
    "opiniao_editorial",
})

VALID_CLAIM_TYPES = frozenset({
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
    "descricao_narrativa",
})

VALID_CONFIDENCE_LEVELS = frozenset({
    "confirmado",
    "provavel",
    "conflitante",
    "nao_verificado",
})

VALID_STANCES = frozenset({
    "apoia",
    "contesta",
    "matiza",
    "menciona",
})

# Precompiled regexes & ASCII translation table for fast normalization
_NON_WORD_SPACE_RE = re.compile(r"[^\w\s]")
_ELLIPSIS_RE = re.compile(r"\[\.\.\.\]|\.\.\.")

# Maps every ASCII non-[a-zA-Z0-9_\s] character to space, and lowercases A-Z
_ASCII_NORM_TABLE = str.maketrans({
    i: (chr(i).lower() if (chr(i).isalnum() or chr(i) == "_" or chr(i).isspace()) else " ")
    for i in range(128)
})

# Character histogram lookup table for exact SequenceMatcher.quick_ratio upper-bound pruning:
# 0..25 -> 'a'..'z', 26..35 -> '0'..'9', 36 -> ' ', 37 -> '_', 38 -> other unicode word chars
_NUM_BUCKETS = 39
_SPACE_BUCKET = 36
_UNDERSCORE_BUCKET = 37
_OTHER_BUCKET = 38

_ASCII_BUCKET_LUT = np.full(128, _OTHER_BUCKET, dtype=np.int32)
for _c in range(ord("a"), ord("z") + 1):
    _ASCII_BUCKET_LUT[_c] = _c - ord("a")
for _c in range(ord("0"), ord("9") + 1):
    _ASCII_BUCKET_LUT[_c] = 26 + (_c - ord("0"))
_ASCII_BUCKET_LUT[ord(" ")] = _SPACE_BUCKET
_ASCII_BUCKET_LUT[ord("_")] = _UNDERSCORE_BUCKET


def normalize_text(text: str) -> str:
    """Normaliza texto removendo pontuação, diacríticos e múltiplos espaços."""
    if not text:
        return ""
    if text.isascii():
        return " ".join(text.translate(_ASCII_NORM_TABLE).split())

    # Remove acentuação via decomposição NFKD
    nfkd = unicodedata.normalize("NFKD", text)
    clean = "".join(c for c in nfkd if not unicodedata.combining(c))
    if clean.isascii():
        return " ".join(clean.translate(_ASCII_NORM_TABLE).split())

    clean = _NON_WORD_SPACE_RE.sub(" ", clean.lower())
    return " ".join(clean.split())


def _char_histogram(text: str) -> np.ndarray:
    """Computes a 39-bucket character frequency vector for upper-bound pruning."""
    hist = np.zeros(_NUM_BUCKETS, dtype=np.int32)
    if not text:
        return hist
    if text.isascii():
        codes = np.frombuffer(text.encode("ascii"), dtype=np.uint8)
        buckets = _ASCII_BUCKET_LUT[codes]
        return np.bincount(buckets, minlength=_NUM_BUCKETS).astype(np.int32, copy=False)

    for ch in text:
        code = ord(ch)
        if code < 128:
            hist[_ASCII_BUCKET_LUT[code]] += 1
        else:
            hist[_OTHER_BUCKET] += 1
    return hist


@dataclass(frozen=True)
class _TranscriptIndex:
    norm_text: str
    words: Tuple[str, ...]
    word_char_cumsum: np.ndarray  # shape: (len(words) + 1, _NUM_BUCKETS), int32


@lru_cache(maxsize=32)
def _get_transcript_index(transcript_text: str) -> _TranscriptIndex:
    """Normalizes, tokenizes and builds cumulative character histograms for a transcript."""
    norm_text = normalize_text(transcript_text)
    words = tuple(norm_text.split())
    n_words = len(words)

    cumsum = np.zeros((n_words + 1, _NUM_BUCKETS), dtype=np.int32)
    if n_words > 0:
        if norm_text.isascii():
            # Vectorized single-pass word-boundary prefix sum over ASCII bytes
            raw = np.frombuffer(norm_text.encode("ascii"), dtype=np.uint8)
            space_positions = np.flatnonzero(raw == 32)
            # Assign each byte to its word index (0..n_words-1)
            word_ids = np.zeros(len(raw), dtype=np.int32)
            if len(space_positions) > 0:
                word_ids[space_positions + 1] = 1
                np.cumsum(word_ids, out=word_ids)
                non_space_mask = raw != 32
                non_space_words = word_ids[non_space_mask]
                non_space_buckets = _ASCII_BUCKET_LUT[raw[non_space_mask]]
            else:
                non_space_words = word_ids
                non_space_buckets = _ASCII_BUCKET_LUT[raw]

            flat_idx = non_space_words * _NUM_BUCKETS + non_space_buckets
            counts = np.bincount(flat_idx, minlength=n_words * _NUM_BUCKETS).reshape(n_words, _NUM_BUCKETS)
            np.cumsum(counts, axis=0, out=cumsum[1:])
        else:
            counts = np.zeros((n_words, _NUM_BUCKETS), dtype=np.int32)
            for idx, w in enumerate(words):
                counts[idx] = _char_histogram(w)
            np.cumsum(counts, axis=0, out=cumsum[1:])

    return _TranscriptIndex(norm_text=norm_text, words=words, word_char_cumsum=cumsum)


def _build_lcs_masks(needle: str) -> Dict[str, int]:
    """Builds character bitmasks for bit-parallel Allison-Dix LCS."""
    masks: Dict[str, int] = {}
    bit = 1
    for ch in needle:
        masks[ch] = masks.get(ch, 0) | bit
        bit <<= 1
    return masks


def _bit_parallel_lcs_len(window: str, masks: Dict[str, int]) -> int:
    """
    Computes exact Longest Common Subsequence length using bit-parallel
    operations over Python's C arbitrary-precision integers.

    Every matching-block decomposition of difflib.SequenceMatcher is a valid
    common subsequence, so `2 * lcs / (len(a) + len(b)) >= SequenceMatcher.ratio()`
    always holds unconditionally (zero false negatives).
    """
    s = 0
    get = masks.get
    for ch in window:
        m = get(ch, 0)
        if m:
            u = s | m
            s = u & ~(u - ((s << 1) | 1))
    return s.bit_count()


def _best_fuzzy_window_ratio(
    needle: str,
    needle_words: List[str],
    index: _TranscriptIndex,
    min_similarity: float,
) -> float:
    """
    Finds the best sliding-window SequenceMatcher ratio for `needle` over `index`.

    Uses a two-stage exact upper-bound cascade:
      1. Vectorized NumPy cumulative character-histogram upper bound (= quick_ratio).
      2. Bit-parallel exact LCS upper bound (order-preserving, >= SequenceMatcher.ratio()).
    Both bounds are mathematically guaranteed >= SequenceMatcher.ratio(), preserving
    100% recall while eliminating unnecessary O(L^2) SequenceMatcher DP evaluations.
    """
    window_size = len(needle_words)
    n_words = len(index.words)
    if window_size == 0 or n_words == 0:
        return 0.0

    step = max(1, window_size // 4)
    starts = np.arange(0, max(1, n_words - window_size + 1), step, dtype=np.int32)
    ends = np.minimum(starts + window_size, n_words)

    win_hist = index.word_char_cumsum[ends] - index.word_char_cumsum[starts]
    win_hist[:, _SPACE_BUCKET] = np.maximum(0, ends - starts - 1)
    win_lens = win_hist.sum(axis=1)

    needle_hist = _char_histogram(needle)
    needle_len = len(needle)
    matches = np.minimum(win_hist, needle_hist).sum(axis=1)
    upper_bounds = (2.0 * matches) / (needle_len + win_lens)

    # Reuse one SequenceMatcher instance with b=needle (builds b2j index once)
    matcher = SequenceMatcher(None, "", needle)
    words = index.words
    lcs_masks = _build_lcs_masks(needle)
    best_ratio = 0.0
    best_rejected_window: Optional[str] = None
    best_rejected_lcs_ub = 0.0

    candidate_indices = np.flatnonzero(upper_bounds >= min_similarity)
    if len(candidate_indices) > 0:
        order = candidate_indices[np.argsort(-upper_bounds[candidate_indices])]
        for idx in order:
            if upper_bounds[idx] <= best_ratio:
                break
            s = int(starts[idx])
            e = int(ends[idx])
            window_str = " ".join(words[s:e])
            lcs_ub = (2.0 * _bit_parallel_lcs_len(window_str, lcs_masks)) / (
                needle_len + len(window_str)
            )
            if lcs_ub < min_similarity:
                if best_ratio == 0.0 and lcs_ub > best_rejected_lcs_ub:
                    best_rejected_lcs_ub = lcs_ub
                    best_rejected_window = window_str
                continue
            if lcs_ub <= best_ratio:
                continue
            matcher.set_seq1(window_str)
            r = matcher.ratio()
            if r > best_ratio:
                best_ratio = r
                if best_ratio >= 0.95:
                    break
        if best_ratio > 0.0:
            return best_ratio
        if best_rejected_window is not None:
            matcher.set_seq1(best_rejected_window)
            return matcher.ratio()
        return 0.0

    # No window can meet min_similarity; score top few upper-bound windows for diagnostics
    top_k = min(3, len(upper_bounds))
    top_indices = np.argpartition(-upper_bounds, top_k - 1)[:top_k]
    for idx in top_indices:
        if upper_bounds[idx] <= best_ratio:
            continue
        s = int(starts[idx])
        e = int(ends[idx])
        matcher.set_seq1(" ".join(words[s:e]))
        r = matcher.ratio()
        if r > best_ratio:
            best_ratio = r
    return best_ratio


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
        min_similarity: float = 0.75,
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
                "error": "Campo 'excerpt' está vazio ou ausente.",
            }

        if not transcript_text or not transcript_text.strip():
            return {
                "valid": False,
                "match_type": "no_transcript",
                "similarity": 0.0,
                "error": "Transcrição do documento não fornecida para validação.",
            }

        norm_excerpt = normalize_text(excerpt)
        index = _get_transcript_index(transcript_text)
        norm_transcript = index.norm_text

        # 1. Correspondência exata de substring direta
        if norm_excerpt in norm_transcript:
            return {
                "valid": True,
                "match_type": "exact",
                "similarity": 1.0,
                "error": None,
            }

        # 2. Se a citação contém elipses (... ou [...]), valida cada cláusula sequencialmente
        if "..." in excerpt or "[...]" in excerpt:
            norm_clauses = [
                nc
                for raw_c in _ELLIPSIS_RE.split(excerpt)
                if len(nc := normalize_text(raw_c)) >= 8
            ]

            if norm_clauses:
                all_clauses_valid = True
                last_pos = -1
                clause_sims: List[float] = []

                for norm_c in norm_clauses:
                    pos = norm_transcript.find(norm_c, max(0, last_pos))
                    if pos != -1:
                        last_pos = pos + len(norm_c)
                        clause_sims.append(1.0)
                    else:
                        best_c_ratio = _best_fuzzy_window_ratio(
                            norm_c, norm_c.split(), index, min_similarity
                        )
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
                        "error": None,
                    }

        # 3. Busca aproximada por janelas deslizantes para tolerar pequenas variações da transcrição ASR
        excerpt_words = norm_excerpt.split()
        if not excerpt_words or not index.words:
            return {
                "valid": False,
                "match_type": "none",
                "similarity": 0.0,
                "error": "Excerto não pôde ser tokenizado.",
            }

        best_ratio = _best_fuzzy_window_ratio(
            norm_excerpt, excerpt_words, index, min_similarity
        )

        if best_ratio >= min_similarity:
            return {
                "valid": True,
                "match_type": "fuzzy",
                "similarity": round(best_ratio, 3),
                "error": None,
            }

        return {
            "valid": False,
            "match_type": "none",
            "similarity": round(best_ratio, 3),
            "error": (
                f"Citação literal não encontrada no documento original "
                f"(similaridade máxima: {best_ratio:.2f} < {min_similarity:.2f})."
            ),
        }

    @staticmethod
    def validate_timestamp(
        timestamp_str: str,
        duration_seconds: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Valida formato do timestamp e se está dentro do limite da duração."""
        seconds = parse_timestamp_seconds(timestamp_str)
        if seconds is None:
            return {
                "valid": False,
                "seconds": None,
                "error": f"Formato de timestamp inválido: '{timestamp_str}'. Use 'MM:SS' ou 'HH:MM:SS'.",
            }

        if seconds < 0:
            return {
                "valid": False,
                "seconds": seconds,
                "error": f"Timestamp negativo ({seconds}s) não é permitido.",
            }

        if duration_seconds is not None and duration_seconds > 0:
            # Tolerância de 5 segundos para eventuais descompassos de fim de vídeo
            if seconds > (duration_seconds + 5.0):
                return {
                    "valid": False,
                    "seconds": seconds,
                    "error": (
                        f"Timestamp {timestamp_str} ({seconds:.1f}s) excede a duração total "
                        f"do vídeo ({duration_seconds:.1f}s)."
                    ),
                }

        return {
            "valid": True,
            "seconds": seconds,
            "error": None,
        }

    @classmethod
    def validate_claim(
        cls,
        claim_data: Dict[str, Any],
        transcript_text: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        require_transcript: bool = False,
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
            errors.append(f"Tipo de claim inválido: '{claim_type}'. Válidos: {sorted(VALID_CLAIM_TYPES)}")

        # Validação da postura (stance)
        stance = claim_data.get("stance", "apoia")
        if stance not in VALID_STANCES:
            errors.append(f"Postura inválida: '{stance}'. Válidas: {sorted(VALID_STANCES)}")

        # Validação do nível de confiança
        confidence = claim_data.get("confidence_level", "provavel")
        if confidence not in VALID_CONFIDENCE_LEVELS:
            errors.append(
                f"Nível de confiança inválido: '{confidence}'. Válidos: {sorted(VALID_CONFIDENCE_LEVELS)}"
            )

        # Validação da tipologia de discurso
        discourse = claim_data.get("tipo_discurso")
        if discourse and discourse not in VALID_DISCOURSE_TYPES:
            warnings.append(
                f"Tipo de discurso não padronizado: '{discourse}'. Recomendados: {sorted(VALID_DISCOURSE_TYPES)}"
            )

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
                warnings.append(
                    f"Citação confirmada por similaridade aproximada ({excerpt_res['similarity']:.1%})."
                )
        elif require_transcript:
            errors.append("Transcrição obrigatória não fornecida para validação anti-alucinação.")

        is_valid = len(errors) == 0

        return {
            "is_valid": is_valid,
            "status": "ACCEPTED" if is_valid else "REJECTED",
            "errors": errors,
            "warnings": warnings,
            "timestamp_validation": timestamp_res,
            "excerpt_validation": excerpt_res,
        }
