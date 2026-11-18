from fastapi import APIRouter, HTTPException
from app.repositories.camaras_repo import CamarasRepository
from app.models.camaras import Camaras

router = APIRouter(prefix="/camaras", tags=["Gestión de cámaras"])
repo = CamarasRepository()

@router.get("/")
def listar_camaras():
    return repo.obtener_todos()

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