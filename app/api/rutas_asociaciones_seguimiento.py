from fastapi import APIRouter, HTTPException
from app.repositories.asociaciones_seguimiento_repo import Asociaciones_seguimientoRepository
from app.models.asociaciones_seguimiento import Asociaciones_seguimiento

router = APIRouter(prefix="/asociaciones_seguimiento", tags=["Gestión de asociaciones de seguimiento"])
repo = Asociaciones_seguimientoRepository()

@router.get("/")
def listar_asociaciones_seguimiento():
    return repo.obtener_todos()

@router.get("/{id_asociacion}")
def obtener_asociacion_seguimiento(id_asociacion: int):
    asociacion = repo.obtener_por_id(id_asociacion)
    if not asociacion:
        raise HTTPException(status_code=404, detail="asociacion de seguimiento no encontrada")
    return asociacion

@router.post("/")
def crear_asociacion_seguimiento(asociacion_seguimiento: Asociaciones_seguimiento):
    nueva_asociacion = repo.crear(asociacion_seguimiento)
    return {"mensaje": "asociacion de seguimiento registrada exitosamente", "id": nueva_asociacion}

@router.delete("/{id_asociacion}")
def eliminar_asociacion_seguimiento(id_asociacion: int):
    exito = repo.eliminar(id_asociacion)
    if not exito:
        raise HTTPException(status_code=404, detail="asociacion de seguimiento no encontrada")
    return {"mensaje": "asociacion de seguimiento eliminada correctamente"}

@router.put("/{id_asociacion}")
def actualizar_asociacion_seguimiento(id_asociacion: int, asociacion_seguimiento: Asociaciones_seguimiento):
    asociacion_actualizada = repo.actualizar(id_asociacion, asociacion_seguimiento)
    if not asociacion_actualizada:
        raise HTTPException(status_code=404, detail="asociacion de seguimiento no encontrada")
    return {"mensaje": "asociacion de seguimiento actualizada correctamente"}