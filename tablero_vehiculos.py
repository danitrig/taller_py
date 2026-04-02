import tkinter as tk
from tkinter import messagebox
import sqlite3
from database import DatabaseManager
from tkcalendar import DateEntry
from datetime import datetime

class TableroVehiculos:
    def __init__(self, root, menu_principal):
        self.root = root
        self.menu_principal = menu_principal
        self.root.title("TALLER - Tablero de Vehículos")
        self.root.geometry("1920x1080")
        self.root.state('zoomed')
        self.root.configure(bg='#f0f0f0')
        
        # Conectar a la base de datos
        self.db_manager = DatabaseManager()
        self.conexion = self.db_manager.get_connection()
        self.cursor = self.conexion.cursor()
        if self.db_manager.tipo_bd == 'sqlite':
            self.cursor.execute("PRAGMA foreign_keys = ON")
        
        # Variables de paginación y filtros
        self.pagina_actual = 0
        self.vehiculos_por_pagina = 30
        self.mostrar_terminados = tk.BooleanVar(value=False)
        
        self.crear_widgets()
        
        # Al cerrar, volver al menú
        self.root.protocol("WM_DELETE_WINDOW", self.volver_menu)
    
    def crear_widgets(self):
            # Frame del título
            title_frame = tk.Frame(self.root, bg='#1e3a8a', height=70)
            title_frame.pack(fill='x', padx=0, pady=0)
            title_frame.pack_propagate(False)
            
            # Botón volver al menú (izquierda)
            btn_volver = tk.Button(title_frame,
                                text="← MENÚ",
                                font=('Arial', 12, 'bold'),
                                bg='#FFB800',
                                fg='black',
                                command=lambda: self.autenticar_nfc(self.volver_menu_autenticado))
            btn_volver.pack(side='left', padx=10)
            
            # Texto del título (centro)
            title_label = tk.Label(title_frame, 
                                text="🚛 VEHÍCULOS EN TALLER", 
                                font=('Segoe UI', 28, 'bold'),
                                fg='white',
                                bg='#1e3a8a')
            title_label.pack(expand=True)
            
            # Frame contenedor para las celdas
            grid_frame = tk.Frame(self.root, bg='#f5f5f5')
            grid_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # ⚠️ NO LLAMAR A cargar_vehiculos AQUÍ
            
            # Frame para controles en la parte inferior
            controles_frame = tk.Frame(self.root, bg='#f0f0f0')
            controles_frame.pack(fill='x', side='bottom', padx=10, pady=10)
            
            # Frame superior: Botones de acción
            botones_frame = tk.Frame(controles_frame, bg='#f0f0f0')
            botones_frame.pack(fill='x', pady=(0, 10))
            
            # Botón Añadir Vehículo
            btn_add_vehiculo = tk.Button(botones_frame,
                                        text="➕ AÑADIR VEHÍCULO",
                                        font=('Arial', 12, 'bold'),
                                        bg='#4CAF50',
                                        fg='white',
                                        width=18,
                                        height=2,
                                        command=lambda: self.autenticar_nfc(self.abrir_ventana_vehiculo_autenticado))
            btn_add_vehiculo.pack(side='left', padx=5)
            
            # Botón Añadir Mecánico
            """btn_add_mecanico = tk.Button(botones_frame,
                                        text="➕ AÑADIR MECÁNICO",
                                        font=('Arial', 12, 'bold'),
                                        bg='#2196F3',
                                        fg='white',
                                        width=18,
                                        height=2,
                                        command=self.abrir_ventana_mecanico)
            btn_add_mecanico.pack(side='left', padx=5)"""
            
            # Botón Refrescar
            btn_refrescar = tk.Button(botones_frame,
                                    text="🔄 REFRESCAR",
                                    font=('Arial', 12, 'bold'),
                                    bg='#FF9800',
                                    fg='white',
                                    width=18,
                                    height=2,
                                    command=self.refrescar)
            btn_refrescar.pack(side='left', padx=5)
            
            # Checkbox para mostrar/ocultar terminados
            check_terminados = tk.Checkbutton(botones_frame,
                                            text="Mostrar vehículos terminados",
                                            font=('Arial', 11),
                                            bg='#f0f0f0',
                                            variable=self.mostrar_terminados,
                                            command=self.refrescar)
            check_terminados.pack(side='left', padx=20)
            
            # Frame inferior: Paginación
            paginacion_frame = tk.Frame(controles_frame, bg='#f0f0f0')
            paginacion_frame.pack(fill='x')
            
            # Etiqueta de información de página
            self.label_pagina = tk.Label(paginacion_frame,
                                        text="Página 1 de 1",
                                        font=('Arial', 12, 'bold'),
                                        bg='#f0f0f0')
            self.label_pagina.pack(side='left', padx=20)
            
            # Botones de navegación
            self.btn_anterior = tk.Button(paginacion_frame,
                                        text="◀ Anterior",
                                        font=('Arial', 11, 'bold'),
                                        bg='#607D8B',
                                        fg='white',
                                        width=15,
                                        command=self.pagina_anterior,
                                        state='disabled')
            self.btn_anterior.pack(side='left', padx=5)
            
            self.btn_siguiente = tk.Button(paginacion_frame,
                                        text="Siguiente ▶",
                                        font=('Arial', 11, 'bold'),
                                        bg='#607D8B',
                                        fg='white',
                                        width=15,
                                        command=self.pagina_siguiente)
            self.btn_siguiente.pack(side='left', padx=5)
            
            # Etiqueta de total de vehículos
            self.label_total = tk.Label(paginacion_frame,
                                        text="Total: 0 vehículos",
                                        font=('Arial', 11),
                                        bg='#f0f0f0')
            self.label_total.pack(side='right', padx=20)
            
            # ✅ AHORA SÍ CARGAR LOS VEHÍCULOS (al final, después de crear todos los widgets)
            self.cargar_vehiculos(grid_frame)
        
    def cargar_vehiculos(self, grid_frame):
        """Carga los vehículos en el grid con paginación"""
        
        # Limpiar grid si existe
        for widget in grid_frame.winfo_children():
            widget.destroy()
        
        # Construir query con filtro de terminados
        if self.mostrar_terminados.get():
            # Mostrar todos
            query = '''
                SELECT d.id, d.matricula, d.fecha_entrada, d.fecha_salida, 
                       ec.color, ec.nombre_estado
                FROM detalles d
                JOIN estados_camion ec ON d.estado_camion_id = ec.id
                ORDER BY d.id ASC
            '''
        else:
            # Ocultar terminados
            query = '''
                SELECT d.id, d.matricula, d.fecha_entrada, d.fecha_salida, 
                       ec.color, ec.nombre_estado
                FROM detalles d
                JOIN estados_camion ec ON d.estado_camion_id = ec.id
                WHERE ec.nombre_estado != 'Terminado'
                ORDER BY d.id ASC
            '''
        
        self.cursor.execute(query)
        todos_vehiculos = self.cursor.fetchall()
        
        # Calcular paginación
        total_vehiculos = len(todos_vehiculos)
        total_paginas = max(1, (total_vehiculos + self.vehiculos_por_pagina - 1) // self.vehiculos_por_pagina)
        
        # Ajustar página actual si es necesario
        if self.pagina_actual >= total_paginas:
            self.pagina_actual = max(0, total_paginas - 1)
        
        # Obtener vehículos de la página actual
        inicio = self.pagina_actual * self.vehiculos_por_pagina
        fin = inicio + self.vehiculos_por_pagina
        vehiculos_pagina = todos_vehiculos[inicio:fin]
        
        # Actualizar etiquetas de información
        self.label_pagina.config(text=f"Página {self.pagina_actual + 1} de {total_paginas}")
        self.label_total.config(text=f"Total: {total_vehiculos} vehículos")
        
        # Actualizar estado de botones de navegación
        self.btn_anterior.config(state='normal' if self.pagina_actual > 0 else 'disabled')
        self.btn_siguiente.config(state='normal' if self.pagina_actual < total_paginas - 1 else 'disabled')
        
        # Configuración del grid fijo
        COLUMNAS = 10
        FILAS = 3
        ANCHO_CELDA = 184
        ALTO_CELDA = 260
        
        # Crear las 30 celdas (10x3)
        posicion = 0
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                
                # Si hay vehículo para esta posición
                if posicion < len(vehiculos_pagina):
                    vehiculo = vehiculos_pagina[posicion]
                    vehiculo_id = vehiculo[0]
                    matricula = vehiculo[1]
                    fecha_entrada = vehiculo[2]
                    fecha_salida = vehiculo[3]
                    color_camion = vehiculo[4]
                    nombre_estado_camion = vehiculo[5]
                    
                    # Buscar mecánicos asignados
                    self.cursor.execute('''
                        SELECT m.nombre, et.color, et.nombre_estado
                        FROM asignaciones a
                        JOIN mecanicos m ON a.mecanico_id = m.id
                        JOIN estados_trabajador et ON a.estado_trabajador_id = et.id
                        WHERE a.detalle_id = ?
                        ORDER BY a.fecha_asignacion DESC
                        LIMIT 5
                    ''', (vehiculo_id,))
                    
                    mecanicos_asignados = self.cursor.fetchall()
                    
                else:
                    # Celda vacía
                    matricula = ""
                    fecha_entrada = ""
                    fecha_salida = None
                    color_camion = "#FFFFFF"
                    mecanicos_asignados = []
                
                # Crear la celda principal
                celda = tk.Frame(grid_frame, 
                                 bg='#FFFFFF',
                                 relief='solid',
                                 borderwidth=2,
                                 width=ANCHO_CELDA,
                                 height=ALTO_CELDA)
                celda.grid(row=fila, column=columna, padx=3, pady=3)
                celda.grid_propagate(False)
                celda.pack_propagate(False)
                
                # Solo mostrar contenido si hay vehículo
                if matricula:
                    self.crear_celda_vehiculo(celda, matricula, fecha_entrada, fecha_salida, 
                                             color_camion, mecanicos_asignados)
                
                posicion += 1
    def autenticar_nfc(self, accion_callback, *args):
        # BYPASS DE NFC
        self.usuario_actual = {'id': 1, 'nombre': 'Desarrollador', 'rol': 'jefe'}
        accion_callback(*args)
        return

        #Ventana modal para autenticar con NFC antes de ejecutar una acción

        from nfc_reader import NFCReader
        import time
        
        # Crear ventana modal
        ventana = tk.Toplevel(self.root)
        ventana.title("Autenticación NFC")
        ventana.geometry("450x350")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.transient(self.root)
        
        # Centrar ventana
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (450 // 2)
        y = (ventana.winfo_screenheight() // 2) - (350 // 2)
        ventana.geometry(f"+{x}+{y}")
        
        # Título
        tk.Label(ventana,
                text="🔐 AUTENTICACIÓN REQUERIDA",
                font=('Arial', 16, 'bold'),
                bg='#FF9800',
                fg='white',
                pady=15).pack(fill='x')
        
        # Frame principal
        main_frame = tk.Frame(ventana, bg='white', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Icono e instrucción
        tk.Label(main_frame,
                text="📱",
                font=('Arial', 48),
                bg='white').pack(pady=10)
        
        tk.Label(main_frame,
                text="Acerca tu llavero NFC al lector",
                font=('Arial', 13, 'bold'),
                bg='white').pack(pady=10)
        
        # Mensaje de estado
        msg_label = tk.Label(main_frame,
                            text="Esperando tarjeta...",
                            font=('Arial', 11),
                            bg='white',
                            fg='#666')
        msg_label.pack(pady=15)
        
        # Animación de puntos
        puntos = ["", ".", "..", "..."]
        indice_puntos = [0]
        
        def animar_puntos():
            if ventana.winfo_exists():
                msg_label.config(text=f"Esperando tarjeta{puntos[indice_puntos[0]]}")
                indice_puntos[0] = (indice_puntos[0] + 1) % len(puntos)
                ventana.after(500, animar_puntos)
        
        animar_puntos()
        
        # Inicializar lector
        lector = NFCReader()
        exito_lector, mensaje_lector = lector.detectar_lector()
        
        if not exito_lector:
            msg_label.config(text="❌ Lector NFC no detectado", fg='red')
            tk.Button(main_frame,
                    text="Cerrar",
                    font=('Arial', 11, 'bold'),
                    bg='#f44336',
                    fg='white',
                    width=15,
                    command=ventana.destroy).pack(pady=20)
            return
        
        # Variable de control
        lectura_exitosa = [False]
        
        # Función de lectura continua
        def intentar_lectura():
            if not ventana.winfo_exists() or lectura_exitosa[0]:
                return
            
            exito, resultado = lector.leer_tarjeta()
            
            if exito:
                lectura_exitosa[0] = True
                codigo_nfc = resultado
                
                # Buscar usuario en la BD
                self.cursor.execute('''
                    SELECT m.id, m.nombre, r.nombre_rol
                    FROM mecanicos m
                    JOIN roles r ON m.rol_id = r.id
                    WHERE m.codigo_nfc = ?
                ''', (codigo_nfc,))
                
                usuario = self.cursor.fetchone()
                
                if usuario:
                    usuario_id = usuario[0]
                    nombre = usuario[1]
                    rol = usuario[2]
                    
                    msg_label.config(text=f"✅ Bienvenido, {nombre}", fg='green')
                    
                    # Guardar usuario autenticado
                    self.usuario_actual = {
                        'id': usuario_id,
                        'nombre': nombre,
                        'rol': rol
                    }
                    
                    # Cerrar ventana y ejecutar callback
                    ventana.after(1000, lambda: [
                        ventana.destroy(),
                        accion_callback(*args)
                    ])
                    
                else:
                    msg_label.config(text="❌ Usuario no registrado", fg='red')
                    ventana.after(2000, ventana.destroy)
            
            else:
                # Reintentar cada 500ms
                ventana.after(500, intentar_lectura)
        
        # Botón cancelar
        tk.Button(main_frame,
                text="❌ CANCELAR",
                font=('Arial', 11, 'bold'),
                bg='#607D8B',
                fg='white',
                width=15,
                command=ventana.destroy).pack(pady=20)
        
        # Iniciar lectura
        intentar_lectura()
        
    
    def crear_celda_vehiculo(self, celda, matricula, fecha_entrada, fecha_salida, 
                            color_camion, mecanicos_asignados):
        """Crea el contenido de una celda de vehículo"""
        
        # CABECERA
        cabecera = tk.Frame(celda, bg=color_camion, height=75)
        cabecera.pack(fill='x')
        cabecera.pack_propagate(False)
        
        # Fechas
        fechas_frame = tk.Frame(cabecera, bg=color_camion)
        fechas_frame.pack(pady=3)
        
        fecha_ent_label = tk.Label(fechas_frame, 
                            text=fecha_entrada,
                            font=('Arial', 10, 'bold'),
                            bg=color_camion,
                            fg='black')
        fecha_ent_label.pack(side='left')
        
        separador_fechas = tk.Label(fechas_frame,
                            text=" | ",
                            font=('Arial', 10, 'bold'),
                            bg=color_camion,
                            fg='black')
        separador_fechas.pack(side='left')
        
        if fecha_salida:
            fecha_sal_label = tk.Label(fechas_frame, 
                                text=fecha_salida,
                                font=('Arial', 10, 'bold'),
                                bg=color_camion,
                                fg='black')
            fecha_sal_label.pack(side='left')
        else:
            fecha_vacia = tk.Label(fechas_frame, 
                                text="        ",
                                font=('Arial', 10, 'bold'),
                                bg=color_camion)
            fecha_vacia.pack(side='left')
        
        # Matrícula
        matricula_label = tk.Label(cabecera, 
                            text=matricula,
                            font=('Arial', 22, 'bold'),
                            bg=color_camion,
                            fg='black')
        matricula_label.pack(pady=3)
        
        # LÍNEA SEPARADORA
        linea_separadora = tk.Frame(celda, bg='black', height=3)
        linea_separadora.pack(fill='x')
        
        # MECÁNICOS
        mecanicos_frame = tk.Frame(celda, bg='#FFFFFF')
        mecanicos_frame.pack(fill='both', expand=True, padx=3, pady=3)
        
        if mecanicos_asignados:
            for mecanico_data in mecanicos_asignados:
                nombre_mecanico = mecanico_data[0]
                color_estado_trabajador = mecanico_data[1]
                
                mecanico_celda = tk.Frame(mecanicos_frame,
                                        bg=color_estado_trabajador,
                                        relief='solid',
                                        borderwidth=1,
                                        height=28)
                mecanico_celda.pack(fill='x', pady=2)
                mecanico_celda.pack_propagate(False)
                
                mecanico_label = tk.Label(mecanico_celda,
                                text=nombre_mecanico,
                                font=('Arial', 11, 'bold'),
                                bg=color_estado_trabajador,
                                fg='black')
                mecanico_label.pack(expand=True)
        
        # Hacer toda la celda clickeable
        # Hacer toda la celda clickeable CON autenticación NFC
        celda.bind('<Button-1>', lambda e, m=matricula: self.autenticar_nfc(self.abrir_gestionar_asignaciones_autenticado, m))
        cabecera.bind('<Button-1>', lambda e, m=matricula: self.autenticar_nfc(self.abrir_gestionar_asignaciones_autenticado, m))
        matricula_label.bind('<Button-1>', lambda e, m=matricula: self.autenticar_nfc(self.abrir_gestionar_asignaciones_autenticado, m))
    def pagina_anterior(self):
        """Va a la página anterior"""
        if self.pagina_actual > 0:
            self.pagina_actual -= 1
            self.refrescar()
    
    def pagina_siguiente(self):
        """Va a la página siguiente"""
        self.pagina_actual += 1
        self.refrescar()
    
    def abrir_ventana_vehiculo(self):
        """Ventana para añadir vehículo"""
        
        # Crear ventana
        ventana = tk.Toplevel(self.root)
        ventana.title("Añadir Vehículo")
        ventana.geometry("550x500")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.transient(self.root)
        
        # Título
        titulo = tk.Label(ventana,
                         text="🚛 AÑADIR NUEVO VEHÍCULO",
                         font=('Arial', 18, 'bold'),
                         bg='#4CAF50',
                         fg='white',
                         pady=15)
        titulo.pack(fill='x')
        
        # Formulario
        form_frame = tk.Frame(ventana, bg='white', padx=30, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        # Matrícula
        tk.Label(form_frame, text="Matrícula:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        entry_matricula = tk.Entry(form_frame, font=('Arial', 12), width=30)
        entry_matricula.pack(fill='x')
        entry_matricula.focus()
        
        # Fecha y Hora Entrada
        tk.Label(form_frame, text="Fecha y Hora Entrada:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        
        fecha_hora_frame = tk.Frame(form_frame, bg='white')
        fecha_hora_frame.pack(fill='x')
        
        now = datetime.now()
        
        date_entrada = DateEntry(fecha_hora_frame,
                                width=12,
                                font=('Arial', 12),
                                background='#4CAF50',
                                foreground='white',
                                borderwidth=2,
                                date_pattern='yyyy-mm-dd',
                                state='readonly',
                                year=now.year,
                                month=now.month,
                                day=now.day)
        date_entrada.pack(side='left', padx=(0, 10))
        
        spin_hora = tk.Spinbox(fecha_hora_frame, from_=0, to=23, width=3, font=('Arial', 12), format="%02.0f")
        spin_hora.delete(0, 'end')
        spin_hora.insert(0, now.strftime("%H"))
        spin_hora.pack(side='left')
        
        tk.Label(fecha_hora_frame, text=":", font=('Arial', 12, 'bold'), bg='white').pack(side='left')
        
        spin_minuto = tk.Spinbox(fecha_hora_frame, from_=0, to=59, width=3, font=('Arial', 12), format="%02.0f")
        spin_minuto.delete(0, 'end')
        spin_minuto.insert(0, now.strftime("%M"))
        spin_minuto.pack(side='left')
        
        # Estado
        tk.Label(form_frame, text="Estado:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        
        self.cursor.execute('SELECT id, nombre_estado FROM estados_camion')
        estados = self.cursor.fetchall()
        
        estado_var = tk.StringVar()
        estado_var.set(estados[0][1])
        
        estados_dict = {e[1]: e[0] for e in estados}
        combo_estados = tk.OptionMenu(form_frame, estado_var, *estados_dict.keys())
        combo_estados.config(font=('Arial', 12), width=25)
        combo_estados.pack(fill='x')
        
        # Mensaje
        msg_label = tk.Label(form_frame, text="", font=('Arial', 10), bg='white')
        msg_label.pack(pady=10)
        
        def guardar():
            matricula = entry_matricula.get().strip().upper()
            hora = str(spin_hora.get()).zfill(2)
            minuto = str(spin_minuto.get()).zfill(2)
            fecha_entrada = f"{date_entrada.get_date().strftime('%Y-%m-%d')} {hora}:{minuto}"
            estado_nombre = estado_var.get()
            estado_id = estados_dict[estado_nombre]
            
            if not matricula:
                msg_label.config(text="⚠️ La matrícula es obligatoria", fg='red')
                return
            
            try:
                with self.conexion:
                    self.cursor.execute('''
                        INSERT INTO detalles (matricula, fecha_entrada, fecha_salida, estado_camion_id)
                        VALUES (?, ?, NULL, ?)
                    ''', (matricula, fecha_entrada, estado_id))
                
                msg_label.config(text="✅ Vehículo añadido correctamente", fg='green')
                ventana.after(1000, lambda: [ventana.destroy(), self.refrescar()])
                
            except Exception as e:
                msg_label.config(text=f"❌ Error: {str(e)}", fg='red')
        
        # Botones
        botones_frame = tk.Frame(form_frame, bg='white')
        botones_frame.pack(pady=30)
        
        btn_guardar = tk.Button(botones_frame,
                               text="💾 GUARDAR",
                               font=('Arial', 14, 'bold'),
                               bg='#4CAF50',
                               fg='white',
                               width=15,
                               height=2,
                               command=guardar)
        btn_guardar.pack(side='left', padx=10)
        
        btn_cancelar = tk.Button(botones_frame,
                                text="❌ CANCELAR",
                                font=('Arial', 14, 'bold'),
                                bg='#f44336',
                                fg='white',
                                width=15,
                                height=2,
                                command=ventana.destroy)
        btn_cancelar.pack(side='left', padx=10)
    
    def abrir_ventana_mecanico(self):
        """Ventana para añadir mecánico"""
        
        # Crear ventana
        ventana = tk.Toplevel(self.root)
        ventana.title("Añadir Mecánico")
        ventana.geometry("550x450")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.transient(self.root)
        
        # Título
        titulo = tk.Label(ventana,
                         text="👨‍🔧 AÑADIR NUEVO MECÁNICO",
                         font=('Arial', 18, 'bold'),
                         bg='#2196F3',
                         fg='white',
                         pady=15)
        titulo.pack(fill='x')
        
        # Formulario
        form_frame = tk.Frame(ventana, bg='white', padx=30, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        # Nombre
        tk.Label(form_frame, text="Nombre:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        entry_nombre = tk.Entry(form_frame, font=('Arial', 12), width=30)
        entry_nombre.pack(fill='x')
        entry_nombre.focus()
        
        # Código NFC
        tk.Label(form_frame, text="Código NFC:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        entry_nfc = tk.Entry(form_frame, font=('Arial', 12), width=30)
        entry_nfc.pack(fill='x')
        
        # Rol
        tk.Label(form_frame, text="Rol:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        
        self.cursor.execute('SELECT id, nombre_rol FROM roles')
        roles = self.cursor.fetchall()
        
        rol_var = tk.StringVar()
        rol_var.set(roles[1][1].capitalize())
        
        roles_dict = {r[1].capitalize(): r[0] for r in roles}
        combo_roles = tk.OptionMenu(form_frame, rol_var, *roles_dict.keys())
        combo_roles.config(font=('Arial', 12), width=25)
        combo_roles.pack(fill='x')
        
        # Mensaje
        msg_label = tk.Label(form_frame, text="", font=('Arial', 10), bg='white')
        msg_label.pack(pady=10)
        
        # Función guardar
        def guardar():
            nombre = entry_nombre.get().strip()
            codigo_nfc = entry_nfc.get().strip().upper()
            rol_nombre = rol_var.get()
            rol_id = roles_dict[rol_nombre]
            
            if not nombre:
                msg_label.config(text="⚠️ El nombre es obligatorio", fg='red')
                return
            
            if not codigo_nfc:
                msg_label.config(text="⚠️ El código NFC es obligatorio", fg='red')
                return
            
            try:
                self.cursor.execute('''
                    INSERT INTO mecanicos (nombre, codigo_nfc, rol_id)
                    VALUES (?, ?, ?)
                ''', (nombre, codigo_nfc, rol_id))
                self.conexion.commit()
                
                msg_label.config(text="✅ Mecánico añadido correctamente", fg='green')
                ventana.after(1000, ventana.destroy)
                
            except sqlite3.IntegrityError:
                msg_label.config(text="❌ Error: El código NFC ya existe", fg='red')
            except Exception as e:
                msg_label.config(text=f"❌ Error: {str(e)}", fg='red')
        
        # Botones
        botones_frame = tk.Frame(form_frame, bg='white')
        botones_frame.pack(pady=30)
        
        btn_guardar = tk.Button(botones_frame,
                               text="💾 GUARDAR",
                               font=('Arial', 14, 'bold'),
                               bg='#2196F3',
                               fg='white',
                               width=15,
                               height=2,
                               command=guardar)
        btn_guardar.pack(side='left', padx=10)
        
        btn_cancelar = tk.Button(botones_frame,
                                text="❌ CANCELAR",
                                font=('Arial', 14, 'bold'),
                                bg='#f44336',
                                fg='white',
                                width=15,
                                height=2,
                                command=ventana.destroy)
        btn_cancelar.pack(side='left', padx=10)
        
    def abrir_gestionar_asignaciones(self, matricula):
        """Ventana para gestionar asignaciones de un vehículo"""
        
        # Obtener información del vehículo
        self.cursor.execute('''
            SELECT d.id, d.matricula, ec.nombre_estado, ec.color, d.estado_camion_id
            FROM detalles d
            JOIN estados_camion ec ON d.estado_camion_id = ec.id
            WHERE d.matricula = ?
        ''', (matricula,))
        
        vehiculo = self.cursor.fetchone()
        if not vehiculo:
            return
        
        vehiculo_id = vehiculo[0]
        matricula = vehiculo[1]
        estado_vehiculo = vehiculo[2]
        color_vehiculo = vehiculo[3]
        estado_vehiculo_id = vehiculo[4]
        
        # Crear ventana
        ventana = tk.Toplevel(self.root)
        ventana.title(f"Asignaciones - {matricula}")
        ventana.geometry("700x600")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.transient(self.root)
        
        # Título con color del estado del vehículo
        titulo = tk.Label(ventana,
                        text=f"🚛 ASIGNACIONES - {matricula}",
                        font=('Arial', 18, 'bold'),
                        bg=color_vehiculo,
                        fg='black',
                        pady=15)
        titulo.pack(fill='x')
        
        # Frame para subtítulo con estado selector
        subtitulo_frame = tk.Frame(ventana, bg='white', pady=10)
        subtitulo_frame.pack(fill='x')
        
        # Texto del estado
        tk.Label(subtitulo_frame,
                text="Estado del vehículo:",
                font=('Arial', 12, 'bold'),
                bg='white',
                fg='black').pack(side='left', padx=20)
        
        # Obtener todos los estados disponibles
        self.cursor.execute('SELECT id, nombre_estado FROM estados_camion')
        estados_vehiculo = self.cursor.fetchall()
        
        # Variable para el selector
        estado_vehiculo_var = tk.StringVar()
        estado_vehiculo_var.set(estado_vehiculo)
        
        # Diccionario de estados
        estados_vehiculo_dict = {e[1]: e[0] for e in estados_vehiculo}
        
        # Selector de estado del vehículo
        combo_estado_vehiculo = tk.OptionMenu(subtitulo_frame, estado_vehiculo_var, *estados_vehiculo_dict.keys())
        combo_estado_vehiculo.config(font=('Arial', 11), width=20, bg='#E3F2FD')
        combo_estado_vehiculo.pack(side='left', padx=10)
        
        # Frame principal
        main_frame = tk.Frame(ventana, bg='white', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Sección: Mecánicos asignados actuales
        tk.Label(main_frame, 
                text="👨‍🔧 Mecánicos Asignados:",
                font=('Arial', 14, 'bold'),
                bg='white').pack(anchor='w', pady=(0, 10))
        
        # Frame para lista de asignados
        asignados_frame = tk.Frame(main_frame, bg='#f9f9f9', relief='solid', borderwidth=1)
        asignados_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Obtener asignaciones actuales
        self.cursor.execute('''
            SELECT a.id, m.nombre, et.nombre_estado, et.color, m.id
            FROM asignaciones a
            JOIN mecanicos m ON a.mecanico_id = m.id
            JOIN estados_trabajador et ON a.estado_trabajador_id = et.id
            WHERE a.detalle_id = ?
            ORDER BY a.fecha_asignacion DESC
        ''', (vehiculo_id,))
        
        asignaciones = self.cursor.fetchall()
        
        if asignaciones:
            for asignacion in asignaciones:
                asignacion_id = asignacion[0]
                nombre_mecanico = asignacion[1]
                estado_trabajador = asignacion[2]
                color_estado = asignacion[3]
                mecanico_id = asignacion[4]
                
                # Frame para cada asignación
                asig_frame = tk.Frame(asignados_frame, bg=color_estado, relief='solid', borderwidth=1)
                asig_frame.pack(fill='x', padx=5, pady=3)
                
                # Nombre del mecánico
                tk.Label(asig_frame,
                        text=f"{nombre_mecanico} - {estado_trabajador}",
                        font=('Arial', 11, 'bold'),
                        bg=color_estado,
                        fg='black').pack(side='left', padx=10, pady=5)
                
                # Botón cambiar estado
                btn_cambiar_estado = tk.Button(asig_frame,
                                            text="🔄 Cambiar Estado",
                                            font=('Arial', 9),
                                            bg='#FF9800',
                                            fg='white',
                                            command=lambda aid=asignacion_id: self.cambiar_estado_asignacion_sin_refrescar(aid, ventana, vehiculo_id, matricula))
                btn_cambiar_estado.pack(side='right', padx=5)
                
                # Botón eliminar asignación
                btn_eliminar = tk.Button(asig_frame,
                                        text="❌ Quitar",
                                        font=('Arial', 9),
                                        bg='#f44336',
                                        fg='white',
                                        command=lambda aid=asignacion_id: self.eliminar_asignacion_sin_refrescar(aid, ventana, vehiculo_id, matricula))
                btn_eliminar.pack(side='right', padx=5)
        else:
            tk.Label(asignados_frame,
                    text="No hay mecánicos asignados",
                    font=('Arial', 11, 'italic'),
                    bg='#f9f9f9',
                    fg='gray').pack(pady=20)
        
        # Sección: Añadir nuevo mecánico
        tk.Label(main_frame,
                text="➕ Añadir Mecánico:",
                font=('Arial', 14, 'bold'),
                bg='white').pack(anchor='w', pady=(10, 10))
        
        # Frame para añadir
        add_frame = tk.Frame(main_frame, bg='white')
        add_frame.pack(fill='x')
        
        # Selector de mecánico
        tk.Label(add_frame, text="Mecánico:", font=('Arial', 11), bg='white').pack(side='left', padx=(0, 5))
        
        # Obtener mecánicos disponibles (que no estén ya asignados)
        self.cursor.execute('''
            SELECT m.id, m.nombre
            FROM mecanicos m
            WHERE m.id NOT IN (
                SELECT mecanico_id FROM asignaciones WHERE detalle_id = ?
            )
            ORDER BY m.nombre
        ''', (vehiculo_id,))
        
        mecanicos_disponibles = self.cursor.fetchall()
        
        if mecanicos_disponibles:
            mecanico_var = tk.StringVar()
            mecanico_var.set(f"{mecanicos_disponibles[0][0]} - {mecanicos_disponibles[0][1]}")
            
            mecanicos_dict = {f"{m[0]} - {m[1]}": m[0] for m in mecanicos_disponibles}
            
            combo_mecanicos = tk.OptionMenu(add_frame, mecanico_var, *mecanicos_dict.keys())
            combo_mecanicos.config(font=('Arial', 10), width=20)
            combo_mecanicos.pack(side='left', padx=5)
            
            # Selector de estado del trabajador
            tk.Label(add_frame, text="Estado:", font=('Arial', 11), bg='white').pack(side='left', padx=(10, 5))
            
            self.cursor.execute('SELECT id, nombre_estado FROM estados_trabajador')
            estados_trabajador = self.cursor.fetchall()
            
            estado_var = tk.StringVar()
            estado_var.set(estados_trabajador[0][1])
            
            estados_dict = {e[1]: e[0] for e in estados_trabajador}
            
            combo_estados = tk.OptionMenu(add_frame, estado_var, *estados_dict.keys())
            combo_estados.config(font=('Arial', 10), width=15)
            combo_estados.pack(side='left', padx=5)
            
            # Botón añadir
            def añadir_mecanico():
                mecanico_seleccionado = mecanico_var.get()
                mecanico_id = mecanicos_dict[mecanico_seleccionado]
                estado_nombre = estado_var.get()
                estado_id = estados_dict[estado_nombre]
                
                try:
                    with self.conexion:
                        self.cursor.execute('''
                            INSERT INTO asignaciones (detalle_id, mecanico_id, fecha_asignacion, estado_trabajador_id)
                            VALUES (?, ?, ?, ?)
                        ''', (vehiculo_id, mecanico_id, datetime.now().strftime('%Y-%m-%d'), estado_id))
                    
                    # Cerrar y reabrir ventana SIN refrescar el tablero
                    ventana.destroy()
                    self.abrir_gestionar_asignaciones(matricula)
                    
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo añadir: {str(e)}")
            
            btn_add = tk.Button(add_frame,
                            text="➕ Añadir",
                            font=('Arial', 11, 'bold'),
                            bg='#4CAF50',
                            fg='white',
                            command=añadir_mecanico)
            btn_add.pack(side='left', padx=10)
        else:
            tk.Label(add_frame,
                    text="Todos los mecánicos ya están asignados",
                    font=('Arial', 10, 'italic'),
                    bg='white',
                    fg='gray').pack(side='left')
        
        # Función para guardar y cerrar
        def guardar_y_cerrar():
            # Guardar estado del vehículo
            nuevo_estado_nombre = estado_vehiculo_var.get()
            nuevo_estado_id = estados_vehiculo_dict[nuevo_estado_nombre]
            
            try:
                with self.conexion:
                    self.cursor.execute('''
                        UPDATE detalles
                        SET estado_camion_id = ?
                        WHERE id = ?
                    ''', (nuevo_estado_id, vehiculo_id))
                
                # Cerrar ventana y refrescar tablero
                ventana.destroy()
                self.refrescar()
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")
        
        # Frame de botones finales
        botones_finales = tk.Frame(main_frame, bg='white')
        botones_finales.pack(pady=20)
        
        # Botón guardar y cerrar
        btn_guardar = tk.Button(botones_finales,
                            text="💾 GUARDAR Y CERRAR",
                            font=('Arial', 12, 'bold'),
                            bg='#4CAF50',
                            fg='white',
                            width=20,
                            command=guardar_y_cerrar)
        btn_guardar.pack(side='left', padx=5)
        
        # Botón cerrar sin guardar
        btn_cerrar = tk.Button(botones_finales,
                            text="❌ CANCELAR",
                            font=('Arial', 12, 'bold'),
                            bg='#607D8B',
                            fg='white',
                            width=20,
                            command=lambda: [ventana.destroy(), self.refrescar()])
        btn_cerrar.pack(side='left', padx=5)
    
    def cambiar_estado_asignacion(self, asignacion_id, ventana_padre, vehiculo_id, matricula):
        """Cambia el estado de una asignación"""
        
        # Obtener estados disponibles
        self.cursor.execute('SELECT id, nombre_estado, color FROM estados_trabajador')
        estados = self.cursor.fetchall()
        
        # Crear ventana pequeña
        ventana = tk.Toplevel(ventana_padre)
        ventana.title("Cambiar Estado")
        ventana.geometry("350x300")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.transient(ventana_padre)
        
        tk.Label(ventana,
                text="Selecciona el nuevo estado:",
                font=('Arial', 12, 'bold'),
                bg='white').pack(pady=20)
        
        # Botones para cada estado
        for estado in estados:
            estado_id = estado[0]
            nombre = estado[1]
            color = estado[2]
            
            btn = tk.Button(ventana,
                           text=nombre,
                           font=('Arial', 11, 'bold'),
                           bg=color,
                           fg='black',
                           width=25,
                           height=2,
                           command=lambda eid=estado_id: self.actualizar_estado_asignacion(asignacion_id, eid, ventana, ventana_padre, vehiculo_id, matricula))
            btn.pack(pady=5)
    
    def actualizar_estado_asignacion(self, asignacion_id, nuevo_estado_id, ventana_cambio, ventana_padre, vehiculo_id, matricula):
        """Actualiza el estado en la BD"""
        try:
            with self.conexion:
                self.cursor.execute('''
                    UPDATE asignaciones
                    SET estado_trabajador_id = ?
                    WHERE id = ?
                ''', (nuevo_estado_id, asignacion_id))
            
            # Cerrar ventanas y reabrir
            ventana_cambio.destroy()
            ventana_padre.destroy()
            self.abrir_gestionar_asignaciones(matricula)
            self.refrescar()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {str(e)}")
    
    def eliminar_asignacion(self, asignacion_id, ventana_padre, vehiculo_id, matricula):
        """Elimina una asignación"""
        
        respuesta = messagebox.askyesno("Confirmar",
                                          "¿Quitar este mecánico del vehículo?")
        
        if respuesta:
            try:
                with self.conexion:
                    self.cursor.execute('DELETE FROM asignaciones WHERE id = ?', (asignacion_id,))
                
                # Cerrar y reabrir ventana
                ventana_padre.destroy()
                self.abrir_gestionar_asignaciones(matricula)
                self.refrescar()
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")
                
    def cambiar_estado_asignacion_sin_refrescar(self, asignacion_id, ventana_padre, vehiculo_id, matricula):
        """Cambia el estado de una asignación SIN refrescar el tablero"""
        
        # Obtener estados disponibles
        self.cursor.execute('SELECT id, nombre_estado, color FROM estados_trabajador')
        estados = self.cursor.fetchall()
        
        # Crear ventana pequeña
        ventana = tk.Toplevel(ventana_padre)
        ventana.title("Cambiar Estado")
        ventana.geometry("350x300")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.transient(ventana_padre)
        
        tk.Label(ventana,
                text="Selecciona el nuevo estado:",
                font=('Arial', 12, 'bold'),
                bg='white').pack(pady=20)
        
        # Botones para cada estado
        for estado in estados:
            estado_id = estado[0]
            nombre = estado[1]
            color = estado[2]
            
            btn = tk.Button(ventana,
                        text=nombre,
                        font=('Arial', 11, 'bold'),
                        bg=color,
                        fg='black',
                        width=25,
                        height=2,
                        command=lambda eid=estado_id: self.actualizar_estado_asignacion_sin_refrescar(asignacion_id, eid, ventana, ventana_padre, vehiculo_id, matricula))
            btn.pack(pady=5)

    def actualizar_estado_asignacion_sin_refrescar(self, asignacion_id, nuevo_estado_id, ventana_cambio, ventana_padre, vehiculo_id, matricula):
        """Actualiza el estado en la BD SIN refrescar el tablero"""
        try:
            with self.conexion:
                self.cursor.execute('''
                    UPDATE asignaciones
                    SET estado_trabajador_id = ?
                    WHERE id = ?
                ''', (nuevo_estado_id, asignacion_id))
            
            # Cerrar ventanas y reabrir SIN refrescar tablero
            ventana_cambio.destroy()
            ventana_padre.destroy()
            self.abrir_gestionar_asignaciones(matricula)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {str(e)}")

    def eliminar_asignacion_sin_refrescar(self, asignacion_id, ventana_padre, vehiculo_id, matricula):
        """Elimina una asignación SIN refrescar el tablero"""
        
        respuesta = messagebox.askyesno("Confirmar",
                                        "¿Quitar este mecánico del vehículo?")
        
        if respuesta:
            try:
                with self.conexion:
                    self.cursor.execute('DELETE FROM asignaciones WHERE id = ?', (asignacion_id,))
                
                # Cerrar y reabrir ventana SIN refrescar tablero
                ventana_padre.destroy()
                self.abrir_gestionar_asignaciones(matricula)
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")   
    
    def refrescar(self):
        """Recarga el grid"""
        # Buscar el grid_frame y recargarlo
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) and widget.cget('bg') == '#f5f5f5':
                self.cargar_vehiculos(widget)
                break
    
    def volver_menu(self):
        """Vuelve al menú principal"""
        self.conexion.close()
        self.root.destroy()
        if self.menu_principal:
            self.menu_principal.state('zoomed')
            self.menu_principal.deiconify()

    def abrir_gestionar_asignaciones_autenticado(self, matricula):
        """Abre gestión de asignaciones según el rol del usuario"""
        
        if not hasattr(self, 'usuario_actual'):
            messagebox.showerror("Error", "No hay usuario autenticado")
            return
        
        rol = self.usuario_actual['rol']
        
        if rol == 'jefe':
            # Jefe: acceso total
            self.abrir_gestionar_asignaciones(matricula)
        
        elif rol == 'mecanico':
            # Mecánico: solo puede gestionar su propia asignación
            self.abrir_gestionar_asignacion_mecanico(matricula)
        
        else:
            messagebox.showerror("Error", "Rol no reconocido")

    def volver_menu_autenticado(self):
        """Vuelve al menú solo si es jefe"""
        
        if not hasattr(self, 'usuario_actual'):
            return
        
        rol = self.usuario_actual['rol']
        
        if rol == 'jefe':
            self.volver_menu()
        else:
            messagebox.showwarning("Acceso denegado", 
                                "Solo el jefe puede acceder al menú")

    def abrir_gestionar_asignacion_mecanico(self, matricula):
        """Ventana simplificada para que un mecánico gestione solo su asignación"""
        
        # Obtener información del vehículo
        self.cursor.execute('''
            SELECT d.id, d.matricula, ec.nombre_estado, ec.color
            FROM detalles d
            JOIN estados_camion ec ON d.estado_camion_id = ec.id
            WHERE d.matricula = ?
        ''', (matricula,))
        
        vehiculo = self.cursor.fetchone()
        if not vehiculo:
            return
        
        vehiculo_id = vehiculo[0]
        matricula = vehiculo[1]
        estado_vehiculo = vehiculo[2]
        color_vehiculo = vehiculo[3]
        
        mecanico_id = self.usuario_actual['id']
        nombre_mecanico = self.usuario_actual['nombre']
        
        # Verificar si el mecánico ya está asignado
        self.cursor.execute('''
            SELECT a.id, et.nombre_estado, et.color
            FROM asignaciones a
            JOIN estados_trabajador et ON a.estado_trabajador_id = et.id
            WHERE a.detalle_id = ? AND a.mecanico_id = ?
        ''', (vehiculo_id, mecanico_id))
        
        asignacion = self.cursor.fetchone()
        
        # Crear ventana
        ventana = tk.Toplevel(self.root)
        ventana.title(f"Mi Asignación - {matricula}")
        ventana.geometry("500x600")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.transient(self.root)
        
        # Título
        tk.Label(ventana,
                text=f"🚛 {matricula}",
                font=('Arial', 18, 'bold'),
                bg=color_vehiculo,
                fg='black',
                pady=15).pack(fill='x')
        
        # Frame principal
        main_frame = tk.Frame(ventana, bg='white', padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        tk.Label(main_frame,
                text=f"Mecánico: {nombre_mecanico}",
                font=('Arial', 13, 'bold'),
                bg='white').pack(pady=10)
        
        if asignacion:
            # Ya está asignado - puede cambiar su estado
            asignacion_id = asignacion[0]
            estado_actual = asignacion[1]
            color_estado = asignacion[2]
            
            tk.Label(main_frame,
                    text=f"Estado actual:",
                    font=('Arial', 12),
                    bg='white').pack(pady=10)
            
            tk.Label(main_frame,
                    text=estado_actual,
                    font=('Arial', 16, 'bold'),
                    bg=color_estado,
                    fg='black',
                    relief='solid',
                    borderwidth=2,
                    padx=20,
                    pady=10).pack(pady=10)
            
            tk.Label(main_frame,
                    text="Selecciona nuevo estado:",
                    font=('Arial', 11, 'bold'),
                    bg='white').pack(pady=15)
            
            # Obtener estados disponibles
            self.cursor.execute('SELECT id, nombre_estado, color FROM estados_trabajador')
            estados = self.cursor.fetchall()
            
            # Botones para cambiar estado
            for estado in estados:
                estado_id = estado[0]
                nombre = estado[1]
                color = estado[2]
                
                btn = tk.Button(main_frame,
                            text=nombre,
                            font=('Arial', 11, 'bold'),
                            bg=color,
                            fg='black',
                            width=25,
                            height=2,
                            command=lambda eid=estado_id: self.cambiar_mi_estado(asignacion_id, eid, ventana))
                btn.pack(pady=3)
        
        else:
            # No está asignado - puede asignarse
            tk.Label(main_frame,
                    text="No estás asignado a este vehículo",
                    font=('Arial', 12),
                    bg='white',
                    fg='#666').pack(pady=20)
            
            tk.Label(main_frame,
                    text="¿Deseas asignarte?",
                    font=('Arial', 11, 'bold'),
                    bg='white').pack(pady=10)
            
            # Obtener estados disponibles
            self.cursor.execute('SELECT id, nombre_estado, color FROM estados_trabajador')
            estados = self.cursor.fetchall()
            
            tk.Label(main_frame,
                    text="Selecciona tu estado inicial:",
                    font=('Arial', 10),
                    bg='white').pack(pady=10)
            
            # Botones para asignarse con un estado
            for estado in estados:
                estado_id = estado[0]
                nombre = estado[1]
                color = estado[2]
                
                btn = tk.Button(main_frame,
                            text=f"{nombre}",
                            font=('Arial', 10, 'bold'),
                            bg=color,
                            fg='black',
                            width=30,
                            height=2,
                            command=lambda eid=estado_id: self.asignarme_vehiculo(vehiculo_id, mecanico_id, eid, ventana))
                btn.pack(pady=3)
        
        # Botón cerrar
        tk.Button(main_frame,
                text="❌ CERRAR",
                font=('Arial', 11, 'bold'),
                bg='#607D8B',
                fg='white',
                width=20,
                command=lambda: [ventana.destroy(), self.refrescar()]).pack(pady=20)

    def cambiar_mi_estado(self, asignacion_id, nuevo_estado_id, ventana):
        """Cambia el estado de la asignación del mecánico"""
        try:
            with self.conexion:
                self.cursor.execute('''
                    UPDATE asignaciones
                    SET estado_trabajador_id = ?
                    WHERE id = ?
                ''', (nuevo_estado_id, asignacion_id))
            
            ventana.destroy()
            self.refrescar()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {str(e)}")

    def asignarme_vehiculo(self, vehiculo_id, mecanico_id, estado_id, ventana):
        """Asigna el mecánico al vehículo"""
        try:
            with self.conexion:
                self.cursor.execute('''
                    INSERT INTO asignaciones (detalle_id, mecanico_id, fecha_asignacion, estado_trabajador_id)
                    VALUES (?, ?, ?, ?)
                ''', (vehiculo_id, mecanico_id, datetime.now().strftime('%Y-%m-%d'), estado_id))
            
            ventana.destroy()
            self.refrescar()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo asignar: {str(e)}")
        
    def abrir_ventana_vehiculo_autenticado(self):
        """Abre ventana añadir vehículo solo si es jefe"""
        
        if not hasattr(self, 'usuario_actual'):
            return
        
        rol = self.usuario_actual['rol']
        
        if rol == 'jefe':
            self.abrir_ventana_vehiculo()
        else:
            messagebox.showwarning("Acceso denegado", 
                                "Solo el jefe puede añadir vehículos")
if __name__ == "__main__":
    root = tk.Tk()
    app = TableroVehiculos(root, None)
    root.mainloop()