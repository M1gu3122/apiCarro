from datetime import date
from fastapi import APIRouter, HTTPException, Query
from psycopg2 import Error as DatabaseError
from app.repositories.reportes_repo import ReportesRepository

router = APIRouter(prefix="/reportes", tags=["Reportes"])
repo = ReportesRepository()


@router.get("/")
def obtener_reportes(desde: date | None = None, hasta: date | None = None, id_zona: int | None = Query(None, ge=1), zona_horaria: str = Query("America/Bogota", max_length=64)):
    try:
        return repo.obtener_reporte(desde, hasta, id_zona, zona_horaria)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except (DatabaseError, RuntimeError) as error:
        raise HTTPException(status_code=503, detail="No se pudo consultar el reporte") from error
