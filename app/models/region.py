from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Region(Base):
    """
    Entidade Região/Território:
    Representa municípios, bairros, favelas, complexos ou regiões históricas.
    
    Regra de Geolocalização:
    - Latitude e Longitude são estritamente NULLABLE.
    - Nenhuma coordenada pode ser inventada se a fonte não fornecer localização precisa.
    - Preserva original_name e normalized_name.
    """
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    original_name = Column(String(255), nullable=False)
    normalized_name = Column(String(255), nullable=False, index=True)
    region_type = Column(String(100), nullable=False, default="bairro")
    # tipos: bairro, favela, complexo, municipio, zona, territorio_historico
    municipality = Column(String(100), nullable=True, default="Rio de Janeiro")
    
    # Coordenadas estritamente opcionais (não inventar coordenadas!)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_precision = Column(String(50), nullable=False, default="aproximada")
    # precisão: exata, aproximada, centroide, desconhecida
    geometry_source = Column(String(100), nullable=True)  # ex: IBGE, IPP/Data.Rio, Pesquisa
    geometry_confidence = Column(String(50), nullable=True)  # alta, media, baixa
    
    geojson_boundary = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)

    # Relacionamento com eventos
    event_links = relationship("EventRegion", back_populates="region", cascade="all, delete-orphan")

    @property
    def name(self) -> str:
        """Compatibilidade para exibição com a grafia original."""
        return self.original_name

    @property
    def has_coordinates(self) -> bool:
        return self.latitude is not None and self.longitude is not None

    def __repr__(self):
        coords = f"({self.latitude}, {self.longitude})" if self.has_coordinates else "(sem coordenadas)"
        return f"<Region(id={self.id}, name='{self.original_name}', coords={coords})>"
