from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


from .config import settings
from .database import engine
from .models import user, todo  # Importar para que SQLAlchemy cree las tablas
from .routers import auth, todos
from .services.user_service import user_service
from .database import SessionLocal

# ────────────────────────────────────────────
#  Crear tablas en la base de datos al arrancar
# ────────────────────────────────────────────
from .database import Base
Base.metadata.create_all(bind=engine)

# Crear admin por defecto si no existe
db = SessionLocal()
try:
    user_service.create_admin_if_not_exists(db)
finally:
    db.close()


# ────────────────────────────────────────────
#  Instancia de FastAPI
# ────────────────────────────────────────────
app = FastAPI(
    title="📝 ToDoList API",
    description="""
## API REST para gestión de tareas personales

**Proyecto Final** del curso de Python Avanzado.
Aplica: POO, SOLID, Pydantic, SQLAlchemy, JWT Auth, Rate Limiting y buenas prácticas.

### Cómo usar:
1. **Registra** un usuario en `/auth/register`
2. **Inicia sesión** en `/auth/login` para obtener un token JWT
3. Haz clic en **Authorize** 🔒 e introduce: `Bearer <tu_token>`
4. Usa los endpoints de `/todos` para gestionar tus tareas
    """,
    version="1.0.0",
    contact={
        "name": "Proyecto Final — Curso Python Avanzado",
    },
)



# ────────────────────────────────────────────
#  Middleware CORS 
# ────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# ────────────────────────────────────────────
#  Incluir routers
# ────────────────────────────────────────────

app.include_router(todos.router)


# ────────────────────────────────────────────
#  Endpoint raíz
# ────────────────────────────────────────────
@app.get("/", tags=["Root"], summary="Bienvenida")
async def root() -> dict:
    """Endpoint de bienvenida con información de la API."""
    return {
        "message": "📝 Bienvenido a la API de Todo List",
        "docs": "http://127.0.0.1:8000/docs",
        "version": "1.0.0",
    }
