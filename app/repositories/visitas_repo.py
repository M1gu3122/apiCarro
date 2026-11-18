from app.core.database import Database
from app.models.visitas import Visitas

class VisitasRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM visitas ORDER BY id_visita ASC;")
        visitas = cursor.fetchall()
        conn.close()
        return visitas

    def obtener_por_id(self, id_visita: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.*, ve.placa, ve.marca, ve.modelo, ve.color
            FROM visitas v LEFT JOIN vehiculos ve ON ve.id_vehiculo = v.id_vehiculo
            WHERE v.id_visita = %s
        """, (id_visita,))
        visita = cursor.fetchone()
        conn.close()
        return visita

    def crear(self, visita: Visitas):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO visitas (fecha_entrada,fecha_salida,estado,id_vehiculo) 
            VALUES (%s, %s, %s, %s) RETURNING id_visita;
        """
        cursor.execute(query, (visita.fecha_entrada, visita.fecha_salida, visita.estado, visita.id_vehiculo))
        nueva_visita = cursor.fetchone()['id_visita']
        conn.commit()
        conn.close()
        return nueva_visita

    def eliminar(self, id_visita: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM visitas WHERE id_visita = %s RETURNING id_visita;", (id_visita,))
        visita_eliminada = cursor.fetchone()
        conn.commit()
        conn.close()
        return visita_eliminada is not None

    def actualizar(self, id_visita: int, visita: Visitas):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE visitas
            SET fecha_entrada = %s, fecha_salida = %s, estado = %s, id_vehiculo = %s
            WHERE id_visita = %s
            RETURNING id_visita;
        """
        cursor.execute(query, (visita.fecha_entrada, visita.fecha_salida, visita.estado, visita.id_vehiculo, id_visita))
        visita_actualizada = cursor.fetchone()
        conn.commit()
        conn.close()
        return visita_actualizada is not None
    def obtener_catalogos(self):
        conn = self.db.get_connection()
        if conn is None:
            raise RuntimeError("Base de datos no disponible")
        try:
            resultado = {}
            with conn.cursor() as cursor:
                cursor.execute('SELECT id_vehiculo, placa, marca, modelo, color FROM vehiculos ORDER BY placa, id_vehiculo')
                resultado['vehiculos'] = cursor.fetchall()
            return resultado
        finally:
            conn.close()
