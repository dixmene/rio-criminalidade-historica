from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Source(Base):
    """
    Entidade Fonte: Registra a bibliografia, documento oficial, jornal,
    depoimento ou relatório arquivístico.
    """
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    citation = Column(Text, nullable=False)  # Citação bibliográfica completa (ABNT/Chicago)
    author = Column(String(255), nullable=True)
    publication_year = Column(Integer, nullable=True, index=True)
    source_type = Column(String(100), nullable=False, default="documento_oficial")  
    # tipos: documento_oficial, artigo_academico, livro, jornal, relatorio_comissao, depoimento
    url = Column(String(500), nullable=True)
    archive_ref = Column(String(255), nullable=True)  # ex: Arquivo Nacional / Fundo DOPS
    reliability_rating = Column(Integer, default=5)  # 1 a 5
    is_demo = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamento de proveniência com eventos
    event_links = relationship("EventSource", back_populates="source", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Source(id={self.id}, title='{self.title[:30]}...', year={self.publication_year})>"
