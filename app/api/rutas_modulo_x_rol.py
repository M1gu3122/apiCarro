from fastapi import APIRouter, HTTPException
from app.repositories.modulo_x_rol_repo import Modulo_x_rolRepository
from app.models.modulo_x_rol import Modulo_x_rol

router = APIRouter(prefix="/modulo_x_rol", tags=["Gestión de módulos por rol"])
repo = Modulo_x_rolRepository()

@router.get("/")
def listar_modulo_x_rol():
    return repo.obtener_todos()

@router.get("/{id_rol}/{id_modulo}")
def obtener_modulo_x_rol(id_rol: int, id_modulo: int):
    modulo_x_rol = repo.obtener_por_id(id_rol, id_modulo)
    if not modulo_x_rol:
        raise HTTPException(status_code=404, detail="modulo_x_rol no encontrado")
    return modulo_x_rol

@router.post("/")
def crear_modulo_x_rol(modulo_x_rol: Modulo_x_rol):
    nuevo_id = repo.crear(modulo_x_rol)
    return {"mensaje": "modulo_x_rol registrado exitosamente", "id": nuevo_id}

@router.delete("/{id_rol}/{id_modulo}")
def eliminar_modulo_x_rol(id_rol: int, id_modulo: int):
    exito = repo.eliminar(id_rol, id_modulo)
    if not exito:
        raise HTTPException(status_code=404, detail="modulo_x_rol no encontrado")
    return {"mensaje": "modulo_x_rol eliminado correctamente"}

@router.put("/{id_rol}/{id_modulo}")
def actualizar_modulo_x_rol(id_rol: int, id_modulo: int, modulo_x_rol: Modulo_x_rol):
    modulo_actualizado = repo.actualizar(id_rol, id_modulo, modulo_x_rol)
    if not modulo_actualizado:
        raise HTTPException(status_code=404, detail="modulo_x_rol no encontrado")
    return {"mensaje": "modulo_x_rol actualizado correctamente"}