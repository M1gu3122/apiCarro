from fastapi import APIRouter, HTTPException
from app.repositories.vehiculos_repo import VehiculosRepository
from app.models.vehiculos import Vehiculos

router = APIRouter(prefix="/vehiculos", tags=["Gestión de vehículos"])
repo = VehiculosRepository()

@router.get("/")
def listar_vehiculos():
    return repo.obtener_todos()

@router.get("/{id_vehiculo}")
def obtener_vehiculo(id_vehiculo: int):
    vehiculo = repo.obtener_por_id(id_vehiculo)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="vehiculo no encontrado")
    return vehiculo

@router.post("/")
def crear_vehiculo(vehiculo: Vehiculos):
    nuevo_id = repo.crear(vehiculo)
    return {"mensaje": "vehiculo registrado exitosamente", "id": nuevo_id}

@router.delete("/{id_vehiculo}")
def desactivar_vehiculo(id_vehiculo: int):
    exito = repo.desactivar(id_vehiculo)
    if not exito:
        raise HTTPException(status_code=404, detail="vehiculo no encontrado")
    return {"mensaje": "vehiculo desactivado correctamente"}

@router.put("/{id_vehiculo}")
def actualizar_vehiculo(id_vehiculo: int, vehiculo: Vehiculos):
    vehiculo_actualizado = repo.actualizar(id_vehiculo, vehiculo)
    if not vehiculo_actualizado:
        raise HTTPException(status_code=404, detail="vehiculo no encontrado")
    return {"mensaje": "vehiculo actualizado correctamente"}
