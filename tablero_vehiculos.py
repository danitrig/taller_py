import tkinter as tk
from tkinter import ttk, messagebox
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
                       ec.color, ec.nombre_estado, c.nombre_cliente, d.num_factura
                FROM detalles d
                JOIN estados_camion ec ON d.estado_camion_id = ec.id
                LEFT JOIN clientes c ON d.cl_id = c.id_cliente
                ORDER BY d.id DESC
            '''
        else:
            # Ocultar terminados
            query = '''
                SELECT d.id, d.matricula, d.fecha_entrada, d.fecha_salida, 
                       ec.color, ec.nombre_estado, c.nombre_cliente, d.num_factura
                FROM detalles d
                JOIN estados_camion ec ON d.estado_camion_id = ec.id
                LEFT JOIN clientes c ON d.cl_id = c.id_cliente
                WHERE ec.nombre_estado != 'Terminado'
                ORDER BY d.id DESC
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
                    vehiculo = vehiculos_pagina[posicion]
                    vehiculo_id = vehiculo[0]
                    matricula = vehiculo[1]
                    fecha_entrada = vehiculo[2]
                    fecha_salida = vehiculo[3]
                    color_camion = vehiculo[4]
                    nombre_estado_camion = vehiculo[5]
                    nombre_cliente = vehiculo[6] if vehiculo[6] else ""
                    num_factura = vehiculo[7] if vehiculo[7] else ""
                    
                    # Buscar tareas y sus mecánicos asignados
                    # Manejo dual asegurando que se extraen correctamente las tareas de dt_id
                    self.cursor.execute('''
                        SELECT t.descrip, m.id, m.nombre, et.color
                        FROM tareas t
                        LEFT JOIN asignaciones a ON t.id_tarea = a.tarea_id
                        LEFT JOIN mecanicos m ON a.mecanico_id = m.id
                        LEFT JOIN estados_trabajador et ON a.estado_trabajador_id = et.id
                        WHERE t.id_dt = ?
                        ORDER BY t.id_tarea ASC
                    ''', (vehiculo_id,))
                    
                    tareas_asignadas = self.cursor.fetchall()
                    
                else:
                    # Celda vacía
                    matricula = ""
                    fecha_entrada = ""
                    fecha_salida = None
                    color_camion = "#FFFFFF"
                    nombre_cliente = ""
                    num_factura = ""
                    tareas_asignadas = []
                
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
                                             color_camion, num_factura, nombre_cliente, tareas_asignadas)
                
                posicion += 1
    def autenticar_nfc(self, accion_callback, *args):


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
                            color_camion, num_factura, nombre_cliente, tareas_asignadas):
        """Crea el contenido de una celda de vehículo"""
        
        def format_fecha(f_str):
            if not f_str: return ""
            partes = str(f_str).split(' ')
            fs = partes[0].split('-')
            hora = partes[1][:5] if len(partes) > 1 else ""
            if len(fs) == 3:
                return f"{fs[2]}-{fs[1]} {hora}".strip()
            return f_str

        fecha_entrada = format_fecha(fecha_entrada)
        fecha_texto = fecha_entrada
        if fecha_salida:
            fecha_salida = format_fecha(fecha_salida)
            fecha_texto += f"  |  {fecha_salida}"
        
        # CABECERA
        cabecera = tk.Frame(celda, bg=color_camion)
        cabecera.pack(fill='x')
        
        # Etiqueta unificada de fechas
        tk.Label(cabecera, 
                 text=fecha_texto,
                 font=('Arial', 8, 'bold'),
                 bg=color_camion,
                 fg='#333333').pack(pady=(2, 0))
        
        # Num factura SIEMPRE OCUPA ESPACIO, si está vacío pongo espacios
        tk.Label(cabecera, 
                 text=num_factura if num_factura else " ",
                 font=('Arial', 10, 'bold'),
                 bg=color_camion,
                 fg='#222222').pack()
                     
        # Matrícula (Reducido de 24 a 18 para que quepa en 184px de ancho)
        matricula_label = tk.Label(cabecera, 
                            text=matricula,
                            font=('Arial', 18, 'bold'),
                            bg=color_camion,
                            fg='black')
        matricula_label.pack(pady=0)
        
        # Nombre Cliente SIEMPRE OCUPA ESPACIO
        tk.Label(cabecera, 
                 text=nombre_cliente.upper() if nombre_cliente else " ",
                 font=('Arial', 9, 'bold'),
                 bg=color_camion,
                 fg='#333333').pack(pady=(0, 2))
        
        # LÍNEA SEPARADORA FINA MÚLTIPLE (Estilo imagen)
        tk.Frame(celda, bg='white', height=2).pack(fill='x')
        tk.Frame(celda, bg='black', height=2).pack(fill='x')
        
        # TAREAS
        tareas_frame = tk.Frame(celda, bg='#FFFFFF')
        tareas_frame.pack(fill='both', expand=True, padx=0, pady=0)
        
        if tareas_asignadas:
            for tarea_data in tareas_asignadas:
                descrip_tarea = tarea_data[0] or ""
                mecanico_id = tarea_data[1]
                nombre_mecanico = tarea_data[2] or ""
                color_et = tarea_data[3] or "#DDDDDD"  # GRIS si no hay mecánico o estado
                
                # Tratar iniciales del mecánico (Ej: "02 DMC")
                if mecanico_id and nombre_mecanico:
                    if len(nombre_mecanico) <= 3:
                        iniciales = nombre_mecanico.upper()
                    else:
                        partes_nombre = nombre_mecanico.split()
                        if len(partes_nombre) == 1:
                            iniciales = nombre_mecanico[:3].upper()
                        else:
                            iniciales = "".join([p[0].upper() for p in partes_nombre[:3]])
                    mecanico_texto = f"{mecanico_id:02d} {iniciales}"
                else:
                    mecanico_texto = ""
                
                # Fila contenedora de esta tarea
                fila_tarea = tk.Frame(tareas_frame, bg=color_et, borderwidth=1, relief='solid')
                fila_tarea.pack(fill='x', pady=0)

                # Columna Izquierda (Mecánico)
                left_col = tk.Frame(fila_tarea, bg=color_et, width=65)
                left_col.pack(side='left', fill='y')
                left_col.pack_propagate(False)
                
                tk.Label(left_col, text=mecanico_texto, font=('Arial', 10, 'bold'), bg=color_et, fg='black').pack(expand=True)
                
                # Separador vertical
                tk.Frame(fila_tarea, bg='black', width=1).pack(side='left', fill='y')
                
                # Columna Derecha (Tarea descripción)
                right_col = tk.Frame(fila_tarea, bg=color_et)
                right_col.pack(side='left', fill='both', expand=True)
                
                tk.Label(right_col, text=descrip_tarea, font=('Arial', 9), bg=color_et, fg='black', justify='left', anchor='w').pack(fill='both', expand=True, padx=4)
        
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
        ventana.geometry("550x700")
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
        
        # Cliente (Combobox)
        tk.Label(form_frame, text="Cliente:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        try:
            self.cursor.execute('SELECT id_cliente, nombre_cliente FROM clientes ORDER BY nombre_cliente ASC')
            clientes_db = self.cursor.fetchall()
        except:
            clientes_db = []
            
        clientes_dict = {c[1]: c[0] for c in clientes_db}
        cliente_var = tk.StringVar()
        
        opciones_clientes = ["-- Sin Cliente --"] + list(clientes_dict.keys())
        cliente_var.set(opciones_clientes[0])
        
        combo_clientes = ttk.Combobox(form_frame, textvariable=cliente_var, values=opciones_clientes, font=('Arial', 12), state='readonly')
        combo_clientes.pack(fill='x')
        
        # Factura
        tk.Label(form_frame, text="Nº Factura (Opcional):", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        entry_factura = tk.Entry(form_frame, font=('Arial', 12), width=30)
        entry_factura.pack(fill='x')
        
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
            
            factura_val = entry_factura.get().strip() or None
            cl_nombre = cliente_var.get()
            cl_id = clientes_dict.get(cl_nombre, None)
            
            if not matricula:
                msg_label.config(text="⚠️ La matrícula es obligatoria", fg='red')
                return
            
            try:
                with self.conexion:
                    self.cursor.execute('''
                        INSERT INTO detalles (matricula, fecha_entrada, fecha_salida, estado_camion_id, num_factura, cl_id)
                        VALUES (?, ?, NULL, ?, ?, ?)
                    ''', (matricula, fecha_entrada, estado_id, factura_val, cl_id))
                
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
        

    def abrir_gestionar_tareas(self, matricula):
        """Ventana principal (Jefe) para gestionar tareas de un vehículo"""
        self.cursor.execute('SELECT d.id, d.matricula, ec.nombre_estado, ec.color FROM detalles d JOIN estados_camion ec ON d.estado_camion_id = ec.id WHERE d.matricula = ?', (matricula,))
        vehiculo = self.cursor.fetchone()
        if not vehiculo: return
        vehiculo_id, matricula, estado_vehiculo, color_vehiculo = vehiculo
        
        ventana = tk.Toplevel(self.root)
        ventana.title(f"Tareas - {matricula}")
        ventana.geometry("900x750")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.transient(self.root)
        
        tk.Label(ventana, text=f"🚛 TAREAS - {matricula}", font=('Arial', 18, 'bold'), bg=color_vehiculo, fg='black', pady=15).pack(fill='x')
        
        main_frame = tk.Frame(ventana, bg='white', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Añadir Nueva Tarea
        add_frame = tk.Frame(main_frame, bg='#f0f0f0', pady=5, padx=5, relief='solid', borderwidth=1)
        add_frame.pack(fill='x', pady=5)
        tk.Label(add_frame, text="Nueva Tarea:", font=('Arial', 11, 'bold'), bg='#f0f0f0').pack(side='left', padx=5)
        entry_tarea = tk.Entry(add_frame, font=('Arial', 11), width=40)
        entry_tarea.pack(side='left', padx=5)
        
        def guardar_tarea():
            descrip = entry_tarea.get().strip()
            if descrip:
                try:
                    with self.conexion:
                        self.cursor.execute('INSERT INTO tareas (descrip, id_dt) VALUES (?, ?)', (descrip, vehiculo_id))
                    ventana.destroy()
                    self.abrir_gestionar_tareas(matricula)
                except Exception as e:
                    messagebox.showerror("Error", str(e))
        tk.Button(add_frame, text="➕ Agregar Tarea", font=('Arial', 10, 'bold'), bg='#4CAF50', fg='white', command=guardar_tarea).pack(side='left', padx=5)
        
        # Canvas enrollable para Tareas
        canvas_contenedor = tk.Frame(main_frame, bg='white')
        canvas_contenedor.pack(fill='both', expand=True, pady=10)
        canvas = tk.Canvas(canvas_contenedor, bg='white')
        scrollbar = ttk.Scrollbar(canvas_contenedor, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.cursor.execute('SELECT id_tarea, descrip FROM tareas WHERE id_dt = ? ORDER BY id_tarea ASC', (vehiculo_id,))
        tareas = self.cursor.fetchall()
        
        if not tareas:
            tk.Label(scrollable_frame, text="No hay tareas registradas.", font=('Arial', 11, 'italic'), bg='white', fg='gray').pack(pady=20)
            
        for tarea in tareas:
            tarea_id, descrip = tarea
            tarea_frame = tk.Frame(scrollable_frame, bg='#fff', relief='solid', borderwidth=1)
            tarea_frame.pack(fill='x', pady=5, padx=5)
            
            tarea_header = tk.Frame(tarea_frame, bg='#fff')
            tarea_header.pack(fill='x', padx=10, pady=5)
            
            tk.Label(tarea_header, text=f"🔧 {descrip}", font=('Arial', 12, 'bold'), bg='#fff').pack(side='left')
            tk.Button(tarea_header, text="🗑️ Eliminar Tarea", font=('Arial', 9), bg='#f44336', fg='white', 
                      command=lambda t=tarea_id: self.eliminar_tarea(t, ventana, matricula)).pack(side='right')
            
            # Asignaciones de esta tarea
            asig_frame = tk.Frame(tarea_frame, bg='#f9f9f9', relief='flat')
            asig_frame.pack(fill='x', padx=10, pady=5)
            
            self.cursor.execute('''SELECT a.id, m.nombre, et.nombre_estado, et.color 
                                   FROM asignaciones a JOIN mecanicos m ON a.mecanico_id = m.id
                                   JOIN estados_trabajador et ON a.estado_trabajador_id = et.id
                                   WHERE a.tarea_id = ? ORDER BY a.fecha_asignacion DESC''', (tarea_id,))
            asignaciones = self.cursor.fetchall()
            
            if asignaciones:
                for asig in asignaciones:
                    aid, mnombre, enombre, ecolor = asig
                    f = tk.Frame(asig_frame, bg=ecolor, relief='solid', borderwidth=1)
                    f.pack(fill='x', pady=2)
                    tk.Label(f, text=f"{mnombre} - {enombre}", font=('Arial', 10, 'bold'), bg=ecolor).pack(side='left', padx=10, pady=2)
                    tk.Button(f, text="❌ Quitar", bg='#f44336', fg='white', command=lambda a=aid: self.eliminar_asignacion_tarea(a, ventana, matricula)).pack(side='right', padx=5)
                    tk.Button(f, text="🔄 Estado", bg='#FF9800', fg='white', command=lambda a=aid: self.cambiar_estado_tarea(a, ventana, matricula)).pack(side='right', padx=5)
            else:
                tk.Label(asig_frame, text="Sin mecánicos asignados", font=('Arial', 9, 'italic'), bg='#f9f9f9').pack(anchor='w')
                
            # Añadir mecanico a tarea
            add_mec_f = tk.Frame(tarea_frame, bg='#fff')
            add_mec_f.pack(fill='x', padx=10, pady=5)
            
            self.cursor.execute('SELECT id, nombre FROM mecanicos WHERE id NOT IN (SELECT mecanico_id FROM asignaciones WHERE tarea_id = ?)', (tarea_id,))
            mecs_disp = self.cursor.fetchall()
            if mecs_disp:
                mec_var = tk.StringVar(value=mecs_disp[0][1])
                mecs_dict = {m[1]: m[0] for m in mecs_disp}
                tk.OptionMenu(add_mec_f, mec_var, *mecs_dict.keys()).pack(side='left')
                tk.Button(add_mec_f, text="➕ Asignar a Tarea", font=('Arial', 9), bg='#2196F3', fg='white', 
                          command=lambda t=tarea_id, mv=mec_var, md=mecs_dict: self.asignar_mec_tarea(t, md[mv.get()], ventana, matricula)).pack(side='left', padx=5)
                
        # Botones finales
        tk.Button(ventana, text="❌ CERRAR", font=('Arial', 12, 'bold'), bg='#607D8B', fg='white', command=lambda: [ventana.destroy(), self.refrescar()]).pack(pady=10)

    def asignar_mec_tarea(self, tarea_id, mecanico_id, ventana, matricula):
        try:
            with self.conexion:
                self.cursor.execute("INSERT INTO asignaciones (tarea_id, mecanico_id, fecha_asignacion, estado_trabajador_id) VALUES (?, ?, date('now'), 1)", (tarea_id, mecanico_id))
            ventana.destroy()
            self.abrir_gestionar_tareas(matricula)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def eliminar_asignacion_tarea(self, asignacion_id, ventana, matricula):
        if messagebox.askyesno("Confirmar", "¿Quitar mecánico?"):
            try:
                with self.conexion:
                    self.cursor.execute('DELETE FROM asignaciones WHERE id = ?', (asignacion_id,))
                ventana.destroy()
                self.abrir_gestionar_tareas(matricula)
                self.refrescar()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
    def eliminar_tarea(self, tarea_id, ventana, matricula):
        if messagebox.askyesno("Confirmar", "¿Eliminar esta tarea y todos sus mecánicos asignados?"):
            try:
                with self.conexion:
                    self.cursor.execute('DELETE FROM asignaciones WHERE tarea_id = ?', (tarea_id,))
                    self.cursor.execute('DELETE FROM tareas WHERE id_tarea = ?', (tarea_id,))
                ventana.destroy()
                self.abrir_gestionar_tareas(matricula)
                self.refrescar()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
    def cambiar_estado_tarea(self, asignacion_id, ventana_padre, matricula):
        self.cursor.execute('SELECT id, nombre_estado, color FROM estados_trabajador')
        estados = self.cursor.fetchall()
        ventana = tk.Toplevel(ventana_padre)
        ventana.geometry("350x300")
        for est in estados:
            tk.Button(ventana, text=est[1], bg=est[2], font=('Arial', 11, 'bold'), height=2, width=25,
                      command=lambda eid=est[0]: self.set_estado_asignacion(asignacion_id, eid, ventana, ventana_padre, matricula)).pack(pady=5)
                      
    def set_estado_asignacion(self, asig_id, est_id, vtn, vtn_p, matricula):
        with self.conexion:
            self.cursor.execute('UPDATE asignaciones SET estado_trabajador_id = ? WHERE id = ?', (est_id, asig_id))
        vtn.destroy()
        vtn_p.destroy()
        self.abrir_gestionar_tareas(matricula)
        self.refrescar()

    def abrir_gestionar_asignaciones_autenticado(self, matricula):
        if not hasattr(self, 'usuario_actual'): return
        rol = self.usuario_actual['rol']
        if rol == 'jefe':
            self.abrir_gestionar_tareas(matricula)
        elif rol == 'mecanico':
            self.abrir_mis_tareas_mecanico(matricula)

    def abrir_mis_tareas_mecanico(self, matricula):
        self.cursor.execute('SELECT d.id FROM detalles d WHERE d.matricula = ?', (matricula,))
        vehiculo = self.cursor.fetchone()
        if not vehiculo: return
        vehiculo_id = vehiculo[0]
        mecanico_id = self.usuario_actual['id']
        
        ventana = tk.Toplevel(self.root)
        ventana.title(f"Mis Tareas - {matricula}")
        ventana.geometry("500x600")
        tk.Label(ventana, text=f"🚛 {matricula} - Mis Tareas", font=('Arial', 16, 'bold')).pack(pady=10)
        
        main_frame = tk.Frame(ventana, bg='white', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Tareas no asignadas al mecanico
        tk.Label(main_frame, text="Asignarse a una tarea:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w')
        self.cursor.execute('''SELECT id_tarea, descrip FROM tareas WHERE id_dt = ? 
                               AND id_tarea NOT IN (SELECT tarea_id FROM asignaciones WHERE mecanico_id = ?)''', (vehiculo_id, mecanico_id))
        tareas_disp = self.cursor.fetchall()
        if tareas_disp:
            for t in tareas_disp:
                tk.Button(main_frame, text=f"Asignarme a: {t[1]}", font=('Arial', 10), command=lambda tid=t[0]: self.mecanico_asignarse_tarea(tid, mecanico_id, ventana, matricula)).pack(pady=5)
        else:
            tk.Label(main_frame, text="No hay tareas libres", bg='white').pack()
            
        # Mis Tareas
        tk.Label(main_frame, text="Mis Asignaciones:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(20,5))
        self.cursor.execute('''SELECT a.id, t.descrip, et.nombre_estado, et.color
                               FROM asignaciones a JOIN tareas t ON a.tarea_id = t.id_tarea
                               JOIN estados_trabajador et ON a.estado_trabajador_id = et.id
                               WHERE t.id_dt = ? AND a.mecanico_id = ?''', (vehiculo_id, mecanico_id))
        mis_asigs = self.cursor.fetchall()
        if mis_asigs:
            for asig in mis_asigs:
                asig_id, desc, enombre, ecolor = asig
                f = tk.Frame(main_frame, bg=ecolor, relief='solid', borderwidth=1)
                f.pack(fill='x', pady=5)
                tk.Label(f, text=f"{desc} - {enombre}", bg=ecolor, font=('Arial', 11, 'bold')).pack(side='left', padx=10, pady=5)
                tk.Button(f, text="Cambiar Estado", font=('Arial', 9), command=lambda aid=asig_id: self.cambiar_estado_tarea(aid, ventana, matricula)).pack(side='right', padx=10)
        
        tk.Button(ventana, text="❌ CERRAR", command=lambda: [ventana.destroy(), self.refrescar()]).pack(pady=10)

    def mecanico_asignarse_tarea(self, tarea_id, mecanico_id, ventana, matricula):
        try:
            with self.conexion:
                self.cursor.execute("INSERT INTO asignaciones (tarea_id, mecanico_id, fecha_asignacion, estado_trabajador_id) VALUES (?, ?, date('now'), 1)", (tarea_id, mecanico_id))
            ventana.destroy()
            self.abrir_mis_tareas_mecanico(matricula)
        except Exception as e:
            messagebox.showerror("Error", str(e))

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