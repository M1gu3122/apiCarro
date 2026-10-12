from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Roles(BaseModel):
    id_rol: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None
    estado: bool = True
    creado: Optional[datetime] = None
    actualizado: Optional[datetime] = None
