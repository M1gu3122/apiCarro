
import os
import bcrypt
import jwt

from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_MINUTOS = 30

# Correspondencia con el catálogo modulo existente; no depende del nombre del rol.
MODULOS_POR_RECURSO = {
    "dashboard": 1, "vehiculos": 2, "tipos_vehiculo": 2,
    "visitas": 3, "camaras": 4, "monitoreo": 4,
    "zonas": 5, "ocupacion_zona": 5,
    "seguimientos": 6, "eventos_vehiculo": 6, "asociaciones_seguimiento": 6,
    "alertas": 7, "reportes": 8,
    "usuarios": 9, "roles": 9, "modulo": 9, "modulo_x_rol": 9,
}
RUTAS_POR_MODULO = {
    1: ["/"], 2: ["/vehiculos"], 3: ["/visitas"],
    4: ["/monitoreo", "/camaras"], 5: ["/zonas"],
    6: ["/eventos", "/seguimientos"], 7: ["/alertas"],
    8: ["/reportes"], 9: ["/administracion"],
}

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


def es_hash_contrasena(valor: str) -> bool:
    """Indica si el valor ya viene cifrado (hash bcrypt)."""
    if not isinstance(valor, str):
        return False
    return valor.startswith(("$2a$", "$2b$", "$2y$"))


def asegurar_hash_contrasena(valor: str) -> str:
    """Cifra la contraseña solo si todavía no es un hash bcrypt."""
    if es_hash_contrasena(valor):
        return valor
    return hashear_contrasena(valor)


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


def crear_token(id_usuario: int, id_rol: int) -> str:
    ahora = datetime.now(timezone.utc)

    payload = {
        "sub": str(id_usuario),
        "id_rol": str(id_rol),
        "iat": ahora,
        "exp": ahora + timedelta(minutes=TOKEN_MINUTOS)
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def obtener_id_usuario(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> int:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Debes iniciar sesión", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM], options={"require": ["sub", "exp", "iat"]})
        id_usuario = int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, KeyError, TypeError) as error:
        raise HTTPException(status_code=401, detail="Token inválido o expirado", headers={"WWW-Authenticate": "Bearer"}) from error

    from app.repositories.usuarios_repo import UsuariosRepository
    from psycopg2 import Error as DatabaseError
    try:
        usuario = UsuariosRepository().obtener_perfil_sesion(id_usuario)
    except (DatabaseError, RuntimeError) as error:
        raise HTTPException(status_code=503, detail="No se pudo comprobar la sesión") from error
    if usuario is None or not usuario["estado"]:
        raise HTTPException(status_code=401, detail="La sesión ya no está activa", headers={"WWW-Authenticate": "Bearer"})
    request.state.usuario_sesion = usuario
    request.state.expira_en = int(payload["exp"])
    return id_usuario


def obtener_modulos_usuario(request: Request, id_usuario: int = Depends(obtener_id_usuario)):
    from app.repositories.modulo_x_rol_repo import Modulo_x_rolRepository
    from psycopg2 import Error as DatabaseError
    try:
        modulos = Modulo_x_rolRepository().obtener_habilitados_por_usuario(id_usuario)
    except (DatabaseError, RuntimeError) as error:
        raise HTTPException(status_code=503, detail="No se pudieron comprobar los permisos") from error
    modulos = [{**modulo, "rutas": [ruta for ruta in RUTAS_POR_MODULO.get(modulo["id_modulo"], []) if not (request.state.usuario_sesion.get("solo_lectura") and ruta == "/camaras")]} for modulo in modulos]
    request.state.modulos_usuario = modulos
    return modulos


def requerir_modulo(id_modulo: int):
    def comprobar_acceso(request: Request, modulos=Depends(obtener_modulos_usuario)):
        if not any(modulo["id_modulo"] == id_modulo for modulo in modulos):
            raise HTTPException(status_code=403, detail="No tienes permiso para acceder a este módulo")
        if request.state.usuario_sesion.get("solo_lectura"):
            recurso = request.url.path.strip("/").split("/")[0]
            if request.method not in {"GET", "HEAD", "OPTIONS"} or recurso in {"usuarios", "roles", "modulo", "modulo_x_rol", "camaras", "zonas", "ocupacion_zona"}:
                raise HTTPException(status_code=403, detail="Tu rol solo permite consultar la información")
    return comprobar_acceso
