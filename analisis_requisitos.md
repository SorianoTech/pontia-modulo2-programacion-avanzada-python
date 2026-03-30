# Análisis de Cumplimiento: Entrega ToDoList API

Este documento analiza el estado actual del proyecto `Entrega-todolist` frente a los requisitos especificados en `enunciado_contenedores.md`.

## 📊 Resumen Ejecutivo

Actualmente, el proyecto **cumple parcialmente** con los requisitos funcionales de la aplicación FastAPI, pero **incumple** varios de los requisitos críticos de containerización y orquestación solicitados en el enunciado.

| Requisito | Estado | Observaciones |
| :--- | :---: | :--- |
| **FastAPI App** | ✅ | Implementada con Python y FastAPI. |
| **Métodos CRUD** | ✅ | GET total, GET ID, POST y DELETE implementados. |
| **Puerto 8080** | ❌ | Actualmente configurado en el puerto **8000**. |
| **Control de Errores** | ✅ | Implementados errores 404 y 400. |
| **Logging** | ❌ | No se ha implementado trazabilidad en el código actual. |
| **Base de Datos Separada** | ❌ | Usa **SQLite** en un archivo local; se requiere un contenedor independiente. |
| **Volúmenes Persistentes** | ⚠️ | Usa volúmenes, pero vinculados a SQLite. No hay volumen nombrado solicitado. |
| **Red Propia** | ❌ | No se define una red personalizada en el Compose. |
| **Comunicación por Nombre** | ❌ | Al ser un único contenedor, no hay comunicación entre servicios. |

---

## 🔍 Detalle del Análisis

### 1. Aplicación FastAPI y CRUD
- **Cumplimiento**: La aplicación está bien estructurada siguiendo principios SOLID.
- **Endpoints**:
  - `GET /todos/`: ✅
  - `GET /todos/{id}`: ✅
  - `POST /todos/`: ✅
  - `DELETE /todos/{id}`: ✅
- **Control de Errores**: Se manejan correctamente los códigos 404 (Entidad no encontrada) y 400 (Bad Request/Validation).

### 2. Docker y Docker Compose
- **Containerización**: El `Dockerfile` es de alta calidad (multi-stage build, usuario no-root), pero el `docker-compose.yml` es insuficiente para el enunciado.
- **Base de Datos**: El enunciado exige una **imagen independiente** con la base de datos (ej. Postgres, MySQL). Actualmente el `docker-compose.yml` solo tiene el servicio `app` y utiliza SQLite.
- **Persistencia**: Se pide un **volumen con nombre**. El proyecto actual usa un montaje de host (`./data:/app/data`).
- **Puerto**: El enunciado pide el puerto **8080**. El proyecto usa el **8000**.

### 3. Red y Comunicación
- **Incumplimiento**: No se ha creado una red personalizada. Se requiere que ambos contenedores (App y DB) coexistan en una red específica y se comuniquen mediante el nombre del contenedor de la base de datos.
- **DATABASE_URL**: Actualmente apunta a un archivo local `sqlite:///./data/todos.db`. Debería apuntar al servicio de la BD (ej. `postgresql://user:pass@db:5432/dbname`).

### 4. Logging
- **Incumplimiento**: No se observa uso del módulo `logging` de Python para dejar trazabilidad de las acciones (creación de tareas, errores, etc.) más allá de lo que vuelca uvicorn por defecto.

---

## 🛠️ Recomendaciones de Mejora (Roadmap)

Para cumplir al 100% con la entrega, se recomienda:

1.  **Migrar a PostgreSQL/MySQL**: Añadir un servicio `db` en `docker-compose.yml`.
2.  **Configurar Volumen Nombrado**: Cambiar el montaje de host por un volumen gestionado por Docker (ej. `db_data`).
3.  **Ajustar Puertos**: Cambiar el mapping en el Compose de `8080:8000` a `8080:8000`.
4.  **Definir Red**: Crear una red `todolist-network` en el nivel superior del Compose.
5.  **Implementar Logging**: Añadir un logger en `main.py` y servicios para registrar operaciones críticas.
6.  **Actualizar Dependencias**: Añadir drivers para la base de datos elegida (ej. `psycopg2-binary` para Postgres) en `requirements.txt`.
