from fastapi import APIRouter, HTTPException
from app.repositories.visitas_repo import VisitasRepository
from app.models.visitas import Visitas

router = APIRouter(prefix="/visitas", tags=["Gestión de visitas"])
repo = VisitasRepository()

@router.get("/")
def listar_visitas():
    return repo.obtener_todos()

@router.get("/{id_visita}")
def obtener_visita(id_visita: int):
    visita = repo.obtener_por_id(id_visita)
    if not visita:
        raise HTTPException(status_code=404, detail="visita no encontrada")
    return visita

@router.post("/")
def crear_visita(visita: Visitas):
    nueva_visita = repo.crear(visita)
    return {"mensaje": "visita registrada exitosamente", "id": nueva_visita}

@router.delete("/{id_visita}")
def eliminar_visita(id_visita: int):
    exito = repo.eliminar(id_visita)
    if not exito:
        raise HTTPException(status_code=404, detail="visita no encontrada")
    return {"mensaje": "visita eliminada correctamente"}

@router.put("/{id_visita}")
def actualizar_visita(id_visita: int, visita: Visitas):
    visita_actualizada = repo.actualizar(id_visita, visita)
    if not visita_actualizada:
        raise HTTPException(status_code=404, detail="visita no encontrada")
    return {"mensaje": "visita actualizada correctamente"}