import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT"),
    cursor_factory=RealDictCursor
)

cur = conn.cursor()

# 13. ocupacion_zona - insertar 10 registros (tabla vacía)
print("Insertando ocupacion_zona...")
for i in range(1, 11):
    fecha_hora = '2024-01-01 10:00:00'
    cantidad_vehiculos = i * 2  # 2, 4, 6, ... 20
    id_zona = i
    cur.execute("INSERT INTO ocupacion_zona (fecha_hora, cantidad_vehiculos, id_zona) VALUES (%s, %s, %s) RETURNING id_ocupacion;", (fecha_hora, cantidad_vehiculos, id_zona))
    id_ocupacion = cur.fetchone()['id_ocupacion']
    print(f"Ocupacion {i} insertada: id_ocupacion={id_ocupacion}, cantidad={cantidad_vehiculos}")

conn.commit()

# 14. asociaciones_seguimiento - insertar 10 asociaciones (tabla vacía)
print("\nInsertando asociaciones_seguimiento...")
for i in range(1, 11):
    metodo = ['Color', 'Patrón', 'Combined', 'Color', 'Patrón', 'Combined', 'Color', 'Patrón', 'Combined', 'Color'][i-1]
    confianza = round(0.85 + (i * 0.01), 4)
    resultado = ['pendiente', 'aceptada', 'rechazada'][i % 3]
    id_seguimiento_origen = i
    id_seguimiento_destino = i + 1 if i < 10 else 1  # evitar que sean el mismo
    cur.execute("INSERT INTO asociaciones_seguimiento (metodo, confianza, resultado, id_seguimiento_origen, id_seguimiento_destino) VALUES (%s, %s, %s, %s, %s) RETURNING id_asociacion;", (metodo, confianza, resultado, id_seguimiento_origen, id_seguimiento_destino))
    id_asociacion = cur.fetchone()['id_asociacion']
    print(f"Asociacion {i} insertada: id_asociacion={id_asociacion}, origen={id_seguimiento_origen}, destino={id_seguimiento_destino}")

conn.commit()

# 12. alertas - insertar 10 alertas (tabla vacía, con constraint check)
print("\nInsertando alertas...")
for i in range(1, 11):
    tipo_alerta = ['Congestión', 'Tiempo exceedido', 'Zona prohibida', 'Falla sistema', 'Riesgo seguridad', 'Congestión', 'Tiempo exceedido', 'Zona prohibida', 'Falla sistema', 'Riesgo seguridad'][i-1]
    mensaje = f'Mensaje de alerta {i} para el concesionario'
    # El constraint ck_alertas_resolucion requiere:
    # - si estado_resolucion='resuelta', entonces fecha_resolucion NO puede ser NULL
    # - si estado_resolucion <>'resuelta', entonces fecha_resolucion debe ser NULL
    if i % 4 == 0:
        estado_resolucion = 'resuelta'
        fecha_resolucion = '2024-01-01 12:00:00'  # NOT NULL cuando es 'resuelta'
    else:
        estado_resolucion = ['pendiente', 'en_proceso', 'descartada'][i % 3]
        fecha_resolucion = None
    id_visita = i
    id_zona = i
    cur.execute("INSERT INTO alertas (tipo_alerta, mensaje, estado, estado_resolucion, fecha_resolucion, id_visita, id_zona) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_alerta;", (tipo_alerta, mensaje, True, estado_resolucion, fecha_resolucion, id_visita, id_zona))
    id_alerta = cur.fetchone()['id_alerta']
    print(f"Alerta {i} insertada: id_alerta={id_alerta}, tipo={tipo_alerta}, resolucion={estado_resolucion}")

conn.commit()

print("\n¡Registros insertados exitosamente en las tablas vacías!")
cur.close()
conn.close()