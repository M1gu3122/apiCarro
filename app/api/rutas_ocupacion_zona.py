from fastapi import APIRouter, HTTPException
from app.repositories.ocupacion_zona_repo import Ocupacion_zonaRepository
from app.models.ocupacion_zona import Ocupacion_zona

router = APIRouter(prefix="/ocupacion_zona", tags=["Gestión de ocupación de zona"])
repo = Ocupacion_zonaRepository()

@router.get("/")
def listar_ocupacion_zona():
    return repo.obtener_todos()

@router.get("/{id_ocupacion}")
def obtener_ocupacion_zona(id_ocupacion: int):
    ocupacion = repo.obtener_por_id(id_ocupacion)
    if not ocupacion:
        raise HTTPException(status_code=404, detail="ocupacion de zona no encontrada")
    return ocupacion

@router.post("/")
def crear_ocupacion_zona(ocupacion_zona: Ocupacion_zona):
    nueva_ocupacion = repo.crear(ocupacion_zona)
    return {"mensaje": "ocupacion de zona registrada exitosamente", "id": nueva_ocupacion}

@router.delete("/{id_ocupacion}")
def eliminar_ocupacion_zona(id_ocupacion: int):
    exito = repo.eliminar(id_ocupacion)
    if not exito:
        raise HTTPException(status_code=404, detail="ocupacion de zona no encontrada")
    return {"mensaje": "ocupacion de zona eliminada correctamente"}

@router.put("/{id_ocupacion}")
def actualizar_ocupacion_zona(id_ocupacion: int, ocupacion_zona: Ocupacion_zona):
    ocupacion_actualizada = repo.actualizar(id_ocupacion, ocupacion_zona)
    if not ocupacion_actualizada:
        raise HTTPException(status_code=404, detail="ocupacion de zona no encontrada")
    return {"mensaje": "ocupacion de zona actualizada correctamente"}