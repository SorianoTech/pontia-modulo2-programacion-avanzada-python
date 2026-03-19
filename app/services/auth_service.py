
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models.user import User
from ..schemas.user import TokenData

# Esquema de seguridad Bearer Token
security = HTTPBearer()


class AuthService:
    """
    Servicio responsable ÚNICAMENTE de la lógica de autenticación.
    (SOLID - SRP: Single Responsibility Principle)

    Responsabilidades:
        - Hashear y verificar contraseñas con bcrypt
        - Generar y verificar tokens JWT
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """Genera el hash bcrypt de una contraseña en texto plano."""
        # bcrypt requiere bytes y tiene un límite de 72 bytes
        salt = bcrypt.gensalt()
        pw_bytes = password.encode('utf-8')[:72]
        hashed = bcrypt.hashpw(pw_bytes, salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Compara una contraseña en texto plano con su hash."""
        pw_bytes = plain_password.encode('utf-8')[:72]
        return bcrypt.checkpw(
            pw_bytes, 
            hashed_password.encode('utf-8')
        )

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Genera un JWT token firmado con HS256.

        Args:
            data: Payload a incluir en el token.
            expires_delta: Tiempo de vida del token. Por defecto usa config.

        Returns:
            Token JWT como string.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> TokenData:
        """
        Verifica y decodifica un JWT token.

        Args:
            token: JWT token como string.

        Returns:
            TokenData con el username extraído.

        Raises:
            HTTPException 401 si el token es inválido o expirado.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str | None = payload.get("sub")
            if username is None:
                raise credentials_exception
            return TokenData(username=username)
        except JWTError:
            raise credentials_exception


# Instancia global del servicio
auth_service = AuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency de FastAPI: extrae y valida el usuario a partir del JWT.
    Usada en todos los endpoints protegidos.

    Returns:
        El objeto User activo del token.

    Raises:
        HTTPException 401 si el token es inválido.
        HTTPException 400 si el usuario está desactivado.
    """
    token_data = auth_service.verify_token(credentials.credentials)
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo",
        )
    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency que verifica que el usuario autenticado sea administrador.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación no permitida: se requieren privilegios de administrador",
        )
    return current_user
