from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any

from app.core.database import Database
from app.core.security import get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["Autenticación y Sesión"])

# --- Modelos Pydantic ---

class LoginRequest(BaseModel):
    """Solicitud de inicio de sesión."""
    correo: EmailStr = Field(..., description="Correo electrónico del usuario")
    contrasena: str = Field(..., min_length=6, description="Contraseña del usuario")


class TokenResponse(BaseModel):
    """Respuesta del token de acceso."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # En segundos
    refresh_token: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Solicitud para renovar token usando refresh token."""
    refresh_token: str = Field(..., description="Token de refresco vigente")


class UserInfoResponse(BaseModel):
    """Respuesta con información básica del usuario (sin contraseña)."""
    id_usuario: int
    nombre: str
    correo: str
    id_rol: int
    rol_nombre: str
    estado: bool


# --- Dependencias (importadas después para evitar circular imports) ---
from app.core.dependencies import get_db_connection, get_current_active_user, check_user_role

# --- Endpoints de Autenticación ---

@router.post("/login", response_model=TokenResponse, summary="Iniciar sesión")
def login(request: LoginRequest, db_conn: object = Depends(get_db_connection)):
    """
    Endpoint de login que verifica credenciales y genera tokens JWT.
    
    Flujo:
    1. Busca usuario por correo en la base de datos
    2. Verifica contraseña usando bcrypt
    3. Si exitoso, genera access_token y refresh_token
    4. Retorna ambos tokens con tiempos de expiración
    """
    cursor = db_conn.cursor(cursor_factory=RealDictCursor)

    # 1. Buscar usuario por correo
    cursor.execute(
        "SELECT * FROM usuarios WHERE correo = %s;",
        (request.correo,),
    )
    user = cursor.fetchone()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Verificar contraseña usando la función de hash de bcrypt
    if not verify_password(request.contrasena, user["contrasena_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Verificar que el usuario esté activo
    if user["estado"] is not True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cuenta desactivada",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Obtener el nombre del rol para incluir en el token
    cursor.execute(
        "SELECT nombre FROM roles WHERE id_rol = %s;",
        (user["id_rol"],),
    )
    role_result = cursor.fetchone()
    role_name = role_result["nombre"] if role_result else "usuario"

    # 4. Preparar datos para el payload del token
    token_data = {
        "sub": str(user["id_usuario"]),  # Subject: ID del usuario como string
        "roles": [role_name],  # Roles del usuario (lista para consistencia)
        "tipo": "acceso",
    }

    # 5. Crear access token (válido 30 minutos)
    from app.core.security_jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
    access_token = create_access_token(data=token_data)
    expires_in = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convertir a segundos

    # 6. Crear refresh token (válido 7 días)
    from app.core.security_jwt import create_refresh_token
    refresh_token = create_refresh_token(data=token_data)

    # 7. Retornar ambos tokens
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "refresh_token": refresh_token,
    }


@router.post("/refresh", response_model=TokenResponse, summary="Renovar token")
def refresh_token_endpoint(request: RefreshTokenRequest, db_conn: object = Depends(get_db_connection)):
    """
    Endpoint para renovar el access token usando un refresh token.
    """
    from app.core.security_jwt import decode_token

    try:
        # Decodificar el token sin verificar expiration primero para leer el payload
        payload = decode_token(request.refresh_token)

        # Verificar que sea token de refresh y no access
        token_type = payload.get("type", "access")
        if token_type != "refresh":
            raise ValueError("Token no es un refresh token")

        # Extraer el user ID
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Refresh token sin user ID")

        # Verificar que el usuario siga existiendo y esté activo
        cursor = db_conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT id_usuario, nombre, correo, id_rol, estado FROM usuarios WHERE id_usuario = %s AND estado = TRUE;",
            (int(user_id),),
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o desactivado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Crear nuevos tokens
        token_data = {
            "sub": str(user["id_usuario"]),
            "roles": [payload.get("roles", ["usuario"])[0]],
            "tipo": "acceso",
        }

        from app.core.security_jwt import create_access_token

        new_access_token = create_access_token(data=token_data)
        new_refresh_token = create_refresh_token(data=token_data)

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "refresh_token": new_refresh_token,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error al renovar token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout", summary="Cerrar sesión")
def logout():
    """
    Endpoint de cierre de sesión.
    
    Observación: JWT es stateless, por lo que el servidor no 'remembera'
    sesiones cerradas. El logout es principalmente del lado del cliente
    (eliminar el token del almacenamiento). Este endpoint puede usarse
    para registrar logout en logs o invalidar tokens en una blacklist si
    se implementa esa característica posteriormente.
    """
    return {"mensaje": "Sesión cerrada exitosamente. Elimine el token del cliente."}


# --- Endpoint de prueba para verificar autenticación ---
from app.core.dependencies import get_current_active_user

@router.get("/perfil", response_model=UserInfoResponse, summary="Obtener perfil de usuario")
def obtener_perfil(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """
    Endpoint de ejemplo que requiere autenticación.
    Retorna la información del perfil del usuario logueado.
    """
    rol_map = {1: "administrador", 2: "operador"}
    rol_nombre = rol_map.get(current_user.get("id_rol"), "usuario")

    return UserInfoResponse(
        id_usuario=current_user["id_usuario"],
        nombre=current_user["nombre"],
        correo=current_user["correo"],
        id_rol=current_user["id_rol"],
        rol_nombre=rol_nombre,
        estado=current_user["estado"],
    )