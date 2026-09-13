from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Organization(Base):
    """
    Entidade Organização: Agências estatais, órgãos de segurança,
    coletivos da sociedade civil, sindicatos, grupos armados ou partidos.
    """
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    acronym = Column(String(50), nullable=True, index=True)  # ex: OAB, DOPS, SNI, PMERJ
    org_type = Column(String(100), nullable=False, default="sociedade_civil")
    # tipos: orgao_estatal, policial, militar, sociedade_civil, sindicato, grupo_politico
    notes = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamento com eventos
    event_links = relationship("EventOrganization", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', acronym='{self.acronym}')>"
