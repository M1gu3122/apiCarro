from app.core.database import Database
from app.models.seguimientos import Seguimientos

class SeguimientosRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM seguimientos ORDER BY id_seguimiento ASC;")
        seguimientos = cursor.fetchall()
        conn.close()
        return seguimientos

    def obtener_por_id(self, id_seguimiento: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM seguimientos WHERE id_seguimiento = %s;", (id_seguimiento,))
        seguimiento = cursor.fetchone()
        conn.close()
        return seguimiento

    def crear(self, seguimiento: Seguimientos):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO seguimientos (id_tracking,inicio,fin,confianza_promedio,estado,id_visita,id_camara) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_seguimiento;
        """
        cursor.execute(query, (seguimiento.id_tracking, seguimiento.inicio, seguimiento.fin, seguimiento.confianza_promedio, seguimiento.estado, seguimiento.id_visita, seguimiento.id_camara))
        nuevo_seguimiento = cursor.fetchone()['id_seguimiento']
        conn.commit()
        conn.close()
        return nuevo_seguimiento

    def eliminar(self, id_seguimiento: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM seguimientos WHERE id_seguimiento = %s RETURNING id_seguimiento;", (id_seguimiento,))
        seguimiento_eliminado = cursor.fetchone()
        conn.commit()
        conn.close()
        return seguimiento_eliminado is not None

    def actualizar(self, id_seguimiento: int, seguimiento: Seguimientos):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE seguimientos
            SET id_tracking = %s, fin = %s, confianza_promedio = %s, estado = %s, id_visita = %s, id_camara = %s
            WHERE id_seguimiento = %s
            RETURNING id_seguimiento;
        """
        cursor.execute(query, (seguimiento.id_tracking, seguimiento.fin, seguimiento.confianza_promedio, seguimiento.estado, seguimiento.id_visita, seguimiento.id_camara, id_seguimiento))
        seguimiento_actualizado = cursor.fetchone()
        conn.commit()
        conn.close()
        return seguimiento_actualizado is not None
    def obtener_catalogos(self):
        conn = self.db.get_connection()
        if conn is None:
            raise RuntimeError("Base de datos no disponible")
        try:
            resultado = {}
            with conn.cursor() as cursor:
                cursor.execute('SELECT id_visita, id_vehiculo FROM visitas ORDER BY id_visita')
                resultado['visitas'] = cursor.fetchall()
                cursor.execute('SELECT id_vehiculo, placa FROM vehiculos ORDER BY id_vehiculo')
                resultado['vehiculos'] = cursor.fetchall()
                cursor.execute('SELECT id_camara, nombre, id_zona FROM camaras ORDER BY id_camara')
                resultado['camaras'] = cursor.fetchall()
                cursor.execute('SELECT id_zona, nombre FROM zonas ORDER BY id_zona')
                resultado['zonas'] = cursor.fetchall()
            return resultado
        finally:
            conn.close()
