from datetime import date
from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from src.normalization.rules import normalize_date
from app.schemas.claim import ClaimCreate, ClaimResponse


class EventSourceLinkInput(BaseModel):
    source_id: int = Field(..., description="ID da fonte documental cadastrada")
    page: Optional[str] = Field(None, description="Página exata da citação")
    section: Optional[str] = Field(None, description="Seção, capítulo ou tomo da citação")
    page_or_section: Optional[str] = Field(None, description="Página ou seção (compatibilidade retroativa)")
    excerpt: str = Field(..., min_length=5, description="Trecho literal que comprova a afirmação (obrigatório)")
    claim: Optional[str] = Field(None, description="Afirmação ou proposição factual sustentada")
    claim_assertion: Optional[str] = Field(None, description="Afirmação sintetizada (compatibilidade retroativa)")
    source_assessment: Optional[str] = Field(None, description="Avaliação da fonte: oficial, academica, testemunhal, pericial, jornalistica")
    assessment_notes: Optional[str] = Field(None, description="Notas de análise crítica da fonte")
    confidence_level: Optional[str] = Field("confirmado", description="Nível de validação da evidência nesta ligação")
    validation_status: str = Field("confirmado", description="Status de validação (confirmado, provavel, conflitante, nao_verificado)")
    confidence_notes: Optional[str] = Field(None, description="Notas críticas sobre convergência ou divergência")

    def model_post_init(self, __context):
        if self.page_or_section and not self.page and not self.section:
            self.page = self.page_or_section
        elif self.page and not self.page_or_section:
            self.page_or_section = self.page

        if self.claim and not self.claim_assertion:
            self.claim_assertion = self.claim
        elif self.claim_assertion and not self.claim:
            self.claim = self.claim_assertion

        if self.confidence_level and not self.validation_status:
            self.validation_status = self.confidence_level
        elif self.validation_status and not self.confidence_level:
            self.confidence_level = self.validation_status


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
    title: str = Field(..., min_length=3, description="Título do evento")
    event_type: str = Field("acontecimento_geral", description="Classificação do evento histórico")
    date_display: str = Field(..., description="Data exatamente como informada pela fonte (ex: 'maio de 1978', '1975', '15/03/1983')")
    date_start: Optional[Union[date, str]] = Field(None, description="Data normalizada de início (Date ou ISO YYYY-MM-DD)")
    date_end: Optional[Union[date, str]] = Field(None, description="Data de fim (Date ou ISO YYYY-MM-DD se intervalo)")
    year: Optional[int] = Field(None, description="Ano de referência para linha do tempo")
    temporal_precision: str = Field("dia", description="Precisão temporal: dia, mes, ano, decada, intervalo, aproximado, desconhecido")
    exact_date: bool = Field(False, description="True somente se dia, mês e ano forem exatos")
    date_is_estimated: bool = Field(False, description="True se os limites de date_start/date_end foram inferidos/estimados")
    description: str = Field(..., min_length=10, description="Descrição detalhada dos fatos documentados")
    historical_context: Optional[str] = Field(None, description="Contexto social/político ampliado")
    confidence_level: str = Field("confirmado", description="Nível de confiança geral do evento")
    is_demo: bool = Field(False, description="Flag indicativa de dados técnicos de teste [DEMO]")


class EventCreate(EventBase):
    sources: List[EventSourceLinkInput] = Field(
        default_factory=list,
        description="Fontes vinculadas que sustentam a afirmação do evento."
    )
    claims: Optional[List[ClaimCreate]] = Field(
        default_factory=list,
        description="Afirmações atomizadas associadas ao evento."
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

    @model_validator(mode="after")
    def validate_provenance_and_temporality(self):
        # 1. Regra de Proveniência Estrita:
        # Eventos históricos reais (is_demo=False) JAMAIS podem ser cadastrados sem fontes vinculadas.
        if not self.is_demo and len(self.sources) == 0:
            raise ValueError(
                "Regra de Proveniência Violada: Nenhum evento histórico real pode ser cadastrado sem pelo menos uma fonte documentada."
            )

        # 2. Auto-preenchimento temporal inteligente a partir de date_display se não fornecido
        if self.year is None and self.date_display:
            dt, yr, exact = normalize_date(self.date_display)
            if self.date_start is None and dt:
                self.date_start = dt
            if self.year is None:
                self.year = yr
            if not self.exact_date:
                self.exact_date = exact

        return self


class EventRead(EventBase):
    id: int
    claims: List[ClaimResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)
