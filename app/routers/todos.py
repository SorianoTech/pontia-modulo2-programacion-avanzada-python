
from fastapi import APIRouter, Depends, Request
from ..limiter import limiter
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models.user import User
from ..schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from ..services.auth_service import get_current_user
from ..services.todo_service import todo_service

# Limiter ya importado de ..limiter

router = APIRouter(
    prefix="/todos",
    tags=["Tareas (ToDo)"],
)


@router.get(
    "/",
    response_model=list[TodoResponse],
    summary="Listar todas mis tareas",
    description="Devuelve todas las tareas pertenecientes al usuario autenticado.",
)
@limiter.limit(settings.RATE_LIMIT)
async def get_todos(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TodoResponse]:
    """
    Retorna la lista completa de tareas del usuario autenticado.

    Requiere: **Bearer token** en el header Authorization.
    """
    return todo_service.get_todos(db, owner_id=current_user.id)


@router.get(
    "/expired",
    response_model=list[TodoResponse],
    summary="Listar tareas caducadas",
    description="Devuelve las tareas cuya fecha límite ya ha pasado.",
)
@limiter.limit(settings.RATE_LIMIT)
async def get_expired_todos(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TodoResponse]:
    """Retorna las tareas del usuario con deadline anterior a ahora."""
    return todo_service.get_expired_todos(db, owner_id=current_user.id)


@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Obtener una tarea por ID",
    description="Devuelve el detalle de una tarea específica si pertenece al usuario.",
)
@limiter.limit(settings.RATE_LIMIT)
async def get_todo(
    request: Request,
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TodoResponse:
    """Retorna una tarea específica por su ID."""
    return todo_service.get_todo(db, todo_id, owner_id=current_user.id)


@router.post(
    "/",
    response_model=TodoResponse,
    status_code=201,
    summary="Crear nueva tarea",
    description="Crea una nueva tarea para el usuario autenticado.",
)
@limiter.limit(settings.RATE_LIMIT)
async def create_todo(
    request: Request,
    todo_data: TodoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TodoResponse:
    """
    Crea una nueva tarea.

    - **title**: Título de la tarea (obligatorio)
    - **description**: Descripción opcional (sanitizada contra XSS)

    Requiere: **Bearer token** en el header Authorization.
    """
    return todo_service.create_todo(db, todo_data, owner_id=current_user.id)


@router.put(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Actualizar tarea",
    description="Actualiza los campos de una tarea existente. Solo el propietario puede editar.",
)
@limiter.limit(settings.RATE_LIMIT)
async def update_todo(
    request: Request,
    todo_id: int,
    todo_data: TodoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TodoResponse:
    """
    Actualiza una tarea existente (actualización parcial: solo los campos enviados).

    - **title**: Nuevo título (opcional)
    - **description**: Nueva descripción (opcional, sanitizada contra XSS)
    - **completed**: Estado de completitud (opcional)

    Requiere: **Bearer token** en el header Authorization.
    """
    return todo_service.update_todo(db, todo_id, todo_data, owner_id=current_user.id)


@router.patch(
    "/{todo_id}/complete",
    response_model=TodoResponse,
    summary="Marcar tarea como completada",
    description="Cambia el estado de una tarea a 'completada' (True).",
)
@limiter.limit(settings.RATE_LIMIT)
async def complete_todo(
    request: Request,
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TodoResponse:
    """
    Marca una tarea como completada de forma rápida.

    Requiere: **Bearer token** en el header Authorization.
    """
    return todo_service.complete_todo(db, todo_id, owner_id=current_user.id)


@router.delete(
    "/{todo_id}",
    summary="Eliminar tarea",
    description="Elimina permanentemente una tarea. Solo el propietario puede eliminar.",
)
@limiter.limit(settings.RATE_LIMIT)
async def delete_todo(
    request: Request,
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Elimina una tarea existente del usuario autenticado.

    Requiere: **Bearer token** en el header Authorization.
    """
    return todo_service.delete_todo(db, todo_id, owner_id=current_user.id)
