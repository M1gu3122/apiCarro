from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.core.database import Database
from app.core.security_jwt import (
    decode_token,
    get_token_subject,
    get_token_roles,
    get_token_type,
)
from psycopg2.extras import RealDictCursor


# Esquema de bearer token para FastAPI
bearer_scheme = HTTPBearer(auto_error=False)


def get_db_connection() -> object:
    """
    Dependencia que proporciona una conexión a la base de datos.
    Retorna una conexión psycopg2 válida o lanza excepción.
    """
    db = Database()
    conn = db.get_connection()
    if conn is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de conexión a la base de datos",
        )
    return conn


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db_conn: object = Depends(get_db_connection),
) -> Dict[str, Any]:
    """
    Dependencia principal de autenticación que:
    
    1. Extrae el token del header Authorization: Bearer <token>
    2. Decodifica y valida el token JWT
    3. Consulta la base de datos para obtener el usuario
    4. Verifica que el usuario esté activo (estado = TRUE)
    5. Retorna un diccionario con los datos del usuario
    
    :return: Diccionario con {id_usuario, nombre, correo, id_rol, estado}
    :raises HTTPException: 401 si no hay token, token inválido o usuario no encontrado
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización faltante",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # --- PASO 1: Decodificar y validar token JWT ---
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (ValueError, Exception) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --- PASO 2: Obtener el ID de usuario del payload ---
    try:
        user_id = get_token_subject(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --- PASO 3: Consultar la base de datos ---
    cursor = db_conn.cursor(cursor_factory=RealDictCursor)

    # Consultar usuario por ID, filtrando solo los activos (estado = TRUE)
    # Esto respeta la política de "baja lógica" de tu base de datos
    cursor.execute(
        "SELECT id_usuario, nombre, correo, id_rol, estado, creado, actualizado "
        "FROM usuarios WHERE id_usuario = %s AND estado = TRUE;",
        (int(user_id),),
    )
    user = cursor.fetchone()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o desactivado (cuenta deshabilitada)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --- PASO 4: Retornar datos del usuario ---
    return {
        "id_usuario": user["id_usuario"],
        "nombre": user["nombre"],
        "correo": user["correo"],
        "id_rol": user["id_rol"],
        "estado": user["estado"],
        "creado": user["creado"],
        "actualizado": user["actualizado"],
    }


def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Dependencia adicional que verifica que el usuario esté activo.
    Esta es una capa extra de seguridad.
    
    :param current_user: Resultado de get_current_user
    :return: Mismo diccionario si el usuario está activo
    :raises HTTPException 403 si el usuario está desactivado
    """
    if current_user.get("estado") is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada. Contacte al administrador.",
        )
    return current_user


def check_user_role(
    allowed_roles: List[str],
    current_user: Dict[str, Any] = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Dependencia para verificar que el usuario tiene uno de los roles permitidos.
    
    :param allowed_roles: Lista de strings con roles permitidos
        ej: ["administrador"], ["operador", "vendedor"], ["administrador", "operador"]
    :param current_user: Resultado de get_current_active_user
    :return: Diccionario del usuario si tiene permiso
    :raises HTTPException 403 si el usuario no tiene los roles requeridos
    """
    # Obtener roles desde el payload del token (ya validado en get_current_user)
    # Los roles se almacenan en el token durante el login
    user_roles: List[str] = current_user.get("roles", [])

    # Verificar si el usuario tiene AL MENOS UNO de los roles permitidos
    # Lógica: any(role in allowed_roles for role in user_roles)
    has_permission = any(role in allowed_roles for role in user_roles)

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No tiene permisos suficientes. "
            f"Roles requeridos: {', '.join(allowed_roles)}. "
            f"Roles del usuario: {', '.join(user_roles) if user_roles else 'ninguno'}",
        )

    return current_user


def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db_conn: object = Depends(get_db_connection),
) -> Optional[Dict[str, Any]]:
    """
    Dependencia de autenticación OPCIONAL.
    
    A diferencia de get_current_user que lanza excepción si no hay token,
    esta función retorna None si no hay token, y los datos del usuario si hay
    y son válidos. Útil para endpoints que pueden ser públicos o privados.
    
    :return: Diccionario de usuario o None
    """
    if credentials is None:
        return None

    token = credentials.credentials

    try:
        payload = decode_token(token)
        user_id = get_token_subject(token)

        cursor = db_conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "SELECT id_usuario, nombre, correo, id_rol, estado "
            "FROM usuarios WHERE id_usuario = %s AND estado = TRUE;",
            (int(user_id),),
        )
        user = cursor.fetchone()

        if user is None:
            return None

        return {
            "id_usuario": user["id_usuario"],
            "nombre": user["nombre"],
            "correo": user["correo"],
            "id_rol": user["id_rol"],
            "estado": user["estado"],
        }

    except Exception:
        return None