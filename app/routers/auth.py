from fastapi import APIRouter, Depends, Request

from sqlalchemy.orm import Session

from ..config import settings

from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse, Token
from ..services.user_service import user_service
from ..services.auth_service import auth_service, get_current_user, get_current_admin

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Registrar nuevo usuario",
    description="Crea una cuenta nueva con username, email y contraseña.",
)

def register(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Registra un nuevo usuario en el sistema.

    - **username**: Nombre único (mínimo 3 caracteres)
    - **email**: Email válido y único
    - **password**: Contraseña (mínimo 6 caracteres)
    """
    new_user = user_service.create_user(db, user_data)
    return new_user


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión",
    description="Autentica un usuario y devuelve un JWT Bearer token.",
)

def login(
    request: Request,
    username: str,
    password: str,
    db: Session = Depends(get_db),
) -> Token:
    """
    Autentica al usuario y genera un JWT token.

    - **username**: Nombre de usuario
    - **password**: Contraseña en texto plano

    Devuelve un `access_token` de tipo Bearer válido por 30 minutos.
    """
    user = user_service.authenticate_user(db, username, password)
    access_token = auth_service.create_access_token(data={"sub": user.username})
    return Token(access_token=access_token)


@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="Listar todos los usuarios",
    description="Devuelve una lista de todos los usuarios registrados (requiere autenticación).",
)
def get_all_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
) -> list[UserResponse]:
    """Obtiene todos los usuarios de la base de datos."""
    return user_service.get_users(db)
