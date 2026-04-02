import sqlite3
import logging

# Configurar logging básico para el manejo de base de datos
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CursorProxy:
    """Interceptor de cursor que traduce automáticamente sintaxis SQLite a Postgres."""
    def __init__(self, cursor, tipo_bd):
        self._cursor = cursor
        self._tipo_bd = tipo_bd
        
    def execute(self, query, params=None):
        if params is None:
            params = ()
        if self._tipo_bd == 'postgres' and '?' in query:
            query = query.replace('?', '%s')
        return self._cursor.execute(query, params)
        
    def executescript(self, sql_script):
        # execute_script es propio de sqlite. Postgres puede usar execute normal para bloques
        if self._tipo_bd == 'postgres':
            # Nota: psycopg2 permite múltiples sentencias en execute()
            return self._cursor.execute(sql_script)
        else:
            return self._cursor.executescript(sql_script)
            
    def executemany(self, query, seq_of_params):
        if self._tipo_bd == 'postgres' and '?' in query:
            query = query.replace('?', '%s')
        return self._cursor.executemany(query, seq_of_params)
        
    def __getattr__(self, name):
        return getattr(self._cursor, name)

class ConnectionProxy:
    """Interceptor de conexión que devuelve el cursor proxy modificado."""
    def __init__(self, conn, tipo_bd):
        self._conn = conn
        self._tipo_bd = tipo_bd
        
    def cursor(self, *args, **kwargs):
        c = self._conn.cursor(*args, **kwargs)
        return CursorProxy(c, self._tipo_bd)
        
    def __getattr__(self, name):
        return getattr(self._conn, name)
    
    def __enter__(self):
        if hasattr(self._conn, '__enter__'):
            self._conn.__enter__()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self._conn, '__exit__'):
            self._conn.__exit__(exc_type, exc_val, exc_tb)

class DatabaseManager:
    """
    Gestor central de la Base de Datos.
    Actualmente configurado para SQLite, preparado estructuralmente para PostgreSQL.
    Patrón Singleton para evitar múltiples instancias de conexión innecesarias.
    """
    _instancia = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instancia:
            cls._instancia = super(DatabaseManager, cls).__new__(cls)
        return cls._instancia

    def __init__(self, tipo_bd='sqlite', sqlite_db_path='taller_camarina.db', **kwargs):
        # Evitar re-inicialización en el Singleton
        if not hasattr(self, 'inicializado'):
            self.tipo_bd = tipo_bd
            self.sqlite_db_path = sqlite_db_path
            
            # Configuraciones futuras para Postgres (host, port, user, password, dbname)
            self.pg_config = kwargs
            
            self.inicializado = True
            logging.info(f"DatabaseManager inicializado conectando a: {self.tipo_bd}")

    def get_connection(self):
        """Devuelve una conexión a la base de datos envuelta en un Proxy traductor."""
        try:
            if self.tipo_bd == 'sqlite':
                conn = sqlite3.connect(self.sqlite_db_path)
                return ConnectionProxy(conn, 'sqlite')
            
            elif self.tipo_bd == 'postgres':
                try:
                    import psycopg2
                except ImportError:
                    raise ImportError("Falta el driver psycopg2. Instálalo ejecutando: pip install psycopg2")
                
                conn = psycopg2.connect(
                    host=self.pg_config.get('host', 'localhost'),
                    port=self.pg_config.get('port', 5432),
                    dbname=self.pg_config.get('dbname', 'taller_camarina'),
                    user=self.pg_config.get('user', 'postgres'),
                    password=self.pg_config.get('password', 'admin') # Cambia esto
                )
                return ConnectionProxy(conn, 'postgres')
            
            else:
                raise ValueError(f"Motor de base de datos no soportado: {self.tipo_bd}")
                
        except Exception as e:
            logging.error(f"Error al obtener conexión a la BD: {e}")
            raise
    
    def execute_query(self, query, params=(), commit=False):
        """
        Ejecuta una consulta y opcionalmente hace commit. 
        Útil para ahorrar líneas de código en los módulos de Tkinter.
        Retorna los resultados si es un SELECT.
        """
        # Formatear la query para Postgres si fuera necesario en el futuro (cambiar ? por %s)
        if self.tipo_bd == 'postgres' and '?' in query:
            query = query.replace('?', '%s')
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if commit:
                conn.commit()
                return cursor.lastrowid
            else:
                return cursor.fetchall()
