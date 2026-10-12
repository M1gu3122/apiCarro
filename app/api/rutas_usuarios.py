from fastapi import APIRouter, HTTPException
from app.models.usuarios import Usuarios
from app.repositories.usuarios_repo import UsuariosRepository

router = APIRouter(prefix="/usuarios", tags=["Gestión de Usuarioss"])
repo = UsuariosRepository()

@router.get("/")
def listar_usuarios():
    return repo.obtener_todos()

@router.get("/{id_usuario}")
def obtener_usuario(id_usuario: int):
    usuario = repo.obtener_por_id(id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="usuario no encontrado")
    return usuario

@router.post("/")
def crear_usuario(Usuarios: Usuarios):
    nuevo_id = repo.crear(Usuarios)
    return {"mensaje": "Usuarioregistrado exitosamente", "id": nuevo_id}

@router.delete("/{id_usuario}")
def eliminar_usuario(id_usuario: int):
    exito = repo.eliminar(id_usuario)
    if not exito:
        raise HTTPException(status_code=404, detail="Usuarios no encontrado")
    return {"mensaje": "Usuario eliminado correctamente"}

@router.put("/{id_usuario}")
def actualizar_Usuarios(id_usuario: int, Usuarios: Usuarios):
    exito = repo.actualizar(id_usuario, Usuarios)
    if not exito:
        raise HTTPException(status_code=404, detail="Usuarios no encontrado")
    return {"mensaje": "Usuario actualizado correctamente"}
