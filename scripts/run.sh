#!/bin/bash

# Asegurar que corremos desde la raiz del proyecto
cd "$(dirname "$0")/.."

echo ""
echo "=========================================="
echo "  🚀 CONFIGURACION RAPIDA: ToDoList API   "
echo "=========================================="
echo ""

# 1. Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "[1/4] Creando entorno virtual..."
    python3 -m venv venv
else
    echo "[1/4] El entorno virtual ya existe. Saltando..."
fi

# 2. Activar e instalar dependencias
echo "[2/4] Instalando dependencias..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Configurar variables de entorno
echo "[3/4] Configurando archivo .env..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "   > Archivo .env creado desde .env.example."
    else
        echo "   > [!] Error: No se encuentra .env.example"
    fi
else
    echo "   > El archivo .env ya existe."
fi

# 4. Ejecutar
echo ""
echo "[4/4] TODO LISTO. Iniciando servidor..."
echo ""
uvicorn app.main:app --reload
