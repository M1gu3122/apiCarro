
import os
import bcrypt
import jwt

from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_MINUTOS = 30

if not SECRET_KEY:
    raise RuntimeError(
        "Debes configurar SECRET_KEY en el archivo .env"
    )

bearer_scheme = HTTPBearer(auto_error=False)


def generar_hash(contrasena: str) -> str:
    return bcrypt.hashpw(
        contrasena.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def hashear_contrasena(contrasena: str) -> str:
    return generar_hash(contrasena)


def verificar_contrasena(
    contrasena: str,
    contrasena_hash: str
) -> bool:
    try:
        return bcrypt.checkpw(
            contrasena.encode("utf-8"),
            contrasena_hash.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


def crear_token(id_usuario: int) -> str:
    ahora = datetime.now(timezone.utc)

    payload = {
        "sub": str(id_usuario),
        "iat": ahora,
        "exp": ahora + timedelta(minutes=TOKEN_MINUTOS)
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def obtener_id_usuario(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    )
) -> int:

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debes iniciar sesión",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return int(payload["sub"])

    except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
