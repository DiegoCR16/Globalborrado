import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api/auth/login/'

def test_1_retail_success():
    print("\n--- Test 1: Login Cliente Minorista (Sin MFA) ---")
    payload = {"username": "cliente_minorista", "password": "password123"}
    response = requests.post(BASE_URL, json=payload)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_2_corporate_missing_mfa():
    print("\n--- Test 2: Login Cliente Corporativo sin MFA (Debe fallar con 403) ---")
    payload = {"username": "cliente_corporativo", "password": "password123"}
    response = requests.post(BASE_URL, json=payload)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_3_corporate_success_with_mfa():
    print("\n--- Test 3: Login Cliente Corporativo con MFA (123456) ---")
    payload = {"username": "cliente_corporativo", "password": "password123", "mfa_token": "123456"}
    response = requests.post(BASE_URL, json=payload)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_4_invalid_credentials():
    print("\n--- Test 4: Credenciales Inválidas (Debe fallar con 401) ---")
    payload = {"username": "cliente_minorista", "password": "wrongpassword"}
    response = requests.post(BASE_URL, json=payload)
    print(f"Status Code: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

if __name__ == '__main__':
    print("=== Ejecutando pruebas interactivos de API para PSE-4 ===")
    print("Asegúrate de tener el servidor corriendo en otra terminal con: python manage.py runserver")
    try:
        test_1_retail_success()
        test_2_corporate_missing_mfa()
        test_3_corporate_success_with_mfa()
        test_4_invalid_credentials()
        print("\n=== ¡Pruebas completadas con éxito! ===")
    except requests.exceptions.ConnectionError:
        print("\n[ERROR]: No se pudo conectar al servidor. Ejecuta primero 'python manage.py runserver' en otra terminal.")
