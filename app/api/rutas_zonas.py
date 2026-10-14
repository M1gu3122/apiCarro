from fastapi import APIRouter, HTTPException
from app.repositories.zonas_repo import ZonasRepository
from app.models.zonas import Zonas

router = APIRouter(prefix="/zonas", tags=["Gestión de zonas"])
repo = ZonasRepository()

@router.get("/")
def listar_zonas():
    return repo.obtener_todos()

@router.get("/{id_zona}")
def obtener_zona(id_zona: int):
    zona = repo.obtener_por_id(id_zona)
    if not zona:
        raise HTTPException(status_code=404, detail="zona no encontrada")
    return zona

@router.post("/")
def crear_zona(zona: Zonas):
    nueva_zona = repo.crear(zona)
    return {"mensaje": "zona registrada exitosamente", "id": nueva_zona}

@router.delete("/{id_zona}")
def eliminar_zona(id_zona: int):
    exito = repo.eliminar(id_zona)
    if not exito:
        raise HTTPException(status_code=404, detail="zona no encontrada")
    return {"mensaje": "zona eliminada correctamente"}

@router.put("/{id_zona}")
def actualizar_zona(id_zona: int, zona: Zonas):
    zona_actualizada = repo.actualizar(id_zona, zona)
    if not zona_actualizada:
        raise HTTPException(status_code=404, detail="zona no encontrada")
    return {"mensaje": "zona actualizada correctamente"}