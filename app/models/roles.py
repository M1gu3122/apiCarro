from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

class Roles(BaseModel):
    id_rol: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None
    estado: bool = True
    solo_lectura: bool = False
    
    

    @field_validator("nombre")
    @classmethod
    def normalizar_nombre(cls, nombre: str) -> str:
        return nombre.strip().lower()
