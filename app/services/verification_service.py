"""
Serviço de Gestão da Fila de Verificação Epistemológica (Verification Queue)
===========================================================================

Responsável por auditar continuamente o banco de afirmações (Claims), identificar
lacunas de evidência, detectar falsa triangulação e priorizar o trabalho
investigativo da equipe de pesquisa histórica.

Critérios de Priorização:
- CRÍTICA:
  Afirmações ativamente disputadas (is_disputed=True) ou com posturas conflitantes ('contesta').
- ALTA:
  Falsa triangulação detectada: múltiplas fontes citam a mesma afirmação, mas compartilham
  a mesma raiz genealógica (independent_root_count == 1).
- MÉDIA:
  Afirmações baseadas unicamente em fontes secundárias ou audiovisuais, sem ancoragem
  em fontes primárias (inquéritos policiais, relatórios de CPI, processos judiciais, imprensa de época).
- BAIXA:
  Afirmações já ancoradas em 2 ou mais fontes independentes com pelo menos uma fonte primária.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.claim import Claim, ClaimSource
from app.models.event import Event
from app.models.source import Source
from app.services.genealogy_service import GenealogyService

PRIMARY_SOURCE_TYPES = frozenset({
    "documento_oficial",
    "documento_judicial",
    "relatorio_cpi",
    "hemeroteca_jornal_epoca",
    "arquivo_publico",
    "entrevista",
})

_PRIORITY_ORDER = {"CRITICA": 0, "ALTA": 1, "MEDIA": 2, "BAIXA": 3}


class VerificationService:
    """Auditor e gestor do fluxo de verificação de veracidade histórica."""

    @classmethod
    def audit_claim(
        cls,
        claim: Claim,
        root_cache: Optional[Dict[int, Source]] = None,
        non_root_ids: Optional[Set[int]] = None,
    ) -> Dict[str, Any]:
        """Realiza auditoria epistemológica completa de uma Claim."""
        # 1. Avalia genealogia e raízes independentes
        geo_eval = GenealogyService.evaluate_claim_epistemology(claim, root_cache=root_cache)

        # 2. Contabiliza fontes primárias e monta sumário em passagem única
        primary_count = 0
        secondary_count = 0
        sources_summary: List[Dict[str, Any]] = []
        for link in claim.source_links:
            src = link.source
            is_primary = src.source_type in PRIMARY_SOURCE_TYPES
            if is_primary:
                primary_count += 1
            else:
                secondary_count += 1
            is_root = (src.id not in non_root_ids) if non_root_ids is not None else src.is_root
            sources_summary.append({
                "source_id": src.id,
                "title": src.title,
                "type": src.source_type,
                "is_primary": is_primary,
                "is_root": is_root,
            })

        evidence_count = geo_eval["evidence_count"]
        root_count = geo_eval["independent_root_count"]
        has_shared_roots = geo_eval["has_shared_roots"]
        is_disputed = claim.is_disputed or claim.confidence_level == "conflitante"

        # 3. Determina Prioridade e Ação Recomendada
        priority = "BAIXA"
        reasons: List[str] = []
        action = "Afirmação adequadamente fundamentada."

        if is_disputed:
            priority = "CRITICA"
            reasons.append("Controvérsia ativa: fontes divergem sobre os fatos relatados.")
            action = "Confrontar documentação primária divergente e elaborar nota crítica na ficha epistemológica."
        elif evidence_count > 1 and root_count == 1:
            priority = "ALTA"
            reasons.append(
                "Falsa triangulação detectada: múltiplas fontes apoiam a afirmação, mas derivam da mesma raiz."
            )
            shared_names = [
                f"'{r['root_title']}' ({r['derived_count']} derivações)"
                for r in geo_eval["shared_roots"]
            ]
            action = f"Localizar segunda fonte independente não derivada de {', '.join(shared_names)}."
        elif primary_count == 0:
            priority = "MEDIA"
            reasons.append(
                "Ausência de fonte primária: embasada exclusivamente em fontes secundárias ou audiovisuais."
            )
            action = "Pesquisar documentos judiciais, inquéritos policiais ou hemeroteca da época do evento."
        elif root_count < 2:
            priority = "MEDIA"
            reasons.append("Apenas uma fonte documental apoia a afirmação.")
            action = "Buscar fonte documental adicional para triangulação histórica."

        ev = claim.event
        return {
            "claim_id": claim.id,
            "event_id": claim.event_id,
            "event_title": ev.title if ev else "Sem Evento Vinculado",
            "event_date": ev.date_display if ev else None,
            "statement": claim.statement,
            "claim_type": claim.claim_type,
            "current_confidence": claim.confidence_level,
            "is_disputed": claim.is_disputed,
            "evidence_count": evidence_count,
            "independent_root_count": root_count,
            "primary_source_count": primary_count,
            "secondary_source_count": secondary_count,
            "has_shared_roots": has_shared_roots,
            "shared_roots": geo_eval["shared_roots"],
            "priority": priority,
            "reasons": reasons,
            "recommended_action": action,
            "sources_summary": sources_summary,
        }

    @classmethod
    def generate_verification_queue(
        cls,
        session: Session,
        include_demo: bool = False,
        min_priority: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Varre todas as claims cadastradas e gera a fila de verificação ordenada por prioridade.
        Utiliza eager loading e índice genealógico em memória para eliminar consultas N+1.
        """
        query = session.query(Claim).options(
            joinedload(Claim.event),
            selectinload(Claim.source_links).joinedload(ClaimSource.source),
        )
        if not include_demo:
            query = query.filter(Claim.is_demo == False)

        claims = query.all()
        genealogy_index = GenealogyService.build_genealogy_index(session)
        root_cache = genealogy_index.root_cache
        non_root_ids: Set[int] = set(genealogy_index.dependent_parent_by_source.keys())

        queue: List[Dict[str, Any]] = []
        counts = {
            "CRITICA": 0,
            "ALTA": 0,
            "MEDIA": 0,
            "BAIXA": 0,
        }
        max_rank = _PRIORITY_ORDER.get(min_priority, 3) if min_priority else 3

        false_triangulations = 0
        unanchored_secondary = 0
        disputed = 0

        for c in claims:
            audit = cls.audit_claim(c, root_cache=root_cache, non_root_ids=non_root_ids)
            prio = audit["priority"]
            counts[prio] += 1

            if not min_priority or _PRIORITY_ORDER[prio] <= max_rank:
                queue.append(audit)
                if audit["has_shared_roots"]:
                    false_triangulations += 1
                if audit["primary_source_count"] == 0:
                    unanchored_secondary += 1
                if audit["is_disputed"]:
                    disputed += 1

        # Ordena a fila por prioridade decrescente (CRITICA -> ALTA -> MEDIA -> BAIXA)
        queue.sort(key=lambda x: _PRIORITY_ORDER[x["priority"]])

        return {
            "total_claims_audited": len(claims),
            "queue_size": len(queue),
            "summary_by_priority": counts,
            "false_triangulations_detected": false_triangulations,
            "unanchored_secondary_claims": unanchored_secondary,
            "disputed_claims": disputed,
            "queue": queue,
        }
