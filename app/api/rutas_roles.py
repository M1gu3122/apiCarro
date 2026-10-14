from fastapi import APIRouter, HTTPException
from app.repositories.roles_repo import Roles
from app.repositories.roles_repo import RolesRepository

router = APIRouter(prefix="/roles", tags=["Gestión de roles"])
repo = RolesRepository()

@router.get("/")
def listar_roles():
    return repo.obtener_todos()

@router.get("/{id_rol}")
def obtener_rol(id_rol: int):
    rol = repo.obtener_por_id(id_rol)
    if not rol:
        raise HTTPException(status_code=404, detail="rol no encontrado")
    return rol

@router.post("/")
def crear_rol(rol: Roles):
    nuevo_id = repo.crear(rol)
    return {"mensaje": "rol registrado exitosamente", "id": nuevo_id}

@router.delete("/{id_rol}")
def eliminar_rol(id_rol: int):
    rol = repo.eliminar(id_rol)
    if not rol:
        raise HTTPException(status_code=404, detail="rol no encontrado")
    return {"mensaje": "rol eliminado correctamente"}

@router.put("/{id_rol}")
def actualizar_rol(id_rol: int, rol: Roles):
    rol = repo.actualizar(id_rol, Roles)
    if not rol:
        raise HTTPException(status_code=404, detail="rol no encontrado")
    return {"mensaje": "rol actualizado correctamente"}
