@echo off
SETLOCAL EnableDelayedExpansion

:: Asegurar que corremos desde la raiz del proyecto
cd /d "%~dp0.."

echo.
echo ==========================================
echo   🚀 CONFIGURACION RAPIDA: ToDoList API
echo ==========================================
echo.

:: 1. Crear entorno virtual si no existe
if not exist venv (
    echo [1/4] Creando entorno virtual...
    python -m venv venv
) else (
    echo [1/4] El entorno virtual ya existe. Saltando...
)

:: 2. Instalar dependencias
echo [2/4] Instalando dependencias (esto puede tardar un poco)...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

:: 3. Configurar variables de entorno
echo [3/4] Configurando archivo .env...
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo    ^> Archivo .env creado desde .env.example.
        echo    ^> RECUERDA: Edita el archivo .env con tus claves reales.
    ) else (
        echo    ^> [!] Error: No se encuentra .env.example
    )
) else (
    echo    ^> El archivo .env ya existe.
)

:: 4. Ejecutar
echo.
echo [4/4] TODO LISTO. Iniciando servidor...
echo.
uvicorn app.main:app --reload
