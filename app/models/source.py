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
    - O modelo EventSource registra a AVALIAÇÃO DA AFIRMAÇÃO.
    - SourceDerivation registra a linhagem documental entre fontes.
    """
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    citation = Column(Text, nullable=False)  # Citação bibliográfica formal (ABNT/Chicago)
    author = Column(String(255), nullable=True)
    publisher = Column(String(255), nullable=True)  # Editora, veículo ou órgão expedidor
    source_type = Column(String(100), nullable=False, default="oficial_relatorio")
    # tipos: academico_tese, academico_artigo, academico_livro, oficial_relatorio,
    # documento_judicial, jornalismo_investigativo, jornalismo_hemeroteca, historia_oral,
    # video_youtube, entrevista, arquivo_digital

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

    # Genealogia documental: uma fonte pode derivar de várias fontes e ser
    # reutilizada por várias outras fontes.
    derived_sources = relationship(
        "SourceDerivation",
        foreign_keys="SourceDerivation.parent_source_id",
        back_populates="parent_source",
        cascade="all, delete-orphan",
    )
    source_derivations = relationship(
        "SourceDerivation",
        foreign_keys="SourceDerivation.derived_source_id",
        back_populates="derived_source",
        cascade="all, delete-orphan",
    )

    @property
    def is_root(self) -> bool:
        """True se a fonte não deriva de nenhuma outra fonte ou se todas as suas derivações forem independentes."""
        if not self.source_derivations:
            return True
        return all(d.is_independent for d in self.source_derivations)

    def get_root_source(self, visited=None) -> "Source":
        """
        Percorre recursivamente a linhagem documental ascendente até encontrar
        a fonte raiz primária / original. Protegido contra ciclos no grafo.
        """
        if visited is None:
            visited = set()
        if self.id in visited:
            return self
        visited.add(self.id)

        # Busca derivações ascendentes dependentes (is_independent == False)
        dependent_derivations = [
            d for d in self.source_derivations
            if not d.is_independent and d.parent_source is not None
        ]
        if not dependent_derivations:
            return self

        # Segue recursivamente a fonte ascendente
        return dependent_derivations[0].parent_source.get_root_source(visited)

    def get_all_derived_sources(self, visited=None) -> list:
        """Retorna lista de todas as fontes que derivam direta ou indiretamente desta fonte."""
        if visited is None:
            visited = set()
        if self.id in visited:
            return []
        visited.add(self.id)

        results = []
        for link in self.derived_sources:
            child = link.derived_source
            if child and child.id not in visited:
                results.append(child)
                results.extend(child.get_all_derived_sources(visited))
        return results

    def __repr__(self):
        return f"<Source(id={self.id}, title='{self.title[:30]}...', year={self.publication_year})>"
