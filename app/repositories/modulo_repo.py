from app.core.database import Database
from app.models.modulo import Modulo

class ModuloRepository:
    def __init__(self):
        self.db = Database()

    def obtener_todos(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM modulo ORDER BY id_modulo ASC;")
        modulos = cursor.fetchall()
        conn.close()
        return modulos

    def obtener_por_id(self, id_modulo: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM modulo WHERE id_modulo = %s;", (id_modulo,))
        modulo = cursor.fetchone()
        conn.close()
        return modulo

    def crear(self, modulo: Modulo):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO modulo (nombre_modulo,estado) 
            VALUES (%s, %s) RETURNING id_modulo;
        """
        cursor.execute(query, (modulo.nombre_modulo, modulo.estado))
        nuevo_modulo = cursor.fetchone()['id_modulo']
        conn.commit()
        conn.close()
        return nuevo_modulo

    def eliminar(self, id_modulo: int):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM modulo WHERE id_modulo = %s RETURNING id_modulo;", (id_modulo,))
        modulo_eliminado = cursor.fetchone()
        conn.commit()
        conn.close()
        return modulo_eliminado is not None

    def actualizar(self, id_modulo: int, modulo: Modulo):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            UPDATE modulo
            SET nombre_modulo = %s, estado = %s
            WHERE id_modulo = %s
            RETURNING id_modulo;
        """
        cursor.execute(query, (modulo.nombre_modulo, modulo.estado, id_modulo))
        modulo_actualizado = cursor.fetchone()
        conn.commit()
        conn.close()
        return modulo_actualizado is not None