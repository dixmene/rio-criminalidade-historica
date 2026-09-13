"""
Módulo de Classificação Temática da Atividade Legislativa (CMRJ / ALERJ).
Implementa a Taxonomia de Pautas Sensíveis aos Mercados do Crime Organizado:
1. Transporte complementar (vans, mototáxis, itinerários)
2. Uso e ocupação do solo urbano (desafetação, anistia a loteamentos, entraves a demolição)
3. Monopólios de utilidades (botijão de gás/GLP, água mineral, internet/gatonet)
4. Comércio de sucata e reciclagem (ferros-velhos, fios de cobre, baterias)
5. Moções de aplauso e condecorações (homenagens a investigados/condenados)
"""

import re
import unicodedata
from typing import Dict, Any, List, Tuple


TAXONOMIA_PAUTAS_SENSIVEIS = {
    "transporte_complementar": {
        "nome": "Transporte Complementar e Alternativo",
        "descricao": "Proposições sobre vans, kombis, mototáxis, trajetos, permissões e fiscalização de transporte.",
        "peso": 1.0,
        "keywords": [
            r"\bvan\b", r"\bvans\b", r"\bkombi\b", r"\bkombis\b",
            r"\bmototaxi\b", r"\bmototaxis\b", r"\bmoto-taxi\b",
            r"\btransporte complementar\b", r"\btransporte alternativo\b",
            r"\blotacao\b", r"\bitinerario de van\b", r"\bpermissao de transporte\b"
        ]
    },
    "uso_solo_urbano": {
        "nome": "Uso e Ocupação do Solo Urbano / Grilagem",
        "descricao": "Proposições de desafetação de áreas públicas, anistia a loteamentos irregulares e suspensão de demolições.",
        "peso": 1.0,
        "keywords": [
            r"\bdesafetacao\b", r"\bdesafetar\b", r"\bloteamento irregular\b",
            r"\bloteamento clandestino\b", r"\banistia de construcao\b",
            r"\bregularizacao fundiaria\b", r"\bsuspensao de demolicao\b",
            r"\barea de preservacao\b", r"\bocupacao irregular\b", r"\bmais valia\b"
        ]
    },
    "monopolio_utilidades": {
        "nome": "Monopólios de Utilidades e Serviços Básicos",
        "descricao": "Regulação e comércio de botijões de gás (GLP), água mineral, tv a cabo e provedores de internet locais.",
        "peso": 0.9,
        "keywords": [
            r"\bglp\b", r"\bbotijao de gas\b", r"\bgas liquefeito\b",
            r"\bagua mineral\b", r"\bdistribuicao de gas\b",
            r"\bprovedor de internet\b", r"\bcabeamento\b", r"\btv a cabo\b",
            r"\bsinal de telecomunicacoes\b"
        ]
    },
    "comercio_sucata": {
        "nome": "Comércio de Sucata e Reciclagem",
        "descricao": "Fiscalização, alvarás e regras para ferros-velhos e recicladoras (circuito de receptação de fios e metais).",
        "peso": 0.85,
        "keywords": [
            r"\bferro-velho\b", r"\bferros-velhos\b", r"\bsucata\b",
            r"\bfios de cobre\b", r"\bcobre\b", r"\bdesmanche\b",
            r"\bmaterial reciclavel\b", r"\bpecas usadas\b"
        ]
    },
    "mocoes_homenagens": {
        "nome": "Moções de Aplauso e Condecorações",
        "descricao": "Moções de louvor, medalhas (ex.: Pedro Ernesto, Tiradentes) e homenagens concedidas no parlamento.",
        "peso": 0.7,
        "keywords": [
            r"\bmocao de aplauso\b", r"\bmocao de louvor\b", r"\bmedalha pedro ernesto\b",
            r"\bmedalha tiradentes\b", r"\bhomenagem\b", r"\bcondecoracao\b",
            r"\bvoto de congratulacoes\b"
        ]
    }
}


def _normalize_text(text: str) -> str:
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acento.lower().strip()


def classify_legislative_text(ementa: str, texto_completo: str = "") -> Dict[str, Any]:
    """
    Analisa ementa e texto de proposição legislativa, calculando índice de convergência temática.
    Respeita estritamente o cuidado metodológico de não presumir causalidade ou intenção ilícita.
    """
    combined = f"{ementa or ''} {texto_completo or ''}"
    normalized = _normalize_text(combined)

    matches_by_eixo = {}
    total_score = 0.0

    for eixo_key, info in TAXONOMIA_PAUTAS_SENSIVEIS.items():
        detected_keywords = []
        for kw_pattern in info["keywords"]:
            if re.search(kw_pattern, normalized):
                detected_keywords.append(kw_pattern.replace(r"\b", ""))

        if detected_keywords:
            score = round(min(1.0, len(detected_keywords) * 0.35) * info["peso"], 2)
            matches_by_eixo[eixo_key] = {
                "eixo_nome": info["nome"],
                "score": score,
                "termos": detected_keywords,
                "descricao": info["descricao"]
            }
            total_score += score

    if not matches_by_eixo:
        return {
            "possui_convergencia_sensivel": False,
            "eixo_principal": "Pauta Administrativa / Geral",
            "score_convergencia": 0.0,
            "termos_identificados": [],
            "todos_eixos": {},
            "cuidado_metodologico": "Nenhum termo de pauta sensível mapeado na proposição."
        }

    # Selecionar eixo de maior score
    sorted_eixos = sorted(matches_by_eixo.items(), key=lambda x: x[1]["score"], reverse=True)
    best_key, best_data = sorted_eixos[0]

    all_terms = []
    for d in matches_by_eixo.values():
        all_terms.extend(d["termos"])

    score_final = round(min(1.0, total_score), 2)

    return {
        "possui_convergencia_sensivel": True,
        "eixo_principal": best_data["eixo_nome"],
        "eixo_chave": best_key,
        "score_convergencia": score_final,
        "termos_identificados": sorted(list(set(all_terms))),
        "todos_eixos": matches_by_eixo,
        "cuidado_metodologico": (
            "ATENÇÃO METODOLÓGICA: Esta classificação mede convergência temática e incidência sobre "
            "mercados historicamente disputados no Rio de Janeiro. Não implica condenação judicial nem "
            "pressupõe intenção criminosa do autor."
        )
    }
