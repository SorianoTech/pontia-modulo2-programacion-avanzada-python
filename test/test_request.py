import requests
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"
USER_DATA = {
    "username": "final_test_user",
    "email": "final@example.com",
    "password": "password123"
}

def test_api():
    # 1. Registro y Login
    print("--- Autenticación ---")
    resp_register = requests.post(f"{BASE_URL}/auth/register", json=USER_DATA)
    params = {"username": USER_DATA["username"], "password": USER_DATA["password"]}
    print(f"Registro: {resp_register.json()}")
    resp_login = requests.post(f"{BASE_URL}/auth/login", params=params)
    
    if resp_login.status_code != 200:
        print("Fallo en login")
        return
    
    token = resp_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login exitoso.")

    # 2. Crear Tarea con Deadline Futuro (Válida)
    print("\n--- CP1: Crear tarea válida con deadline futuro ---")
    deadline_futuro = (datetime.now() + timedelta(days=2)).isoformat()
    tarea_ok = {
        "title": "Nota Importante",
        "description": "Esta es una nota con censura de mierda", # Debería censurarse mierda
        "deadline": deadline_futuro
    }
    resp_post = requests.post(f"{BASE_URL}/todos/", json=tarea_ok, headers=headers)
    print(f"POST /todos/: {resp_post.status_code}")
    if resp_post.status_code == 201:
        todo_id = resp_post.json()["id"]
        print(f"Tarea creada ID: {todo_id}")
        print(f"Contenido censurado: {resp_post.json()['description']}")

        # 3. Obtener Tarea por ID
        print(f"\n--- CP2: Obtener tarea por ID ({todo_id}) ---")
        resp_get_id = requests.get(f"{BASE_URL}/todos/{todo_id}", headers=headers)
        print(f"GET /todos/{todo_id}: {resp_get_id.status_code}")
        print(f"Body coincide: {resp_get_id.json()['id'] == todo_id}")

    # 4. Crear Tarea Caducada
    print("\n--- CP3: Crear tarea caducada (deadline pasado) ---")
    deadline_pasado = (datetime.now() - timedelta(days=1)).isoformat()
    tarea_old = {"title": "Nota Caducada", "deadline": deadline_pasado}
    requests.post(f"{BASE_URL}/todos/", json=tarea_old, headers=headers)
    
    # 5. Listar Caducadas
    print("\n--- CP4: Listar tareas caducadas ---")
    resp_expired = requests.get(f"{BASE_URL}/todos/expired", headers=headers)
    print(f"GET /todos/expired: {resp_expired.status_code}")
    print(f"Tareas caducadas encontradas: {len(resp_expired.json())}")
    print(f"Tareas caducadas encontradas: {resp_expired.json()}")

    # 6. Prueba de ERROR (Cuerpo inválido - Título vacío)
    print("\n--- CP5: Prueba de ERROR 422 (Título vacío) ---")
    tarea_error = {"title": "  ", "description": "Error esperado"}
    resp_error = requests.post(f"{BASE_URL}/todos/", json=tarea_error, headers=headers)
    print(f"POST /todos/ (error): {resp_error.status_code}")
    if resp_error.status_code == 422:
        print("Resultado esperado: 422 Unprocessable Entity")

    # 7. Prueba de PROTECCIÓN ADMIN
    print("\n--- CP6: Prueba de Protección Admin (/auth/users) ---")
    # Caso A: Usuario normal intenta acceder
    resp_users_fail = requests.get(f"{BASE_URL}/auth/users", headers=headers)
    print(f"Usuario NORMAL (GET /auth/users): {resp_users_fail.status_code}")
    if resp_users_fail.status_code == 403:
        print("Resultado esperado: 403 Forbidden (Acceso denegado)")

    # Caso B: Admin real intenta acceder
    admin_params = {"username": "admin", "password": "admin123"}
    resp_admin = requests.post(f"{BASE_URL}/auth/login", params=admin_params)
    if resp_admin.status_code == 200:
        admin_token = resp_admin.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        resp_users_ok = requests.get(f"{BASE_URL}/auth/users", headers=admin_headers)
        print(f"Usuario ADMIN (GET /auth/users): {resp_users_ok.status_code}")
        if resp_users_ok.status_code == 200:
            print(f"Acceso concedido. Usuarios en el sistema: {len(resp_users_ok.json())}")
            print(f"Los usuarios existentes son: {resp_users_ok.json()}")

if __name__ == "__main__":
    test_api()
