from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RegionBase(BaseModel):
    name: str = Field(..., description="Nome do território/bairro/favela")
    region_type: str = Field("bairro", description="Tipo de região")
    municipality: str = Field("Rio de Janeiro", description="Município")
    latitude: float = Field(..., description="Latitude geográfica")
    longitude: float = Field(..., description="Longitude geográfica")
    geojson_boundary: Optional[str] = Field(None, description="Geometria GeoJSON opcional")
    description: Optional[str] = Field(None, description="Descrição histórica do território")
    is_demo: bool = Field(False)


class RegionCreate(RegionBase):
    pass


class RegionRead(RegionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
