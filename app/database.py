import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")
        self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("Conexión a la base de datos establecida")
            return self.connection
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            return None
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexión a la base de datos cerrada")
    
    def get_cursor(self):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        return self.connection.cursor(dictionary=True)
    
    def execute_query(self, query, params=None):
        cursor = self.get_cursor()
        try:
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor
        except Error as e:
            print(f"Error en la consulta: {e}")
            self.connection.rollback()
            raise
    
    def fetch_one(self, query, params=None):
        cursor = self.get_cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as e:
            print(f"Error en la consulta: {e}")
            raise
    
    def fetch_all(self, query, params=None):
        cursor = self.get_cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            print(f"Error en la consulta: {e}")
            raise

# Instancia global de la base de datos
db = Database()