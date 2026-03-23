from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models.user import User
from ..schemas.user import UserCreate
from .auth_service import auth_service


class UserService:
    """
    Servicio responsable ÚNICAMENTE del CRUD de usuarios.
    (SOLID - SRP: Single Responsibility Principle)
    """

    def get_by_username(self, db: Session, username: str) -> User | None:
        """
        Busca un usuario por nombre de usuario.

        Args:
            db: Sesión de base de datos.
            username: Nombre de usuario a buscar.

        Returns:
            El objeto User si existe, None en caso contrario.
        """
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, email: str) -> User | None:
        """
        Busca un usuario por email.

        Args:
            db: Sesión de base de datos.
            email: Email a buscar.

        Returns:
            El objeto User si existe, None en caso contrario.
        """
        return db.query(User).filter(User.email == email).first()

    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """
        Crea un nuevo usuario en la base de datos.

        Args:
            db: Sesión de base de datos.
            user_data: Datos validados por Pydantic.

        Returns:
            El nuevo objeto User creado.

        Raises:
            HTTPException 400 si el username o email ya existen.
        """
        # Verificar unicidad
        if self.get_by_username(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso",
            )
        if self.get_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado",
            )

        # Hashear contraseña antes de guardar [Seguridad]
        hashed_password = auth_service.hash_password(user_data.password)

        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def create_admin_if_not_exists(self, db: Session) -> None:
        """
        Crea un usuario administrador por defecto si no existe ninguno.
        """
        admin_username = "admin"
        if not self.get_by_username(db, admin_username):
            hashed_password = auth_service.hash_password("admin123")
            admin_user = User(
                username=admin_username,
                email="admin@example.com",
                hashed_password=hashed_password,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            print(f"Usuario administrador '{admin_username}' creado con éxito.")

    def authenticate_user(self, db: Session, username: str, password: str) -> User:
        """
        Verifica credenciales y devuelve el usuario si son correctas.

        Args:
            db: Sesión de base de datos.
            username: Nombre de usuario.
            password: Contraseña en texto plano.

        Returns:
            El objeto User autenticado.

        Raises:
            HTTPException 401 si las credenciales son incorrectas.
        """
        user = self.get_by_username(db, username)
        if not user or not auth_service.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nombre de usuario o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    def get_users(self, db: Session) -> list[User]:
        """
        Obtiene la lista de todos los usuarios registrados.

        Args:
            db: Sesión de base de datos.

        Returns:
            Lista de objetos User.
        """
        return db.query(User).all()


# Instancia global del servicio
user_service = UserService()
