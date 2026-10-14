from app.core.database import Database
from app.models.camaras import Camaras

class CamarasRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM camaras ORDER BY id_camara ASC;")
        camaras = cursor.fetchall()
        conn.close()
        return camaras

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
            INSERT INTO camaras (nombre,ubicacion,fecha_registro,estado,creado,actualizado,id_zona) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_camara;
        """
        cursor.execute(query, (camara.nombre, camara.ubicacion, camara.fecha_registro, camara.estado, camara.creado, camara.actualizado, camara.id_zona))
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
            SET nombre = %s, ubicacion = %s, fecha_registro = %s, estado = %s, creado = %s, actualizado = %s, id_zona = %s
            WHERE id_camara = %s
            RETURNING id_camara;
        """
        cursor.execute(query, (camara.nombre, camara.ubicacion, camara.fecha_registro, camara.estado, camara.creado, camara.actualizado, camara.id_zona, id_camara))
        camara_actualizada = cursor.fetchone()
        conn.commit()
        conn.close()
        return camara_actualizada is not None