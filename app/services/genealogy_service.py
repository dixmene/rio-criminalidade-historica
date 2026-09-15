"""
Serviço de Genealogia Documental e Análise de Independência de Fontes.

Implementa a resolução de raízes documentais (root sources) para impedir
que múltiplas fontes que derivam ou reproduzem a mesma obra/inquérito
sejam falsamente contabilizadas como evidências independentes (anti-falsa triangulação).
"""

from typing import List, Dict, Set, Any, Optional
from app.models.source import Source
from app.models.claim import Claim


PRIMARY_SOURCE_TYPES = {
    "documento_judicial",
    "oficial_relatorio",
    "arquivo_digital",
}

SECONDARY_SOURCE_TYPES = {
    "academico_livro",
    "academico_artigo",
    "academico_tese",
    "jornalismo_investigativo",
    "jornalismo_hemeroteca",
    "historia_oral",
    "audiovisual_youtube",
    "video_youtube",
    "entrevista",
}


class GenealogyService:
    """Serviço de resolução e auditoria da genealogia de fontes."""

    @staticmethod
    def get_root_source(source: Source) -> Source:
        """Retorna a raiz documental primordial de uma fonte."""
        if not source:
            return None
        return source.get_root_source()

    @classmethod
    def group_by_root(cls, sources: List[Source]) -> Dict[int, List[Source]]:
        """
        Agrupa uma lista de fontes por sua fonte raiz comum.
        Chave: ID da raiz documental.
        Valor: lista de fontes que compartilham aquela raiz.
        """
        roots_map: Dict[int, List[Source]] = {}
        for src in sources:
            root = cls.get_root_source(src)
            root_id = root.id if root else src.id
            if root_id not in roots_map:
                roots_map[root_id] = []
            roots_map[root_id].append(src)
        return roots_map

    @classmethod
    def count_independent_roots(cls, sources: List[Source]) -> int:
        """
        Calcula o número de raízes documentais verdadeiramente independentes
        em um conjunto de fontes. Fontes com a mesma raiz contam como 1 raiz.
        """
        if not sources:
            return 0
        roots_map = cls.group_by_root(sources)
        return len(roots_map)

    @classmethod
    def evaluate_claim_epistemology(cls, claim: Claim) -> Dict[str, Any]:
        """
        Avalia o estatuto epistemológico de uma Claim a partir de sua rede de fontes.
        
        Retorna métricas auditáveis:
        - evidence_count: total de fontes que apoiam
        - independent_root_count: total de raízes documentais independentes
        - primary_source_count: quantidade de fontes primárias/oficiais
        - secondary_source_count: quantidade de fontes secundárias/narrativas
        - conflicting_source_count: quantidade de fontes que contestam
        - suggested_status: 'confirmado' | 'provavel' | 'conflitante' | 'nao_verificado'
        - common_roots: mapeamento de possíveis fontes comuns entre derivados
        """
        supporting_sources = claim.supporting_sources
        contradicting_sources = claim.contradicting_sources
        matizing_sources = [link.source for link in claim.source_links if link.stance == "matiza"]

        # Agrupamento por raiz
        supporting_roots_map = cls.group_by_root(supporting_sources)
        independent_root_count = len(supporting_roots_map)
        conflicting_count = len(contradicting_sources)

        # Contagem por tipologia documental
        primary_count = sum(1 for s in supporting_sources if s.source_type in PRIMARY_SOURCE_TYPES)
        secondary_count = sum(1 for s in supporting_sources if s.source_type in SECONDARY_SOURCE_TYPES)

        # Regras epistemológicas normativas (Protocolo de Pesquisa):
        # 1. Se há fontes que contestam explicitamente -> CONFLITANTE
        # 2. Se há >= 2 raízes independentes e sem contestação -> CONFIRMADO
        # 3. Se há 1 raiz consistente e sem contestação -> PROVÁVEL
        # 4. Se não há evidências ou apenas menções -> NÃO_VERIFICADO
        if conflicting_count > 0:
            status = "conflitante"
        elif independent_root_count >= 2:
            status = "confirmado"
        elif independent_root_count == 1:
            status = "provavel"
        else:
            status = "nao_verificado"

        # Formata relatório de raízes comuns
        common_roots_info = []
        for r_id, srcs in supporting_roots_map.items():
            if len(srcs) > 1:
                root_obj = srcs[0].get_root_source()
                common_roots_info.append({
                    "root_id": r_id,
                    "root_title": root_obj.title if root_obj else "Desconhecido",
                    "derived_count": len(srcs),
                    "derived_titles": [s.title for s in srcs]
                })

        return {
            "claim_id": claim.id,
            "statement": claim.statement,
            "evidence_count": len(supporting_sources),
            "independent_root_count": independent_root_count,
            "primary_source_count": primary_count,
            "secondary_source_count": secondary_count,
            "conflicting_source_count": conflicting_count,
            "matizing_source_count": len(matizing_sources),
            "suggested_status": status,
            "has_shared_roots": len(common_roots_info) > 0,
            "shared_roots": common_roots_info
        }
