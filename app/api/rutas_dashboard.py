from fastapi import APIRouter, HTTPException, Query
from psycopg2 import Error as DatabaseError
from app.repositories.dashboard_repo import DashboardRepository

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
repo = DashboardRepository()


@router.get("/")
def obtener_dashboard(zona_horaria: str = Query("America/Bogota", max_length=64), umbral_minutos: int | None = Query(None, ge=1, le=525600)):
    try:
        return repo.obtener_resumen(zona_horaria, umbral_minutos)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except (DatabaseError, RuntimeError) as error:
        raise HTTPException(status_code=503, detail="No se pudo consultar el dashboard") from error
