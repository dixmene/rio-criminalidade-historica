from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PersonBase(BaseModel):
    name: str = Field(..., description="Nome completo da pessoa/liderança")
    aliases: Optional[str] = Field(None, description="Alcunhas ou codinomes")
    role_description: Optional[str] = Field(None, description="Papel histórico")
    notes: Optional[str] = Field(None, description="Notas complementares")
    is_demo: bool = Field(False)


class PersonCreate(PersonBase):
    pass


class PersonRead(PersonBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
