from typing import Literal
from fastapi import APIRouter, HTTPException, Query
from psycopg2 import Error as DatabaseError
from app.repositories.monitoreo_repo import MonitoreoRepository

router = APIRouter(prefix="/monitoreo", tags=["Monitoreo vehicular"])
repo = MonitoreoRepository()


@router.get("/")
def obtener_monitoreo(busqueda: str = Query("", max_length=200), estado: Literal["dentro", "finalizadas", "sin_identificar", "todas"] = "dentro",
                     id_zona: int | None = Query(None, ge=1), permanencia: Literal["todas", "excede", "abiertas"] = "todas",
                     umbral_minutos: int | None = Query(None, ge=1, le=525600), inicio: int = Query(0, ge=0), limite: int = Query(10, ge=1, le=100),
                     ordenar: Literal["id_visita", "placa", "fecha_entrada", "duracion_minutos", "zona", "camara"] = "fecha_entrada",
                     direccion: Literal["asc", "desc"] = "desc"):
    try:
        return repo.obtener_monitoreo(busqueda, estado, id_zona, permanencia, umbral_minutos, inicio, limite, ordenar, direccion)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except (DatabaseError, RuntimeError) as error:
        raise HTTPException(status_code=503, detail="No se pudo consultar el monitoreo") from error
