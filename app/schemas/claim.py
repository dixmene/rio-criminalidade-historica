from datetime import datetime, date
from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClaimSourceLinkInput(BaseModel):
    source_id: int = Field(..., description="ID da fonte documental cadastrada")
    stance: str = Field("apoia", description="Postura da fonte: apoia, contesta, matiza, menciona")
    page: Optional[str] = Field(None, description="Página da citação")
    section: Optional[str] = Field(None, description="Seção, capítulo ou tomo")
    excerpt: str = Field(..., min_length=5, description="Trecho literal comprobatório")
    source_assessment: Optional[str] = Field(None, description="Avaliação da fonte (oficial, academica, testemunhal, pericial)")
    assessment_notes: Optional[str] = Field(None, description="Notas de análise crítica")
    confidence_level: str = Field("provavel", description="Nível de confiança: confirmado, provavel, conflitante, nao_verificado")

    @field_validator("stance")
    @classmethod
    def validate_stance(cls, v: str) -> str:
        allowed = {"apoia", "contesta", "matiza", "menciona"}
        if v.lower() not in allowed:
            raise ValueError(f"stance deve ser um de: {allowed}")
        return v.lower()


class ClaimBase(BaseModel):
    event_id: int = Field(..., description="ID do evento histórico associado")
    claim_type: str = Field("fato", description="Tipo de afirmação (fato, data, autoria, territorio, baixa_letal, motivacao)")
    statement: str = Field(..., min_length=5, description="Enunciado factual específico")
    confidence_level: str = Field("provavel", description="Nível de validação epistemológica")
    is_disputed: bool = Field(False, description="Flag indicando controvérsia ativa entre fontes")
    epistemological_notes: Optional[str] = Field(None, description="Análise crítica do confronto de versões")
    is_demo: bool = Field(False)

    @field_validator("confidence_level")
    @classmethod
    def validate_confidence(cls, v: str) -> str:
        allowed = {"confirmado", "provavel", "conflitante", "nao_verificado"}
        if v.lower() not in allowed:
            raise ValueError(f"confidence_level deve ser um de: {allowed}")
        return v.lower()


class ClaimCreate(ClaimBase):
    sources: List[ClaimSourceLinkInput] = Field(
        default_factory=list,
        description="Fontes que sustentam, contestam ou matizam esta afirmação."
    )


class ClaimSourceResponse(BaseModel):
    id: int
    claim_id: int
    source_id: int
    stance: str
    page: Optional[str] = None
    section: Optional[str] = None
    excerpt: str
    source_assessment: Optional[str] = None
    assessment_notes: Optional[str] = None
    confidence_level: str
    model_config = ConfigDict(from_attributes=True)


class ClaimResponse(ClaimBase):
    id: int
    created_at: Optional[datetime] = None
    source_links: List[ClaimSourceResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)
