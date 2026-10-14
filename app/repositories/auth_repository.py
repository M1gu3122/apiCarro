import os
import jwt

from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"


def verificar_contrasena(
    contrasena: str,
    contrasena_hash: str
) -> bool:
    return password_hash.verify(
        contrasena,
        contrasena_hash
    )


def crear_token(id_usuario: int) -> str:
    ahora = datetime.now(timezone.utc)

    payload = {
        "sub": str(id_usuario),
        "iat": ahora,
        "exp": ahora + timedelta(minutes=30)
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )