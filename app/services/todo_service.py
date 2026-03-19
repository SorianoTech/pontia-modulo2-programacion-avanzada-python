
import bleach
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.todo import Todo
from ..schemas.todo import TodoCreate, TodoUpdate
from ..managers.note_manager import NoteManager


class TodoService:
    """
    Servicio responsable ÚNICAMENTE del CRUD de tareas.
    (SOLID - SRP: Single Responsibility Principle)

    Seguridad aplicada:
        - SQL Injection: prevenido por SQLAlchemy ORM (nunca SQL raw)
        - XSS: las descriptions se sanitizan con bleach.clean()
    """

    @staticmethod
    def _sanitize(text: str) -> str:
        """
        Sanitiza texto usando NoteManager (POO).
        """
        return NoteManager.clean_text(text)

    def get_todos(self, db: Session, owner_id: int) -> list[Todo]:
        """
        Devuelve todas las tareas del usuario especificado.

        Args:
            db: Sesión de base de datos.
            owner_id: ID del usuario propietario.

        Returns:
            Lista de todos del usuario.
        """
        return db.query(Todo).filter(Todo.owner_id == owner_id).all()

    def get_todo(self, db: Session, todo_id: int, owner_id: int) -> Todo:
        """
        Obtiene una tarea por ID verificando que pertenece al usuario.

        Args:
            db: Sesión de base de datos.
            todo_id: ID de la tarea.
            owner_id: ID del usuario (para verificar ownership).

        Returns:
            El objeto Todo solicitado.

        Raises:
            HTTPException 404 si no existe o no pertenece al usuario.
        """
        todo = (
            db.query(Todo)
            .filter(Todo.id == todo_id, Todo.owner_id == owner_id)
            .first()
        )
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarea con id={todo_id} no encontrada",
            )
        return todo

    def create_todo(self, db: Session, todo_data: TodoCreate, owner_id: int) -> Todo:
        """
        Crea una nueva tarea para el usuario indicado.
        La description se sanitiza contra XSS antes de guardar.
        El deadline se valida usando las reglas de NoteManager.

        Args:
            db: Sesión de base de datos.
            todo_data: Datos validados por Pydantic.
            owner_id: ID del usuario propietario.

        Returns:
            El nuevo objeto Todo creado.
        """
        # Validación de reglas de negocio del dominio (deadline)
        try:
            NoteManager.validate_deadline(todo_data.deadline)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        db_todo = Todo(
            title=self._sanitize(todo_data.title),
            description=self._sanitize(todo_data.description),
            deadline=todo_data.deadline,
            owner_id=owner_id,
        )
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo

    def update_todo(
        self,
        db: Session,
        todo_id: int,
        todo_data: TodoUpdate,
        owner_id: int,
    ) -> Todo:
        """
        Actualiza una tarea existente (solo los campos proporcionados).

        Args:
            db: Sesión de base de datos.
            todo_id: ID de la tarea a actualizar.
            todo_data: Campos a actualizar (todos opcionales).
            owner_id: ID del usuario (verifica ownership).

        Returns:
            El objeto Todo actualizado.

        Raises:
            HTTPException 404 si no existe o no pertenece al usuario.
            HTTPException 400 si el deadline es inválido.
        """
        todo = self.get_todo(db, todo_id, owner_id)

        # Actualizar solo los campos enviados (partial update)
        if todo_data.title is not None:
            todo.title = self._sanitize(todo_data.title)
        if todo_data.description is not None:
            todo.description = self._sanitize(todo_data.description)
        if todo_data.completed is not None:
            todo.completed = todo_data.completed
        if todo_data.deadline is not None:
            try:
                NoteManager.validate_deadline(todo_data.deadline)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            todo.deadline = todo_data.deadline

        db.commit()
        db.refresh(todo)
        return todo

    def delete_todo(self, db: Session, todo_id: int, owner_id: int) -> dict:
        """
        Elimina una tarea existente.

        Args:
            db: Sesión de base de datos.
            todo_id: ID de la tarea a eliminar.
            owner_id: ID del usuario (verifica ownership).

        Returns:
            Mensaje de confirmación.

        Raises:
            HTTPException 404 si no existe o no pertenece al usuario.
        """
        todo = self.get_todo(db, todo_id, owner_id)
        db.delete(todo)
        db.commit()
        return {"message": f"Tarea '{todo.title}' eliminada correctamente"}

    def complete_todo(self, db: Session, todo_id: int, owner_id: int) -> Todo:
        """
        Marca una tarea como completada.

        Args:
            db: Sesión de base de datos.
            todo_id: ID de la tarea.
            owner_id: ID del usuario (verifica ownership).

        Returns:
            El objeto Todo actualizado.
        """
        todo = self.get_todo(db, todo_id, owner_id)
        todo.completed = True
        db.commit()
        db.refresh(todo)
        return todo

    def get_expired_todos(self, db: Session, owner_id: int) -> list[Todo]:
        """
        Devuelve las tareas caducadas del usuario.
        """
        now = datetime.now()
        return (
            db.query(Todo)
            .filter(
                Todo.owner_id == owner_id,
                Todo.deadline != None,
                Todo.deadline < now
            )
            .all()
        )


# Instancia global del servicio
todo_service = TodoService()
