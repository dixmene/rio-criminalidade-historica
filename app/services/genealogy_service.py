"""
Serviço de Genealogia Documental e Análise de Independência de Fontes.

Implementa a resolução de raízes documentais (root sources) para impedir
que múltiplas fontes que derivam ou reproduzem a mesma obra/inquérito
sejam falsamente contabilizadas como evidências independentes (anti-falsa triangulação).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy.orm import Session

from app.models.associations import SourceDerivation
from app.models.claim import Claim
from app.models.source import Source


PRIMARY_SOURCE_TYPES = frozenset({
    "documento_judicial",
    "oficial_relatorio",
    "arquivo_digital",
})

SECONDARY_SOURCE_TYPES = frozenset({
    "academico_livro",
    "academico_artigo",
    "academico_tese",
    "jornalismo_investigativo",
    "jornalismo_hemeroteca",
    "historia_oral",
    "audiovisual_youtube",
    "video_youtube",
    "entrevista",
})


@dataclass(frozen=True)
class GenealogyIndex:
    """
    Snapshot em memória do grafo de derivações documentais (construído em O(V + E)
    com apenas 2 consultas SQL), eliminando travessias N+1 sobre SQLAlchemy.
    """

    sources_by_id: Dict[int, Source]
    root_cache: Dict[int, Source]
    dependent_parent_by_source: Dict[int, int]
    all_derivations: List[Tuple[int, int, int, bool]]  # (id, parent_id, derived_id, is_independent)


class GenealogyService:
    """Serviço de resolução e auditoria da genealogia de fontes."""

    @staticmethod
    def build_genealogy_index(session: Session) -> GenealogyIndex:
        """
        Carrega todas as fontes e arestas de derivação em 2 queries e resolve
        a raiz documental de cada fonte em tempo O(V + E) com detecção de ciclos.
        """
        sources = session.query(Source).all()
        sources_by_id: Dict[int, Source] = {s.id: s for s in sources}

        deriv_rows = session.query(
            SourceDerivation.id,
            SourceDerivation.parent_source_id,
            SourceDerivation.derived_source_id,
            SourceDerivation.is_independent,
        ).all()

        all_derivations: List[Tuple[int, int, int, bool]] = [
            (r[0], r[1], r[2], bool(r[3])) for r in deriv_rows
        ]

        # Primeiro ascendente dependente (is_independent == False) por fonte derivada,
        # preservando exatamente a semântica de Source.get_root_source().
        dependent_parent: Dict[int, int] = {}
        for _, parent_id, derived_id, is_indep in all_derivations:
            if not is_indep and parent_id in sources_by_id and derived_id not in dependent_parent:
                dependent_parent[derived_id] = parent_id

        root_cache: Dict[int, Source] = {}
        for sid, src in sources_by_id.items():
            if sid in root_cache:
                continue
            path: List[int] = []
            visited_in_walk: Set[int] = set()
            curr_id: Optional[int] = sid
            resolved_root: Source = src

            while curr_id is not None:
                if curr_id in root_cache:
                    resolved_root = root_cache[curr_id]
                    break
                if curr_id in visited_in_walk:
                    # Ciclo detectado: replica comportamento de proteção de get_root_source()
                    resolved_root = sources_by_id[curr_id]
                    break
                visited_in_walk.add(curr_id)
                path.append(curr_id)
                next_parent = dependent_parent.get(curr_id)
                if next_parent is None:
                    resolved_root = sources_by_id[curr_id]
                    break
                curr_id = next_parent

            for node_id in path:
                root_cache[node_id] = resolved_root

        return GenealogyIndex(
            sources_by_id=sources_by_id,
            root_cache=root_cache,
            dependent_parent_by_source=dependent_parent,
            all_derivations=all_derivations,
        )

    @staticmethod
    def find_cyclic_sources(index: GenealogyIndex) -> List[Dict[str, Any]]:
        """
        Detecta em O(V + E) todas as fontes cujo caminho ascendente dependente
        atinge um ciclo no grafo de derivações.
        """
        # 0 = não visitado, 1 = no caminho atual, 2 = acíclico, 3 = cíclico
        state: Dict[int, int] = {}
        dependent_parent = index.dependent_parent_by_source
        cycles: List[Dict[str, Any]] = []

        for sid, src in index.sources_by_id.items():
            st = state.get(sid, 0)
            if st == 0:
                path: List[int] = []
                curr: Optional[int] = sid
                is_cyclic = False
                while curr is not None:
                    curr_state = state.get(curr, 0)
                    if curr_state == 1 or curr_state == 3:
                        is_cyclic = True
                        break
                    if curr_state == 2:
                        is_cyclic = False
                        break
                    state[curr] = 1
                    path.append(curr)
                    curr = dependent_parent.get(curr)

                final_state = 3 if is_cyclic else 2
                for node_id in path:
                    state[node_id] = final_state
                st = final_state

            if st == 3:
                cycles.append({"source_id": sid, "title": src.title})

        return cycles

    @staticmethod
    def get_root_source(
        source: Optional[Source],
        root_cache: Optional[Dict[int, Source]] = None,
    ) -> Optional[Source]:
        """Retorna a raiz documental primordial de uma fonte (com memoização opcional)."""
        if not source:
            return None
        if root_cache is not None and source.id is not None:
            cached = root_cache.get(source.id)
            if cached is not None:
                return cached
            root = source.get_root_source()
            root_cache[source.id] = root
            return root
        return source.get_root_source()

    @classmethod
    def group_by_root(
        cls,
        sources: List[Source],
        root_cache: Optional[Dict[int, Source]] = None,
    ) -> Dict[int, List[Source]]:
        """
        Agrupa uma lista de fontes por sua fonte raiz comum.
        Chave: ID da raiz documental.
        Valor: lista de fontes que compartilham aquela raiz.
        """
        cache = root_cache if root_cache is not None else {}
        roots_map: Dict[int, List[Source]] = {}
        for src in sources:
            root = cls.get_root_source(src, root_cache=cache)
            root_id = root.id if root else src.id
            if root_id not in roots_map:
                roots_map[root_id] = []
            roots_map[root_id].append(src)
        return roots_map

    @classmethod
    def count_independent_roots(
        cls,
        sources: List[Source],
        root_cache: Optional[Dict[int, Source]] = None,
    ) -> int:
        """
        Calcula o número de raízes documentais verdadeiramente independentes
        em um conjunto de fontes. Fontes com a mesma raiz contam como 1 raiz.
        """
        if not sources:
            return 0
        roots_map = cls.group_by_root(sources, root_cache=root_cache)
        return len(roots_map)

    @classmethod
    def evaluate_claim_epistemology(
        cls,
        claim: Claim,
        root_cache: Optional[Dict[int, Source]] = None,
    ) -> Dict[str, Any]:
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
        cache = root_cache if root_cache is not None else {}
        supporting_sources: List[Source] = []
        conflicting_count = 0
        matizing_count = 0
        primary_count = 0
        secondary_count = 0

        for link in claim.source_links:
            stance = link.stance
            if stance == "apoia":
                src = link.source
                supporting_sources.append(src)
                stype = src.source_type
                if stype in PRIMARY_SOURCE_TYPES:
                    primary_count += 1
                elif stype in SECONDARY_SOURCE_TYPES:
                    secondary_count += 1
            elif stance == "contesta":
                conflicting_count += 1
            elif stance == "matiza":
                matizing_count += 1

        # Agrupamento por raiz guardando o objeto raiz para evitar retravessia
        supporting_roots_map: Dict[int, List[Source]] = {}
        root_objs: Dict[int, Optional[Source]] = {}
        for src in supporting_sources:
            root = cls.get_root_source(src, root_cache=cache)
            root_id = root.id if root else src.id
            if root_id not in supporting_roots_map:
                supporting_roots_map[root_id] = []
                root_objs[root_id] = root
            supporting_roots_map[root_id].append(src)

        independent_root_count = len(supporting_roots_map)

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

        # Formata relatório de raízes comuns sem retravessia
        common_roots_info = []
        for r_id, srcs in supporting_roots_map.items():
            if len(srcs) > 1:
                root_obj = root_objs.get(r_id)
                common_roots_info.append({
                    "root_id": r_id,
                    "root_title": root_obj.title if root_obj else "Desconhecido",
                    "derived_count": len(srcs),
                    "derived_titles": [s.title for s in srcs],
                })

        return {
            "claim_id": claim.id,
            "statement": claim.statement,
            "evidence_count": len(supporting_sources),
            "independent_root_count": independent_root_count,
            "primary_source_count": primary_count,
            "secondary_source_count": secondary_count,
            "conflicting_source_count": conflicting_count,
            "matizing_source_count": matizing_count,
            "suggested_status": status,
            "has_shared_roots": len(common_roots_info) > 0,
            "shared_roots": common_roots_info,
        }
