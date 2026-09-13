from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class OrganizationBase(BaseModel):
    name: str = Field(..., description="Nome da organização")
    acronym: Optional[str] = Field(None, description="Sigla (ex: OAB, DOPS)")
    org_type: str = Field("sociedade_civil", description="Tipo de organização")
    notes: Optional[str] = Field(None, description="Notas históricas")
    is_demo: bool = Field(False)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationRead(OrganizationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
