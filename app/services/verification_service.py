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

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.claim import Claim, ClaimSource
from app.models.source import Source
from app.models.event import Event
from app.services.genealogy_service import GenealogyService

PRIMARY_SOURCE_TYPES = {
    "documento_oficial",
    "documento_judicial",
    "relatorio_cpi",
    "hemeroteca_jornal_epoca",
    "arquivo_publico",
    "entrevista"
}


class VerificationService:
    """Auditor e gestor do fluxo de verificação de veracidade histórica."""

    @classmethod
    def audit_claim(cls, claim: Claim) -> Dict[str, Any]:
        """Realiza auditoria epistemológica completa de uma Claim."""
        # 1. Avalia genealogia e raízes independentes
        geo_eval = GenealogyService.evaluate_claim_epistemology(claim)

        # 2. Contabiliza fontes primárias
        primary_sources = []
        secondary_sources = []
        for src in claim.sources:
            if src.source_type in PRIMARY_SOURCE_TYPES:
                primary_sources.append(src)
            else:
                secondary_sources.append(src)

        evidence_count = geo_eval["evidence_count"]
        root_count = geo_eval["independent_root_count"]
        has_shared_roots = geo_eval["has_shared_roots"]
        is_disputed = claim.is_disputed or claim.confidence_level == "conflitante"

        # 3. Determina Prioridade e Ação Recomendada
        priority = "BAIXA"
        reasons = []
        action = "Afirmação adequadamente fundamentada."

        if is_disputed:
            priority = "CRITICA"
            reasons.append("Controvérsia ativa: fontes divergem sobre os fatos relatados.")
            action = "Confrontar documentação primária divergente e elaborar nota crítica na ficha epistemológica."
        elif evidence_count > 1 and root_count == 1:
            priority = "ALTA"
            reasons.append("Falsa triangulação detectada: múltiplas fontes apoiam a afirmação, mas derivam da mesma raiz.")
            shared_names = [f"'{r['root_title']}' ({r['derived_count']} derivações)" for r in geo_eval["shared_roots"]]
            action = f"Localizar segunda fonte independente não derivada de {', '.join(shared_names)}."
        elif len(primary_sources) == 0:
            priority = "MEDIA"
            reasons.append("Ausência de fonte primária: embasada exclusivamente em fontes secundárias ou audiovisuais.")
            action = "Pesquisar documentos judiciais, inquéritos policiais ou hemeroteca da época do evento."
        elif root_count < 2:
            priority = "MEDIA"
            reasons.append("Apenas uma fonte documental apoia a afirmação.")
            action = "Buscar fonte documental adicional para triangulação histórica."

        return {
            "claim_id": claim.id,
            "event_id": claim.event_id,
            "event_title": claim.event.title if claim.event else "Sem Evento Vinculado",
            "event_date": claim.event.date_display if claim.event else None,
            "statement": claim.statement,
            "claim_type": claim.claim_type,
            "current_confidence": claim.confidence_level,
            "is_disputed": claim.is_disputed,
            "evidence_count": evidence_count,
            "independent_root_count": root_count,
            "primary_source_count": len(primary_sources),
            "secondary_source_count": len(secondary_sources),
            "has_shared_roots": has_shared_roots,
            "shared_roots": geo_eval["shared_roots"],
            "priority": priority,
            "reasons": reasons,
            "recommended_action": action,
            "sources_summary": [
                {
                    "source_id": s.id,
                    "title": s.title,
                    "type": s.source_type,
                    "is_primary": s.source_type in PRIMARY_SOURCE_TYPES,
                    "is_root": s.is_root
                }
                for s in claim.sources
            ]
        }

    @classmethod
    def generate_verification_queue(
        cls,
        session: Session,
        include_demo: bool = False,
        min_priority: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Varre todas as claims cadastradas e gera a fila de verificação ordenada por prioridade.
        """
        query = session.query(Claim)
        if not include_demo:
            query = query.filter(Claim.is_demo == False)

        claims = query.all()
        queue = []
        counts = {
            "CRITICA": 0,
            "ALTA": 0,
            "MEDIA": 0,
            "BAIXA": 0
        }

        priority_order = {"CRITICA": 0, "ALTA": 1, "MEDIA": 2, "BAIXA": 3}

        for c in claims:
            audit = cls.audit_claim(c)
            prio = audit["priority"]
            counts[prio] += 1

            if min_priority:
                if priority_order[prio] <= priority_order.get(min_priority, 3):
                    queue.append(audit)
            else:
                queue.append(audit)

        # Ordena a fila por prioridade decrescente (CRITICA -> ALTA -> MEDIA -> BAIXA)
        queue.sort(key=lambda x: priority_order[x["priority"]])

        return {
            "total_claims_audited": len(claims),
            "queue_size": len(queue),
            "summary_by_priority": counts,
            "false_triangulations_detected": sum(1 for item in queue if item["has_shared_roots"]),
            "unanchored_secondary_claims": sum(1 for item in queue if item["primary_source_count"] == 0),
            "disputed_claims": sum(1 for item in queue if item["is_disputed"]),
            "queue": queue
        }
