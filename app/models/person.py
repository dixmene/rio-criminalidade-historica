from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Person(Base):
    """
    Entidade Pessoa / Liderança Documentada:
    Preserva original_name e normalized_name para buscas consistentes.
    """
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, index=True)
    original_name = Column(String(255), nullable=False)
    normalized_name = Column(String(255), nullable=False, index=True)
    aliases = Column(String(255), nullable=True)  # Codinomes / alcunhas documentadas
    role_description = Column(String(255), nullable=True)  # Papel histórico atestado
    birth_year = Column(Integer, nullable=True)
    death_year = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)

    # Relacionamento com eventos
    event_links = relationship("EventPerson", back_populates="person", cascade="all, delete-orphan")

    @property
    def name(self) -> str:
        """Compatibilidade para exibição com a grafia original."""
        return self.original_name

    def __repr__(self):
        return f"<Person(id={self.id}, name='{self.original_name}', normalized='{self.normalized_name}')>"
