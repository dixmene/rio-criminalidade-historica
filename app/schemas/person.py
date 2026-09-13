from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from src.normalization.rules import normalize_name


class PersonBase(BaseModel):
    original_name: str = Field(..., description="Nome completo da pessoa na grafia original")
    normalized_name: Optional[str] = Field(None, description="Nome normalizado em maiúsculas sem acentos")
    aliases: Optional[str] = Field(None, description="Alcunhas ou codinomes documentados")
    role_description: Optional[str] = Field(None, description="Papel histórico atestado")
    birth_year: Optional[int] = Field(None, description="Ano de nascimento")
    death_year: Optional[int] = Field(None, description="Ano de falecimento")
    notes: Optional[str] = Field(None, description="Notas complementares de pesquisa")
    is_demo: bool = Field(False)


class PersonCreate(PersonBase):
    def model_post_init(self, __context):
        if not self.normalized_name and self.original_name:
            norm = normalize_name(self.original_name)
            self.normalized_name = norm["normalized_name"]


class PersonRead(PersonBase):
    id: int
    name: str = Field(..., description="Nome para exibição (original_name)")
    model_config = ConfigDict(from_attributes=True)
