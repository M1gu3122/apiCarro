from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Modulo(BaseModel):
    id_modulo: Optional[int] = None
    nombre_modulo: str
    estado: bool = True
    creado: Optional[datetime] = None
    actualizado: Optional[datetime] = None