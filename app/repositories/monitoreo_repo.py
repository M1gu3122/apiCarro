from app.core.database import Database


class MonitoreoRepository:
    def __init__(self):
        self.db = Database()

    def obtener_monitoreo(self, busqueda="", estado="dentro", id_zona=None, permanencia="todas", umbral_minutos=None,
                          inicio=0, limite=10, ordenar="fecha_entrada", direccion="desc"):
        columnas = {"id_visita": "id_visita", "placa": "placa", "fecha_entrada": "fecha_entrada",
                    "duracion_minutos": "duracion_minutos", "zona": "zona", "camara": "camara"}
        if ordenar not in columnas or direccion not in ("asc", "desc"):
            raise ValueError("Orden no válido")
        if permanencia == "excede" and umbral_minutos is None:
            raise ValueError("Indique el umbral de permanencia en minutos")
        parametros = {"busqueda": "%" + busqueda.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%",
                      "estado": estado, "zona": id_zona, "permanencia": permanencia, "umbral": umbral_minutos, "inicio": inicio, "limite": limite}
        base = """
            WITH detalle AS (
                SELECT v.id_visita, v.fecha_entrada, v.fecha_salida, v.estado, v.id_vehiculo,
                       ve.placa, ve.marca, ve.modelo, ve.color, ev.id_evento, ev.fecha_hora AS ultimo_evento,
                       ev.tipo_evento, ev.confianza, ev.id_zona, ev.id_camara, z.nombre AS zona, c.nombre AS camara,
                       GREATEST(EXTRACT(EPOCH FROM (COALESCE(v.fecha_salida, CURRENT_TIMESTAMP) - v.fecha_entrada)) / 60, 0) AS duracion_minutos,
                       (SELECT COUNT(*) FROM alertas a WHERE a.id_visita = v.id_visita AND a.estado IS TRUE
                        AND LOWER(a.estado_resolucion) IN ('pendiente','en_proceso')) AS alertas_abiertas
                FROM visitas v LEFT JOIN vehiculos ve ON ve.id_vehiculo = v.id_vehiculo
                LEFT JOIN LATERAL (
                    SELECT e.id_evento, e.fecha_hora, e.tipo_evento, e.confianza, e.id_zona, e.id_camara
                    FROM eventos_vehiculo e WHERE e.id_visita = v.id_visita AND e.estado IS TRUE
                    AND (e.fecha_hora IS NULL OR e.fecha_hora <= CURRENT_TIMESTAMP)
                    ORDER BY e.fecha_hora DESC NULLS LAST, e.id_evento DESC LIMIT 1
                ) ev ON TRUE LEFT JOIN zonas z ON z.id_zona = ev.id_zona LEFT JOIN camaras c ON c.id_camara = ev.id_camara
            ), filtradas AS (
                SELECT * FROM detalle WHERE
                  (%(estado)s = 'todas' OR (%(estado)s = 'dentro' AND fecha_salida IS NULL AND estado IS TRUE AND fecha_entrada <= CURRENT_TIMESTAMP)
                   OR (%(estado)s = 'finalizadas' AND fecha_salida IS NOT NULL)
                   OR (%(estado)s = 'sin_identificar' AND (id_vehiculo IS NULL OR NULLIF(TRIM(placa), '') IS NULL)))
                  AND (%(zona)s::integer IS NULL OR id_zona = %(zona)s)
                  AND (%(permanencia)s = 'todas' OR (%(permanencia)s = 'abiertas' AND fecha_salida IS NULL)
                       OR (%(permanencia)s = 'excede' AND duracion_minutos >= %(umbral)s))
                  AND CONCAT_WS(' ', placa, marca, modelo, id_visita::text) ILIKE %(busqueda)s
            )
        """
        conexion = self.db.get_connection()
        if conexion is None:
            raise RuntimeError("Base de datos no disponible")
        try:
            conexion.set_session(readonly=True, isolation_level="REPEATABLE READ")
            with conexion.cursor() as cursor:
                cursor.execute(base + """
                    SELECT CURRENT_TIMESTAMP AS generado_en, (SELECT COUNT(*) FROM detalle) AS total,
                           (SELECT COUNT(*) FROM filtradas) AS total_filtrado,
                           (SELECT COUNT(*) FROM filtradas WHERE NULLIF(TRIM(placa),'') IS NOT NULL) AS identificadas,
                           COUNT(*) FILTER (WHERE fecha_salida IS NULL AND estado IS TRUE AND fecha_entrada <= CURRENT_TIMESTAMP) AS dentro,
                           AVG(duracion_minutos) FILTER (WHERE fecha_salida IS NULL AND estado IS TRUE AND fecha_entrada <= CURRENT_TIMESTAMP) AS permanencia_media,
                           CASE WHEN %(umbral)s::integer IS NULL THEN NULL ELSE COUNT(*) FILTER
                             (WHERE fecha_salida IS NULL AND estado IS TRUE AND fecha_entrada <= CURRENT_TIMESTAMP AND duracion_minutos >= %(umbral)s) END AS sobre_umbral,
                           COUNT(*) FILTER (WHERE fecha_salida IS NULL AND estado IS TRUE AND fecha_entrada <= CURRENT_TIMESTAMP
                                            AND (id_vehiculo IS NULL OR NULLIF(TRIM(placa),'') IS NULL)) AS sin_identificacion
                    FROM detalle
                """, parametros)
                resumen = dict(cursor.fetchone())
                cursor.execute(base + "SELECT * FROM filtradas ORDER BY " + columnas[ordenar] + " " + direccion +
                               " NULLS LAST, id_visita ASC LIMIT %(limite)s OFFSET %(inicio)s", parametros)
                registros = [dict(fila) for fila in cursor.fetchall()]
                cursor.execute("SELECT id_zona, nombre FROM zonas ORDER BY nombre, id_zona")
                zonas = [dict(fila) for fila in cursor.fetchall()]
                return {"resumen": resumen, "registros": registros, "zonas": zonas, "umbral_minutos": umbral_minutos}
        finally:
            conexion.close()
