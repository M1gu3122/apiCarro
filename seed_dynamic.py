import psycopg2
from psycopg2.extras import RealDictCursor
import os
import random
from datetime import datetime, timedelta
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

# 1. Limpiar y reiniciar todas las tablas y secuencias
print("Limpiando base de datos...")
cur.execute('TRUNCATE TABLE asociaciones_seguimiento, ocupacion_zona, alertas, eventos_vehiculo, seguimientos, camaras, visitas, vehiculos, tipos_vehiculo, zonas, modulo_x_rol, modulo, usuarios, roles CASCADE;')

sequences = [
    'roles_id_rol_seq', 'usuarios_id_usuario_seq', 'modulo_id_modulo_seq',
    'tipos_vehiculo_id_tipo_seq', 'zonas_id_zona_seq', 'vehiculos_id_vehiculo_seq',
    'visitas_id_visita_seq', 'camaras_id_camara_seq', 'seguimientos_id_seguimiento_seq',
    'eventos_vehiculo_id_evento_seq', 'alertas_id_alerta_seq', 'ocupacion_zona_id_ocupacion_seq',
    'asociaciones_seguimiento_id_asociacion_seq'
]
for seq in sequences:
    cur.execute('ALTER SEQUENCE ' + seq + ' RESTART WITH 1;')

conn.commit()
print("Base de datos limpia y secuencias reiniciadas")

# 2. Insertar roles (5 roles únicos de una lista de 10)
print("Insertando roles...")
nombres_roles = ['Administrador', 'Operador']
for i in range(len(nombres_roles)):
    nombre = nombres_roles[i-1]  # Usar roles deterministas para evitar duplicados
    descripcion = 'Rol ' + nombre + ' para el concessionario'
    estado = random.choice([True, True])  # 2/3 probabilidad True
    cur.execute("INSERT INTO roles (nombre, descripcion, estado) VALUES (%s, %s, %s) RETURNING id_rol;", (nombre, descripcion, estado))
    id_rol = cur.fetchone()['id_rol']
    print("Rol " + str(i) + ": id_rol=" + str(id_rol) + ", nombre=" + nombre)

conn.commit()

# 3. Insertar modulos (8 modulos aleatorios)
print("\nInsertando modulos...")
modulo_names = ['Gestión', 'Ventas', 'Mantenimiento', 'Inventario', 'RRHH', 'Reportes', 'Configuración', 'Seguridad', 'Atención al cliente', 'Logística']
for i, nombre in enumerate(modulo_names[:8], 1):
    cur.execute("INSERT INTO modulo (nombre_modulo, estado) VALUES (%s, %s) RETURNING id_modulo;", (nombre, True))
    id_modulo = cur.fetchone()['id_modulo']
    print("Modulo " + str(i) + ": id_modulo=" + str(id_modulo) + ", nombre=" + nombre)

conn.commit()

# 3b. Insertar modulo_x_rol (relacionar roles y modulos)
print("\nInsertando modulo_x_rol...")
cur.execute("SELECT id_modulo FROM modulo")
modulos = [r['id_modulo'] for r in cur.fetchall()]
cur.execute("SELECT id_rol FROM roles")
roles_ids = [r['id_rol'] for r in cur.fetchall()]

for id_rol in roles_ids:
    num_modulos = random.randint(3, min(6, len(modulos)))
    modulos_asignados = random.sample(modulos, k=num_modulos)
    for id_modulo in modulos_asignados:
        estado = random.choice([True, True, False])
        cur.execute("INSERT INTO modulo_x_rol (id_rol, id_modulo, estado) VALUES (%s, %s, %s);", (id_rol, id_modulo, estado))
        print("  Relacion: id_rol=" + str(id_rol) + ", id_modulo=" + str(id_modulo))

conn.commit()

# 4. Insertar tipos_vehiculo (10 tipos)
print("\nInsertando tipos_vehiculo...")
tipos_nombres = ['Auto', 'Camioneta', 'Camión', 'Motocicleta', 'Bus', 'Furgoneta', 'Deportivo', 'SUV', 'Hatchback', 'Pickup']
for i, nombre in enumerate(tipos_nombres, 1):
    descripcion = 'Tipo de vehiculo: ' + nombre
    cur.execute("INSERT INTO tipos_vehiculo (nombre, descripcion, estado) VALUES (%s, %s, %s) RETURNING id_tipo;", (nombre, descripcion, True))
    id_tipo = cur.fetchone()['id_tipo']
    print("Tipo " + str(i) + ": id_tipo=" + str(id_tipo) + ", nombre=" + nombre)

conn.commit()

# 5. Insertar zonas (10 zonas aleatorias)
print("\nInsertando zonas...")
for i in range(1, 11):
    nombre = "Zona " + str(i)
    tipo = random.choice(['entrada', 'espera', 'mantenimiento', 'despacho', 'lavado', 'partes', 'administrativa', 'exterior'])
    capacidad = random.randint(1, 50)
    cur.execute("INSERT INTO zonas (nombre, tipo, capacidad_maxima) VALUES (%s, %s, %s) RETURNING id_zona;", (nombre, tipo, capacidad))
    id_zona = cur.fetchone()['id_zona']
    print("Zona " + str(i) + ": id_zona=" + str(id_zona) + ", nombre=" + nombre + ", cap=" + str(capacidad))

conn.commit()

# 6. Insertar vehiculos (10 vehiculos aleatorios con relacion a tipos y marcas)
print("\nInsertando vehiculos...")
tipos_ids = list(range(1, 11))
marcas = ['Toyota', 'Ford', 'Chevrolet', 'Volkswagen', 'Honda', 'Fiat', 'Renault', 'Nissan', 'Hyundai', 'Kia']
modelos = ['Corolla', 'Fusion', 'Onix', 'Gol', 'Civic', 'Argo', 'Duster', 'Ranger', 'Compass', 'Wrangler']
colores = ['Blanco', 'Negro', 'Rojo', 'Plateado', 'Azul', 'Gris']

for i in range(1, 11):
    placa = "ABC" + str(random.randint(100, 999))
    marca = random.choice(marcas)
    modelo = random.choice(modelos)
    color = random.choice(colores)
    id_tipo = random.choice(tipos_ids)
    fecha_registro = (datetime.now() - timedelta(days=random.randint(1, 365))).date()
    
    cur.execute("INSERT INTO vehiculos (placa, marca, modelo, color, fecha_registro, estado, id_tipo) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_vehiculo;", (placa, marca, modelo, color, fecha_registro, True, id_tipo))
    id_vehiculo = cur.fetchone()['id_vehiculo']
    print("Vehiculo " + str(i) + ": id_vehiculo=" + str(id_vehiculo) + ", placa=" + placa + ", marca=" + marca + ", modelo=" + modelo)

conn.commit()

# 7. Insertar usuarios (10 usuarios con roles aleatorios y emails únicos)
print("\nInsertando usuarios...")
nombres = ['Carlos', 'Maria', 'Juan', 'Laura', 'Pedro', 'Sofia', 'Miguel', 'Andrea', 'Diego', 'Patricia']
apellidos = ['Gomez', 'Rodriguez', 'Martinez', 'Lopez', 'Sanchez', 'Perez', 'Gonzalez', 'Ruiz', 'Torres', 'Jimenez']

for i in range(1, 11):
    nombre = nombres[i-1]
    apellido = apellidos[i-1]
    nombre_completo = nombre + " " + apellido
    correo = nombre.lower().replace(" ", ".") + str(i) + "@concesionario.com"
    contrasena_hash = "$2b$12$randomhash" + str(i)
    id_rol = roles_ids[(i-1) % len(roles_ids)]  # Rotar por roles disponibles
    estado = random.choice([True, True, True, False])
    
    cur.execute("INSERT INTO usuarios (nombre, correo, contrasena_hash, estado, id_rol) VALUES (%s, %s, %s, %s, %s) RETURNING id_usuario;", (nombre_completo, correo, contrasena_hash, estado, id_rol))
    id_usuario = cur.fetchone()['id_usuario']
    print("Usuario " + str(i) + ": id_usuario=" + str(id_usuario) + ", nombre=" + nombre_completo + ", rol_id=" + str(id_rol))

conn.commit()

# 8. Insertar camaras (10 camaras relacionadas con zonas)
print("\nInsertando camaras...")
for i in range(1, 11):
    nombre = "Camara " + str(i)
    ubicacion = "Punto " + str(i)
    id_zona = random.choice(range(1, 11))
    cur.execute("INSERT INTO camaras (nombre, ubicacion, id_zona) VALUES (%s, %s, %s) RETURNING id_camara;", (nombre, ubicacion, id_zona))
    id_camara = cur.fetchone()['id_camara']
    print("Camara " + str(i) + ": id_camara=" + str(id_camara) + ", nombre=" + nombre + ", zona_id=" + str(id_zona))

conn.commit()

# 9. Insertar visitas (10 visitas relacionadas con vehiculos)
print("\nInsertando visitas...")
for i in range(1, 11):
    id_vehiculo = random.choice(range(1, 11))
    fecha_entrada = (datetime.now() - timedelta(days=random.randint(0, 30))).replace(hour=random.randint(8, 18), minute=random.randint(0, 59))
    tiene_salida = random.random() < 0.7
    if tiene_salida:
        fecha_salida = fecha_entrada + timedelta(hours=random.randint(1, 8))
    else:
        fecha_salida = None
    
    cur.execute("INSERT INTO visitas (fecha_entrada, fecha_salida, estado, id_vehiculo) VALUES (%s, %s, %s, %s) RETURNING id_visita;", (fecha_entrada, fecha_salida, True, id_vehiculo))
    id_visita = cur.fetchone()['id_visita']
    salida_str = fecha_salida.strftime('%H:%M') if fecha_salida else 'Aun dentro'
    print("Visita " + str(i) + ": id_visita=" + str(id_visita) + ", vehiculo_id=" + str(id_vehiculo) + ", entrada=" + fecha_entrada.strftime("%H:%M") + ", salida=" + salida_str)

conn.commit()

# 10. Insertar seguimientos (10 seguimientos)
print("\nInsertando seguimientos...")
for i in range(1, 11):
    id_visita = random.choice(range(1, 11))
    id_camara = random.choice(range(1, 11))
    id_tracking = "track" + str(random.randint(100, 999))
    
    horas_inicio = random.randint(8, 17)
    minutos_inicio = random.choice([0, 15, 30, 45])
    inicio = datetime(2024, 1, 1, horas_inicio, minutos_inicio)
    
    tiene_fin = random.random() < 0.5
    if tiene_fin:
        fin = inicio + timedelta(hours=random.randint(1, 6))
    else:
        fin = None
    
    confianza_promedio = round(random.uniform(0.80, 0.99), 4)
    
    cur.execute("INSERT INTO seguimientos (id_tracking, inicio, fin, confianza_promedio, estado, id_visita, id_camara) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_seguimiento;", (id_tracking, inicio, fin, confianza_promedio, True, id_visita, id_camara))
    id_seguimiento = cur.fetchone()['id_seguimiento']
    print("Seguimiento " + str(i) + ": id_seguimiento=" + str(id_seguimiento) + ", tracking=" + id_tracking + ", confianza=" + str(confianza_promedio))

conn.commit()

# 11. Insertar eventos_vehiculo (10 eventos)
print("\nInsertando eventos_vehiculo...")
for i in range(1, 11):
    id_visita = random.choice(range(1, 11))
    id_camara = random.choice(range(1, 11))
    id_zona = random.choice(range(1, 11))
    
    tipos_evento = ['Ingreso', 'Salida', 'Mantenimiento', 'Revision', 'Estacionamiento', 'Fallido']
    tipo_evento = random.choice(tipos_evento)
    
    horas_evento = random.randint(8, 18)
    minutos_evento = random.choice([0, 15, 30, 45])
    fecha_hora = datetime(2024, 1, 1, horas_evento, minutos_evento)
    
    confianza = round(random.uniform(0.75, 0.98), 4)
    id_seguimiento = random.choice(range(1, 11))
    
    cur.execute("INSERT INTO eventos_vehiculo (tipo_evento, fecha_hora, confianza, estado, id_visita, id_camara, id_seguimiento, id_zona) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_evento;", (tipo_evento, fecha_hora, confianza, True, id_visita, id_camara, id_seguimiento, id_zona))
    id_evento = cur.fetchone()['id_evento']
    print("Evento " + str(i) + ": id_evento=" + str(id_evento) + ", tipo=" + tipo_evento + ", hora=" + fecha_hora.strftime("%H:%M"))

conn.commit()

# 12. Insertar alertas (10 alertas con constraint check válido)
print("\nInsertando alertas...")
for i in range(1, 11):
    id_visita = random.choice(range(1, 11))
    id_zona = random.choice(range(1, 11))
    id_usuario = random.choice(roles_ids)
    
    tipos_alerta = ['Congestión', 'Tiempo exceedido', 'Zona prohibida', 'Falla sistema', 'Riesgo seguridad']
    tipo_alerta = random.choice(tipos_alerta)
    
    mensaje = "Alerta " + str(i) + ": " + tipo_alerta + " detectada"
    
    # Cumplir constraint ck_alertas_resolucion:
    # si estado_resolucion='resuelta' entonces fecha_resolucion NOT NULL
    # si estado_resolucion <>'resuelta' entonces fecha_resolucion NULL
    if random.random() < 0.4:
        estado_resolucion = 'resuelta'
        fecha_resolucion = datetime.now() - timedelta(days=random.randint(1, 10))
    else:
        estado_resolucion = random.choice(['pendiente', 'en_proceso', 'descartada'])
        fecha_resolucion = None
    
    cur.execute("INSERT INTO alertas (tipo_alerta, mensaje, estado, estado_resolucion, fecha_resolucion, id_visita, id_zona, id_usuario_resuelve) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_alerta;", (tipo_alerta, mensaje, True, estado_resolucion, fecha_resolucion, id_visita, id_zona, id_usuario))
    id_alerta = cur.fetchone()['id_alerta']
    print("Alerta " + str(i) + ": id_alerta=" + str(id_alerta) + ", tipo=" + tipo_alerta + ", resolucion=" + estado_resolucion)

conn.commit()

# 13. Insertar ocupacion_zona (10 registros relacionados con zonas)
print("\nInsertando ocupacion_zona...")
for i in range(1, 11):
    id_zona = random.choice(range(1, 11))
    cur.execute("SELECT capacidad_maxima FROM zonas WHERE id_zona = %s", (id_zona,))
    capacidad = cur.fetchone()['capacidad_maxima']
    cantidad = random.randint(0, min(capacidad, 20))
    
    fecha_hora = datetime.now() - timedelta(hours=random.randint(0, 24))
    fecha_hora = fecha_hora.replace(minute=random.choice([0, 15, 30, 45]))
    
    cur.execute("INSERT INTO ocupacion_zona (fecha_hora, cantidad_vehiculos, id_zona) VALUES (%s, %s, %s) RETURNING id_ocupacion;", (fecha_hora, cantidad, id_zona))
    id_ocupacion = cur.fetchone()['id_ocupacion']
    print("Ocupacion " + str(i) + ": id_ocupacion=" + str(id_ocupacion) + ", zona_id=" + str(id_zona) + ", vehiculos=" + str(cantidad) + "/" + str(capacidad))

conn.commit()

# 14. Insertar asociaciones_seguimiento (10 asociaciones)
print("\nInsertando asociaciones_seguimiento...")
for i in range(1, 11):
    id_seguimiento_origen = random.choice(range(1, 11))
    id_seguimiento_destino = random.choice([s for s in range(1, 11) if s != id_seguimiento_origen])
    
    metodos = ['Color', 'Patrón', 'Combined']
    metodo = random.choice(metodos)
    confianza = round(random.uniform(0.80, 0.98), 4)
    resultado = random.choice(['pendiente', 'aceptada', 'rechazada'])
    
    cur.execute("INSERT INTO asociaciones_seguimiento (metodo, confianza, resultado, id_seguimiento_origen, id_seguimiento_destino) VALUES (%s, %s, %s, %s, %s) RETURNING id_asociacion;", (metodo, confianza, resultado, id_seguimiento_origen, id_seguimiento_destino))
    id_asociacion = cur.fetchone()['id_asociacion']
    print("Asociacion " + str(i) + ": id_asociacion=" + str(id_asociacion) + ", origen=" + str(id_seguimiento_origen) + ", destino=" + str(id_seguimiento_destino) + ", resultado=" + resultado)

conn.commit()

print("\n" + "="*60)
print("BASE DE DATOS DINÁMICA COMPLETADA EXITOSAMENTE")
print("="*60)
print("\nResumen de registros insertados:")
print("  - Roles: 5 (de una lista de 10 posibles)")
print("  - Modulos: 8")
print("  - modulo_x_rol: " + str(len(roles_ids) * random.randint(3, 6)) + " relaciones")
print("  - Tipos_vehiculo: 10")
print("  - Zonas: 10")
print("  - Vehiculos: 10")
print("  - Usuarios: 10")
print("  - Camaras: 10")
print("  - Visitas: 10")
print("  - Seguimientos: 10")
print("  - Eventos_vehiculo: 10")
print("  - Alertas: 10")
print("  - Ocupacion_zona: 10")
print("  - Asociaciones_seguimiento: 10")
print("="*60)

cur.close()
conn.close()