from fastapi import APIRouter, HTTPException, Query
from psycopg2 import Error as DatabaseError
from app.repositories.camaras_repo import CamarasRepository
from app.models.camaras import Camaras

router = APIRouter(prefix="/camaras", tags=["Gestión de cámaras"])
repo = CamarasRepository()

@router.get("/")
def listar_camaras():
    try:
        return repo.obtener_todos()
    except (DatabaseError, RuntimeError) as error:
        raise HTTPException(status_code=503, detail="No se pudieron consultar las cámaras") from error

@router.get("/catalogos")
def obtener_catalogos():
    return repo.obtener_catalogos()

@router.get("/{id_camara}")
def obtener_camara(id_camara: int):
    camara = repo.obtener_por_id(id_camara)
    if not camara:
        raise HTTPException(status_code=404, detail="camara no encontrada")
    return camara

@router.post("/")
def crear_camara(camara: Camaras):
    nueva_camara = repo.crear(camara)
    return {"mensaje": "camara registrada exitosamente", "id": nueva_camara}

@router.delete("/{id_camara}")
def eliminar_camara(id_camara: int):
    exito = repo.eliminar(id_camara)
    if not exito:
        raise HTTPException(status_code=404, detail="camara no encontrada")
    return {"mensaje": "camara eliminada correctamente"}

@router.put("/{id_camara}")
def actualizar_camara(id_camara: int, camara: Camaras):
    camara_actualizada = repo.actualizar(id_camara, camara)
    if not camara_actualizada:
        raise HTTPException(status_code=404, detail="camara no encontrada")
    return {"mensaje": "camara actualizada correctamente"}

@router.get("/{id_camara}/actividad")
def obtener_actividad_camara(id_camara: int, inicio: int = Query(0, ge=0), limite: int = Query(10, ge=1, le=100)):
    try:
        actividad = repo.obtener_actividad(id_camara, inicio, limite)
    except (DatabaseError, RuntimeError) as error:
        raise HTTPException(status_code=503, detail="No se pudo consultar la actividad") from error
    if actividad is None:
        raise HTTPException(status_code=404, detail="Cámara no encontrada")
    return actividad
