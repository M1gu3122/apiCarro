from app.core.database import Database
from app.models.zonas import Zonas

class ZonasRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM zonas ORDER BY id_zona ASC;")
        zonas = cursor.fetchall()
        conn.close()
        return zonas

    def obtener_por_id(self, id_zona: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM zonas WHERE id_zona = %s;", (id_zona,))
        zona = cursor.fetchone()
        conn.close()
        return zona

    def crear(self, zona: Zonas):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO zonas (nombre,tipo,capacidad_maxima,poligono,estado) 
            VALUES (%s, %s, %s, %s, %s) RETURNING id_zona;
        """
        cursor.execute(query, (zona.nombre, zona.tipo, zona.capacidad_maxima, zona.poligono, zona.estado))
        nueva_zona = cursor.fetchone()['id_zona']
        conn.commit()
        conn.close()
        return nueva_zona

    def eliminar(self, id_zona: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM zonas WHERE id_zona = %s RETURNING id_zona;", (id_zona,))
        zona_eliminada = cursor.fetchone()
        conn.commit()
        conn.close()
        return zona_eliminada is not None

    def actualizar(self, id_zona: int, zona: Zonas):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = """
            UPDATE zonas
            SET nombre = %s, tipo = %s, capacidad_maxima = %s, poligono = %s, estado = %s
            WHERE id_zona = %s
            RETURNING id_zona;
        """
        cursor.execute(query, (zona.nombre, zona.tipo, zona.capacidad_maxima, zona.poligono, zona.estado, id_zona))
        zona_actualizada = cursor.fetchone()
        conn.commit()
        conn.close()
        return zona_actualizada is not None