
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings


# Motor de base de datos
# Detectar si es SQLite para aplicar connect_args específicos
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
engine_args = {}
if is_sqlite:
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    **engine_args
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
