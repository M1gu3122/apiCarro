from app.core.database import Database
from app.models.roles import Roles

class RolesRepository:
    def __init__(self):
        # Composición: El repositorio instancia su propia conexión
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM roles ORDER BY id_rol ASC;")
        roles = cursor.fetchall()
        conn.close()
        return roles

    def obtener_por_id(self, id_rol: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM roles WHERE id_rol = %s;", (id_rol,))
        rol = cursor.fetchone()
        conn.close()
        return rol

    def crear(self, rol: Roles):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO roles (nombre,descripcion,estado) 
            VALUES (%s, %s, %s) RETURNING id_rol;
        """
        cursor.execute(query, (rol.nombre, rol.descripcion, rol.estado))
        nuevo_rol = cursor.fetchone()['id_rol']
        conn.commit()
        conn.close()
        return nuevo_rol

    def eliminar(self, id_rol: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM roles WHERE id_rol = %s RETURNING id_rol;", (id_rol,))
        rol_eliminado = cursor.fetchone()
        conn.commit()
        conn.close()
        return rol_eliminado is not None

    def actualizar(self, id_rol: int, rol: Roles):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE roles
            SET nombre = %s, descripcion = %s, estado = %s
            WHERE id_rol = %s
            RETURNING id_rol;
        """
        cursor.execute(query, (rol.nombre, rol.descripcion, rol.estado, id_rol))
        rol_actualizado = cursor.fetchone()
        conn.commit()
        conn.close()
        return rol_actualizado is not None
        
