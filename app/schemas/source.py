from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SourceBase(BaseModel):
    title: str = Field(..., description="Título da fonte ou documento")
    citation: str = Field(..., description="Citação bibliográfica completa")
    author: Optional[str] = Field(None, description="Autor ou órgão emissor")
    publication_year: Optional[int] = Field(None, description="Ano de publicação")
    source_type: str = Field("documento_oficial", description="Tipo de documento")
    url: Optional[str] = Field(None, description="Link de acesso digital")
    archive_ref: Optional[str] = Field(None, description="Referência arquivística / fundo")
    reliability_rating: int = Field(5, ge=1, le=5, description="Grau de confiabilidade de 1 a 5")
    is_demo: bool = Field(False, description="Flag de identificação de dados DEMO")


class SourceCreate(SourceBase):
    pass


class SourceRead(SourceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
