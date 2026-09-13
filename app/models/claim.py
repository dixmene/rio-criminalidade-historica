"""
Modelo de Afirmação / Assertion Historiográfica (Claim).

Epistemologia do Projeto:
Em vez de simplesmente vincular um Evento a uma Fonte com uma verdade única pré-estabelecida,
o modelo decompõe o conhecimento histórico em Proposições Factualmente Auditáveis (Claims).

Fluxo Epistemológico:
    EVENTO HISTÓRICO
          │
          ▼
    CLAIM (Afirmação / Proposição Específica)
          │
          ├──► FONTE A (Postura: 'apoia', Trecho X, Pág Y)
          ├──► FONTE B (Postura: 'contesta', Trecho W, Pág Z)
          └──► FONTE C (Postura: 'matiza', Trecho K)

Isso permite registrar controvérsias historiográficas sem artificialismos e sem forçar
uma versão unilateral quando as fontes documentais divergem.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey, DateTime
)
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Claim(Base):
    """
    Entidade Claim (Afirmação / Proposição Historiográfica):
    Representa uma asserção específica relativa a um acontecimento histórico.
    
    Exemplos de Afirmações:
    - 'Comando Vermelho expulsou a quadrilha rival do morro em maio de 1984.'
    - 'O número de vítimas fatais na operação policial foi de 12 pessoas.'
    - 'A organização X mantinha posto de observação com fuzis na localidade Y.'
    """
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    
    claim_type = Column(String(50), nullable=False, default="fato")
    # tipos: fato, data, autoria, territorio, baixa_letal, motivacao, presenca_armada
    
    statement = Column(Text, nullable=False)  # O enunciado factual afirmado
    confidence_level = Column(String(30), nullable=False, default="provavel", index=True)
    # confirmado, provavel, conflitante, nao_verificado
    
    is_disputed = Column(Boolean, default=False, nullable=False)  # Controvérsia ativa entre fontes
    epistemological_notes = Column(Text, nullable=True)  # Análise crítica sobre o confronto de versões
    
    is_demo = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)

    # Relacionamentos
    event = relationship("Event", back_populates="claims")
    source_links = relationship("ClaimSource", back_populates="claim", cascade="all, delete-orphan")

    @property
    def sources(self):
        return [link.source for link in self.source_links]

    @property
    def supporting_sources(self):
        return [link.source for link in self.source_links if link.stance == "apoia"]

    @property
    def contradicting_sources(self):
        return [link.source for link in self.source_links if link.stance == "contesta"]

    def __repr__(self):
        return f"<Claim(id={self.id}, type='{self.claim_type}', statement='{self.statement[:35]}...', disputed={self.is_disputed})>"


class ClaimSource(Base):
    """
    Associação entre Claim e Fonte Documental:
    Registra como cada documento específico se posiciona em relação à afirmação
    ('apoia', 'contesta', 'matiza', 'menciona') com a citação literal comprobatória.
    """
    __tablename__ = "claim_sources"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)

    stance = Column(String(30), default="apoia", nullable=False)
    # posturas: apoia, contesta, matiza, menciona
    
    page = Column(String(50), nullable=True)
    section = Column(String(100), nullable=True)
    excerpt = Column(Text, nullable=False)  # Citação textual literal do documento
    source_assessment = Column(String(100), nullable=True)  # ex: oficial, academica, testemunhal, pericial
    assessment_notes = Column(Text, nullable=True)
    confidence_level = Column(String(30), default="provavel", nullable=False)
    created_at = Column(DateTime, default=utc_now)

    # Relacionamentos
    claim = relationship("Claim", back_populates="source_links")
    source = relationship("Source", back_populates="claim_links")

    def __repr__(self):
        return f"<ClaimSource(claim_id={self.claim_id}, source_id={self.source_id}, stance='{self.stance}')>"
