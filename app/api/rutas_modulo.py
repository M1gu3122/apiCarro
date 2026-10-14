from fastapi import APIRouter, HTTPException
from app.repositories.modulo_repo import ModuloRepository
from app.models.modulo import Modulo

router = APIRouter(prefix="/modulo", tags=["Gestión de módulos"])
repo = ModuloRepository()

@router.get("/")
def listar_modulos():
    return repo.obtener_todos()

@router.get("/{id_modulo}")
def obtener_modulo(id_modulo: int):
    modulo = repo.obtener_por_id(id_modulo)
    if not modulo:
        raise HTTPException(status_code=404, detail="modulo no encontrado")
    return modulo

@router.post("/")
def crear_modulo(modulo: Modulo):
    nuevo_id = repo.crear(modulo)
    return {"mensaje": "modulo registrado exitosamente", "id": nuevo_id}

@router.delete("/{id_modulo}")
def eliminar_modulo(id_modulo: int):
    modulo = repo.eliminar(id_modulo)
    if not modulo:
        raise HTTPException(status_code=404, detail="modulo no encontrado")
    return {"mensaje": "modulo eliminado correctamente"}

@router.put("/{id_modulo}")
def actualizar_modulo(id_modulo: int, modulo: Modulo):
    modulo_actualizado = repo.actualizar(id_modulo, modulo)
    if not modulo_actualizado:
        raise HTTPException(status_code=404, detail="modulo no encontrado")
    return {"mensaje": "modulo actualizado correctamente"}