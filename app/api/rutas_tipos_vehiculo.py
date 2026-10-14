from fastapi import APIRouter, HTTPException
from app.repositories.tipos_vehiculo_repo import Tipos_vehiculoRepository
from app.models.tipos_vehiculo import Tipos_vehiculo

router = APIRouter(prefix="/tipos_vehiculo", tags=["Gestión de tipos de vehículo"])
repo = Tipos_vehiculoRepository()

@router.get("/")
def listar_tipos_vehiculo():
    return repo.obtener_todos()

@router.get("/{id_tipo}")
def obtener_tipo_vehiculo(id_tipo: int):
    tipo = repo.obtener_por_id(id_tipo)
    if not tipo:
        raise HTTPException(status_code=404, detail="tipo de vehículo no encontrado")
    return tipo

@router.post("/")
def crear_tipo_vehiculo(tipo_vehiculo: Tipos_vehiculo):
    nuevo_id = repo.crear(tipo_vehiculo)
    return {"mensaje": "tipo de vehículo registrado exitosamente", "id": nuevo_id}

@router.delete("/{id_tipo}")
def eliminar_tipo_vehiculo(id_tipo: int):
    exito = repo.eliminar(id_tipo)
    if not exito:
        raise HTTPException(status_code=404, detail="tipo de vehículo no encontrado")
    return {"mensaje": "tipo de vehículo eliminado correctamente"}

@router.put("/{id_tipo}")
def actualizar_tipo_vehiculo(id_tipo: int, tipo_vehiculo: Tipos_vehiculo):
    tipo_actualizado = repo.actualizar(id_tipo, tipo_vehiculo)
    if not tipo_actualizado:
        raise HTTPException(status_code=404, detail="tipo de vehículo no encontrado")
    return {"mensaje": "tipo de vehículo actualizado correctamente"}