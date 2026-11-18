from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UsuarioSesion(BaseModel):
    id_usuario: int
    nombre: str
    correo: EmailStr
    id_rol: int | None = None
    rol: str | None = None
    solo_lectura: bool = False


class ModuloSesion(BaseModel):
    id_modulo: int
    nombre_modulo: str
    rutas: list[str]


class SesionResponse(BaseModel):
    usuario: UsuarioSesion
    expira_en: int
    modulos: list[ModuloSesion]
