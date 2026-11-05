from app.core.database import Database
from app.models.ocupacion_zona import Ocupacion_zona

class Ocupacion_zonaRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ocupacion_zona ORDER BY id_ocupacion ASC;")
        ocupaciones = cursor.fetchall()
        conn.close()
        return ocupaciones

    def obtener_por_id(self, id_ocupacion: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ocupacion_zona WHERE id_ocupacion = %s;", (id_ocupacion,))
        ocupacion = cursor.fetchone()
        conn.close()
        return ocupacion

    def crear(self, ocupacion_zona: Ocupacion_zona):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO ocupacion_zona (fecha_hora,cantidad_vehiculos,estado,id_zona) 
            VALUES (%s, %s, %s, %s) RETURNING id_ocupacion;
        """
        cursor.execute(query, (ocupacion_zona.fecha_hora, ocupacion_zona.cantidad_vehiculos, ocupacion_zona.estado, ocupacion_zona.id_zona))
        nueva_ocupacion = cursor.fetchone()['id_ocupacion']
        conn.commit()
        conn.close()
        return nueva_ocupacion

    def eliminar(self, id_ocupacion: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ocupacion_zona WHERE id_ocupacion = %s RETURNING id_ocupacion;", (id_ocupacion,))
        ocupacion_eliminada = cursor.fetchone()
        conn.commit()
        conn.close()
        return ocupacion_eliminada is not None

    def actualizar(self, id_ocupacion: int, ocupacion_zona: Ocupacion_zona):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE ocupacion_zona
            SET fecha_hora = %s, cantidad_vehiculos = %s, estado = %s, id_zona = %s
            WHERE id_ocupacion = %s
            RETURNING id_ocupacion;
        """
        cursor.execute(query, (ocupacion_zona.fecha_hora, ocupacion_zona.cantidad_vehiculos, ocupacion_zona.estado, ocupacion_zona.id_zona, id_ocupacion))
        ocupacion_actualizada = cursor.fetchone()
        conn.commit()
        conn.close()
        return ocupacion_actualizada is not None