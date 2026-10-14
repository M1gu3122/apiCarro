from app.core.security import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security_jwt import create_access_token, decode_token, create_refresh_token

# Probar creación de token
token = create_access_token({'sub': '1', 'roles': ['administrador']})
print('Token creado exitosamente, largo:', len(token), 'caracteres')

# Probar decodificación
payload = decode_token(token)
print('Payload decodificado correctamente')
print('  - sub:', payload.get('sub'))
print('  - roles:', payload.get('roles'))
print('  - tipo:', payload.get('type'))

# Probar refresh token
refresh = create_refresh_token({'sub': '1', 'roles': ['administrador']})
print('Refresh token creado, largo:', len(refresh), 'caracteres')

refresh_payload = decode_token(refresh)
print('Refresh payload verificado')
print('  - type:', refresh_payload.get('type'))
print('  - sub:', refresh_payload.get('sub'))

print()
print('Todas las funciones JWT funcionan correctamente!')