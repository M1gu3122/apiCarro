from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Visitas(BaseModel):
    id_visita: Optional[int] = None
    fecha_entrada: datetime
    fecha_salida: datetime
    estado: bool = True
    id_vehiculo: int
    