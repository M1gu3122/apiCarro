from app.core.database import Database
from app.models.tipos_vehiculo import Tipos_vehiculo

class Tipos_vehiculoRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tipos_vehiculo ORDER BY id_tipo ASC;")
        tipos_vehiculo = cursor.fetchall()
        conn.close()
        return tipos_vehiculo

    def obtener_por_id(self, id_tipo: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tipos_vehiculo WHERE id_tipo = %s;", (id_tipo,))
        tipo_vehiculo = cursor.fetchone()
        conn.close()
        return tipo_vehiculo

    def crear(self, tipo_vehiculo: Tipos_vehiculo):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO tipos_vehiculo (nombre,descripcion,estado,creado,actualizado) 
            VALUES (%s, %s, %s, %s, %s) RETURNING id_tipo;
        """
        cursor.execute(query, (tipo_vehiculo.nombre, tipo_vehiculo.descripcion, tipo_vehiculo.estado, tipo_vehiculo.creado, tipo_vehiculo.actualizado))
        nuevo_tipo = cursor.fetchone()['id_tipo']
        conn.commit()
        conn.close()
        return nuevo_tipo

    def eliminar(self, id_tipo: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tipos_vehiculo WHERE id_tipo = %s RETURNING id_tipo;", (id_tipo,))
        tipo_eliminado = cursor.fetchone()
        conn.commit()
        conn.close()
        return tipo_eliminado is not None

    def actualizar(self, id_tipo: int, tipo_vehiculo: Tipos_vehiculo):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE tipos_vehiculo
            SET nombre = %s, descripcion = %s, estado = %s, creado = %s, actualizado = %s
            WHERE id_tipo = %s
            RETURNING id_tipo;
        """
        cursor.execute(query, (tipo_vehiculo.nombre, tipo_vehiculo.descripcion, tipo_vehiculo.estado, tipo_vehiculo.creado, tipo_vehiculo.actualizado, id_tipo))
        tipo_actualizado = cursor.fetchone()
        conn.commit()
        conn.close()
        return tipo_actualizado is not None