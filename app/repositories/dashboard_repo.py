from app.core.database import Database


class DashboardRepository:
    def __init__(self):
        self.db = Database()

    def obtener_resumen(self, zona_horaria, umbral_minutos=None):
        conexion = self.db.get_connection()
        if conexion is None:
            raise RuntimeError("Base de datos no disponible")
        parametros = {"tz": zona_horaria, "umbral": umbral_minutos}
        try:
            conexion.set_session(readonly=True, isolation_level="REPEATABLE READ")
            with conexion.cursor() as cursor:
                cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_timezone_names WHERE name = %s) AS valida", (zona_horaria,))
                if not cursor.fetchone()["valida"]:
                    raise ValueError("Zona horaria no válida")
                cursor.execute("""
                    SELECT CURRENT_TIMESTAMP AS generado_en,
                           (CURRENT_TIMESTAMP AT TIME ZONE %(tz)s)::date AS fecha,
                           (SELECT COUNT(*) FROM visitas WHERE estado IS TRUE AND fecha_salida IS NULL AND fecha_entrada <= CURRENT_TIMESTAMP) AS vehiculos_dentro,
                           (SELECT COUNT(*) FROM visitas WHERE (fecha_entrada AT TIME ZONE %(tz)s)::date = (CURRENT_TIMESTAMP AT TIME ZONE %(tz)s)::date) AS entradas_hoy,
                           (SELECT COUNT(*) FROM visitas WHERE (fecha_salida AT TIME ZONE %(tz)s)::date = (CURRENT_TIMESTAMP AT TIME ZONE %(tz)s)::date) AS salidas_hoy,
                           (SELECT COUNT(*) FROM alertas WHERE estado IS TRUE AND LOWER(estado_resolucion) IN ('pendiente', 'en_proceso')) AS alertas_pendientes,
                           CASE WHEN %(umbral)s::integer IS NULL THEN NULL ELSE
                               (SELECT COUNT(*) FROM visitas WHERE estado IS TRUE AND fecha_salida IS NULL AND fecha_entrada <= CURRENT_TIMESTAMP
                                AND EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - fecha_entrada)) / 60 >= %(umbral)s) END AS permanencia_prolongada,
                           (SELECT COUNT(*) FROM camaras WHERE estado IS TRUE) AS camaras_activas,
                           (SELECT COUNT(*) FROM camaras WHERE estado IS FALSE) AS camaras_inactivas,
                           (SELECT COUNT(*) FROM camaras) AS camaras_total,
                           (SELECT COUNT(*) FROM visitas) AS visitas_total
                """, parametros)
                resumen = dict(cursor.fetchone())
                cursor.execute("""
                    WITH horas AS (SELECT generate_series(0, 23) AS hora),
                    entradas AS (
                        SELECT EXTRACT(HOUR FROM fecha_entrada AT TIME ZONE %(tz)s)::int AS hora, COUNT(*) AS cantidad
                        FROM visitas WHERE (fecha_entrada AT TIME ZONE %(tz)s)::date = (CURRENT_TIMESTAMP AT TIME ZONE %(tz)s)::date GROUP BY 1
                    ), salidas AS (
                        SELECT EXTRACT(HOUR FROM fecha_salida AT TIME ZONE %(tz)s)::int AS hora, COUNT(*) AS cantidad
                        FROM visitas WHERE (fecha_salida AT TIME ZONE %(tz)s)::date = (CURRENT_TIMESTAMP AT TIME ZONE %(tz)s)::date GROUP BY 1
                    )
                    SELECT h.hora, COALESCE(e.cantidad, 0) AS entradas, COALESCE(s.cantidad, 0) AS salidas,
                           CASE WHEN h.hora > EXTRACT(HOUR FROM CURRENT_TIMESTAMP AT TIME ZONE %(tz)s) THEN NULL ELSE
                           (SELECT COUNT(*) FROM visitas v
                            WHERE v.fecha_entrada <= LEAST(CURRENT_TIMESTAMP, (((CURRENT_TIMESTAMP AT TIME ZONE %(tz)s)::date + (h.hora + 1) * INTERVAL '1 hour') AT TIME ZONE %(tz)s))
                            AND (v.fecha_salida IS NULL OR v.fecha_salida > LEAST(CURRENT_TIMESTAMP, (((CURRENT_TIMESTAMP AT TIME ZONE %(tz)s)::date + (h.hora + 1) * INTERVAL '1 hour') AT TIME ZONE %(tz)s)))) END AS dentro
                    FROM horas h LEFT JOIN entradas e ON e.hora = h.hora LEFT JOIN salidas s ON s.hora = h.hora ORDER BY h.hora
                """, parametros)
                movimientos = [dict(fila) for fila in cursor.fetchall()]
                cursor.execute("""
                    SELECT z.id_zona, z.nombre, z.capacidad_maxima, o.cantidad_vehiculos, o.fecha_hora AS fecha_medicion,
                           CASE WHEN z.capacidad_maxima > 0 THEN ROUND(o.cantidad_vehiculos * 100.0 / z.capacidad_maxima, 1) END AS porcentaje
                    FROM zonas z LEFT JOIN LATERAL (
                        SELECT cantidad_vehiculos, fecha_hora FROM ocupacion_zona
                        WHERE id_zona = z.id_zona AND estado IS TRUE AND fecha_hora <= CURRENT_TIMESTAMP
                        ORDER BY fecha_hora DESC, id_ocupacion DESC LIMIT 1
                    ) o ON TRUE WHERE z.estado IS TRUE ORDER BY z.nombre, z.id_zona
                """)
                zonas = [dict(fila) for fila in cursor.fetchall()]
                cursor.execute("""
                    SELECT COUNT(*) AS cantidad FROM zonas z INNER JOIN LATERAL (
                        SELECT cantidad_vehiculos FROM ocupacion_zona WHERE id_zona = z.id_zona AND estado IS TRUE AND fecha_hora <= CURRENT_TIMESTAMP
                        ORDER BY fecha_hora DESC, id_ocupacion DESC LIMIT 1
                    ) o ON o.cantidad_vehiculos > 0 WHERE z.estado IS TRUE
                """)
                resumen["zonas_ocupadas"] = cursor.fetchone()["cantidad"]
                cursor.execute("""
                    SELECT e.id_evento, e.tipo_evento, e.fecha_hora, e.confianza, e.id_visita,
                           c.nombre AS camara, z.nombre AS zona, v.placa
                    FROM eventos_vehiculo e LEFT JOIN camaras c ON c.id_camara = e.id_camara
                    LEFT JOIN zonas z ON z.id_zona = e.id_zona LEFT JOIN visitas vi ON vi.id_visita = e.id_visita
                    LEFT JOIN vehiculos v ON v.id_vehiculo = vi.id_vehiculo
                    ORDER BY e.fecha_hora DESC NULLS LAST, e.id_evento DESC LIMIT 10
                """)
                eventos = [dict(fila) for fila in cursor.fetchall()]
                cursor.execute("""
                    SELECT a.id_alerta, a.tipo_alerta, a.mensaje, a.fecha_deteccion, a.estado_resolucion,
                           a.id_visita, z.nombre AS zona, v.placa
                    FROM alertas a LEFT JOIN zonas z ON z.id_zona = a.id_zona
                    LEFT JOIN visitas vi ON vi.id_visita = a.id_visita LEFT JOIN vehiculos v ON v.id_vehiculo = vi.id_vehiculo
                    WHERE a.estado IS TRUE AND LOWER(a.estado_resolucion) IN ('pendiente', 'en_proceso')
                    ORDER BY a.fecha_deteccion DESC NULLS LAST, a.id_alerta DESC LIMIT 10
                """)
                alertas = [dict(fila) for fila in cursor.fetchall()]
                return {"resumen": resumen, "movimientos_hora": movimientos, "ocupacion_zonas": zonas,
                        "ultimos_eventos": eventos, "alertas_abiertas": alertas, "umbral_minutos": umbral_minutos, "zona_horaria": zona_horaria}
        finally:
            conexion.close()
