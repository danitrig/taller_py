import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager

class GestionClientes:
    def __init__(self, root, menu_principal):
        self.root = root
        self.menu_principal = menu_principal
        self.root.title("Gestión de Clientes")
        self.root.geometry("1000x700")
        if hasattr(self.root, 'state'):
            self.root.state('zoomed')
        self.root.configure(bg='#f0f0f0')
        
        # Conectar a la base de datos
        self.db_manager = DatabaseManager()
        
        # Variables para ordenamiento
        self.orden_columna = 'nombre_cliente'  # Columna por defecto
        self.orden_ascendente = True   # Orden ascendente por defecto
        
        self.crear_widgets()
        self.cargar_clientes()
        
        # Al cerrar, volver al menú
        self.root.protocol("WM_DELETE_WINDOW", self.volver_menu)
    
    def crear_widgets(self):
        # CABECERA
        header_frame = tk.Frame(self.root, bg='#3F51B5', height=70)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Botón volver
        btn_volver = tk.Button(header_frame,
                              text="← MENÚ",
                              font=('Arial', 12, 'bold'),
                              bg='#C5CAE9',
                              fg='black',
                              command=self.volver_menu)
        btn_volver.pack(side='left', padx=10, pady=15)
        
        # Título
        titulo = tk.Label(header_frame,
                         text="👥 GESTIÓN DE CLIENTES",
                         font=('Arial', 24, 'bold'),
                         bg='#3F51B5',
                         fg='white')
        titulo.pack(expand=True)
        
        # FRAME PRINCIPAL
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # BOTONES DE ACCIÓN
        botones_frame = tk.Frame(main_frame, bg='#f0f0f0')
        botones_frame.pack(fill='x', pady=(0, 10))
        
        btn_nuevo = tk.Button(botones_frame,
                             text="➕ NUEVO CLIENTE",
                             font=('Arial', 12, 'bold'),
                             bg='#4CAF50',
                             fg='white',
                             command=self.nuevo_cliente)
        btn_nuevo.pack(side='left', padx=5)
        
        btn_editar = tk.Button(botones_frame,
                              text="✏️ EDITAR",
                              font=('Arial', 12, 'bold'),
                              bg='#FF9800',
                              fg='white',
                              command=self.editar_cliente)
        btn_editar.pack(side='left', padx=5)
        
        btn_eliminar = tk.Button(botones_frame,
                                text="🗑️ ELIMINAR",
                                font=('Arial', 12, 'bold'),
                                bg='#f44336',
                                fg='white',
                                command=self.eliminar_cliente)
        btn_eliminar.pack(side='left', padx=5)
        
        btn_refrescar = tk.Button(botones_frame,
                                 text="🔄 REFRESCAR",
                                 font=('Arial', 12, 'bold'),
                                 bg='#607D8B',
                                 fg='white',
                                 command=self.cargar_clientes)
        btn_refrescar.pack(side='left', padx=5)
        
        # TABLA (Treeview)
        tabla_frame = tk.Frame(main_frame, bg='white')
        tabla_frame.pack(fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Crear Treeview
        columnas = ('ID', 'Nombre Cliente', 'Descripción')
        self.tabla = ttk.Treeview(tabla_frame,
                                  columns=columnas,
                                  show='headings',
                                  yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tabla.yview)
        
        # Configurar columnas con ordenamiento clickeable
        self.tabla.heading('ID', text='ID ▼', command=lambda: self.ordenar_por('id_cliente'))
        self.tabla.heading('Nombre Cliente', text='Nombre Cliente ▼', command=lambda: self.ordenar_por('nombre_cliente'))
        self.tabla.heading('Descripción', text='Descripción', command=lambda: self.ordenar_por('descripcion'))
        
        self.tabla.column('ID', width=80, anchor='center')
        self.tabla.column('Nombre Cliente', width=300, anchor='w')
        self.tabla.column('Descripción', width=450, anchor='w')
        
        # Estilo para filas alternadas
        self.tabla.tag_configure('oddrow', background='#f9f9f9')
        self.tabla.tag_configure('evenrow', background='#ffffff')
        
        self.tabla.pack(fill='both', expand=True)

    def ordenar_por(self, columna):
        """Ordena la tabla por la columna seleccionada"""
        if self.orden_columna == columna:
            self.orden_ascendente = not self.orden_ascendente
        else:
            self.orden_columna = columna
            self.orden_ascendente = True
        
        flecha = ' ▲' if self.orden_ascendente else ' ▼'
        
        self.tabla.heading('ID', text='ID' + (flecha if columna == 'id_cliente' else ''))
        self.tabla.heading('Nombre Cliente', text='Nombre Cliente' + (flecha if columna == 'nombre_cliente' else ''))
        self.tabla.heading('Descripción', text='Descripción' + (flecha if columna == 'descripcion' else ''))
        
        self.cargar_clientes()
    
    def cargar_clientes(self):
        """Carga los clientes en la tabla"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Determinar orden
        orden = 'ASC' if self.orden_ascendente else 'DESC'
        columna_orden = self.orden_columna
        
        # Obtener datos ordenados 
        # (Usamos execute_query del db_manager para compatibilidad híbrida)
        query = f'''
            SELECT id_cliente, nombre_cliente, descripcion
            FROM clientes
            ORDER BY {columna_orden} {orden}
        '''
        
        try:
            clientes = self.db_manager.execute_query(query)
            
            # Insertar en tabla
            for index, cliente in enumerate(clientes):
                tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                self.tabla.insert('', 'end', values=list(cliente), tags=(tag,))
        except Exception as e:
            # Si la tabla no existe en la BD sqlite mostrar un mensaje y evitar crash inicial
            if "no such table" in str(e).lower() or "does not exist" in str(e).lower():
                print("Nota: La tabla 'clientes' no existe en la base de datos local SQLite o Postgres.")
            else:
                messagebox.showerror("Error de Carga", f"Error cargando clientes:\n{e}")
    
    def nuevo_cliente(self):
        """Abre ventana para crear nuevo cliente"""
        self.ventana_formulario(modo='nuevo')
    
    def editar_cliente(self):
        """Abre ventana para editar cliente seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un cliente para editar")
            return
        
        item = self.tabla.item(seleccion[0])
        cliente_id = item['values'][0]
        
        self.ventana_formulario(modo='editar', cliente_id=cliente_id)
    
    def eliminar_cliente(self):
        """Elimina el cliente seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un cliente para eliminar")
            return
        
        item = self.tabla.item(seleccion[0])
        cliente_id = item['values'][0]
        nombre = item['values'][1]
        
        respuesta = messagebox.askyesno("Confirmar", f"¿Eliminar al cliente {nombre}?")
        
        if respuesta:
            try:
                self.db_manager.execute_query('DELETE FROM clientes WHERE id_cliente = ?', (cliente_id,), commit=True)
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                self.cargar_clientes()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")
    
    def ventana_formulario(self, modo='nuevo', cliente_id=None):
        """Ventana modal para crear/editar cliente"""
        
        ventana = tk.Toplevel(self.root)
        ventana.title("Nuevo Cliente" if modo == 'nuevo' else "Editar Cliente")
        ventana.geometry("500x350")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.transient(self.root)
        
        # Obtener datos si es edición
        if modo == 'editar' and cliente_id:
            try:
                datos = self.db_manager.execute_query('''
                    SELECT nombre_cliente, descripcion
                    FROM clientes WHERE id_cliente = ?
                ''', (cliente_id,))
                datos = datos[0] if datos else ("", "")
            except Exception as e:
                datos = ("", "")
        else:
            datos = ("", "")
        
        # Frame del formulario
        form_frame = tk.Frame(ventana, bg='#f5f5f5', padx=20, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        # Campos
        tk.Label(form_frame, text="Nombre del Cliente:", font=('Arial', 11, 'bold'), bg='#f5f5f5').pack(anchor='w', pady=(0, 5))
        entry_nombre = tk.Entry(form_frame, font=('Arial', 12))
        entry_nombre.pack(fill='x', pady=(0, 15))
        entry_nombre.insert(0, datos[0] if datos[0] else "")
        entry_nombre.focus()
        
        tk.Label(form_frame, text="Descripción:", font=('Arial', 11, 'bold'), bg='#f5f5f5').pack(anchor='w', pady=(0, 5))
        entry_desc = tk.Text(form_frame, font=('Arial', 12), height=4)
        entry_desc.pack(fill='x', pady=(0, 15))
        entry_desc.insert('1.0', datos[1] if datos[1] else "")
        
        # Mensaje de error interno
        msg_label = tk.Label(form_frame, text="", font=('Arial', 10), bg='#f5f5f5')
        msg_label.pack()
        
        def guardar():
            nombre = entry_nombre.get().strip()
            desc = entry_desc.get("1.0", "end-1c").strip()
            
            if not nombre:
                msg_label.config(text="⚠️ El nombre es obligatorio", fg='red')
                return
            
            try:
                if modo == 'nuevo':
                    self.db_manager.execute_query('''
                        INSERT INTO clientes (nombre_cliente, descripcion)
                        VALUES (?, ?)
                    ''', (nombre, desc), commit=True)
                    msg_label.config(text="✅ Cliente creado correctamente", fg='green')
                else:
                    self.db_manager.execute_query('''
                        UPDATE clientes 
                        SET nombre_cliente = ?, descripcion = ?
                        WHERE id_cliente = ?
                    ''', (nombre, desc, cliente_id), commit=True)
                    msg_label.config(text="✅ Cliente actualizado correctamente", fg='green')
                
                ventana.after(1000, lambda: [ventana.destroy(), self.cargar_clientes()])
                
            except Exception as e:
                msg_label.config(text=f"❌ Error DB: {str(e)}", fg='red')
        
        # Botones
        botones_frame = tk.Frame(form_frame, bg='#f5f5f5')
        botones_frame.pack(pady=10)
        
        btn_guardar = tk.Button(botones_frame,
                               text="💾 GUARDAR",
                               font=('Arial', 11, 'bold'),
                               bg='#4CAF50',
                               fg='white',
                               width=15,
                               command=guardar)
        btn_guardar.pack(side='left', padx=5)
        
        btn_cancelar = tk.Button(botones_frame,
                                text="❌ CANCELAR",
                                font=('Arial', 11, 'bold'),
                                bg='#f44336',
                                fg='white',
                                width=15,
                                command=ventana.destroy)
        btn_cancelar.pack(side='left', padx=5)
        
    def volver_menu(self):
        """Cierra esta ventana y muestra el menú principal"""
        self.root.destroy()
        if hasattr(self, 'menu_principal') and self.menu_principal:
            self.menu_principal.state('zoomed')
            self.menu_principal.deiconify()

