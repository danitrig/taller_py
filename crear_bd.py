import sqlite3

# Conectar a la base de datos
conexion = sqlite3.connect('taller_camarina.db')
cursor = conexion.cursor()
cursor.execute("PRAGMA foreign_keys = ON")  
print("✅ Conectado a la base de datos")

# TABLA 1: ROLES
cursor.execute('''
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_rol TEXT NOT NULL UNIQUE
    )
''')
print("✅ Tabla 'roles' creada")

# Insertar roles iniciales
roles_iniciales = [
    ('jefe',),
    ('mecanico',),
]

cursor.executemany('''
    INSERT OR IGNORE INTO roles (nombre_rol)
    VALUES (?)
''', roles_iniciales)
print("✅ Roles iniciales insertados")

# TABLA 2: ESTADOS_CAMION
cursor.execute('''
    CREATE TABLE IF NOT EXISTS estados_camion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_estado TEXT NOT NULL UNIQUE,
        color TEXT NOT NULL
    )
''')
print("✅ Tabla 'estados_camion' creada")

# Insertar estados de camión
estados_camion_iniciales = [
    ('Libre', '#90EE90'),           # Verde claro
    ('Ocupado', '#87CEEB'),         # Azul claro
    ('En Reparación', '#FFB6C1'),   # Rosa claro
    ('Terminado', '#FFFF99'),       # Amarillo claro
]

cursor.executemany('''
    INSERT OR IGNORE INTO estados_camion (nombre_estado, color)
    VALUES (?, ?)
''', estados_camion_iniciales)
print("✅ Estados de camión insertados")

# TABLA 3: ESTADOS_TRABAJADOR
cursor.execute('''
    CREATE TABLE IF NOT EXISTS estados_trabajador (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_estado TEXT NOT NULL UNIQUE,
        color TEXT NOT NULL
    )
''')
print("✅ Tabla 'estados_trabajador' creada")

# Insertar estados de trabajador
estados_trabajador_iniciales = [
    ('Libre', '#90EE90'),           # Verde claro
    ('Trabajando', '#87CEEB'),      # Azul claro
    ('Pendiente', '#FFD700'),       # Dorado
    ('Terminado', '#98FB98'),       # Verde pálido
]

cursor.executemany('''
    INSERT OR IGNORE INTO estados_trabajador (nombre_estado, color)
    VALUES (?, ?)
''', estados_trabajador_iniciales)
print("✅ Estados de trabajador insertados")

# TABLA 4: MECÁNICOS
cursor.execute('''
    CREATE TABLE IF NOT EXISTS mecanicos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        codigo_nfc TEXT UNIQUE,
        rol_id INTEGER NOT NULL,
        FOREIGN KEY (rol_id) REFERENCES roles(id)
    )
''')
print("✅ Tabla 'mecanicos' creada")

# Insertar mecánicos iniciales
# rol_id: 1=jefe, 2=mecanico
mecanicos_iniciales = [
    ('RMC', '6A22BA6D', 1),    # jefe
    ('DMC', '1AC6D56D', 2),        # mecanico
    ('MMC', 'NFC05', 2),    # mecanico
    ('FJM', 'NFC12', 2),       # mecanico
    ('MPM', 'NFC03', 2),       # mecanico
]

cursor.executemany('''
    INSERT OR IGNORE INTO mecanicos (nombre, codigo_nfc, rol_id)
    VALUES (?, ?, ?)
''', mecanicos_iniciales)
print("✅ Mecánicos iniciales insertados")

# TABLA 5: DETALLES (movimientos de camiones)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS detalles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        matricula TEXT NOT NULL,
        fecha_entrada TEXT NOT NULL,
        fecha_salida TEXT,
        estado_camion_id INTEGER NOT NULL,
        FOREIGN KEY (estado_camion_id) REFERENCES estados_camion(id)
    )
''')
print("✅ Tabla 'detalles' creada")

# Insertar camiones de ejemplo
detalles_iniciales = [
    ('6651HMV', '2024-11-22', None, 1),      # Libre
    ('3080FPP', '2024-11-22', None, 3),      # En Reparación
    ('3718KRT', '2024-11-23', None, 1),      # Libre
    ('4717MVP', '2024-11-22', None, 2),      # Ocupado
    ('9515LTM', '2024-11-23', None, 3),      # En Reparación
    ('3442FNS', '2024-11-22', None, 3),      # En Reparación
    ('8507JSD', '2024-11-11', None, 3),      # En Reparación
    ('9374JCF', '2024-11-22', None, 3),      # En Reparación
    ('3168KFG', '2024-11-22', None, 3),      # En Reparación
    ('8128FPC', '2024-11-20', None, 3),      # En Reparación
]

cursor.executemany('''
    INSERT OR IGNORE INTO detalles (matricula, fecha_entrada, fecha_salida, estado_camion_id)
    VALUES (?, ?, ?, ?)
''', detalles_iniciales)
print("✅ Detalles iniciales insertados")

# TABLA 6: ASIGNACIONES (mecánicos trabajando en camiones)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS asignaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        detalle_id INTEGER NOT NULL,
        mecanico_id INTEGER NOT NULL,
        fecha_asignacion TEXT NOT NULL,
        estado_trabajador_id INTEGER NOT NULL,
        FOREIGN KEY (detalle_id) REFERENCES detalles(id),
        FOREIGN KEY (mecanico_id) REFERENCES mecanicos(id),
        FOREIGN KEY (estado_trabajador_id) REFERENCES estados_trabajador(id)
    )
''')
print("✅ Tabla 'asignaciones' creada")

# Insertar asignaciones de ejemplo
# (detalle_id, mecanico_id, fecha, estado_trabajador_id)
asignaciones_iniciales = [
    (2, 1, '2024-11-22', 2),  # 3080FPP -> Juan López (Trabajando)
    (2, 2, '2024-11-22', 3),  # 3080FPP -> Pedro Martínez (Pendiente)
    (2, 3, '2024-11-22', 3),  # 3080FPP -> Pedro Martínez (Pendiente)
    (2, 4, '2024-11-22', 3),  # 3080FPP -> Pedro Martínez (Pendiente)
    (2, 5, '2024-11-22', 3),  # 3080FPP -> Pedro Martínez (Pendiente)
    (2, 3, '2024-11-22', 3),  # 3080FPP -> Pedro Martínez (Pendiente)
    (2, 4, '2024-11-22', 3),  # 3080FPP -> Pedro Martínez (Pendiente)
    (4, 4, '2024-11-22', 2),  # 4717MVP -> Carlos Ruiz (Trabajando)
    (5, 5, '2024-11-23', 4),  # 9515LTM -> Manuel Díaz (Terminado)
]

cursor.executemany('''
    INSERT OR IGNORE INTO asignaciones (detalle_id, mecanico_id, fecha_asignacion, estado_trabajador_id)
    VALUES (?, ?, ?, ?)
''', asignaciones_iniciales)
print("✅ Asignaciones iniciales insertadas")

# Guardar cambios
conexion.commit()

# Cerrar conexión
conexion.close()

print("✅ Base de datos guardada y cerrada")
print("=" * 50)
print("\n📊 RESUMEN DE TABLAS CREADAS:")
print("   1. ROLES (2 roles)")
print("   2. ESTADOS_CAMION (4 estados)")
print("   3. ESTADOS_TRABAJADOR (4 estados)")
print("   4. MECÁNICOS (5 mecánicos)")
print("   5. DETALLES (10 camiones)")
print("   6. ASIGNACIONES (4 asignaciones con estados)")
print("=" * 50)