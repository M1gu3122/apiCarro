from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Vehiculos(BaseModel):
    id_vehiculo: Optional[int] = None
    placa: str
    marca: str
    modelo: str
    color: str
    fecha_registro: datetime
    estado: bool = True
    creado: Optional[datetime] = None
    actualizado: Optional[datetime] = None
    id_tipo: int