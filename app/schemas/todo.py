from datetime import datetime
from pydantic import BaseModel, field_validator, computed_field
from ..managers.note_manager import NoteManager


class TodoCreate(BaseModel):
    """Schema para crear una nueva tarea."""

    title: str
    description: str = ""
    deadline: datetime | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """El título no puede estar vacío."""
        if not v.strip():
            raise ValueError("El título no puede estar vacío")
        return v.strip()


class TodoUpdate(BaseModel):
    """Schema para actualizar una tarea (todos los campos son opcionales)."""

    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    deadline: datetime | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str | None) -> str | None:
        """Si se proporciona título, no puede estar vacío."""
        if v is not None and not v.strip():
            raise ValueError("El título no puede estar vacío")
        return v.strip() if v else v


class TodoResponse(BaseModel):
    """Schema para devolver datos de una tarea."""

    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime
    deadline: datetime | None = None
    owner_id: int

    @computed_field
    @property
    def status_info(self) -> str:
        """Información calculada sobre el estado temporal de la tarea."""
        return NoteManager.get_time_remaining(self.deadline)

    model_config = {"from_attributes": True}
