import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry  # ← AÑADIR ESTA LÍNEA
from datetime import datetime

class GestionVehiculos:
    def __init__(self, root, menu_principal):
        self.root = root
        self.menu_principal = menu_principal
        self.root.title("Gestión de Vehículos")
        self.root.geometry("1200x700")
        self.root.state('zoomed')
        self.root.configure(bg='#f0f0f0')
        
        # Conectar a la base de datos
        self.conexion = sqlite3.connect('taller_camarina.db')
        self.cursor = self.conexion.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        # Variables para ordenamiento
        self.orden_columna = 'fecha_entrada'
        self.orden_ascendente = False  # Más recientes primero
               
        self.crear_widgets()
        self.cargar_vehiculos()
        
        # Al cerrar, volver al menú
        self.root.protocol("WM_DELETE_WINDOW", self.volver_menu)
    
    def crear_widgets(self):
        # CABECERA
        header_frame = tk.Frame(self.root, bg='#2196F3', height=70)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Botón volver
        btn_volver = tk.Button(header_frame,
                              text="← MENÚ",
                              font=('Arial', 12, 'bold'),
                              bg='#FFB800',
                              fg='black',
                              command=self.volver_menu)
        btn_volver.pack(side='left', padx=10, pady=15)
        
        # Título
        titulo = tk.Label(header_frame,
                         text="🚛 GESTIÓN DE VEHÍCULOS",
                         font=('Arial', 24, 'bold'),
                         bg='#2196F3',
                         fg='white')
        titulo.pack(expand=True)
        
        # FRAME PRINCIPAL
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # BOTONES DE ACCIÓN
        botones_frame = tk.Frame(main_frame, bg='#f0f0f0')
        botones_frame.pack(fill='x', pady=(0, 10))
        
        btn_nuevo = tk.Button(botones_frame,
                             text="➕ NUEVO VEHÍCULO",
                             font=('Arial', 12, 'bold'),
                             bg='#4CAF50',
                             fg='white',
                             command=self.nuevo_vehiculo)
        btn_nuevo.pack(side='left', padx=5)
        
        btn_editar = tk.Button(botones_frame,
                              text="✏️ EDITAR",
                              font=('Arial', 12, 'bold'),
                              bg='#FF9800',
                              fg='white',
                              command=self.editar_vehiculo)
        btn_editar.pack(side='left', padx=5)
        
        btn_eliminar = tk.Button(botones_frame,
                                text="🗑️ ELIMINAR",
                                font=('Arial', 12, 'bold'),
                                bg='#f44336',
                                fg='white',
                                command=self.eliminar_vehiculo)
        btn_eliminar.pack(side='left', padx=5)
        
        btn_refrescar = tk.Button(botones_frame,
                                 text="🔄 REFRESCAR",
                                 font=('Arial', 12, 'bold'),
                                 bg='#607D8B',
                                 fg='white',
                                 command=self.cargar_vehiculos)
        btn_refrescar.pack(side='left', padx=5)
        
        # TABLA (Treeview)
        tabla_frame = tk.Frame(main_frame, bg='white')
        tabla_frame.pack(fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Crear Treeview
        columnas = ('ID', 'Matrícula', 'Fecha Entrada', 'Fecha Salida', 'Estado')
        self.tabla = ttk.Treeview(tabla_frame,
                                  columns=columnas,
                                  show='headings',
                                  yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tabla.yview)
        
        # Configurar columnas con ordenamiento clickeable
        self.tabla.heading('ID', text='ID', command=lambda: self.ordenar_por('id'))
        self.tabla.heading('Matrícula', text='Matrícula', command=lambda: self.ordenar_por('matricula'))
        self.tabla.heading('Fecha Entrada', text='Fecha Entrada ▼', command=lambda: self.ordenar_por('fecha_entrada'))
        self.tabla.heading('Fecha Salida', text='Fecha Salida', command=lambda: self.ordenar_por('fecha_salida'))
        self.tabla.heading('Estado', text='Estado', command=lambda: self.ordenar_por('estado'))
        
        self.tabla.column('ID', width=50, anchor='center')
        self.tabla.column('Matrícula', width=150, anchor='center')
        self.tabla.column('Fecha Entrada', width=150, anchor='center')
        self.tabla.column('Fecha Salida', width=150, anchor='center')
        self.tabla.column('Estado', width=200, anchor='center')
        
        # Estilo para filas alternadas
        self.tabla.tag_configure('oddrow', background='#f9f9f9')
        self.tabla.tag_configure('evenrow', background='#ffffff')
        
        self.tabla.pack(fill='both', expand=True)
        
    def ordenar_por(self, columna):
        """Ordena la tabla por la columna seleccionada"""
        # Si es la misma columna, invertir orden
        if self.orden_columna == columna:
            self.orden_ascendente = not self.orden_ascendente
        else:
            self.orden_columna = columna
            self.orden_ascendente = True
        
        # Actualizar indicador visual en encabezados
        flecha = ' ▲' if self.orden_ascendente else ' ▼'
        
        # Actualizar todos los encabezados
        self.tabla.heading('ID', text='ID' + (flecha if columna == 'id' else ''))
        self.tabla.heading('Matrícula', text='Matrícula' + (flecha if columna == 'matricula' else ''))
        self.tabla.heading('Fecha Entrada', text='Fecha Entrada' + (flecha if columna == 'fecha_entrada' else ''))
        self.tabla.heading('Fecha Salida', text='Fecha Salida' + (flecha if columna == 'fecha_salida' else ''))
        self.tabla.heading('Estado', text='Estado' + (flecha if columna == 'estado' else ''))
        
        # Recargar datos ordenados
        self.cargar_vehiculos()
        
    def cargar_vehiculos(self):
        """Carga los vehículos en la tabla"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Mapear columnas para SQL
        columna_sql = {
            'id': 'd.id',
            'matricula': 'd.matricula',
            'fecha_entrada': 'd.fecha_entrada',
            'fecha_salida': 'd.fecha_salida',
            'estado': 'ec.nombre_estado'
        }
        
        # Determinar orden
        orden = 'ASC' if self.orden_ascendente else 'DESC'
        columna_orden = columna_sql.get(self.orden_columna, 'd.fecha_entrada')
        
        # Obtener datos ordenados
        query = f'''
            SELECT d.id, d.matricula, d.fecha_entrada, d.fecha_salida, ec.nombre_estado
            FROM detalles d
            JOIN estados_camion ec ON d.estado_camion_id = ec.id
            ORDER BY {columna_orden} {orden}
        '''
        
        self.cursor.execute(query)
        vehiculos = self.cursor.fetchall()
        
        # Insertar en tabla
        for index, vehiculo in enumerate(vehiculos):
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            # Convertir None a vacío para fecha_salida
            vehiculo_lista = list(vehiculo)
            if vehiculo_lista[3] is None:
                vehiculo_lista[3] = ''
            self.tabla.insert('', 'end', values=vehiculo_lista, tags=(tag,))
    
    def nuevo_vehiculo(self):
        """Abre ventana para crear nuevo vehículo"""
        self.ventana_formulario(modo='nuevo')
    
    def editar_vehiculo(self):
        """Abre ventana para editar vehículo seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un vehículo para editar")
            return
        
        item = self.tabla.item(seleccion[0])
        vehiculo_id = item['values'][0]
        
        self.ventana_formulario(modo='editar', vehiculo_id=vehiculo_id)
    
    def eliminar_vehiculo(self):
        """Elimina el vehículo seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un vehículo para eliminar")
            return
        
        item = self.tabla.item(seleccion[0])
        vehiculo_id = item['values'][0]
        matricula = item['values'][1]
        
        # Confirmar eliminación
        respuesta = messagebox.askyesno("Confirmar",
                                        f"¿Eliminar el vehículo {matricula}?\n\n"
                                        "ADVERTENCIA: También se eliminarán todas sus asignaciones.")
        
        if respuesta:
            try:
                with self.conexion:
                    # Eliminar asignaciones primero
                    self.cursor.execute('DELETE FROM asignaciones WHERE detalle_id = ?', (vehiculo_id,))
                    # Eliminar vehículo
                    self.cursor.execute('DELETE FROM detalles WHERE id = ?', (vehiculo_id,))
                
                messagebox.showinfo("Éxito", "Vehículo eliminado correctamente")
                self.cargar_vehiculos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")
    
    def ventana_formulario(self, modo='nuevo', vehiculo_id=None):
        """Ventana modal para crear/editar vehículo"""
        
        # Crear ventana
        ventana = tk.Toplevel(self.root)
        ventana.title("Nuevo Vehículo" if modo == 'nuevo' else "Editar Vehículo")
        ventana.geometry("550x550")  # MÁS GRANDE (antes era 500x450)
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.transient(self.root)
        
        # Si es editar, cargar datos
        if modo == 'editar' and vehiculo_id:
            self.cursor.execute('''
                SELECT matricula, fecha_entrada, fecha_salida, estado_camion_id
                FROM detalles WHERE id = ?
            ''', (vehiculo_id,))
            datos = self.cursor.fetchone()
        
        # Título
        color_titulo = '#4CAF50' if modo == 'nuevo' else '#FF9800'
        titulo = tk.Label(ventana,
                         text="🚛 NUEVO VEHÍCULO" if modo == 'nuevo' else "✏️ EDITAR VEHÍCULO",
                         font=('Arial', 18, 'bold'),
                         bg=color_titulo,
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
        if modo == 'editar':
            entry_matricula.insert(0, datos[0])
        
        # Fecha Entrada con selector
        tk.Label(form_frame, text="Fecha Entrada:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        
        # Determinar fecha inicial
        if modo == 'editar':
            fecha_entrada_inicial = datetime.strptime(datos[1], '%Y-%m-%d')
        else:
            fecha_entrada_inicial = datetime.now()
        
        date_entrada = DateEntry(form_frame,
                                width=27,
                                font=('Arial', 12),
                                background='#4CAF50',
                                foreground='white',
                                borderwidth=2,
                                date_pattern='yyyy-mm-dd',
                                state='readonly', 
                                year=fecha_entrada_inicial.year,
                                month=fecha_entrada_inicial.month,
                                day=fecha_entrada_inicial.day)
        date_entrada.pack(fill='x')
        
        # Fecha Salida con selector (opcional)
        tk.Label(form_frame, text="Fecha Salida:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        
        # Frame para fecha salida + checkbox
        fecha_salida_frame = tk.Frame(form_frame, bg='white')
        fecha_salida_frame.pack(fill='x')
        
        # Determinar fecha inicial para salida
        if modo == 'editar' and datos[2]:
            fecha_salida_inicial = datetime.strptime(datos[2], '%Y-%m-%d')
            tiene_fecha_salida = True
        else:
            fecha_salida_inicial = datetime.now()
            tiene_fecha_salida = False
        
        date_salida = DateEntry(fecha_salida_frame,
                               width=27,
                               font=('Arial', 12),
                               background='#2196F3',
                               foreground='white',
                               borderwidth=2,
                               date_pattern='yyyy-mm-dd',
                               state='readonly', 
                               year=fecha_salida_inicial.year,
                               month=fecha_salida_inicial.month,
                               day=fecha_salida_inicial.day)
        date_salida.pack(side='left')
        
        # Checkbox para activar/desactivar fecha salida
        usar_fecha_salida = tk.BooleanVar(value=tiene_fecha_salida)
        
        def toggle_fecha_salida():
            if usar_fecha_salida.get():
                date_salida.config(state='normal')
            else:
                date_salida.config(state='disabled')
        
        check_fecha_salida = tk.Checkbutton(fecha_salida_frame,
                                           text="Fecha de salida",
                                           font=('Arial', 10),
                                           bg='white',
                                           variable=usar_fecha_salida,
                                           command=toggle_fecha_salida)
        check_fecha_salida.pack(side='left', padx=10)
        
        # Estado inicial del selector de salida
        if not tiene_fecha_salida:
            date_salida.config(state='disabled')
        
        # Estado
        tk.Label(form_frame, text="Estado:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        
        self.cursor.execute('SELECT id, nombre_estado FROM estados_camion')
        estados = self.cursor.fetchall()
        
        estado_var = tk.StringVar()
        if modo == 'editar':
            # Buscar el nombre del estado actual
            estado_actual = next((e[1] for e in estados if e[0] == datos[3]), estados[0][1])
            estado_var.set(estado_actual)
        else:
            estado_var.set(estados[0][1])
        
        estados_dict = {e[1]: e[0] for e in estados}
        combo_estados = tk.OptionMenu(form_frame, estado_var, *estados_dict.keys())
        combo_estados.config(font=('Arial', 12), width=25)
        combo_estados.pack(fill='x')
        
        # Mensaje
        msg_label = tk.Label(form_frame, text="", font=('Arial', 10), bg='white')
        msg_label.pack(pady=10)
        
        # Función guardar
        def guardar():
            matricula = entry_matricula.get().strip().upper()
            fecha_entrada = date_entrada.get_date().strftime('%Y-%m-%d')
            
            # Solo usar fecha de salida si está habilitada
            if usar_fecha_salida.get():
                fecha_salida = date_salida.get_date().strftime('%Y-%m-%d')
            else:
                fecha_salida = None
                
            estado_nombre = estado_var.get()
            estado_id = estados_dict[estado_nombre]
            
            if not matricula:
                msg_label.config(text="⚠️ La matrícula es obligatoria", fg='red')
                return
            
            if not fecha_entrada:
                msg_label.config(text="⚠️ La fecha de entrada es obligatoria", fg='red')
                return
            
            try:
                with self.conexion:
                    if modo == 'nuevo':
                        self.cursor.execute('''
                            INSERT INTO detalles (matricula, fecha_entrada, fecha_salida, estado_camion_id)
                            VALUES (?, ?, ?, ?)
                        ''', (matricula, fecha_entrada, fecha_salida, estado_id))
                    else:
                        self.cursor.execute('''
                            UPDATE detalles
                            SET matricula = ?, fecha_entrada = ?, fecha_salida = ?, estado_camion_id = ?
                            WHERE id = ?
                        ''', (matricula, fecha_entrada, fecha_salida, estado_id, vehiculo_id))
                
                msg_label.config(text="✅ Guardado correctamente", fg='green')
                ventana.after(1000, ventana.destroy)
                self.cargar_vehiculos()
                
            except Exception as e:
                msg_label.config(text=f"❌ Error: {str(e)}", fg='red')
        
        # Botones
        botones_frame = tk.Frame(form_frame, bg='white')
        botones_frame.pack(pady=30)  # MÁS espacio arriba (antes 20)

        btn_guardar = tk.Button(botones_frame,
                            text="💾 GUARDAR",
                            font=('Arial', 14, 'bold'),  # MÁS GRANDE (antes 12)
                            bg='#4CAF50',
                            fg='white',
                            width=15,  # MÁS ANCHO (antes 12)
                            height=2,  # AÑADIR altura
                            command=guardar)
        btn_guardar.pack(side='left', padx=10)  # MÁS separación (antes 5)

        btn_cancelar = tk.Button(botones_frame,
                                text="❌ CANCELAR",
                                font=('Arial', 14, 'bold'),  # MÁS GRANDE (antes 12)
                                bg='#f44336',
                                fg='white',
                                width=15,  # MÁS ANCHO (antes 12)
                                height=2,  # AÑADIR altura
                                command=ventana.destroy)
        btn_cancelar.pack(side='left', padx=10)  # MÁS separación (antes 5)
    def volver_menu(self):
        """Vuelve al menú principal"""
        self.conexion.close()
        self.root.destroy()
        if self.menu_principal:
            self.menu_principal.state('zoomed')
            self.menu_principal.deiconify()

if __name__ == "__main__":
    root = tk.Tk()
    app = GestionVehiculos(root, None)
    root.mainloop()