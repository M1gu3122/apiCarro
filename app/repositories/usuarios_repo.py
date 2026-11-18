from app.core.database import Database
from app.models.usuarios import Usuarios
import bcrypt

class UsuariosRepository:
    def __init__(self):
        # Composición: El repositorio instancia su propia conexión
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios ORDER BY id_usuario ASC;")
        usuario = cursor.fetchall()
        conn.close()
        return usuario

    def obtener_por_id(self, id_usuario: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s;", (id_usuario,))
        Usuarios = cursor.fetchone()
        conn.close()
        return Usuarios


    def obtener_por_correo(self, correo: str):
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT *
                FROM usuarios
                WHERE correo = %s;
                """,
                (correo,)
            )

            return cursor.fetchone()

        finally:
            conn.close()
    def crear(self, usuario: Usuarios):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO usuarios (nombre, correo, contrasena_hash,estado,id_rol) 
            VALUES (%s, %s, %s, %s, %s) RETURNING id_usuario;
        """
        cursor.execute(query, (usuario.nombre, usuario.correo, usuario.contrasena_hash, usuario.estado,usuario.id_rol))
        nuevo_id = cursor.fetchone()['id_usuario']
        conn.commit()
        conn.close()
        return nuevo_id

    def eliminar(self, id_usuario: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s RETURNING id_usuario;", (id_usuario,))
        eliminado = cursor.fetchone()
        conn.commit()
        conn.close()
        return eliminado is not None

    def actualizar(self, id_usuario: int, Usuarios: Usuarios):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE usuarios
            SET nombre = %s, correo = %s, contrasena_hash = %s, estado = %s, id_rol = %s
            WHERE id_usuario = %s
            RETURNING id_usuario;
        """
        cursor.execute(query, (Usuarios.nombre,Usuarios.correo, Usuarios.contrasena_hash, Usuarios.estado, Usuarios.id_rol, id_usuario))
        actualizado = cursor.fetchone()
        conn.commit()
        conn.close()
        return actualizado is not None
