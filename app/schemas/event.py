from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventSourceLinkInput(BaseModel):
    source_id: int = Field(..., description="ID da fonte que comprova o fato")
    page_or_section: Optional[str] = Field(None, description="Página, seção ou referência direta na fonte")
    excerpt: str = Field(..., min_length=5, description="Trecho literal/citação da fonte que sustenta o registro")
    claim_assertion: Optional[str] = Field(None, description="Afirmação sustentada")
    validation_status: str = Field("confirmado", description="Nível de validação (confirmado, provavel, conflitante, nao_verificado)")
    confidence_notes: Optional[str] = Field(None, description="Notas de análise crítica ou divergências")


class EventOrganizationLinkInput(BaseModel):
    organization_id: int
    role_in_event: Optional[str] = "participante"


class EventPersonLinkInput(BaseModel):
    person_id: int
    role_in_event: Optional[str] = "envolvido"


class EventRegionLinkInput(BaseModel):
    region_id: int
    specific_location_name: Optional[str] = None


class EventBase(BaseModel):
    title: str = Field(..., min_length=3, description="Título descritivo do evento")
    date_start: str = Field(..., description="Data de início (YYYY-MM-DD ou YYYY)")
    date_end: Optional[str] = Field(None, description="Data de fim (se contínuo)")
    year: int = Field(..., description="Ano do evento para ordenação na timeline")
    exact_date: bool = Field(True, description="Se a data é exata ou aproximada")
    description: str = Field(..., min_length=10, description="Descrição detalhada do ocorrido")
    historical_context: Optional[str] = Field(None, description="Contexto político/social ampliado")
    confidence_level: str = Field("confirmado", description="Nível global de confiança do evento")
    is_demo: bool = Field(False, description="Flag indicativa de dados de teste DEMO")


class EventCreate(EventBase):
    sources: List[EventSourceLinkInput] = Field(
        ...,
        min_length=1,
        description="Regra de Ouro: Pelo menos uma fonte documentada é obrigatória para registrar um evento."
    )
    organizations: Optional[List[EventOrganizationLinkInput]] = Field(default_factory=list)
    people: Optional[List[EventPersonLinkInput]] = Field(default_factory=list)
    regions: Optional[List[EventRegionLinkInput]] = Field(default_factory=list)

    @field_validator("confidence_level")
    @classmethod
    def validate_confidence(cls, v: str) -> str:
        allowed = {"confirmado", "provavel", "conflitante", "nao_verificado"}
        if v not in allowed:
            raise ValueError(f"confidence_level deve ser um de: {allowed}")
        return v


class EventRead(EventBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
