# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /tmp

# Instalar dependencias del sistema necesarias para compilar paquetes Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias en un directorio virtual
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt


# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Crear usuario no-root antes de copiar archivos
RUN useradd -m -u 1000 appuser

# Copiar solo las dependencias instaladas desde el stage anterior
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copiar el código de la aplicación
COPY --chown=appuser:appuser ./app ./app

# Crear directorio de datos con permisos correctos
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

USER appuser

# Agregar el directorio local a PATH para acceder a los binarios instalados
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_URL=sqlite:///./data/todos.db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')" || exit 1

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
