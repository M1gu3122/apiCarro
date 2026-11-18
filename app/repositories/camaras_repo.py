from app.core.database import Database
from app.models.camaras import Camaras

class CamarasRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        if conn is None:
            raise RuntimeError("Base de datos no disponible")
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.*, COALESCE(resumen.eventos_registrados, 0) AS eventos_registrados,
                           COALESCE(resumen.eventos_hoy, 0) AS eventos_hoy,
                           ultimo.tipo_evento AS ultimo_tipo_evento, ultimo.fecha_hora AS ultimo_evento
                    FROM camaras c
                    LEFT JOIN (
                        SELECT id_camara, COUNT(*) AS eventos_registrados,
                               COUNT(*) FILTER (WHERE (fecha_hora AT TIME ZONE 'America/Bogota')::date =
                                   (CURRENT_TIMESTAMP AT TIME ZONE 'America/Bogota')::date) AS eventos_hoy
                        FROM eventos_vehiculo WHERE estado IS TRUE
                          AND (fecha_hora IS NULL OR fecha_hora <= CURRENT_TIMESTAMP)
                        GROUP BY id_camara
                    ) resumen ON resumen.id_camara = c.id_camara
                    LEFT JOIN LATERAL (
                        SELECT tipo_evento, fecha_hora FROM eventos_vehiculo
                        WHERE id_camara = c.id_camara AND estado IS TRUE
                          AND (fecha_hora IS NULL OR fecha_hora <= CURRENT_TIMESTAMP)
                        ORDER BY fecha_hora DESC NULLS LAST, id_evento DESC LIMIT 1
                    ) ultimo ON TRUE
                    ORDER BY c.id_camara ASC
                """)
                return cursor.fetchall()
        finally:
            conn.close()

    def obtener_actividad(self, id_camara: int, inicio: int = 0, limite: int = 10):
        conn = self.db.get_connection()
        if conn is None:
            raise RuntimeError("Base de datos no disponible")
        try:
            conn.set_session(readonly=True, isolation_level="REPEATABLE READ")
            with conn.cursor() as cursor:
                cursor.execute('SELECT id_camara, nombre FROM camaras WHERE id_camara = %s', (id_camara,))
                camara = cursor.fetchone()
                if camara is None:
                    return None
                cursor.execute("""
                    SELECT COUNT(*) AS total FROM eventos_vehiculo
                    WHERE id_camara = %s AND estado IS TRUE
                      AND (fecha_hora IS NULL OR fecha_hora <= CURRENT_TIMESTAMP)
                """, (id_camara,))
                total = cursor.fetchone()['total']
                cursor.execute("""
                    SELECT e.id_evento, e.tipo_evento, e.fecha_hora, e.id_visita, e.confianza,
                           z.nombre AS zona, ve.placa
                    FROM eventos_vehiculo e
                    LEFT JOIN zonas z ON z.id_zona = e.id_zona
                    LEFT JOIN visitas v ON v.id_visita = e.id_visita
                    LEFT JOIN vehiculos ve ON ve.id_vehiculo = v.id_vehiculo
                    WHERE e.id_camara = %s AND e.estado IS TRUE
                      AND (e.fecha_hora IS NULL OR e.fecha_hora <= CURRENT_TIMESTAMP)
                    ORDER BY e.fecha_hora DESC NULLS LAST, e.id_evento DESC
                    LIMIT %s OFFSET %s
                """, (id_camara, limite, inicio))
                return {'camara': camara, 'total': total, 'inicio': inicio, 'limite': limite, 'eventos': cursor.fetchall()}
        finally:
            conn.close()

    def obtener_por_id(self, id_camara: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM camaras WHERE id_camara = %s;", (id_camara,))
        camara = cursor.fetchone()
        conn.close()
        return camara

    def crear(self, camara: Camaras):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO camaras (nombre,ubicacion,fecha_registro,estado,id_zona) 
            VALUES (%s, %s, %s, %s, %s) RETURNING id_camara;
        """
        cursor.execute(query, (camara.nombre, camara.ubicacion, camara.fecha_registro, camara.estado, camara.id_zona))
        nueva_camara = cursor.fetchone()['id_camara']
        conn.commit()
        conn.close()
        return nueva_camara

    def eliminar(self, id_camara: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM camaras WHERE id_camara = %s RETURNING id_camara;", (id_camara,))
        camara_eliminada = cursor.fetchone()
        conn.commit()
        conn.close()
        return camara_eliminada is not None

    def actualizar(self, id_camara: int, camara: Camaras):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE camaras
            SET nombre = %s, ubicacion = %s, fecha_registro = %s, estado = %s, id_zona = %s
            WHERE id_camara = %s
            RETURNING id_camara;
        """
        cursor.execute(query, (camara.nombre, camara.ubicacion, camara.fecha_registro, camara.estado, camara.id_zona, id_camara))
        camara_actualizada = cursor.fetchone()
        conn.commit()
        conn.close()
        return camara_actualizada is not None
    def obtener_catalogos(self):
        conn = self.db.get_connection()
        if conn is None:
            raise RuntimeError("Base de datos no disponible")
        try:
            resultado = {}
            with conn.cursor() as cursor:
                cursor.execute('SELECT id_zona, nombre, tipo FROM zonas ORDER BY nombre, id_zona')
                resultado['zonas'] = cursor.fetchall()
            return resultado
        finally:
            conn.close()
