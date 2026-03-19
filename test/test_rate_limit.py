import requests
import time

BASE_URL = "http://127.0.0.1:8000"
# Usamos las credenciales del usuario admin que se crea por defecto
USER_CREDENTIALS = {"username": "admin", "password": "admin123"}

def test_rate_limit():
    print("--- Obteniendo Token para la prueba ---")
    login_resp = requests.post(f"{BASE_URL}/auth/login", params=USER_CREDENTIALS)
    if login_resp.status_code != 200:
        print("Error en login. Asegúrate de que el servidor esté corriendo.")
        return
    
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n--- Iniciando ráfaga de peticiones (Límite: 20 por minuto) ---")
    print("Realizaremos 25 peticiones seguidas...\n")
    
    for i in range(1, 26):
        start_time = time.time()
        resp = requests.get(f"{BASE_URL}/todos/", headers=headers)
        end_time = time.time()
        
        status = resp.status_code
        if status == 200:
            print(f"Petición {i:02d}: OK (200) - Tiempo: {end_time - start_time:.3f}s")
        elif status == 429:
            print(f"\n¡BLOQUEADO! Petición {i:02d}: {status} Too Many Requests")
            print("Detalle:", resp.json().get('detail'))
            break
        else:
            print(f"Petición {i:02d}: Error {status}")
            break

if __name__ == "__main__":
    test_rate_limit()
