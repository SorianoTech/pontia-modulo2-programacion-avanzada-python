# Resumen de Containerización - ToDoList API

## Estado Actual (Desarrollo)

La aplicación FastAPI ha sido containerizada exitosamente con los siguientes componentes:

### Archivos Creados

1. **Dockerfile** (multi-stage)
   - Stage 1 (builder): Compila dependencias con Python 3.11-slim
   - Stage 2 (runtime): Imagen limpia y segura sin herramientas de compilación
   - Usuario no-root (`appuser`, UID 1000) para seguridad
   - Health check integrado
   - Base de datos SQLite en `/app/data`

2. **docker-compose.yml**
   - Orquesta la aplicación en contenedor
   - Puerto 8000 expuesto
   - Volumen compartido para persistencia de datos
   - Variables de entorno configuradas para desarrollo

3. **.dockerignore**
   - Excluye archivos innecesarios: git, test, scripts, cache, etc.

### Características Actuales

- ✅ Imagen optimizada (~340MB)
- ✅ Multi-stage build (sin herramientas de compilación en runtime)
- ✅ Usuario no-root para seguridad
- ✅ Health check funcional
- ✅ Fácil ejecución: `docker compose up -d`
- ✅ Acceso a documentación interactiva: http://localhost:8000/docs

---

## Cambios Necesarios para Producción

### 1. Seguridad

#### 1.1 Variables de Entorno Sensibles
**Problema actual:** `SECRET_KEY` está hardcodeada en docker-compose.yml

**Solución:**
```bash
# Crear archivo .env.production (NO en git)
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria-aqui
DATABASE_URL=postgresql://user:password@db:5432/todolist_prod
ALLOWED_ORIGINS=["https://tudominio.com"]
```

**Actualizar docker-compose.yml:**
```yaml
env_file:
  - .env.production
```

**Generar SECRET_KEY segura:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 1.2 Base de Datos
**Problema actual:** SQLite no es escalable ni segura para producción

**Solución:** Usar PostgreSQL

```yaml
# En docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    container_name: todolist-db
    environment:
      POSTGRES_USER: todolist_user
      POSTGRES_PASSWORD: tu_password_aqui
      POSTGRES_DB: todolist_prod
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U todolist_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  app:
    # ... resto de configuración
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://todolist_user:${DB_PASSWORD}@db:5432/todolist_prod

volumes:
  postgres_data:
```

**Instalar driver PostgreSQL:**
```bash
# Agregar a requirements.txt
psycopg2-binary==2.9.9
# o usar psycopg[binary] para versiones más recientes
```

#### 1.3 CORS y HTTPS
**Actualizar config.py:**
```python
ALLOWED_ORIGINS: list[str] = [
    "https://tudominio.com",
    "https://www.tudominio.com",
]
```

**Usar proxy inverso (Nginx) con SSL/TLS** - ver sección 5

### 2. Optimización de Imagen

#### 2.1 Reducir Tamaño
**Actualizar Dockerfile:**
```dockerfile
# Usar alpine en lugar de slim
FROM python:3.11-alpine as builder
# ... resto del Dockerfile

FROM python:3.11-alpine
# Alpine es ~50MB más pequeño que slim
```

#### 2.2 Multi-stage con optimizaciones
```dockerfile
# Después de COPY del código en stage 2
RUN find /home/appuser/.local -name "*.pyc" -delete && \
    find /home/appuser/.local -name "*.dist-info" -type d -exec rm -rf {} +
```

### 3. Logging y Monitoreo

#### 3.1 Configurar Logging Centralizado
**Actualizar main.py:**
```python
import logging
import json

# Configurar logging estructurado para producción
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Usar JSON para facilitar parsing
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'service': 'todolist-api'
        }
        return json.dumps(log_obj)
```

**En docker-compose.yml:**
```yaml
app:
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

#### 3.2 Métricas
Agregar Prometheus para monitoreo:
```bash
# Agregar a requirements.txt
prometheus-client==0.21.0
```

```python
# En main.py
from prometheus_client import Counter, Histogram, generate_latest
import time

http_requests_total = Counter('http_requests_total', 'Total HTTP requests')
http_request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    http_requests_total.inc()
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    http_request_duration.observe(duration)
    return response

@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### 4. Escalabilidad

#### 4.1 Múltiples Workers Uvicorn
**Actualizar Dockerfile CMD:**
```dockerfile
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4"]
```

#### 4.2 Load Balancer (Nginx)
**Crear docker-compose con Nginx:**
```yaml
services:
  nginx:
    image: nginx:latest-alpine
    container_name: todolist-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    restart: unless-stopped

  app:
    # ... configuración
    # NO exponer puerto 8000 al host
    expose:
      - "8000"
    deploy:
      replicas: 3  # Con Docker Swarm o Kubernetes
```

**nginx.conf:**
```nginx
upstream todolist_backend {
    server app:8000;
    server app:8000;
    server app:8000;
}

server {
    listen 80;
    server_name tudominio.com www.tudominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tudominio.com www.tudominio.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://todolist_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }

    location /metrics {
        allow 10.0.0.0/8;  # Solo desde red interna
        deny all;
        proxy_pass http://todolist_backend;
    }
}
```

### 5. Certificados SSL/TLS

#### Opción 1: Let's Encrypt con Certbot
```bash
docker run --rm --name certbot \
  -v "/etc/letsencrypt:/etc/letsencrypt" \
  -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
  -p 80:80 \
  certbot/certbot certonly --standalone \
  -d tudominio.com -d www.tudominio.com
```

#### Opción 2: Auto-renovación con Docker
```yaml
services:
  certbot:
    image: certbot/certbot
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt
      - /var/lib/letsencrypt:/var/lib/letsencrypt
    entrypoint: /bin/sh -c 'trap exit TERM; while :; do certbot renew --quiet; sleep 12h & wait $${!}; done;'
    restart: unless-stopped
```

### 6. Gestión de Secrets

#### Usar Docker Secrets (Swarm) o Kubernetes Secrets
**Con Docker Swarm:**
```bash
echo "mi-secret-key-super-larga" | docker secret create app_secret_key -
```

**En docker-compose.yml (Swarm mode):**
```yaml
services:
  app:
    secrets:
      - app_secret_key
    environment:
      SECRET_KEY_FILE: /run/secrets/app_secret_key

# Al final del archivo
secrets:
  app_secret_key:
    external: true
```

### 7. Backups y Persistencia

#### 7.1 Volúmenes Named
```yaml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/data/postgres  # Usar almacenamiento externo

  app_data:
    driver: local
```

#### 7.2 Política de Backup
```bash
# Script backup_db.sh
#!/bin/bash
docker exec todolist-db pg_dump -U todolist_user todolist_prod | gzip > backups/todolist_$(date +%Y%m%d_%H%M%S).sql.gz

# Cron job para backups automáticos
0 2 * * * /home/deploy/backup_db.sh
```

### 8. Dockerfile Optimizado para Producción

```dockerfile
# Stage 1: Build
FROM python:3.11-alpine as builder

WORKDIR /tmp
RUN apk add --no-cache gcc musl-dev

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt && \
    find /root/.local -name "*.pyc" -delete && \
    find /root/.local -name "*.dist-info" -type d -exec rm -rf {} +

# Stage 2: Runtime
FROM python:3.11-alpine

LABEL maintainer="tu-email@tudominio.com"
LABEL description="ToDoList API - Production"

WORKDIR /app

RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

COPY --from=builder --chown=appuser: /root/.local /home/appuser/.local
COPY --chown=appuser:appuser ./app ./app

USER appuser

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--access-log"]
```

### 9. docker-compose.yml Producción
appuser
```yaml
version: '3.9'

services:
  db:
    image: postgres:16-alpine
    container_name: todolist-db
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - todolist-network

  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: todolist-api
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      SECRET_KEY: ${SECRET_KEY}
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 30
      RATE_LIMIT: 100/minute
      AUTH_RATE_LIMIT: 1000/minute
      LOGIN_FAILURE_RATE_LIMIT: 5/minute
      ALLOWED_ORIGINS: ${ALLOWED_ORIGINS}
    expose:
      - "8000"
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - todolist-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:latest-alpine
    container_name: todolist-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - todolist-network

networks:
  todolist-network:
    driver: bridge

volumes:
  postgres_data:
```

### 10. Archivo .env.production (ejemplo)

```bash
# Base de datos
DB_USER=todolist_prod_user
DB_PASSWORD=cambiar-esto-por-una-password-segura-aqui
DB_NAME=todolist_production

# Seguridad
SECRET_KEY=generar-con-python-secrets-module
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=["https://tudominio.com","https://www.tudominio.com"]

# Rate limiting
RATE_LIMIT=100/minute
AUTH_RATE_LIMIT=1000/minute
LOGIN_FAILURE_RATE_LIMIT=5/minute
```

---

## Checklist Producción

- [ ] Base de datos PostgreSQL configurada
- [ ] Variables de entorno en .env.production (NO en git)
- [ ] SECRET_KEY generada con secrets.token_urlsafe(32)
- [ ] SSL/TLS con Let's Encrypt
- [ ] Nginx configurado como proxy inverso
- [ ] Logging centralizado JSON configurado
- [ ] Health checks funcionales
- [ ] Backups automáticos de BD programados
- [ ] Monitoreo con Prometheus/Grafana
- [ ] Rate limiting ajustado para producción
- [ ] CORS configurado solo para dominios permitidos
- [ ] Docker Compose optimizado (docker-compose.prod.yml)
- [ ] Tests ejecutados y pasados
- [ ] Documentación API actualizada

---

## Comandos Clave

**Desarrollo:**
```bash
docker compose up -d
docker compose logs -f app
docker compose down
```

**Producción:**
```bash
# Crear secretos en Swarm
echo "tu-secret-key" | docker secret create app_secret_key -

# Iniciar con archivo específico
docker compose -f docker-compose.prod.yml up -d

# Backup de BD
docker exec todolist-db pg_dump -U todolist_prod_user todolist_production | gzip > backup_$(date +%Y%m%d).sql.gz

# Restore
gunzip < backup_20240115.sql.gz | docker exec -i todolist-db psql -U todolist_prod_user todolist_production
```

---

**Última actualización:** 2024
**Estado:** Documentación de migración a producción
