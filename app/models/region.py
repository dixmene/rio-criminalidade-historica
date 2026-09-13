from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Region(Base):
    """
    Entidade Região/Território: Bairros, Favelas, Zonas ou Municípios
    do Estado do Rio de Janeiro, com coordenadas geográficas para plotagem no mapa.
    """
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    region_type = Column(String(100), nullable=False, default="bairro")
    # tipos: bairro, favela, municipio, zona, complexo, regiao_administrativa
    municipality = Column(String(100), nullable=False, default="Rio de Janeiro")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geojson_boundary = Column(Text, nullable=True)  # Coordenadas/geometria GeoJSON opcional
    description = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamento com eventos
    event_links = relationship("EventRegion", back_populates="region", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Region(id={self.id}, name='{self.name}', coords=({self.latitude}, {self.longitude}))>"
