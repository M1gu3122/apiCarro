from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional ,Dict, Any
from decimal import Decimal

class Usuarios(BaseModel):
    id_usuario: Optional[int] = None
    nombre: str
    correo: EmailStr
    contraseña_hash: str
    estado: bool
    creado: Optional[datetime] = None
    actualizado: Optional[datetime] = None
    id_rol: int



    
    


    


    
