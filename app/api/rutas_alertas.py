from fastapi import APIRouter, HTTPException
from app.repositories.alertas_repo import AlertasRepository
from app.models.alertas import Alertas

router = APIRouter(prefix="/alertas", tags=["Gestión de alertas"])
repo = AlertasRepository()

@router.get("/")
def listar_alertas():
    return repo.obtener_todos()

@router.get("/{id_alerta}")
def obtener_alerta(id_alerta: int):
    alerta = repo.obtener_por_id(id_alerta)
    if not alerta:
        raise HTTPException(status_code=404, detail="alerta no encontrada")
    return alerta

@router.post("/")
def crear_alerta(alerta: Alertas):
    nueva_alerta = repo.crear(alerta)
    return {"mensaje": "alerta registrada exitosamente", "id": nueva_alerta}

@router.delete("/{id_alerta}")
def eliminar_alerta(id_alerta: int):
    exito = repo.eliminar(id_alerta)
    if not exito:
        raise HTTPException(status_code=404, detail="alerta no encontrada")
    return {"mensaje": "alerta eliminada correctamente"}

@router.put("/{id_alerta}")
def actualizar_alerta(id_alerta: int, alerta: Alertas):
    alerta_actualizada = repo.actualizar(id_alerta, alerta)
    if not alerta_actualizada:
        raise HTTPException(status_code=404, detail="alerta no encontrada")
    return {"mensaje": "alerta actualizada correctamente"}