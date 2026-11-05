from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Ocupacion_zona(BaseModel):
    id_ocupacion: Optional[int] = None
    fecha_hora: datetime
    cantidad_vehiculos: int
    estado: bool = True
    id_zona: int