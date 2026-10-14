from app.core.database import Database
from app.models.vehiculos import Vehiculos

class VehiculosRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehiculos ORDER BY id_vehiculo ASC;")
        vehiculos = cursor.fetchall()
        conn.close()
        return vehiculos

    def obtener_por_id(self, id_vehiculo: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehiculos WHERE id_vehiculo = %s;", (id_vehiculo,))
        vehiculo = cursor.fetchone()
        conn.close()
        return vehiculo

    def crear(self, vehiculo: Vehiculos):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO vehiculos (placa,marca,modelo,color,fecha_registro,estado,creado,actualizado,id_tipo) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_vehiculo;
        """
        cursor.execute(query, (vehiculo.placa, vehiculo.marca, vehiculo.modelo, vehiculo.color, vehiculo.fecha_registro, vehiculo.estado, vehiculo.creado, vehiculo.actualizado, vehiculo.id_tipo))
        nuevo_vehiculo = cursor.fetchone()['id_vehiculo']
        conn.commit()
        conn.close()
        return nuevo_vehiculo

    def eliminar(self, id_vehiculo: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vehiculos WHERE id_vehiculo = %s RETURNING id_vehiculo;", (id_vehiculo,))
        vehiculo_eliminado = cursor.fetchone()
        conn.commit()
        conn.close()
        return vehiculo_eliminado is not None

    def actualizar(self, id_vehiculo: int, vehiculo: Vehiculos):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE vehiculos
            SET placa = %s, marca = %s, modelo = %s, color = %s, fecha_registro = %s, estado = %s, creado = %s, actualizado = %s, id_tipo = %s
            WHERE id_vehiculo = %s
            RETURNING id_vehiculo;
        """
        cursor.execute(query, (vehiculo.placa, vehiculo.marca, vehiculo.modelo, vehiculo.color, vehiculo.fecha_registro, vehiculo.estado, vehiculo.creado, vehiculo.actualizado, vehiculo.id_tipo, id_vehiculo))
        vehiculo_actualizado = cursor.fetchone()
        conn.commit()
        conn.close()
        return vehiculo_actualizado is not None