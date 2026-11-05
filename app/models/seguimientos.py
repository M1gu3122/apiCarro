from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal


class Seguimientos(BaseModel):
    id_seguimiento: Optional[int] = None
    id_tracking: str
    inicio: datetime
    fin: Optional[datetime] = None
    confianza_promedio: Optional[Decimal] = None
    estado: bool = True
    id_visita: int
    id_camara: int
    