from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

from app.core.database import Database
from app.core.security import verify_password, get_password_hash
from app.core.security_jwt import create_access_token, decode_token

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# --- Modelos Pydantic ---

class UsuarioCreate(BaseModel):
    """Modelo para crear un nuevo usuario."""
    nombre: str
    correo: EmailStr
    contrasena: str
    id_rol: int


class UsuarioUpdate(BaseModel):
    """Modelo para actualizar un usuario."""
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    contrasena: Optional[str] = None
    estado: Optional[bool] = None


class UsuarioResponse(BaseModel):
    """Modelo de respuesta para usuario (sin contraseña)."""
    id_usuario: int
    nombre: str
    correo: str
    id_rol: int
    estado: bool
    creado: Optional[str] = None
    actualizado: Optional[str] = None


# --- Endpoints ---

@router.post("/", response_model=UsuarioResponse, summary="Crear usuario")
def crear_usuario(usuario: UsuarioCreate, db_conn: object = Body(...)):
    """
    Endpoint para crear un nuevo usuario.
    """
    cursor = db_conn.cursor(cursor_factory=RealDictCursor)

    # 1. Verificar si el correo ya existe
    cursor.execute("SELECT id_usuario FROM usuarios WHERE correo = %s;", (usuario.correo,))
    existente = cursor.fetchone()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado",
        )

    # 2. Hashear la contraseña
    contrasena_hash = get_password_hash(usuario.contrasena)

    # 3. Insertar usuario en la base de datos
    cursor.execute(
        """
        INSERT INTO usuarios (nombre, correo, contrasena_hash, estado, id_rol)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id_usuario, nombre, correo, id_rol, estado, creado, actualizado;
        """,
        (usuario.nombre, usuario.correo, contrasena_hash, True, usuario.id_rol),
    )
    usuario_creado = cursor.fetchone()
    db_conn.commit()

    return usuario_creado


@router.get("/", summary="Listar usuarios")
def listar_usuarios(db_conn: object = Body(...)):
    """
    Listar todos los usuarios.
    """
    cursor = db_conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT id_usuario, nombre, correo, id_rol, estado, creado, actualizado FROM usuarios ORDER BY nombre ASC;"
    )
    usuarios = cursor.fetchall()
    return usuarios


@router.get("/me", summary="Obtener perfil del usuario actual")
def obtener_perfil_actual(
    current_user: Dict[str, Any] = Body(...),
):
    """
    Obtener perfil del usuario actual.
    """
    rol_map = {1: "administrador", 2: "operador"}
    rol_nombre = rol_map.get(current_user.get("id_rol"), "usuario")

    return {
        "id_usuario": current_user["id_usuario"],
        "nombre": current_user["nombre"],
        "correo": current_user["correo"],
        "id_rol": current_user["id_rol"],
        "rol_nombre": rol_nombre,
        "estado": current_user["estado"],
        "creado": str(current_user.get("creado")) if current_user.get("creado") else None,
        "actualizado": str(current_user.get("actualizado")) if current_user.get("actualizado") else None,
    }


@router.get("/{id_usuario}", summary="Obtener usuario por ID")
def obtener_usuario(id_usuario: int, db_conn: object = Body(...)):
    """
    Obtener un usuario específico por su ID.
    """
    cursor = db_conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT id_usuario, nombre, correo, id_rol, estado, creado, actualizado FROM usuarios WHERE id_usuario = %s;",
        (id_usuario,),
    )
    usuario = cursor.fetchone()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return usuario


@router.put("/{id_usuario}", summary="Actualizar usuario")
def actualizar_usuario(id_usuario: int, usuario_data: UsuarioUpdate, db_conn: object = Body(...)):
    """
    Actualizar los datos de un usuario.
    """
    cursor = db_conn.cursor(cursor_factory=RealDictCursor)

    update_fields = []
    query_params = []

    if usuario_data.nombre is not None:
        update_fields.append("nombre = %s")
        query_params.append(usuario_data.nombre)

    if usuario_data.correo is not None:
        cursor.execute("SELECT id_usuario FROM usuarios WHERE correo = %s AND id_usuario != %s;", (usuario_data.correo, id_usuario))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está en uso por otro usuario",
            )
        update_fields.append("correo = %s")
        query_params.append(usuario_data.correo)

    if usuario_data.contrasena is not None:
        contrasena_hash = get_password_hash(usuario_data.contrasena)
        update_fields.append("contrasena_hash = %s")
        query_params.append(contrasena_hash)

    if usuario_data.estado is not None:
        update_fields.append("estado = %s")
        query_params.append(usuario_data.estado)

    if not update_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No hay campos para actualizar")

    query_params.append(id_usuario)

    query = f"UPDATE usuarios SET {', '.join(update_fields)} WHERE id_usuario = %s RETURNING id_usuario, nombre, correo, id_rol, estado, creado, actualizado;"
    
    cursor.execute(query, query_params)
    usuario_actualizado = cursor.fetchone()
    db_conn.commit()

    if not usuario_actualizado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    return usuario_actualizado


@router.delete("/{id_usuario}", summary="Eliminar usuario lógico")
def eliminar_usuario(id_usuario: int, db_conn: object = Body(...)):
    """
    Eliminar usuario lógico (desactivarlo).
    """
    cursor = db_conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT id_usuario, nombre FROM usuarios WHERE id_usuario = %s;", (id_usuario,))
    usuario_existente = cursor.fetchone()

    if not usuario_existente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    cursor.execute(
        "UPDATE usuarios SET estado = FALSE, actualizado = CURRENT_TIMESTAMP WHERE id_usuario = %s RETURNING id_usuario, nombre, estado;",
        (id_usuario,),
    )
    usuario_desactivado = cursor.fetchone()
    db_conn.commit()

    return {
        "mensaje": "Usuario desactivado exitosamente",
        "usuario_desactivado": {"id": usuario_desactivado["id_usuario"], "nombre": usuario_desactivado["nombre"], "estado": usuario_desactivado["estado"]},
    }