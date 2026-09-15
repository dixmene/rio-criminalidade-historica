# -*- coding: utf-8 -*-
"""
Testes Automatizados da Fila de Verificação Epistemológica (VerificationService).
"""

import pytest
from app.models.event import Event
from app.models.source import Source
from app.models.claim import Claim, ClaimSource
from app.models.associations import SourceDerivation
from app.services.verification_service import VerificationService


def test_audit_claim_critical_dispute(db_session):
    """Afirmações disputadas ou conflitantes devem receber prioridade CRITICA."""
    ev = Event(
        title="Evento Disputado",
        date_display="1990",
        description="Descrição factual do evento para testes.",
        is_demo=True
    )
    db_session.add(ev)
    db_session.flush()

    cl = Claim(
        event_id=ev.id,
        statement="Afirmação em controvérsia ativa",
        confidence_level="conflitante",
        is_disputed=True,
        is_demo=True
    )
    db_session.add(cl)
    db_session.flush()

    audit = VerificationService.audit_claim(cl)
    assert audit["priority"] == "CRITICA"
    assert audit["is_disputed"] is True
    assert "Controvérsia ativa" in audit["reasons"][0]


def test_audit_claim_high_priority_false_triangulation(db_session):
    """Múltiplas fontes que derivam da mesma raiz devem gerar prioridade ALTA de verificação."""
    ev = Event(
        title="Evento Falsa Triangulação",
        date_display="1995",
        description="Descrição detalhada do acontecimento.",
        is_demo=True
    )
    src_root = Source(title="Livro Raiz", citation="Autor, 1995", source_type="academico_livro", is_demo=True)
    src_v1 = Source(title="Vídeo A", citation="Canal 1, 2020", source_type="audiovisual_youtube", is_demo=True)
    src_v2 = Source(title="Vídeo B", citation="Canal 2, 2021", source_type="audiovisual_youtube", is_demo=True)
    db_session.add_all([ev, src_root, src_v1, src_v2])
    db_session.flush()

    # V1 e V2 derivam do Livro Raiz
    d1 = SourceDerivation(parent_source_id=src_root.id, derived_source_id=src_v1.id, derivation_type="reproduz", is_independent=False)
    d2 = SourceDerivation(parent_source_id=src_root.id, derived_source_id=src_v2.id, derivation_type="reproduz", is_independent=False)
    db_session.add_all([d1, d2])

    cl = Claim(
        event_id=ev.id,
        statement="Afirmação apoiada por 2 vídeos dependentes",
        confidence_level="provavel",
        is_demo=True
    )
    db_session.add(cl)
    db_session.flush()

    cs1 = ClaimSource(claim_id=cl.id, source_id=src_v1.id, stance="apoia", excerpt="Trecho 1")
    cs2 = ClaimSource(claim_id=cl.id, source_id=src_v2.id, stance="apoia", excerpt="Trecho 2")
    db_session.add_all([cs1, cs2])
    db_session.commit()

    audit = VerificationService.audit_claim(cl)
    assert audit["priority"] == "ALTA"
    assert audit["has_shared_roots"] is True
    assert audit["evidence_count"] == 2
    assert audit["independent_root_count"] == 1


def test_audit_claim_medium_priority_unanchored(db_session):
    """Afirmação com fonte secundária mas sem fonte primária deve receber prioridade MEDIA."""
    ev = Event(
        title="Evento Sem Primária",
        date_display="2000",
        description="Descrição detalhada do acontecimento sem fontes primárias.",
        is_demo=True
    )
    src_sec = Source(title="Vídeo Isolado", citation="Canal, 2020", source_type="audiovisual_youtube", is_demo=True)
    db_session.add_all([ev, src_sec])
    db_session.flush()

    cl = Claim(
        event_id=ev.id,
        statement="Fato com apenas uma fonte secundária",
        confidence_level="provavel",
        is_demo=True
    )
    db_session.add(cl)
    db_session.flush()

    cs = ClaimSource(claim_id=cl.id, source_id=src_sec.id, stance="apoia", excerpt="Trecho único")
    db_session.add(cs)
    db_session.commit()

    audit = VerificationService.audit_claim(cl)
    assert audit["priority"] == "MEDIA"
    assert audit["primary_source_count"] == 0


def test_generate_verification_queue(db_session):
    """Gera fila completa e valida agrupamentos de prioridade."""
    ev = Event(
        title="Evento Fila Geral",
        date_display="2010",
        description="Descrição para teste de fila.",
        is_demo=True
    )
    db_session.add(ev)
    db_session.flush()

    c1 = Claim(event_id=ev.id, statement="Claim em disputa", is_disputed=True, is_demo=True)
    c2 = Claim(event_id=ev.id, statement="Claim provável", confidence_level="provavel", is_demo=True)
    db_session.add_all([c1, c2])
    db_session.commit()

    res = VerificationService.generate_verification_queue(db_session, include_demo=True)
    assert "total_claims_audited" in res
    assert "summary_by_priority" in res
    assert "queue" in res
    assert res["total_claims_audited"] >= 2
    assert res["summary_by_priority"]["CRITICA"] >= 1
