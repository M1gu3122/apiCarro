from app.core.database import Database
from app.models.asociaciones_seguimiento import Asociaciones_seguimiento

class Asociaciones_seguimientoRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM asociaciones_seguimiento ORDER BY id_asociacion ASC;")
        asociaciones = cursor.fetchall()
        conn.close()
        return asociaciones

    def obtener_por_id(self, id_asociacion: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM asociaciones_seguimiento WHERE id_asociacion = %s;", (id_asociacion,))
        asociacion = cursor.fetchone()
        conn.close()
        return asociacion

    def crear(self, asociacion_seguimiento: Asociaciones_seguimiento):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO asociaciones_seguimiento (metodo,confianza,resultado,fecha_evaluacion,estado,creado,actualizado,id_seguimiento_origen,id_seguimiento_destino) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_asociacion;
        """
        cursor.execute(query, (asociacion_seguimiento.metodo, asociacion_seguimiento.confianza, asociacion_seguimiento.resultado, asociacion_seguimiento.fecha_evaluacion, asociacion_seguimiento.estado, asociacion_seguimiento.creado, asociacion_seguimiento.actualizado, asociacion_seguimiento.id_seguimiento_origen, asociacion_seguimiento.id_seguimiento_destino))
        nueva_asociacion = cursor.fetchone()['id_asociacion']
        conn.commit()
        conn.close()
        return nueva_asociacion

    def eliminar(self, id_asociacion: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM asociaciones_seguimiento WHERE id_asociacion = %s RETURNING id_asociacion;", (id_asociacion,))
        asociacion_eliminada = cursor.fetchone()
        conn.commit()
        conn.close()
        return asociacion_eliminada is not None

    def actualizar(self, id_asociacion: int, asociacion_seguimiento: Asociaciones_seguimiento):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE asociaciones_seguimiento
            SET metodo = %s, confianza = %s, resultado = %s, fecha_evaluacion = %s, estado = %s, creado = %s, actualizado = %s, id_seguimiento_origen = %s, id_seguimiento_destino = %s
            WHERE id_asociacion = %s
            RETURNING id_asociacion;
        """
        cursor.execute(query, (asociacion_seguimiento.metodo, asociacion_seguimiento.confianza, asociacion_seguimiento.resultado, asociacion_seguimiento.fecha_evaluacion, asociacion_seguimiento.estado, asociacion_seguimiento.creado, asociacion_seguimiento.actualizado, asociacion_seguimiento.id_seguimiento_origen, asociacion_seguimiento.id_seguimiento_destino, id_asociacion))
        asociacion_actualizada = cursor.fetchone()
        conn.commit()
        conn.close()
        return asociacion_actualizada is not None