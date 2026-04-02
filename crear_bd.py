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
                FOREIGN KEY (rol_id) REFERENCES roles(id)
            );

            -- TABLA 5: DETALLES (movimientos de camiones)
            CREATE TABLE IF NOT EXISTS detalles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricula TEXT NOT NULL,
                fecha_entrada TEXT NOT NULL,
                fecha_salida TEXT,
                estado_camion_id INTEGER NOT NULL,
                FOREIGN KEY (estado_camion_id) REFERENCES estados_camion(id)
            );

            -- TABLA 6: ASIGNACIONES (mecánicos trabajando en camiones)
            CREATE TABLE IF NOT EXISTS asignaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detalle_id INTEGER NOT NULL,
                mecanico_id INTEGER NOT NULL,
                fecha_asignacion TEXT NOT NULL,
                estado_trabajador_id INTEGER NOT NULL,
                FOREIGN KEY (detalle_id) REFERENCES detalles(id),
                FOREIGN KEY (mecanico_id) REFERENCES mecanicos(id),
                FOREIGN KEY (estado_trabajador_id) REFERENCES estados_trabajador(id)
            );

            -- TABLA 7: CLIENTES
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_cliente TEXT,
                descripcion TEXT
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
            ('RMC', '6A22BA6D', 1), ('DMC', '1AC6D56D', 2),
            ('MMC', 'NFC05', 2), ('FJM', 'NFC12', 2), ('MPM', 'NFC03', 2)
        ]
        cursor.executemany('INSERT OR IGNORE INTO mecanicos (nombre, codigo_nfc, rol_id) VALUES (?, ?, ?)', mecanicos_iniciales)

        detalles_iniciales = [
            ('6651HMV', '2024-11-22', None, 1), ('3080FPP', '2024-11-22', None, 3),
            ('3718KRT', '2024-11-23', None, 1), ('4717MVP', '2024-11-22', None, 2),
            ('9515LTM', '2024-11-23', None, 3), ('3442FNS', '2024-11-22', None, 3),
            ('8507JSD', '2024-11-11', None, 3), ('9374JCF', '2024-11-22', None, 3),
            ('3168KFG', '2024-11-22', None, 3), ('8128FPC', '2024-11-20', None, 3)
        ]
        cursor.executemany('INSERT OR IGNORE INTO detalles (matricula, fecha_entrada, fecha_salida, estado_camion_id) VALUES (?, ?, ?, ?)', detalles_iniciales)

        asignaciones_iniciales = [
            (2, 1, '2024-11-22', 2), (2, 2, '2024-11-22', 3),
            (2, 3, '2024-11-22', 3), (2, 4, '2024-11-22', 3),
            (2, 5, '2024-11-22', 3), (2, 3, '2024-11-22', 3),
            (2, 4, '2024-11-22', 3), (4, 4, '2024-11-22', 2),
            (5, 5, '2024-11-23', 4)
        ]
        cursor.executemany('INSERT OR IGNORE INTO asignaciones (detalle_id, mecanico_id, fecha_asignacion, estado_trabajador_id) VALUES (?, ?, ?, ?)', asignaciones_iniciales)
        print("✅ Datos iniciales insertados")

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