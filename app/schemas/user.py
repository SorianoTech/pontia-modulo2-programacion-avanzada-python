from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    """Schema para registrar un nuevo usuario."""

    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_min_length(cls, v: str) -> str:
        """El nombre de usuario debe tener al menos 3 caracteres."""
        if len(v.strip()) < 3:
            raise ValueError("El nombre de usuario debe tener al menos 3 caracteres")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        """La contraseña debe tener al menos 6 caracteres."""
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v


class UserResponse(BaseModel):
    """Schema para devolver datos del usuario (sin contraseña)."""

    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema para la respuesta del token JWT."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Datos extraídos del payload del JWT."""

    username: str | None = None
