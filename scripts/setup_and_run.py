import os
import subprocess
import sys
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Ejecuta un comando y muestra la salida en tiempo real."""
    print(f"Executing: {command}")
    try:
        # shell=True es necesario en Windows para comandos como 'venv\\Scripts\\activate'
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in process.stdout:
            print(f"  {line.strip()}")
        process.wait()
        return process.returncode == 0
    except Exception as e:
        print(f"Error executing command: {e}")
        return False

def setup():
    """Configura el entorno del proyecto."""
    print("\n--- ToDoList Python Launcher ---")
    
    # IMPORTANTE: Como el script esta en /scripts/, retrocedemos una carpeta
    root_dir = Path(__file__).parent.parent
    venv_dir = root_dir / "venv"
    
    # 1. Crear VENV si no existe
    if not venv_dir.exists():
        print("[1/4] Creando entorno virtual...")
        # Cambiamos al directorio raiz para crear el venv alli
        if not run_command(f'"{sys.executable}" -m venv venv', cwd=root_dir):
            print("Error creando venv.")
            return
    else:
        print("[1/4] El entorno virtual ya existe.")

    # 2. Determinar el ejecutable de pip dentro del venv
    if os.name == "nt": # Windows
        pip_path = venv_dir / "Scripts" / "pip.exe"
        uvicorn_path = venv_dir / "Scripts" / "uvicorn.exe"
    else: # Linux/Mac
        pip_path = venv_dir / "bin" / "pip"
        uvicorn_path = venv_dir / "bin" / "uvicorn"

    # 3. Instalar dependencias
    print("[2/4] Instalando dependencias...")
    # Pasamos root_dir para que encuentre requirements.txt
    if not run_command(f'"{pip_path}" install -r requirements.txt', cwd=root_dir):
        print("Error instalando dependencias.")
        return

    # 4. Configurar .env
    print("[3/4] Configurando archivo .env...")
    env_file = root_dir / ".env"
    env_example = root_dir / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("  Archivo .env creado desde .env.example.")
        else:
            print("  [!] Warning: No se encontró .env.example para copiar.")
    else:
        print("  El archivo .env ya existe.")

    # 5. Lanzar Uvicorn
    print("\n[4/4] TODO LISTO. Iniciando servidor...")
    print("---------------------------------------")
    
    try:
        # Ejecutamos con root_dir como CWD para que uvicorn encuentre la carpeta 'app'
        subprocess.run(f'"{uvicorn_path}" app.main:app --reload', shell=True, cwd=root_dir)
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")

if __name__ == "__main__":
    setup()
