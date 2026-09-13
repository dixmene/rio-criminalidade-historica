from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Organization(Base):
    """
    Entidade Organização / Facção / Milícia / Órgão Estatal:
    Preserva original_name e normalized_name para buscas sem perda histórica.
    """
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    original_name = Column(String(255), nullable=False)
    normalized_name = Column(String(255), nullable=False, index=True)
    acronym = Column(String(50), nullable=True, index=True)  # ex: CV, OAB-RJ, DOPS
    org_type = Column(String(100), nullable=False, default="sociedade_civil")
    # tipos: faccao_criminosa, milicia, policial, orgao_estatal, sindicato, sociedade_civil
    foundation_year = Column(Integer, nullable=True)
    dissolution_year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)

    # Relacionamento com eventos
    event_links = relationship("EventOrganization", back_populates="organization", cascade="all, delete-orphan")

    @property
    def name(self) -> str:
        """Compatibilidade para exibição com a grafia original."""
        return self.original_name

    @property
    def organization_type(self) -> str:
        """Propriedade canônica de tipologia da organização."""
        return self.org_type

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.original_name}', acronym='{self.acronym}')>"
