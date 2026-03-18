# 📝 ToDoList API — Proyecto Final del Curso

API REST completa para gestión de tareas personales, construida con **FastAPI** como Proyecto Final del curso de Python Avanzado.

## 🏗️ Tecnologías y conceptos aplicados

| Módulo del curso | Tecnología/Patrón |
|---|---|
| POO + SOLID | Clases `TodoService`, `UserService`, `AuthService` (SRP) |
| Pydantic | Schemas de validación: `TodoCreate`, `TodoUpdate`, etc. |
| FastAPI | Endpoints REST, routers, dependencias |
| SQLAlchemy | ORM con SQLite (`todos.db`) |
| JWT | Autenticación con `python-jose` + `passlib` |
| Seguridad | ORM (anti SQL-injection), `bleach` (anti XSS) |
| Rate Limiting | `slowapi` — Límites dinámicos por endpoint (Auth/API) |
| Best Practices | Type hints, docstrings, manejo de errores |
