import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from passlib.context import CryptContext

from app.core.security import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

# Contexto de hashing para contraseñas (usando bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT de acceso.
    
    :param data: Diccionario con los datos para el payload (sub, roles, etc.)
    :param expires_delta: Tiempo opcional de expiración. Si no se especifica,
        usará el valor default de ACCESS_TOKEN_EXPIRE_MINUTES.
    :return: Token JWT codificado en string
    """
    to_encode = data.copy()
    
    # Calcular fecha de expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Agregar información adicional útil
    to_encode.setdefault("type", "access")
    
    # Codificar el token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_days: int = REFRESH_TOKEN_EXPIRE_DAYS
) -> str:
    """
    Crea un token de refresco con mayor tiempo de vida.
    
    :param data: Diccionario con los datos para el payload
    :param expires_dias: Días hasta la expiración
    :return: Token JWT codificado
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=expires_days)
    to_encode.update({"exp": expire})
    to_encode.setdefault("type", "refresh")
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodifica y valida un token JWT.
    
    :param token: Token JWT a decodificar
    :return: Payload decodificado como diccionario
    :raises jwt.ExpiredSignatureError: Si el token ha expirado
    :raises jwt.InvalidTokenError: Si el token es inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # Re-lanzar con mensaje más claro
        raise jwt.ExpiredSignatureError("El token ha expirado")
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError(f"Token inválido: {str(e)}")


def get_token_subject(token: str) -> str:
    """Extrae el subject (normalmente el ID de usuario) del token."""
    payload = decode_token(token)
    sub: str = payload.get("sub")
    if sub is None:
        raise ValueError("El token no contiene un subject (user ID)")
    return str(sub)


def get_token_roles(token: str) -> List[str]:
    """Extrae los roles del usuario del payload del token."""
    payload = decode_token(token)
    roles: List[str] = payload.get("roles", [])
    # Asegurar que siempre sea una lista
    if roles is None:
        return []
    return roles


def get_token_type(token: str) -> str:
    """Extrae el tipo de token (access vs refresh)."""
    payload = decode_token(token)
    token_type: str = payload.get("type", "access")
    return token_type


def is_token_expired(token: str) -> bool:
    """Verifica si un token está expirado sin lanzar excepción."""
    try:
        decode_token(token)
        return False
    except jwt.ExpiredSignatureError:
        return True


def refresh_access_token(old_token: str) -> str:
    """
    Intenta refrescar un token usando un token de refresh.
    
    :param old_token: Token de refresh antiguo
    :return: Nuevo token de acceso
    :raises: Excepción si el token es inválido o no es un refresh token
    """
    payload = decode_token(old_token)
    
    # Verificar que sea un token de refresh
    token_type = payload.get("type", "access")
    if token_type != "refresh":
        raise ValueError("El token proporcionado no es un token de refresh")
    
    # Extraer el subject (user ID)
    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("El token de refresh no contiene user ID")
    
    # Crear nuevo token de acceso
    new_token = create_access_token(data={"sub": str(user_id)})
    return new_token


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash usando bcrypt."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera un hash seguro de la contraseña usando bcrypt."""
    return pwd_context.hash(password)