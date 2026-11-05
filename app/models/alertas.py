from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal


class Alertas(BaseModel):
    id_alerta: Optional[int] = None
    tipo_alerta: str
    mensaje: str
    fecha_deteccion: Optional[datetime] = None
    estado: bool = True
    estado_resolucion: str
    fecha_resolucion:  str
    id_usuario_resuelve: int
    id_visita: int
    id_zona: int
