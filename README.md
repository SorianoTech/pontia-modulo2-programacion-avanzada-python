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

## 📁 Estructura del proyecto

```
ToDoList/
├── requirements.txt
├── README.md
├── comandos.md          # Guía rápida de comandos
├── todos.db             # Base de datos SQLite (generada al arrancar)
└── app/
    ├── main.py          # Punto de entrada FastAPI
    ├── config.py        # Configuración centralizada
    ├── database.py      # SQLAlchemy engine + session
    ├── limiter.py       # Configuración de Rate Limiting (SlowAPI)
    ├── managers/        # Lógica de procesamiento (Censura/XSS)
    │   └── note_manager.py
    ├── models/          # Modelos SQLAlchemy (tablas DB)
    │   ├── user.py
    │   └── todo.py
    ├── schemas/         # Pydantic schemas (validación)
    │   ├── user.py
    │   └── todo.py
    ├── services/        # Lógica de negocio (CRUD y Auth)
    │   ├── auth_service.py
    │   ├── user_service.py
    │   └── todo_service.py
    └── routers/         # Endpoints REST
        ├── auth.py      # /auth/ (Register, Login, Users)
        └── todos.py     # /todos/ (CRUD completo)
```

## 🚀 Instalación y ejecución

### ⚡ Ejecución rápida (Recomendado)

Si acabas de clonar el repositorio, puedes usar los scripts de automatización ubicados en la carpeta `scripts/`:

**En Windows:**
```bash
.\scripts\run.bat
```

**En Linux / Mac:**
```bash
chmod +x scripts/run.sh
./scripts/run.sh
```

**Launcher Universal (Python):**
```bash
python scripts/setup_and_run.py
```


---

### 🛠️ Instalación manual

#### 1. Crear entorno e instalar dependencias
```bash
python -m venv venv
# Activar (Windows)
.\venv\Scripts\activate
# Activar (Linux)
source venv/bin/activate

pip install -r requirements.txt
```

#### 2. Arrancar el servidor
```bash
uvicorn app.main:app --reload
```


### 3. Probar la API
Navega a **http://127.0.0.1:8000/docs** para la documentación interactiva Swagger UI.

## 🔐 Flujo de autenticación

1. **Registrar** usuario: `POST /auth/register`
2. **Login**: `POST /auth/login` → obtienes un `access_token`
3. **Autorizar**: Haz clic en el botón 🔒 **Authorize** en Swagger e introduce: `Bearer <tu_token>`
4. Ahora puedes usar todos los endpoints `/todos`

## 📋 Endpoints disponibles

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Registrar nuevo usuario | ❌ |
| POST | `/auth/login` | Login y obtener JWT | ❌ |
| GET | `/auth/users` | Listar todos los usuarios (Admin) | 👑 |
| GET | `/todos` | Listar todas tus tareas | ✅ |
| GET | `/todos/expired` | Listar tareas caducadas | ✅ |
| POST | `/todos` | Crear nueva tarea | ✅ |
| PUT | `/todos/{id}` | Actualizar tarea | ✅ |
| PATCH | `/todos/{id}/complete` | Marcar tarea como completada (Rápido) | ✅ |
| DELETE | `/todos/{id}` | Eliminar tarea | ✅ |

## ⚡ Rate Limiting
Se han implementado diferentes límites de velocidad para proteger la integridad del servicio:
- **Endpoints de Tareas**: 20 peticiones por minuto por IP.
- **Registro de Usuarios**: 500 peticiones por minuto por IP.
- **Login (Seguridad)**: Máximo 3 peticiones por minuto para mitigar ataques de fuerza bruta.

## 🔒 Seguridad
- **SQL Injection**: Prevenido por el ORM SQLAlchemy (nunca SQL raw)
- **XSS**: Las descripciones se sanitizan con `bleach.clean()`
- **Contraseñas**: Hasheadas con `bcrypt` (passlib)
- **JWT**: Tokens con expiración de 30 minutos

## 🛡️ Administración y Managers (SOLID / Domain Logic)
La aplicación aplica principios de diseño avanzado para separar responsabilidades:
- **Admin Automático**: Se crea un usuario `admin` (pass: `admin123`) por defecto.
- **Control de Acceso**: Solo los usuarios con el flag `is_admin` pueden acceder a `/auth/users`.
- **NoteManager**: Encapsula las **reglas de negocio** de las tareas:
  - **Censura**: Filtra palabras malsonantes en las descripciones.
  - **Validación de Deadlines**: Impide la creación de tareas con fechas límite en el pasado.
  - **Enriquecimiento**: Proporciona información calculada sobre el tiempo restante (`status_info`).
