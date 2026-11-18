from app.core.database import Database
from app.models.modulo_x_rol import Modulo_x_rol

class Modulo_x_rolRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM modulo_x_rol ORDER BY id_rol, id_modulo ASC;")
        modulo_x_rol = cursor.fetchall()
        conn.close()
        return modulo_x_rol

    def obtener_por_id(self, id_rol: int, id_modulo: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM modulo_x_rol WHERE id_rol = %s AND id_modulo = %s;", (id_rol, id_modulo))
        modulo_x_rol = cursor.fetchone()
        conn.close()
        return modulo_x_rol

    def crear(self, modulo_x_rol: Modulo_x_rol):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO modulo_x_rol (id_rol,id_modulo,estado) 
            VALUES (%s, %s, %s) RETURNING id_rol, id_modulo;
        """
        cursor.execute(query, (modulo_x_rol.id_rol, modulo_x_rol.id_modulo, modulo_x_rol.estado))
        nuevo_modulo_x_rol = cursor.fetchone()
        conn.commit()
        conn.close()
        return nuevo_modulo_x_rol

    def eliminar(self, id_rol: int, id_modulo: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM modulo_x_rol WHERE id_rol = %s AND id_modulo = %s RETURNING id_rol, id_modulo;", (id_rol, id_modulo))
        modulo_x_rol_eliminado = cursor.fetchone()
        conn.commit()
        conn.close()
        return modulo_x_rol_eliminado is not None

    def actualizar(self, id_rol: int, id_modulo: int, modulo_x_rol: Modulo_x_rol):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE modulo_x_rol
            SET id_rol = %s, id_modulo = %s, estado = %s
            WHERE id_rol = %s AND id_modulo = %s
            RETURNING id_rol, id_modulo;
        """
        cursor.execute(query, (modulo_x_rol.id_rol, modulo_x_rol.id_modulo, modulo_x_rol.estado, id_rol, id_modulo))
        modulo_x_rol_actualizado = cursor.fetchone()
        conn.commit()
        conn.close()
        return modulo_x_rol_actualizado is not None