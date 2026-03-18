from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..database import Base


class User(Base):
    """
    Representa un usuario del sistema.

    Atributos:
        id: Clave primaria autoincremental.
        username: Nombre de usuario único.
        email: Email único del usuario.
        hashed_password: Contraseña hasheada con bcrypt.
        is_active: Indica si la cuenta está activa.
        todos: Relación uno-a-muchos con tareas del usuario.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Relación uno-a-muchos: un user tiene muchos todos
    todos = relationship("Todo", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"
