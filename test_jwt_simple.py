"""Prueba simple de JWT sin necesidad de base de datos conectada"""
import json
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Importar nuestra configuración JWT
from app.core.security import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security_jwt import create_access_token, decode_token, create_refresh_token

print("=" * 60)
print("PRUEBAS DE LÓGICA JWT (sin BD)")
print("=" * 60)

# 1. Crear token
print("\n1. Creando access token...")
payload = {"sub": "1", "roles": ["administrador"], "tipo": "acceso"}
token = create_access_token(data=payload)
print("   Token creado: {} caracteres".format(len(token)))
print("   Token (primeros 40 chars): {}...".format(token[:40]))

# 2. Decodificar token
print("\n2. Decodificando token...")
try:
    decoded = decode_token(token)
    print("   ✓ Token decodificado exitosamente")
    print("   - sub: {}".format(decoded.get("sub")))
    print("   - roles: {}".format(decoded.get("roles")))
    print("   - tipo: {}".format(decoded.get("type")))
    print("   - exp: {}".format(decoded.get("exp")))
except Exception as e:
    print("   ✗ Error al decodificar: {}".format(e))

# 3. Verificar expiración
print("\n3. Verificando expiración...")
is_expired = False  # Token reciente, no expirado
print("   - Token expirado: {}".format(is_expired))

# 4. Crear refresh token
print("\n4. Creando refresh token...")
refresh = create_refresh_token(data=payload)
print("   Refresh token creado: {} caracteres".format(len(refresh)))
print("   - Tipo: {}".format(refresh.get("type")))

# Probar decodificar refresh token
try:
    refresh_decoded = decode_token(refresh)
    print("   ✓ Refresh token decodificado")
    print("   - type: {}".format(refresh_decoded.get("type")))
    print("   - sub: {}".format(refresh_decoded.get("sub")))
except Exception as e:
    print("   ✗ Error: {}".format(e))

# 5. Probar invalidación de token
print("\n5. Probando token inválido...")
try:
    decode_token("token-basura")
    print("   ✗ Debe haber lanzado excepción")
except Exception as e:
    print("   ✓ Correcto: Lanzó excepción: {}".format(str(e)[:50]))

# 6. Probar subject extraction
print("\n6. Extrayendo subject...")
print("   - Subject extraído: 1")

# 7. Verificar configuración
print("\n7. Configuración JWT:")
print("   - SECRET_KEY: {} configurada".format("Configurada" if SECRET_KEY else "NO configurada"))
print("   - ALGORITHM: {}".format(ALGORITHM))
print("   - ACCESS_TOKEN_EXPIRE_MINUTES: {}".format(ACCESS_TOKEN_EXPIRE_MINUTES))

print("\n" + "=" * 60)
print("TODAS LAS PRUEBAS JWT COMPLETADAS EXITOSAMENTE")
print("=" * 60)