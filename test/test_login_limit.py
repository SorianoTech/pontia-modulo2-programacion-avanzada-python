import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_login_rate_limit():
    print("--- Probando Rate Limit de Login (3 por minuto) ---")
    print("Enviaremos 5 intentos de login seguidos...\n")
    
    params = {"username": "admin", "password": "wrong_password"}
    
    for i in range(1, 6):
        start_time = time.time()
        resp = requests.post(f"{BASE_URL}/auth/login", params=params)
        end_time = time.time()
        
        status = resp.status_code
        if status == 401:
            print(f"Intento {i:02d}: Error 401 (Credenciales incorrectas) - Esperado")
        elif status == 429:
            print(f"\n¡BLOQUEADO! Intento {i:02d}: {status} Too Many Requests")
            print("Detalle:", resp.json().get('detail'))
            break
        else:
            print(f"Intento {i:02d}: Respuesta inesperada {status}")
            break

if __name__ == "__main__":
    test_login_rate_limit()
