from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Person(Base):
    """
    Entidade Pessoa: Representa lideranças, agentes estatais, vítimas,
    testemunhas ou pesquisadores históricos.
    """
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    aliases = Column(String(255), nullable=True)  # Codinomes / alcunhas
    role_description = Column(String(255), nullable=True)  # Papel histórico comum
    notes = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamento com eventos
    event_links = relationship("EventPerson", back_populates="person", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Person(id={self.id}, name='{self.name}')>"
