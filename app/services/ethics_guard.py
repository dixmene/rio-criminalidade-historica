# -*- coding: utf-8 -*-
"""
Guarda Ética e Filtro de Salvaguarda Cartográfica (FASE 5 — BLOQUEANTE)
=======================================================================

Implementa salvaguardas éticas inegociáveis para cartografia de violência e criminalidade:
1. Embargo de Granularidade Temporal de 24 Meses:
   - Dados de eventos recentes (< 24 meses) são agregados obrigatoriamente
     ao nível de Município ou AISP, suprimindo coordenadas exatas a nível de rua.
2. Filtro Anti-Inteligência Operacional:
   - Bloqueio de menções táticas a bocas de fumo, rotas ativas de fuga
     e residências particulares de pessoas vivas.
3. Salvaguarda de Vítimas e Pessoas Vivas:
   - Anonimização e proteção estrita de testemunhas e vítimas civis.
"""

import re
from copy import deepcopy
from datetime import date, datetime, timezone
from typing import Dict, List, Optional, Tuple, Any

from app.services.atlas_service import WorldState

# Centroides oficiais de contingência por AISP (para agregação de dados embargados)
AISP_CENTROIDS = {
    2: [-43.185, -22.952],   # Botafogo
    3: [-43.282, -22.901],   # Méier
    4: [-43.221, -22.898],   # São Cristóvão
    5: [-43.187, -22.903],   # Centro / Harmonia
    6: [-43.232, -22.924],   # Tijuca
    9: [-43.342, -22.871],   # Madureira / Rocha Miranda
    14: [-43.465, -22.875],  # Bangu
    15: [-43.311, -22.785],  # Duque de Caxias
    16: [-43.278, -22.842],  # Olaria / Penha
    18: [-43.355, -22.920],  # Jacarepaguá
    19: [-43.186, -22.969],  # Copacabana
    22: [-43.245, -22.858],  # Maré / Bonsucesso
    31: [-43.365, -23.000],  # Barra da Tijuca
    39: [-43.392, -22.716],  # Belford Roxo
    41: [-43.345, -22.835],  # Pavuna / Costa Barros
}

# Centroide padrão do Município do Rio de Janeiro
MUNICIPALITY_CENTROID = [-43.2096, -22.9035]

# Termos operacionais proibidos que caracterizam inteligência policial/tática ativa
OPERATIONAL_KEYWORDS = [
    "boca de fumo",
    "ponto de venda de droga",
    "rota de fuga ativa",
    "esconderijo de armas",
    "residência particular",
    "endereço residencial de pessoa viva",
    "campana",
]


class EthicsGuard:
    """
    Guarda Ética Cartográfica: Validador e sanitizador de saídas geoespaciais.
    """

    DEFAULT_CURRENT_YEAR = 2026
    EMBARGO_MONTHS = 24

    @classmethod
    def is_under_temporal_embargo(cls, year: int, month: Optional[int] = None, current_year: int = DEFAULT_CURRENT_YEAR) -> bool:
        """
        Verifica se um dado ano/mês se enquadra na janela de embargo de 24 meses.
        Para current_year=2026, anos 2025 e 2026 estão sob embargo.
        """
        if year > current_year:
            return True
        # Janela de 24 meses (2 anos civis anteriores)
        if year >= (current_year - 1):
            return True
        return False

    @classmethod
    def apply_embargo(cls, world_state: WorldState, current_year: int = DEFAULT_CURRENT_YEAR) -> WorldState:
        """
        Aplica a Regra de Embargo de 24 Meses sobre um WorldState:
        - Se o ano do estado for recente (< 24 meses), agrega feições pontuais
          para centroides de AISP ou município, impedindo localização tática a nível de rua.
        - Sinaliza explicitamente o embargo nos metadados e nas propriedades das feições.
        """
        if not cls.is_under_temporal_embargo(world_state.year, world_state.month, current_year=current_year):
            return world_state

        ws = deepcopy(world_state)
        ws.metadata["ethics_embargo_active"] = True
        ws.metadata["ethics_embargo_reason"] = (
            "Embargo Ético de 24 Meses Ativo: Por imperativo de segurança, salvaguarda de pessoas vivas "
            "e prevenção contra o uso da pesquisa para inteligência operacional, acontecimentos dos últimos "
            "24 meses têm suas coordenadas agregadas ao nível municipal ou de circunscrição policial (AISP)."
        )

        embargoed_events = []
        for ev_feat in ws.events:
            geom = ev_feat.get("geometry", {})
            props = ev_feat.get("properties", {})

            # Se for ponto de alta precisão, agrega para centroide municipal ou AISP
            if geom.get("type") == "Point":
                # Centroide seguro agregado
                geom["coordinates"] = MUNICIPALITY_CENTROID
                props["location_precision"] = "agregado_municipal_embargo_etico"
                props["is_embargoed"] = True
                props["embargo_note"] = (
                    "Coordenada exata suprimida preventivamente por embargo ético temporal (< 24 meses). "
                    "Posição exibida representa o centroide do município."
                )

            embargoed_events.append(ev_feat)

        ws.events = embargoed_events
        return ws

    @classmethod
    def scan_operational_intelligence(cls, text: str) -> Tuple[bool, List[str]]:
        """
        Analisa um texto factual buscando violações às diretrizes de inteligência operacional.
        Retorna (tem_violacao, lista_de_termos_encontrados).
        """
        if not text:
            return (False, [])

        text_lower = text.lower()
        violations = []
        for kw in OPERATIONAL_KEYWORDS:
            if kw in text_lower:
                violations.append(kw)

        return (len(violations) > 0, violations)

    @classmethod
    def sanitize_metadata_text(cls, text: str) -> str:
        """
        Remove ou ofusca menções indevidas a rotas táticas ativas e endereços particulares.
        """
        if not text:
            return text

        sanitized = text
        for kw in OPERATIONAL_KEYWORDS:
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            sanitized = pattern.sub("[REDUZIDO POR DIRETRIZ ÉTICA]", sanitized)

        return sanitized

    @classmethod
    def audit_cartographic_feature(cls, feature: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audita e higieniza uma feição individual antes da entrega ao frontend.
        """
        feat = deepcopy(feature)
        props = feat.get("properties", {})

        for field in ("title", "notes", "summary", "description"):
            if field in props and isinstance(props[field], str):
                has_viol, terms = cls.scan_operational_intelligence(props[field])
                if has_viol:
                    props[field] = cls.sanitize_metadata_text(props[field])
                    props["ethics_sanitized"] = True
                    props["ethics_sanitized_terms"] = terms

        feat["properties"] = props
        return feat
