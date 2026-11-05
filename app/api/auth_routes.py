from fastapi import APIRouter, HTTPException, status

from app.models.auth import LoginRequest, TokenResponse
from app.repositories.usuarios_repo import UsuariosRepository
from app.core.security import verificar_contrasena, crear_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def login(datos: LoginRequest):
    repositorio = UsuariosRepository()

    usuario = repositorio.obtener_por_correo(datos.correo)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    if not usuario["estado"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    if not verificar_contrasena(
        datos.contrasena,
        usuario["contrasena_hash"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    token = crear_token(usuario["id_usuario"], usuario["id_rol"])

    return {
        "access_token": token,
        "token_type": "bearer"
    }