from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Camaras(BaseModel):
    id_camara: Optional[int] = None
    nombre: str
    ubicacion: str
    fecha_registro: datetime
    estado: bool = True
    id_zona: int
