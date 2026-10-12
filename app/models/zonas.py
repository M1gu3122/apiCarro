from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional ,Dict, Any


class Zonas(BaseModel):
    id_zona: Optional[int] = None
    nombre: str
    tipo: str
    capacidad_maxima: int
    poligono: Optional[Dict[str, Any]] = None
    estado : bool = True
    creado: Optional[datetime] = None
    actualizado: Optional[datetime] = None
