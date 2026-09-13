from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Source(Base):
    """
    Entidade Fonte: Registra a bibliografia, documento oficial, jornal,
    depoimento ou relatório arquivístico.

    Diferenciação Conceitual:
    - O modelo Source registra a TIPOLOGIA DO DOCUMENTO e metadados de custódia.
    - O modelo EventSource registra a AVALIAÇÃO DA AFIRMAÇÃO (confirmado, provável, conflitante).
    """
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    citation = Column(Text, nullable=False)  # Citação bibliográfica formal (ABNT/Chicago)
    author = Column(String(255), nullable=True)
    publisher = Column(String(255), nullable=True)  # Editora, veículo ou órgão expedidor
    source_type = Column(String(100), nullable=False, default="oficial_relatorio")
    # tipos: academico_tese, academico_artigo, academico_livro, oficial_relatorio,
    # documento_judicial, jornalismo_investigativo, jornalismo_hemeroteca, historia_oral
    
    publication_year = Column(Integer, nullable=True, index=True)
    publication_date = Column(String(50), nullable=True)
    document_date = Column(String(50), nullable=True)
    url = Column(String(500), nullable=True)
    archive_ref = Column(String(255), nullable=True)  # ex: Arquivo Nacional / Fundo DOPS
    file_hash_sha256 = Column(String(64), nullable=True)
    notes = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)

    # Relacionamento de proveniência com eventos e afirmações (claims)
    event_links = relationship("EventSource", back_populates="source", cascade="all, delete-orphan")
    claim_links = relationship("ClaimSource", back_populates="source", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Source(id={self.id}, title='{self.title[:30]}...', year={self.publication_year})>"
