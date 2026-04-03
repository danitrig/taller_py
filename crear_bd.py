import sqlite3
from database import DatabaseManager

def inicializar_base_datos():
    # Conectar a la base de datos usando el manager principal
    db = DatabaseManager()
    conexion = db.get_connection()
    cursor = conexion.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys = ON")  
        print("✅ Conectado a la base de datos")

        # Creación de tablas mediante un script unificado
        cursor.executescript('''
            -- TABLA 1: ROLES
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_rol TEXT NOT NULL UNIQUE
            );
            
            -- TABLA 2: ESTADOS_CAMION
            CREATE TABLE IF NOT EXISTS estados_camion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_estado TEXT NOT NULL UNIQUE,
                color TEXT NOT NULL
            );

            -- TABLA 3: ESTADOS_TRABAJADOR
            CREATE TABLE IF NOT EXISTS estados_trabajador (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_estado TEXT NOT NULL UNIQUE,
                color TEXT NOT NULL
            );

            -- TABLA 4: MECÁNICOS
            CREATE TABLE IF NOT EXISTS mecanicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                codigo_nfc TEXT UNIQUE,
                rol_id INTEGER NOT NULL,
                nombrecompleto TEXT,
                FOREIGN KEY (rol_id) REFERENCES roles(id)
            );
            
            -- TABLA 5: CLIENTES
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_cliente TEXT,
                descripcion TEXT
            );

            -- TABLA 6: DETALLES (movimientos de camiones)
            CREATE TABLE IF NOT EXISTS detalles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricula TEXT NOT NULL,
                fecha_entrada TEXT NOT NULL,
                fecha_salida TEXT,
                estado_camion_id INTEGER NOT NULL,
                terminado BOOLEAN DEFAULT 0,
                num_factura TEXT,
                cl_id INTEGER,
                FOREIGN KEY (estado_camion_id) REFERENCES estados_camion(id),
                FOREIGN KEY (cl_id) REFERENCES clientes(id_cliente)
            );

            -- TABLA 7: TAREAS
            CREATE TABLE IF NOT EXISTS tareas (
                id_tarea INTEGER PRIMARY KEY AUTOINCREMENT,
                descrip TEXT,
                id_dt INTEGER,
                tarea_fin BOOLEAN DEFAULT 0,
                FOREIGN KEY (id_dt) REFERENCES detalles(id)
            );

            -- TABLA 8: ASIGNACIONES (mecánicos trabajando en tareas)
            CREATE TABLE IF NOT EXISTS asignaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarea_id INTEGER NOT NULL,
                mecanico_id INTEGER NOT NULL,
                fecha_asignacion TEXT NOT NULL,
                estado_trabajador_id INTEGER NOT NULL,
                f_ini_trabajo TEXT,
                f_fin_trabajo TEXT,
                asigna_fin BOOLEAN DEFAULT 0,
                FOREIGN KEY (tarea_id) REFERENCES tareas(id_tarea),
                FOREIGN KEY (mecanico_id) REFERENCES mecanicos(id),
                FOREIGN KEY (estado_trabajador_id) REFERENCES estados_trabajador(id)
            );
        ''')
        print("✅ Tablas creadas correctamente")

        # Inserción de datos iniciales
        roles_iniciales = [('jefe',), ('mecanico',)]
        cursor.executemany('INSERT OR IGNORE INTO roles (nombre_rol) VALUES (?)', roles_iniciales)

        estados_camion_iniciales = [
            ('Libre', '#90EE90'), ('Ocupado', '#87CEEB'),
            ('En Reparación', '#FFB6C1'), ('Terminado', '#FFFF99')
        ]
        cursor.executemany('INSERT OR IGNORE INTO estados_camion (nombre_estado, color) VALUES (?, ?)', estados_camion_iniciales)

        estados_trabajador_iniciales = [
            ('Libre', '#90EE90'), ('Trabajando', '#87CEEB'),
            ('Pendiente', '#FFD700'), ('Terminado', '#98FB98')
        ]
        cursor.executemany('INSERT OR IGNORE INTO estados_trabajador (nombre_estado, color) VALUES (?, ?)', estados_trabajador_iniciales)

        mecanicos_iniciales = [
            ('RMC', '6A22BA6D', 1, 'Ruben Martinez'), ('DMC', '1AC6D56D', 2, 'Diego Miranda'),
            ('MMC', 'NFC05', 2, 'Manuel Miranda'), ('FJM', 'NFC12', 2, 'Francisco Javier'), ('MPM', 'NFC03', 2, 'Miguel Perez')
        ]
        cursor.executemany('INSERT OR IGNORE INTO mecanicos (nombre, codigo_nfc, rol_id, nombrecompleto) VALUES (?, ?, ?, ?)', mecanicos_iniciales)

        detalles_iniciales = [
            ('6651HMV', '2024-11-22', None, 1), ('3080FPP', '2024-11-22', None, 3)
        ]
        cursor.executemany('INSERT OR IGNORE INTO detalles (matricula, fecha_entrada, fecha_salida, estado_camion_id) VALUES (?, ?, ?, ?)', detalles_iniciales)
        print("✅ Datos iniciales de tablas insertados")

        conexion.commit()
        print("✅ Base de datos guardada y cerrada")

        print("=" * 50)
        print("\n📊 RESUMEN DE TABLAS CREADAS:")
        print("   1. ROLES (2 roles)")
        print("   2. ESTADOS_CAMION (4 estados)")
        print("   3. ESTADOS_TRABAJADOR (4 estados)")
        print("   4. MECÁNICOS (5 mecánicos)")
        print("   5. DETALLES (10 camiones)")
        print(f"   6. ASIGNACIONES ({len(asignaciones_iniciales)} asignaciones con estados)")
        print("=" * 50)
        
    finally:
        conexion.close()

if __name__ == "__main__":
    inicializar_base_datos()