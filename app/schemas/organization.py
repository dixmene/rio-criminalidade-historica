from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from src.normalization.rules import normalize_organization


class OrganizationBase(BaseModel):
    original_name: str = Field(..., description="Nome da organização na grafia original")
    normalized_name: Optional[str] = Field(None, description="Nome normalizado em maiúsculas sem acentos")
    acronym: Optional[str] = Field(None, description="Sigla documentada (ex: OAB, DOPS, CV)")
    org_type: str = Field("sociedade_civil", description="Tipo de organização")
    foundation_year: Optional[int] = Field(None, description="Ano de fundação (NULL se desconhecido)")
    dissolution_year: Optional[int] = Field(None, description="Ano de dissolução (NULL se ativa/desconhecido)")
    description: Optional[str] = Field(None, description="Notas históricas documentadas")
    is_demo: bool = Field(False)


class OrganizationCreate(OrganizationBase):
    def model_post_init(self, __context):
        if not self.normalized_name and self.original_name:
            norm = normalize_organization(self.original_name)
            self.normalized_name = norm["normalized_name"]


class OrganizationRead(OrganizationBase):
    id: int
    name: str = Field(..., description="Nome para exibição (original_name)")
    model_config = ConfigDict(from_attributes=True)
