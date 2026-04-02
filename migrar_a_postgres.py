import sqlite3
import psycopg2
import sys

def migrar_sqlite_a_postgres():
    print("Iniciando migración automatizada de SQLite a PostgreSQL...")
    print("---------------------------------------------------------")
    
    # 1. Configurar conexión Postgres
    try:
        pg_conn = psycopg2.connect(
            host='localhost',
            port=5432,
            dbname='taller_camarina',
            user='postgres',
            password='AlfinfBD24'  # La contraseña que configuraste en el menú
        )
        pg_cursor = pg_conn.cursor()
        print("✅ Conectado a PostgreSQL exitosamente.")
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL:\n{e}")
        print("\nAsegúrate de haber creado la base de datos 'taller_camarina' vacía en pgAdmin.")
        sys.exit(1)

    # 2. Configurar conexión SQLite
    try:
        sqlite_conn = sqlite3.connect('taller_camarina.db')
        sqlite_cursor = sqlite_conn.cursor()
        print("✅ Conectado a base de datos SQLite 'taller_camarina.db'.")
    except Exception as e:
        print(f"❌ Error conectando a SQLite:\n{e}")
        pg_conn.close()
        sys.exit(1)

    # 3. Crear tablas en PostgreSQL (Traducción del esquema)
    print("\nCreando esquema de tablas en PostgreSQL...")
    tablas_sql = [
        """
        CREATE TABLE IF NOT EXISTS roles (
            id SERIAL PRIMARY KEY,
            nombre_rol TEXT NOT NULL UNIQUE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS estados_camion (
            id SERIAL PRIMARY KEY,
            nombre_estado TEXT NOT NULL UNIQUE,
            color TEXT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS estados_trabajador (
            id SERIAL PRIMARY KEY,
            nombre_estado TEXT NOT NULL UNIQUE,
            color TEXT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS mecanicos (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            codigo_nfc TEXT UNIQUE,
            rol_id INTEGER NOT NULL REFERENCES roles(id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS detalles (
            id SERIAL PRIMARY KEY,
            matricula TEXT NOT NULL,
            fecha_entrada TEXT NOT NULL,
            fecha_salida TEXT,
            estado_camion_id INTEGER NOT NULL REFERENCES estados_camion(id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS asignaciones (
            id SERIAL PRIMARY KEY,
            detalle_id INTEGER NOT NULL REFERENCES detalles(id),
            mecanico_id INTEGER NOT NULL REFERENCES mecanicos(id),
            fecha_asignacion TEXT NOT NULL,
            estado_trabajador_id INTEGER NOT NULL REFERENCES estados_trabajador(id)
        );
        """
    ]
    
    try:
        for tabla_sql in tablas_sql:
            pg_cursor.execute(tabla_sql)
        pg_conn.commit()
        print("✅ Tablas creadas correctamente en Postgres.")
    except Exception as e:
        print(f"❌ Error creando tablas en Postgres:\n{e}")
        pg_conn.rollback()
        sys.exit(1)

    # 4. Migrar los datos tabla por tabla
    print("\nMigrando datos de SQLite a PostgreSQL...")
    
    # Definición de las tablas y sus columnas a copiar
    tablas_a_migrar = [
        ('roles', 'id, nombre_rol'),
        ('estados_camion', 'id, nombre_estado, color'),
        ('estados_trabajador', 'id, nombre_estado, color'),
        ('mecanicos', 'id, nombre, codigo_nfc, rol_id'),
        ('detalles', 'id, matricula, fecha_entrada, fecha_salida, estado_camion_id'),
        ('asignaciones', 'id, detalle_id, mecanico_id, fecha_asignacion, estado_trabajador_id')
    ]
    
    for tabla, columnas in tablas_a_migrar:
        sqlite_cursor.execute(f"SELECT {columnas} FROM {tabla}")
        filas = sqlite_cursor.fetchall()
        
        if filas:
            placeholders = ",".join(["%s"] * len(columnas.split(",")))
            # Usar INSERT ... ON CONFLICT DO NOTHING para evitar errores si el script se corre 2 veces
            query = f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING"
            
            try:
                pg_cursor.executemany(query, filas)
                pg_conn.commit()
                print(f"   -> Tabla '{tabla}': {len(filas)} filas migradas exitosamente.")
            except Exception as e:
                print(f"   -> ⚠️ Error migrando la tabla '{tabla}': {e}")
                pg_conn.rollback()
        else:
            print(f"   -> Tabla '{tabla}': Sin datos para migrar.")

    # 5. Sincronizar secuencias SERIAL
    # Dado que insertamos IDs fijos (id 1, 2, 3), debemos decirle a Postgres 
    # que sus AUTOINCREMENTs internos sigan a partir del último ID insertado.
    print("\nSincronizando secuencias de IDs...")
    for tabla, _ in tablas_a_migrar:
        try:
            # En Postgres, la secuencia por defecto de una tabla SERIAL se llama "tabla_id_seq"
            pg_cursor.execute(f"SELECT setval('{tabla}_id_seq', COALESCE((SELECT MAX(id)+1 FROM {tabla}), 1), false);")
            pg_conn.commit()
        except Exception as e:
            pg_conn.rollback()
            # Ignoramos errores menores de secuencias
            pass
            

    # Cerrar conexiones
    sqlite_conn.close()
    pg_conn.close()
    
    print("\n🎉 ¡MIGRACIÓN COMPLETADA CON ÉXITO! 🎉")
    print("Ya puedes arrancar la aplicación nativamente en PostgreSQL.")


if __name__ == "__main__":
    migrar_sqlite_a_postgres()
