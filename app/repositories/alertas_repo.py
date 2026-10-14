from app.core.database import Database
from app.models.alertas import Alertas

class AlertasRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alertas ORDER BY id_alerta ASC;")
        alertas = cursor.fetchall()
        conn.close()
        return alertas

    def obtener_por_id(self, id_alerta: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alertas WHERE id_alerta = %s;", (id_alerta,))
        alerta = cursor.fetchone()
        conn.close()
        return alerta

    def crear(self, alerta: Alertas):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO alertas (tipo_alerta,mensaje,fecha_deteccion,estado,estado_resolucion,fecha_resolucion,creado,actualizado,id_usuario_resuelve,id_visita,id_zona) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_alerta;
        """
        cursor.execute(query, (alerta.tipo_alerta, alerta.mensaje, alerta.fecha_deteccion, alerta.estado, alerta.estado_resolucion, alerta.fecha_resolucion, alerta.creado, alerta.actualizado, alerta.id_usuario_resuelve, alerta.id_visita, alerta.id_zona))
        nueva_alerta = cursor.fetchone()['id_alerta']
        conn.commit()
        conn.close()
        return nueva_alerta

    def eliminar(self, id_alerta: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alertas WHERE id_alerta = %s RETURNING id_alerta;", (id_alerta,))
        alerta_eliminada = cursor.fetchone()
        conn.commit()
        conn.close()
        return alerta_eliminada is not None

    def actualizar(self, id_alerta: int, alerta: Alertas):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE alertas
            SET tipo_alerta = %s, mensaje = %s, fecha_deteccion = %s, estado = %s, estado_resolucion = %s, fecha_resolucion = %s, creado = %s, actualizado = %s, id_usuario_resuelve = %s, id_visita = %s, id_zona = %s
            WHERE id_alerta = %s
            RETURNING id_alerta;
        """
        cursor.execute(query, (alerta.tipo_alerta, alerta.mensaje, alerta.fecha_deteccion, alerta.estado, alerta.estado_resolucion, alerta.fecha_resolucion, alerta.creado, alerta.actualizado, alerta.id_usuario_resuelve, alerta.id_visita, alerta.id_zona, id_alerta))
        alerta_actualizada = cursor.fetchone()
        conn.commit()
        conn.close()
        return alerta_actualizada is not None