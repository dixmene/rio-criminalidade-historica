"""
Módulo de Classificação Temática da Atividade Legislativa (CMRJ / ALERJ).
Implementa a Taxonomia de Pautas Sensíveis aos Mercados do Crime Organizado:
1. Transporte complementar (vans, mototáxis, itinerários)
2. Uso e ocupação do solo urbano (desafetação, anistia a loteamentos, entraves a demolição)
3. Monopólios de utilidades (botijão de gás/GLP, água mineral, internet/gatonet)
4. Comércio de sucata e reciclagem (ferros-velhos, fios de cobre, baterias)
5. Moções de aplauso e condecorações (homenagens a investigados/condenados)
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Pattern, Tuple


TAXONOMIA_PAUTAS_SENSIVEIS = {
    "transporte_complementar": {
        "nome": "Transporte Complementar e Alternativo",
        "descricao": "Proposições sobre vans, kombis, mototáxis, trajetos, permissões e fiscalização de transporte.",
        "peso": 1.0,
        "keywords": [
            r"\bvan\b", r"\bvans\b", r"\bkombi\b", r"\bkombis\b",
            r"\bmototaxi\b", r"\bmototaxis\b", r"\bmoto-taxi\b",
            r"\btransporte complementar\b", r"\btransporte alternativo\b",
            r"\blotacao\b", r"\bitinerario de van\b", r"\bpermissao de transporte\b",
        ],
    },
    "uso_solo_urbano": {
        "nome": "Uso e Ocupação do Solo Urbano / Grilagem",
        "descricao": "Proposições de desafetação de áreas públicas, anistia a loteamentos irregulares e suspensão de demolições.",
        "peso": 1.0,
        "keywords": [
            r"\bdesafetacao\b", r"\bdesafetar\b", r"\bloteamento irregular\b",
            r"\bloteamento clandestino\b", r"\banistia de construcao\b",
            r"\bregularizacao fundiaria\b", r"\bsuspensao de demolicao\b",
            r"\barea de preservacao\b", r"\bocupacao irregular\b", r"\bmais valia\b",
        ],
    },
    "monopolio_utilidades": {
        "nome": "Monopólios de Utilidades e Serviços Básicos",
        "descricao": "Regulação e comércio de botijões de gás (GLP), água mineral, tv a cabo e provedores de internet locais.",
        "peso": 0.9,
        "keywords": [
            r"\bglp\b", r"\bbotijao de gas\b", r"\bgas liquefeito\b",
            r"\bagua mineral\b", r"\bdistribuicao de gas\b",
            r"\bprovedor de internet\b", r"\bcabeamento\b", r"\btv a cabo\b",
            r"\bsinal de telecomunicacoes\b",
        ],
    },
    "comercio_sucata": {
        "nome": "Comércio de Sucata e Reciclagem",
        "descricao": "Fiscalização, alvarás e regras para ferros-velhos e recicladoras (circuito de receptação de fios e metais).",
        "peso": 0.85,
        "keywords": [
            r"\bferro-velho\b", r"\bferros-velhos\b", r"\bsucata\b",
            r"\bfios de cobre\b", r"\bcobre\b", r"\bdesmanche\b",
            r"\bmaterial reciclavel\b", r"\bpecas usadas\b",
        ],
    },
    "mocoes_homenagens": {
        "nome": "Moções de Aplauso e Condecorações",
        "descricao": "Moções de louvor, medalhas (ex.: Pedro Ernesto, Tiradentes) e homenagens concedidas no parlamento.",
        "peso": 0.7,
        "keywords": [
            r"\bmocao de aplauso\b", r"\bmocao de louvor\b", r"\bmedalha pedro ernesto\b",
            r"\bmedalha tiradentes\b", r"\bhomenagem\b", r"\bcondecoracao\b",
            r"\bvoto de congratulacoes\b",
        ],
    },
}

# Precompiled keyword specs: (eixo_key, nome, descricao, peso, [(literal, compiled_re), ...])
_COMPILED_TAXONOMIA: List[Tuple[str, str, str, float, List[Tuple[str, Pattern[str]]]]] = [
    (
        eixo_key,
        info["nome"],
        info["descricao"],
        info["peso"],
        [(kw.replace(r"\b", ""), re.compile(kw)) for kw in info["keywords"]],
    )
    for eixo_key, info in TAXONOMIA_PAUTAS_SENSIVEIS.items()
]

_CUIDADO_NEUTRO = "Nenhum termo de pauta sensível mapeado na proposição."
_CUIDADO_SENSIVEL = (
    "ATENÇÃO METODOLÓGICA: Esta classificação mede convergência temática e incidência sobre "
    "mercados historicamente disputados no Rio de Janeiro. Não implica condenação judicial nem "
    "pressupõe intenção criminosa do autor."
)


def _normalize_text(text: str) -> str:
    if not text:
        return ""
    if text.isascii():
        return text.lower().strip()
    nfkd = unicodedata.normalize("NFKD", text)
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acento.lower().strip()


def classify_legislative_text(ementa: str, texto_completo: str = "") -> Dict[str, Any]:
    """
    Analisa ementa e texto de proposição legislativa, calculando índice de convergência temática.
    Respeita estritamente o cuidado metodológico de não presumir causalidade ou intenção ilícita.
    """
    combined = f"{ementa} {texto_completo}" if (ementa and texto_completo) else (ementa or texto_completo or "")
    normalized = _normalize_text(combined)

    matches_by_eixo: Dict[str, Dict[str, Any]] = {}
    total_score = 0.0
    best_key = ""
    best_score = -1.0
    all_terms = set()

    for eixo_key, nome, descricao, peso, compiled_kws in _COMPILED_TAXONOMIA:
        detected_keywords = [
            term
            for term, pattern in compiled_kws
            if term in normalized and pattern.search(normalized)
        ]

        if detected_keywords:
            score = round(min(1.0, len(detected_keywords) * 0.35) * peso, 2)
            matches_by_eixo[eixo_key] = {
                "eixo_nome": nome,
                "score": score,
                "termos": detected_keywords,
                "descricao": descricao,
            }
            total_score += score
            all_terms.update(detected_keywords)
            if score > best_score:
                best_score = score
                best_key = eixo_key

    if not matches_by_eixo:
        return {
            "possui_convergencia_sensivel": False,
            "eixo_principal": "Pauta Administrativa / Geral",
            "score_convergencia": 0.0,
            "termos_identificados": [],
            "todos_eixos": {},
            "cuidado_metodologico": _CUIDADO_NEUTRO,
        }

    return {
        "possui_convergencia_sensivel": True,
        "eixo_principal": matches_by_eixo[best_key]["eixo_nome"],
        "eixo_chave": best_key,
        "score_convergencia": round(min(1.0, total_score), 2),
        "termos_identificados": sorted(all_terms),
        "todos_eixos": matches_by_eixo,
        "cuidado_metodologico": _CUIDADO_SENSIVEL,
    }
