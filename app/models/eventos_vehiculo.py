from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal

class EventoVehiculo(BaseModel):
    id_evento: Optional[int] = None
    tipo_evento: str
    fecha_hora: Optional[datetime] = None
    confianza: Optional[Decimal] = None
    estado: bool = True
    id_visita: int
    id_camara: int
    id_seguimiento: Optional[int] = None
    id_zona: int