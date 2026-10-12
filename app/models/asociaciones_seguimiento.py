from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal

class Asociaciones_seguimiento(BaseModel):
    id_asociacion: Optional[int] = None
    metodo: str
    confianza: Decimal | None = None
    resultado: str
    fecha_evaluacion: datetime
    estado: bool = True
    creado: Optional[datetime] = None
    actualizado: Optional[datetime] = None
    id_seguimiento_origen: int
    id_seguimiento_destino: int
    
    
    
