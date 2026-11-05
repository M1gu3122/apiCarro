from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional ,Dict, Any
from decimal import Decimal

class Usuarios(BaseModel):
    id_usuario: Optional[int] = None
    nombre: str
    correo: EmailStr
    contrasena_hash: str
    estado: bool = True
    id_rol: int



    


    


    
