from pydantic import BaseModel
from datetime import datetime
from typing import Optional 

class Modulo_x_rol(BaseModel):
    id_rol: Optional[int] = None
    id_modulo: int
    estado: bool = True
    creado: Optional[datetime] = None
    actualizado: Optional[datetime] = None
    
    
    