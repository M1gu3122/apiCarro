from app.core.database import Database


class ReportesRepository:
    def __init__(self):
        self.db = Database()

    def obtener_reporte(self, desde=None, hasta=None, id_zona=None, zona_horaria="America/Bogota"):
        conexion = self.db.get_connection()
        if conexion is None:
            raise RuntimeError("Base de datos no disponible")
        parametros = {"desde": desde, "hasta": hasta, "zona": id_zona, "tz": zona_horaria}
        base = """
            WITH limites AS (
                SELECT %(desde)s::date::timestamp AT TIME ZONE %(tz)s AS inicio,
                       (%(hasta)s::date + 1)::timestamp AT TIME ZONE %(tz)s AS fin
            ), eventos_periodo AS (
                SELECT e.* FROM eventos_vehiculo e CROSS JOIN limites l
                WHERE e.fecha_hora >= l.inicio AND e.fecha_hora < l.fin AND (%(zona)s::integer IS NULL OR e.id_zona = %(zona)s)
            ), alertas_periodo AS (
                SELECT a.* FROM alertas a CROSS JOIN limites l
                WHERE a.fecha_deteccion >= l.inicio AND a.fecha_deteccion < l.fin AND (%(zona)s::integer IS NULL OR a.id_zona = %(zona)s)
            ), visitas_zona AS (
                SELECT v.* FROM visitas v WHERE %(zona)s::integer IS NULL
                   OR EXISTS(SELECT 1 FROM eventos_periodo e WHERE e.id_visita = v.id_visita)
            ), visitas_periodo AS (
                SELECT v.* FROM visitas_zona v CROSS JOIN limites l WHERE v.fecha_entrada >= l.inicio AND v.fecha_entrada < l.fin
            )
        """
        try:
            conexion.set_session(readonly=True, isolation_level="REPEATABLE READ")
            with conexion.cursor() as cursor:
                cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_timezone_names WHERE name = %s) AS valida", (zona_horaria,))
                if not cursor.fetchone()["valida"]:
                    raise ValueError("Zona horaria no válida")
                cursor.execute("""
                    SELECT COALESCE(%(desde)s::date, (CURRENT_TIMESTAMP AT TIME ZONE %(tz)s)::date - 29) AS desde,
                           COALESCE(%(hasta)s::date, (CURRENT_TIMESTAMP AT TIME ZONE %(tz)s)::date) AS hasta, CURRENT_TIMESTAMP AS generado_en
                """, parametros)
                periodo = dict(cursor.fetchone())
                if periodo["desde"] > periodo["hasta"]:
                    raise ValueError("La fecha inicial no puede ser posterior a la final")
                if (periodo["hasta"] - periodo["desde"]).days > 365:
                    raise ValueError("Seleccione un rango máximo de 366 días")
                parametros.update(desde=periodo["desde"], hasta=periodo["hasta"])
                cursor.execute(base + """
                    SELECT (SELECT COUNT(*) FROM visitas_periodo) AS visitas,
                           (SELECT COUNT(*) FROM visitas_periodo WHERE fecha_salida IS NULL) AS visitas_abiertas,
                           (SELECT AVG(EXTRACT(EPOCH FROM (fecha_salida - fecha_entrada))/60) FROM visitas_periodo WHERE fecha_salida >= fecha_entrada) AS duracion_media,
                           (SELECT COUNT(*) FROM eventos_periodo) AS eventos,
                           (SELECT COUNT(DISTINCT tipo_evento) FROM eventos_periodo) AS tipos_evento,
                           (SELECT COUNT(*) FROM alertas_periodo) AS alertas,
                           (SELECT COUNT(*) FROM alertas_periodo WHERE estado IS TRUE AND LOWER(estado_resolucion) IN ('pendiente','en_proceso')) AS alertas_abiertas
                """, parametros)
                resumen = dict(cursor.fetchone())
                cursor.execute(base + """
                    , entradas AS (SELECT (fecha_entrada AT TIME ZONE %(tz)s)::date AS fecha, COUNT(*) AS cantidad FROM visitas_periodo GROUP BY 1),
                    salidas AS (SELECT (fecha_salida AT TIME ZONE %(tz)s)::date AS fecha, COUNT(*) AS cantidad FROM visitas_zona CROSS JOIN limites l
                               WHERE fecha_salida >= l.inicio AND fecha_salida < l.fin GROUP BY 1)
                    SELECT dia::date AS fecha, COALESCE(e.cantidad, 0) AS entradas, COALESCE(s.cantidad, 0) AS salidas
                    FROM generate_series(%(desde)s::date::timestamp, %(hasta)s::date::timestamp, INTERVAL '1 day') dia
                    LEFT JOIN entradas e ON e.fecha = dia::date LEFT JOIN salidas s ON s.fecha = dia::date ORDER BY dia
                """, parametros)
                movimientos = [dict(fila) for fila in cursor.fetchall()]
                cursor.execute(base + """
                    , entradas AS (SELECT EXTRACT(HOUR FROM fecha_entrada AT TIME ZONE %(tz)s)::int AS hora, COUNT(*) AS cantidad FROM visitas_periodo GROUP BY 1),
                    salidas AS (SELECT EXTRACT(HOUR FROM fecha_salida AT TIME ZONE %(tz)s)::int AS hora, COUNT(*) AS cantidad FROM visitas_zona CROSS JOIN limites l
                               WHERE fecha_salida >= l.inicio AND fecha_salida < l.fin GROUP BY 1)
                    SELECT h.hora, COALESCE(e.cantidad, 0) AS entradas, COALESCE(s.cantidad, 0) AS salidas
                    FROM generate_series(0,23) h(hora) LEFT JOIN entradas e ON e.hora = h.hora LEFT JOIN salidas s ON s.hora = h.hora ORDER BY h.hora
                """, parametros)
                horas = [dict(fila) for fila in cursor.fetchall()]
                cursor.execute(base + "SELECT tipo_evento, COUNT(*) AS cantidad FROM eventos_periodo GROUP BY tipo_evento ORDER BY cantidad DESC, tipo_evento", parametros)
                tipos = [dict(fila) for fila in cursor.fetchall()]
                cursor.execute(base + """
                    , eventos_zona AS (SELECT id_zona, COUNT(*) AS eventos, COUNT(DISTINCT id_visita) AS visitas_unicas FROM eventos_periodo GROUP BY id_zona),
                    alertas_zona AS (SELECT id_zona, COUNT(*) AS alertas, COUNT(*) FILTER(WHERE estado IS TRUE AND LOWER(estado_resolucion) IN ('pendiente','en_proceso')) AS abiertas FROM alertas_periodo GROUP BY id_zona)
                    SELECT z.id_zona, z.nombre, z.capacidad_maxima, COALESCE(e.eventos,0) AS eventos, COALESCE(e.visitas_unicas,0) AS visitas_unicas,
                           COALESCE(a.alertas,0) AS alertas, COALESCE(a.abiertas,0) AS alertas_abiertas,
                           o.promedio AS ocupacion_promedio, o.maxima AS ocupacion_maxima, o.mediciones,
                           ultima.cantidad_vehiculos AS ultima_ocupacion, ultima.fecha_hora AS ultima_medicion
                    FROM zonas z CROSS JOIN limites l
                    LEFT JOIN eventos_zona e ON e.id_zona = z.id_zona LEFT JOIN alertas_zona a ON a.id_zona = z.id_zona
                    LEFT JOIN LATERAL (SELECT AVG(cantidad_vehiculos) AS promedio, MAX(cantidad_vehiculos) AS maxima, COUNT(*) AS mediciones
                                       FROM ocupacion_zona WHERE id_zona = z.id_zona AND estado IS TRUE AND fecha_hora >= l.inicio AND fecha_hora < l.fin) o ON TRUE
                    LEFT JOIN LATERAL (SELECT cantidad_vehiculos, fecha_hora FROM ocupacion_zona WHERE id_zona = z.id_zona AND estado IS TRUE AND fecha_hora < l.fin
                                       ORDER BY fecha_hora DESC, id_ocupacion DESC LIMIT 1) ultima ON TRUE
                    WHERE %(zona)s::integer IS NULL OR z.id_zona = %(zona)s ORDER BY z.nombre, z.id_zona
                """, parametros)
                zonas = [dict(fila) for fila in cursor.fetchall()]
                cursor.execute("SELECT id_zona, nombre FROM zonas ORDER BY nombre, id_zona")
                catalogo = [dict(fila) for fila in cursor.fetchall()]
                return {"periodo": periodo, "resumen": resumen, "movimientos_dia": movimientos, "movimientos_hora": horas,
                        "tipos_evento": tipos, "resumen_zonas": zonas, "zonas_disponibles": catalogo, "zona_horaria": zona_horaria, "id_zona": id_zona}
        finally:
            conexion.close()
