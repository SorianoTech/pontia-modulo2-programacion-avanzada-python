import requests
from datetime import datetime, timedelta
import random
import string

BASE_URL = "http://127.0.0.1:8000"

#Explica Assert
#Assert es una funcion que verifica si una condicion es verdadera. 
#Si la condicion es verdadera, el programa continua. 
#Si la condicion es falsa, el programa se detiene y muestra un error.

def get_random_string(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def test_api():
    # 0. Datos de prueba aleatorios para evitar conflictos en ejecuciones consecutivas
    suffix = get_random_string()
    username = f"testuser_{suffix}"
    email = f"test_{suffix}@example.com"
    password = "password123"
    
    user_data = {
        "username": username,
        "email": email,
        "password": password
    }

    print("=== INICIANDO PRUEBAS DE API ===")

    # 1. Registro y Login (Original CP1 mejorado con validación)
    print("\n--- CP1: Registro y Login ---")
    resp_register = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Registro: {resp_register.status_code}")
    assert resp_register.status_code == 201, f"Error en registro: {resp_register.text}"
    
    # Validación de contenido del registro
    reg_data = resp_register.json()
    assert reg_data["username"] == username
    assert reg_data["email"] == email
    print("✓ Registro validado.")

    # 2. PRUEBA ADICIONAL: Error 400 (Registro duplicado)
    print("\n--- CP: Prueba de ERROR 400 (Registro duplicado) ---")
    resp_duplicate = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"POST /auth/register (duplicado): {resp_duplicate.status_code}")
    assert resp_duplicate.status_code == 400, "Debería devolver 400 por usuario duplicado"
    print("✓ Error 400 validado.")

    # Login
    params = {"username": username, "password": password}
    resp_login = requests.post(f"{BASE_URL}/auth/login", params=params)
    print(f"Login STATUS: {resp_login.status_code}")
    assert resp_login.status_code == 200, "Fallo en login"
    
    token = resp_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Login exitoso y token obtenido.")

    # 3. Crear Tarea con Deadline Futuro (Original CP2 mejorado con censura)
    print("\n--- CP2: Crear tarea válida con deadline futuro (y censura) ---")
    deadline_futuro = (datetime.now() + timedelta(days=2)).isoformat()
    tarea_ok = {
        "title": "Nota Importante",
        "description": "Esta es una nota con censura de mierda", # 'mierda' debe censurarse
        "deadline": deadline_futuro
    }
    resp_post = requests.post(f"{BASE_URL}/todos/", json=tarea_ok, headers=headers)
    print(f"POST /todos/: {resp_post.status_code}")
    assert resp_post.status_code == 201, "Error creando tarea"
    
    todo_data = resp_post.json()
    todo_id = todo_data["id"]
    # Validación de contenido y censura
    assert "******" in todo_data["description"], "La palabra 'mierda' no fue censurada"
    print(f"✓ Tarea creada ID: {todo_id}")
    print(f"✓ Contenido censurado: {todo_data['description']}")

    # 4. Obtener Tarea por ID (Original CP3)
    print(f"\n--- CP3: Obtener tarea por ID ({todo_id}) ---")
    resp_get_id = requests.get(f"{BASE_URL}/todos/{todo_id}", headers=headers)
    print(f"GET /todos/{todo_id} STATUS: {resp_get_id.status_code}")
    assert resp_get_id.status_code == 200, f"Se esperaba 200 pero se obtuvo {resp_get_id.status_code}"
    
    # Validamos contenido
    data_get = resp_get_id.json()
    assert data_get["id"] == todo_id, f"ID devuelto ({data_get['id']}) no coincide con el creado ({todo_id})"
    print("✓ Tarea obtenida correctamente y el ID coincide.")

    # 5. Crear Tarea Caducada (Original CP4)
    print("\n--- CP4: Crear tarea caducada (deadline pasado) ---")
    deadline_pasado = (datetime.now() - timedelta(days=1)).isoformat()
    tarea_old = {"title": "Nota Caducada", "deadline": deadline_pasado}
    resp_old = requests.post(f"{BASE_URL}/todos/", json=tarea_old, headers=headers)
    assert resp_old.status_code == 201
    todo_expirado_id = resp_old.json()["id"] 
    print(f"POST /todos/ (caducada) STATUS: {resp_old.status_code}")
    assert resp_old.status_code == 201, "Error al crear tarea caducada"
    print("✓ Tarea caducada creada con éxito.")

    # 6. Listar Caducadas (Original CP5)
    print("\n--- CP5: Listar tareas caducadas ---")
    resp_expired = requests.get(f"{BASE_URL}/todos/expired", headers=headers)
    print(f"GET /todos/expired STATUS: {resp_expired.status_code}")
    caducadas = resp_expired.json()
    ids_caducadas = [t["id"] for t in caducadas]
    assert todo_expirado_id in ids_caducadas, "La tarea caducada no aparece en /expired"
    print(f"✓ Tareas caducadas listadas: {len(caducadas)} encontradas.")
    
    # 7. Prueba de ERROR 422 (Original CP6 mejorado)
    print("\n--- CP6: Prueba de ERROR 422 (Título vacío) ---")
    tarea_error = {"title": "  ", "description": "Error esperado"}
    resp_error = requests.post(f"{BASE_URL}/todos/", json=tarea_error, headers=headers)
    print(f"POST /todos/ (error): {resp_error.status_code}")
    assert resp_error.status_code == 422, "Se esperaba 422 por título inválido"
    print("✓ Resultado esperado: 422 Unprocessable Entity")

    # 8. Prueba de PROTECCIÓN ADMIN (Original CP7)
    print("\n--- CP7: Prueba de Protección Admin (/auth/users) ---")
    # Caso A: Usuario normal intenta acceder
    resp_users_fail = requests.get(f"{BASE_URL}/auth/users", headers=headers)
    print(f"Usuario NORMAL (GET /auth/users): {resp_users_fail.status_code}")
    assert resp_users_fail.status_code == 403, "Se esperaba 403 Forbidden"
    print("✓ Resultado esperado: 403 Forbidden (Acceso denegado)")

    # Caso B: Admin real intenta acceder
    print("\n--- CP7.B: Admin real intenta acceder ---")
    admin_params = {"username": "admin", "password": "admin123"}
    resp_admin = requests.post(f"{BASE_URL}/auth/login", params=admin_params)
    assert resp_admin.status_code == 200, "No se pudo loguear como admin (admin/admin123)"
    print(f"Login Admin: {resp_admin.json()}")
    

    print("\n=== TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE ===")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\nERROR: No se pudo conectar con el servidor. Asegúrate de que FastAPI esté corriendo en http://127.0.0.1:8000")
    except AssertionError as e:
        print(f"\nFALLO EN VALIDACIÓN: {e}")
    except Exception as e:
        print(f"\nERROR INESPERADO: {e}")
