from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Camaras(BaseModel):
    id_camara: Optional[int] = None
    nombre: str
    ubicacion: str
    fecha_registro: datetime
    estado: bool = True
    creado: Optional[datetime] = None
    actualizado: Optional[datetime] = None
    id_zona: int
