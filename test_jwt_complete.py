import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

# Importar la aplicación y los routers
from main import app
from app.api.rutas_auth import router as auth_router

# Asegurarnos de que los routers estén incluidos
if not any('/auth' in str(r) for r in app.routes):
    print("Añadiendo router de auth...")
    app.include_router(auth_router, prefix="/auth", tags=["Autenticación"])

# Crear cliente de prueba
client = TestClient(app)

print("=" * 60)
print("PROBANDO ENDPOINTS DE AUTENTICACIÓN JWT")
print("=" * 60)

# Probar 1: Endpoint raíz
print("\n1. Probando endpoint raíz...")
response = client.get("/")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Probar 2: Login
print("\n2. Probando login...")
login_data = {"correo": "admin@test.com", "contrasena": "123456"}
response = client.post("/auth/login", json=login_data)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Access token: {data['access_token'][:50]}...")
    print(f"   Token type: {data['token_type']}")
    print(f"   Expires in: {data['expires_in']} segundos")
    print(f"   Refresh token: {data['refresh_token'][:50]}...")
    
    # Guardar token para pruebas subsiguientes
    access_token = data['access_token']
    
    # Probar 3: Endpoint de perfil
    print("\n3. Probando obtener perfil...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/auth/perfil", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Perfil: {response.json()}")
    
    # Probar 4: Endpoint de logout
    print("\n4. Probando logout...")
    response = client.post("/auth/logout")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Probar 5: Refresh token
    print("\n5. Probando refresh token...")
    refresh_data = {"refresh_token": data['refresh_token']}
    response = client.post("/auth/refresh", json=refresh_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        new_data = response.json()
        print(f"   Nuevo access token: {new_data['access_token'][:50]}...")
        print(f"   Nuevo refresh token: {new_data['refresh_token'][:50]}...")
else:
    print(f"   Error de login: {response.text}")

# Probar 5: Intento con token inválido
print("\n6. Probando token inválido...")
headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid"}
response = client.get("/auth/perfil", headers=headers)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

print("\n" + "=" * 60)
print("PRUEBAS COMPLETADAS")
print("=" * 60)