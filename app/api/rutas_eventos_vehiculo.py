from fastapi import APIRouter, HTTPException
from app.repositories.eventos_vehiculo_repo import Eventos_vehiculoRepository
from app.models.eventos_vehiculo import EventoVehiculo

router = APIRouter(prefix="/eventos_vehiculo", tags=["Gestión de eventos de vehículo"])
repo = Eventos_vehiculoRepository()

@router.get("/")
def listar_eventos_vehiculo():
    return repo.obtener_todos()

@router.get("/{id_evento}")
def obtener_evento_vehiculo(id_evento: int):
    evento = repo.obtener_por_id(id_evento)
    if not evento:
        raise HTTPException(status_code=404, detail="evento de vehículo no encontrado")
    return evento

@router.post("/")
def crear_evento_vehiculo(evento: EventoVehiculo):
    nuevo_id = repo.crear(evento)
    return {"mensaje": "evento de vehículo registrado exitosamente", "id": nuevo_id}

@router.delete("/{id_evento}")
def eliminar_evento_vehiculo(id_evento: int):
    exito = repo.eliminar(id_evento)
    if not exito:
        raise HTTPException(status_code=404, detail="evento de vehículo no encontrado")
    return {"mensaje": "evento de vehículo eliminado correctamente"}

@router.put("/{id_evento}")
def actualizar_evento_vehiculo(id_evento: int, evento: EventoVehiculo):
    evento_actualizado = repo.actualizar(id_evento, evento)
    if not evento_actualizado:
        raise HTTPException(status_code=404, detail="evento de vehículo no encontrado")
    return {"mensaje": "evento de vehículo actualizado correctamente"}