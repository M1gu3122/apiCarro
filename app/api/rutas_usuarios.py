from fastapi import APIRouter, HTTPException
from starlette import status
from app.models.usuarios import Usuarios
from app.repositories.usuarios_repo import UsuariosRepository
from app.core.security import hashear_contrasena, asegurar_hash_contrasena

router = APIRouter(prefix="/usuarios", tags=["Gestión de Usuarios"])
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
def crear_usuario(usuario: Usuarios):
    if repo.obtener_por_correo(usuario.correo):
        raise HTTPException(
            status_code=409,
            detail="El correo ya está registrado"
        )

    # Hashear la contraseña antes de guardar (sin modificar el modelo Usuarios)
    usuario.contrasena_hash = hashear_contrasena(usuario.contrasena_hash)

    nuevo_id = repo.crear(usuario)

    return {
        "mensaje": "Usuario registrado exitosamente",
        "id": nuevo_id
    }


@router.delete("/{id_usuario}")
def eliminar_usuario(id_usuario: int):
    exito = repo.eliminar(id_usuario)
    if not exito:
        raise HTTPException(status_code=404, detail="Usuarios no encontrado")
    return {"mensaje": "Usuario eliminado correctamente"}

@router.put("/{id_usuario}", summary="Actualizar usuario")
def actualizar_Usuarios(id_usuario: int, Usuarios: Usuarios):
    """
    Actualiza un usuario.

    El modelo `Usuarios` exige el registro completo (nombre, correo,
    contrasena_hash, id_rol y estado), por eso las actualizaciones parciales
    deben reenviar todos los campos.
    """
    contrasena = str(Usuarios.contrasena_hash or "").strip()

    if not contrasena:
        # Sin contraseña nueva se conserva el hash vigente del usuario.
        actual = repo.obtener_por_id(id_usuario)
        if not actual:
            raise HTTPException(status_code=404, detail="Usuarios no encontrado")
        Usuarios.contrasena_hash = actual["contrasena_hash"]
    else:
        # Se cifra solo cuando el valor recibido todavía no es un hash bcrypt.
        Usuarios.contrasena_hash = asegurar_hash_contrasena(contrasena)

    exito = repo.actualizar(id_usuario, Usuarios)
    if not exito:
        raise HTTPException(status_code=404, detail="Usuarios no encontrado")

    return {
        "mensaje": "Usuario actualizado correctamente",
        "usuario": repo.obtener_por_id(id_usuario),
    }



