
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings


# Motor de base de datos (SQLite para desarrollo)
engine = create_engine(
    settings.DATABASE_URL,
    # SQLite específico: permite acceso desde múltiples threads
    connect_args={"check_same_thread": False},
)

# Fábrica de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Clase base para todos los modelos SQLAlchemy."""
    pass


def get_db():
    """
    Dependency de FastAPI: proporciona una sesión de DB por request.
    Garantiza que la sesión se cierra siempre (evita leaks).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
