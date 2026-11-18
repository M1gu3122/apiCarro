from app.core.database import Database
from app.models.eventos_vehiculo import EventoVehiculo

class Eventos_vehiculoRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM eventos_vehiculo ORDER BY id_evento ASC;")
        eventos = cursor.fetchall()
        conn.close()
        return eventos

    def obtener_por_id(self, id_evento: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM eventos_vehiculo WHERE id_evento = %s;", (id_evento,))
        evento = cursor.fetchone()
        conn.close()
        return evento

    def crear(self, evento: EventoVehiculo):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO eventos_vehiculo (tipo_evento,fecha_hora,confianza,estado,id_visita,id_camara,id_seguimiento,id_zona) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_evento;
        """
        cursor.execute(query, (evento.tipo_evento, evento.fecha_hora, evento.confianza, evento.estado, evento.id_visita, evento.id_camara, evento.id_seguimiento, evento.id_zona))
        nuevo_evento = cursor.fetchone()['id_evento']
        conn.commit()
        conn.close()
        return nuevo_evento

    def eliminar(self, id_evento: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM eventos_vehiculo WHERE id_evento = %s RETURNING id_evento;", (id_evento,))
        evento_eliminado = cursor.fetchone()
        conn.commit()
        conn.close()
        return evento_eliminado is not None

    def actualizar(self, id_evento: int, evento: EventoVehiculo):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE eventos_vehiculo
            SET tipo_evento = %s, fecha_hora = %s, confianza = %s, estado = %s, id_visita = %s, id_camara = %s, id_seguimiento = %s, id_zona = %s
            WHERE id_evento = %s
            RETURNING id_evento;
        """
        cursor.execute(query, (evento.tipo_evento, evento.fecha_hora, evento.confianza, evento.estado, evento.id_visita, evento.id_camara, evento.id_seguimiento, evento.id_zona, id_evento))
        evento_actualizado = cursor.fetchone()
        conn.commit()
        conn.close()
        return evento_actualizado is not None
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
                cursor.execute('SELECT id_seguimiento, id_tracking FROM seguimientos ORDER BY id_seguimiento')
                resultado['seguimientos'] = cursor.fetchall()
            return resultado
        finally:
            conn.close()
