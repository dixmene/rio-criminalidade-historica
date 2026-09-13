from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SourceBase(BaseModel):
    title: str = Field(..., description="Título da fonte ou documento")
    citation: str = Field(..., description="Citação bibliográfica completa")
    author: Optional[str] = Field(None, description="Autor ou órgão emissor")
    publisher: Optional[str] = Field(None, description="Editora, veículo de imprensa ou órgão expedidor")
    publication_year: Optional[int] = Field(None, description="Ano de publicação")
    publication_date: Optional[str] = Field(None, description="Data de publicação completa se conhecida")
    document_date: Optional[str] = Field(None, description="Data a que os fatos do documento se referem")
    source_type: str = Field("oficial_relatorio", description="Tipologia do documento")
    url: Optional[str] = Field(None, description="Link de acesso digital")
    archive_ref: Optional[str] = Field(None, description="Referência arquivística / fundo / caixa")
    file_hash_sha256: Optional[str] = Field(None, description="Hash SHA-256 do arquivo original")
    notes: Optional[str] = Field(None, description="Notas de análise historiográfica")
    is_demo: bool = Field(False, description="Flag de identificação de dados DEMO")


class SourceCreate(SourceBase):
    pass


class SourceRead(SourceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
