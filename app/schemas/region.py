from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from src.normalization.rules import normalize_location


class RegionBase(BaseModel):
    original_name: str = Field(..., description="Nome do território/bairro/favela na grafia original")
    normalized_name: Optional[str] = Field(None, description="Nome normalizado em maiúsculas sem acentos")
    region_type: str = Field("bairro", description="Tipo de região")
    municipality: Optional[str] = Field("Rio de Janeiro", description="Município de localização")
    latitude: Optional[float] = Field(None, description="Latitude geográfica (opcional, sem invenção de coordenadas)")
    longitude: Optional[float] = Field(None, description="Longitude geográfica (opcional, sem invenção de coordenadas)")
    location_precision: str = Field("aproximada", description="Precisão: exata, aproximada, centroide, desconhecida")
    geometry_source: Optional[str] = Field(None, description="Origem da geometria (IBGE, Data.Rio, etc.)")
    geometry_confidence: Optional[str] = Field(None, description="Confiança cartográfica: alta, media, baixa")
    geojson_boundary: Optional[str] = Field(None, description="Geometria GeoJSON opcional")
    description: Optional[str] = Field(None, description="Descrição histórica do território")
    is_demo: bool = Field(False)


class RegionCreate(RegionBase):
    def model_post_init(self, __context):
        if not self.normalized_name and self.original_name:
            norm = normalize_location(self.original_name)
            self.normalized_name = norm["normalized_name"]


class RegionRead(RegionBase):
    id: int
    name: str = Field(..., description="Nome para exibição (original_name)")
    model_config = ConfigDict(from_attributes=True)
