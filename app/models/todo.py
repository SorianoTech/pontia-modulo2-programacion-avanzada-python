from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Todo(Base):
    """
    Representa una tarea (todo) del sistema.

    Atributos:
        id: Clave primaria autoincremental.
        title: Título de la tarea (obligatorio).
        description: Descripción detallada (sanitizada contra XSS).
        completed: Estado de completitud.
        created_at: Timestamp de creación (automático).
        owner_id: Clave foránea al usuario propietario.
        owner: Relación con el modelo User.
    """

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True, default="")
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deadline = Column(DateTime(timezone=True), nullable=True)

    # Clave foránea: cada todo pertenece a un usuario
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relación inversa: accede al usuario propietario
    owner = relationship("User", back_populates="todos")

    def __repr__(self) -> str:
        return f"Todo(id={self.id!r}, title={self.title!r}, completed={self.completed!r})"
