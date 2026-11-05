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
        cursor.execute("SELECT * FROM visitas WHERE id_visita = %s;", (id_visita,))
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