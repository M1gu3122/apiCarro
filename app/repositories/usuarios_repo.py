from app.core.database import Database
from app.models.usuarios import Usuarios

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
        cursor.execute("SELECT * FROM usuarios WHERE id = %s;", (id_usuario,))
        Usuarios = cursor.fetchone()
        conn.close()
        return Usuarios

    def crear(self, usuario: Usuarios):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO usuarios (nombre, correo, contrasena_hash,estado,creado,actualizado,id_rol) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_usuario;
        """
        cursor.execute(query, (usuario.nombre, usuario.correo, usuario.contrasena_hash, usuario.estado, usuario.creado, usuario.actualizado, usuario.id_rol))
        nuevo_id = cursor.fetchone()['id_usuario']
        conn.commit()
        conn.close()
        return nuevo_id

    def eliminar(self, id_usuario: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s RETURNING id;", (id_usuario,))
        eliminado = cursor.fetchone()
        conn.commit()
        conn.close()
        return eliminado is not None

    def actualizar(self, id_usuario: int, Usuarios: Usuarios):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE usuarios
            SET nombre = %s, grado = %s, promedio = %s
            WHERE id = %s
            RETURNING id;
        """
        cursor.execute(query, (Usuarios.nombre, Usuarios.grado, Usuarios.promedio, id_usuario))
        actualizado = cursor.fetchone()
        conn.commit()
        conn.close()
        return actualizado is not None
