from fastapi import APIRouter, HTTPException
from app.repositories.seguimientos_repo import SeguimientosRepository
from app.models.seguimientos import Seguimientos

router = APIRouter(prefix="/seguimientos", tags=["Gestión de seguimientos"])
repo = SeguimientosRepository()

@router.get("/")
def listar_seguimientos():
    return repo.obtener_todos()

@router.get("/catalogos")
def obtener_catalogos():
    return repo.obtener_catalogos()

@router.get("/{id_seguimiento}")
def obtener_seguimiento(id_seguimiento: int):
    seguimiento = repo.obtener_por_id(id_seguimiento)
    if not seguimiento:
        raise HTTPException(status_code=404, detail="seguimiento no encontrado")
    return seguimiento

@router.post("/")
def crear_seguimiento(seguimiento: Seguimientos):
    nuevo_id = repo.crear(seguimiento)
    return {"mensaje": "seguimiento registrado exitosamente", "id": nuevo_id}

@router.delete("/{id_seguimiento}")
def eliminar_seguimiento(id_seguimiento: int):
    exito = repo.eliminar(id_seguimiento)
    if not exito:
        raise HTTPException(status_code=404, detail="seguimiento no encontrado")
    return {"mensaje": "seguimiento eliminado correctamente"}

@router.put("/{id_seguimiento}")
def actualizar_seguimiento(id_seguimiento: int, seguimiento: Seguimientos):
    seguimiento_actualizado = repo.actualizar(id_seguimiento, seguimiento)
    if not seguimiento_actualizado:
        raise HTTPException(status_code=404, detail="seguimiento no encontrado")
    return {"mensaje": "seguimiento actualizado correctamente"}