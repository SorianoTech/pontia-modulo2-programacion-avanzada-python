import requests

BASE_URL = "http://127.0.0.1:8000"

def register_bulk(n=100):
    print(f"--- Iniciando registro de {n} usuarios ---")
    created = 0
    already_exists = 0
    
    for i in range(1, n + 1):
        payload = {
            "username": f"bulk_user_{i}",
            "email": f"user_{i}@example.com",
            "password": "password123"
        }
        try:
            resp = requests.post(f"{BASE_URL}/auth/register", json=payload)
            if resp.status_code == 201:
                created += 1
                if created % 10 == 0:
                    print(f"Progreso: {created} usuarios creados...")
            elif resp.status_code == 400:
                already_exists += 1
            else:
                print(f"Error inesperado en usuario {i}: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"Error de conexión: {e}")
            break
            
    print("\n--- Resumen ---")
    print(f"Creados nuevos: {created}")
    print(f"Ya existentes: {already_exists}")

if __name__ == "__main__":
    register_bulk(100)
