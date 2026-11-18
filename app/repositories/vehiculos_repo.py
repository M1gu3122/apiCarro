from contextlib import closing

from app.core.database import Database
from app.models.vehiculos import Vehiculos

class VehiculosRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.*, EXISTS (
                SELECT 1 FROM visitas vi WHERE vi.id_vehiculo = v.id_vehiculo
            ) AS tiene_visitas
            FROM vehiculos v ORDER BY v.id_vehiculo ASC;
        """)
        vehiculos = cursor.fetchall()
        conn.close()
        return vehiculos

    def obtener_por_id(self, id_vehiculo: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.*, EXISTS (
                SELECT 1 FROM visitas vi WHERE vi.id_vehiculo = v.id_vehiculo
            ) AS tiene_visitas
            FROM vehiculos v WHERE v.id_vehiculo = %s;
        """, (id_vehiculo,))
        vehiculo = cursor.fetchone()
        conn.close()
        return vehiculo

    def crear(self, vehiculo: Vehiculos):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO vehiculos (placa,marca,modelo,color,fecha_registro,estado,id_tipo) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_vehiculo;
        """
        cursor.execute(query, (vehiculo.placa, vehiculo.marca, vehiculo.modelo, vehiculo.color, vehiculo.fecha_registro, vehiculo.estado, vehiculo.id_tipo))
        nuevo_vehiculo = cursor.fetchone()['id_vehiculo']
        conn.commit()
        conn.close()
        return nuevo_vehiculo

    def desactivar(self, id_vehiculo: int):
        with closing(self.db.get_connection()) as conn, conn, conn.cursor() as cursor:
            cursor.execute(
                "UPDATE vehiculos SET estado = FALSE WHERE id_vehiculo = %s RETURNING id_vehiculo;",
                (id_vehiculo,),
            )
            return cursor.fetchone() is not None

    def actualizar(self, id_vehiculo: int, vehiculo: Vehiculos):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE vehiculos
            SET placa = %s, marca = %s, modelo = %s, color = %s, fecha_registro = %s, estado = %s, id_tipo = %s
            WHERE id_vehiculo = %s
            RETURNING id_vehiculo;
        """
        cursor.execute(query, (vehiculo.placa, vehiculo.marca, vehiculo.modelo, vehiculo.color, vehiculo.fecha_registro, vehiculo.estado, vehiculo.id_tipo, id_vehiculo))
        vehiculo_actualizado = cursor.fetchone()
        conn.commit()
        conn.close()
        return vehiculo_actualizado is not None
