from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from app.models.auth import LoginRequest, TokenResponse, SesionResponse
from app.repositories.usuarios_repo import UsuariosRepository
from app.core.security import verificar_contrasena, crear_token, obtener_id_usuario, obtener_modulos_usuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def login(datos: LoginRequest, response: Response):
    usuario = UsuariosRepository().obtener_por_correo(datos.correo)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo o contraseña incorrectos")
    if not usuario["estado"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo")
    if not verificar_contrasena(datos.contrasena, usuario["contrasena_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo o contraseña incorrectos")
    token = crear_token(usuario["id_usuario"], usuario["id_rol"])
    response.headers["Cache-Control"] = "no-store"
    return {"access_token": token, "token_type": "bearer"}


@router.get("/sesion", response_model=SesionResponse)
def consultar_sesion(request: Request, response: Response, modulos=Depends(obtener_modulos_usuario)):
    response.headers["Cache-Control"] = "no-store"
    return {"usuario": request.state.usuario_sesion, "expira_en": request.state.expira_en, "modulos": modulos}
