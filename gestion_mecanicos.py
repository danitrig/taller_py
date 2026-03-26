import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class GestionMecanicos:
    def __init__(self, root, menu_principal):
        self.root = root
        self.menu_principal = menu_principal
        self.root.title("Gestión de Mecánicos")
        self.root.geometry("1200x700")
        self.root.state('zoomed')
        self.root.configure(bg='#f0f0f0')
        
        # Conectar a la base de datos
        self.conexion = sqlite3.connect('taller_camarina.db')
        self.cursor = self.conexion.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        # Variables para ordenamiento
        self.orden_columna = 'nombre'  # Columna por defecto
        self.orden_ascendente = True   # Orden ascendente por defecto
        
        self.crear_widgets()
        self.cargar_mecanicos()
        
        # Al cerrar, volver al menú
        self.root.protocol("WM_DELETE_WINDOW", self.volver_menu)
    
    def crear_widgets(self):
        # CABECERA
        header_frame = tk.Frame(self.root, bg='#FF9800', height=70)
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
                         text="👨‍🔧 GESTIÓN DE MECÁNICOS",
                         font=('Arial', 24, 'bold'),
                         bg='#FF9800',
                         fg='white')
        titulo.pack(expand=True)
        
        # FRAME PRINCIPAL
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # BOTONES DE ACCIÓN
        botones_frame = tk.Frame(main_frame, bg='#f0f0f0')
        botones_frame.pack(fill='x', pady=(0, 10))
        
        btn_nuevo = tk.Button(botones_frame,
                             text="➕ NUEVO MECÁNICO",
                             font=('Arial', 12, 'bold'),
                             bg='#4CAF50',
                             fg='white',
                             command=self.nuevo_mecanico)
        btn_nuevo.pack(side='left', padx=5)
        
        btn_editar = tk.Button(botones_frame,
                              text="✏️ EDITAR",
                              font=('Arial', 12, 'bold'),
                              bg='#FF9800',
                              fg='white',
                              command=self.editar_mecanico)
        btn_editar.pack(side='left', padx=5)
        
        btn_eliminar = tk.Button(botones_frame,
                                text="🗑️ ELIMINAR",
                                font=('Arial', 12, 'bold'),
                                bg='#f44336',
                                fg='white',
                                command=self.eliminar_mecanico)
        btn_eliminar.pack(side='left', padx=5)
        
        btn_refrescar = tk.Button(botones_frame,
                                 text="🔄 REFRESCAR",
                                 font=('Arial', 12, 'bold'),
                                 bg='#607D8B',
                                 fg='white',
                                 command=self.cargar_mecanicos)
        btn_refrescar.pack(side='left', padx=5)
        
        # TABLA (Treeview)
        tabla_frame = tk.Frame(main_frame, bg='white')
        tabla_frame.pack(fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Crear Treeview
        columnas = ('ID', 'Nombre', 'Código NFC', 'Rol')
        self.tabla = ttk.Treeview(tabla_frame,
                                  columns=columnas,
                                  show='headings',
                                  yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tabla.yview)
        
        # Configurar columnas con ordenamiento clickeable
        self.tabla.heading('ID', text='ID ▼', command=lambda: self.ordenar_por('id'))
        self.tabla.heading('Nombre', text='Nombre Completo ▼', command=lambda: self.ordenar_por('nombre'))
        self.tabla.heading('Código NFC', text='Código NFC', command=lambda: self.ordenar_por('codigo_nfc'))
        self.tabla.heading('Rol', text='Rol', command=lambda: self.ordenar_por('rol'))

        self.tabla.column('ID', width=50, anchor='center')
        self.tabla.column('Nombre', width=300, anchor='w')
        self.tabla.column('Código NFC', width=150, anchor='center')
        self.tabla.column('Rol', width=150, anchor='center')
        
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
            self.tabla.heading('Nombre', text='Nombre Completo' + (flecha if columna == 'nombre' else ''))
            self.tabla.heading('Código NFC', text='Código NFC' + (flecha if columna == 'codigo_nfc' else ''))
            self.tabla.heading('Rol', text='Rol' + (flecha if columna == 'rol' else ''))
            
            # Recargar datos ordenados
            self.cargar_mecanicos()
    
    def cargar_mecanicos(self):
        """Carga los mecánicos en la tabla"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Mapear columnas para SQL
        columna_sql = {
            'id': 'm.id',
            'nombre': 'm.nombre',
            'codigo_nfc': 'm.codigo_nfc',
            'rol': 'r.nombre_rol'
        }
        
        # Determinar orden
        orden = 'ASC' if self.orden_ascendente else 'DESC'
        columna_orden = columna_sql.get(self.orden_columna, 'm.nombre')
        
        # Obtener datos ordenados
        query = f'''
            SELECT m.id, m.nombre, m.codigo_nfc, r.nombre_rol
            FROM mecanicos m
            JOIN roles r ON m.rol_id = r.id
            ORDER BY {columna_orden} {orden}
        '''
        
        self.cursor.execute(query)
        mecanicos = self.cursor.fetchall()
        
        # Insertar en tabla
        for index, mecanico in enumerate(mecanicos):
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            # Capitalizar el rol para mejor visualización
            mecanico_lista = list(mecanico)
            mecanico_lista[3] = mecanico_lista[3].capitalize()
            self.tabla.insert('', 'end', values=mecanico_lista, tags=(tag,))
    
    def nuevo_mecanico(self):
        """Abre ventana para crear nuevo mecánico"""
        self.ventana_formulario(modo='nuevo')
    
    def editar_mecanico(self):
        """Abre ventana para editar mecánico seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un mecánico para editar")
            return
        
        item = self.tabla.item(seleccion[0])
        mecanico_id = item['values'][0]
        
        self.ventana_formulario(modo='editar', mecanico_id=mecanico_id)
    
    def eliminar_mecanico(self):
        """Elimina el mecánico seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un mecánico para eliminar")
            return
        
        item = self.tabla.item(seleccion[0])
        mecanico_id = item['values'][0]
        nombre = item['values'][1]
        
        # Confirmar eliminación
        respuesta = messagebox.askyesno("Confirmar",
                                        f"¿Eliminar al mecánico {nombre}?\n\n"
                                        "ADVERTENCIA: También se eliminarán todas sus asignaciones.")
        
        if respuesta:
            try:
                # Eliminar asignaciones primero
                self.cursor.execute('DELETE FROM asignaciones WHERE mecanico_id = ?', (mecanico_id,))
                # Eliminar mecánico
                self.cursor.execute('DELETE FROM mecanicos WHERE id = ?', (mecanico_id,))
                self.conexion.commit()
                
                messagebox.showinfo("Éxito", "Mecánico eliminado correctamente")
                self.cargar_mecanicos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")
    
    def ventana_formulario(self, modo='nuevo', mecanico_id=None):
        """Ventana modal para crear/editar mecánico"""
        
        # Crear ventana
        ventana = tk.Toplevel(self.root)
        ventana.title("Nuevo Mecánico" if modo == 'nuevo' else "Editar Mecánico")
        ventana.geometry("550x500")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.transient(self.root)
        
        # Si es editar, cargar datos
        if modo == 'editar' and mecanico_id:
            self.cursor.execute('''
                SELECT nombre, codigo_nfc, rol_id
                FROM mecanicos WHERE id = ?
            ''', (mecanico_id,))
            datos = self.cursor.fetchone()
        
        # Título
        color_titulo = '#4CAF50' if modo == 'nuevo' else '#FF9800'
        titulo = tk.Label(ventana,
                         text="👨‍🔧 NUEVO MECÁNICO" if modo == 'nuevo' else "✏️ EDITAR MECÁNICO",
                         font=('Arial', 18, 'bold'),
                         bg=color_titulo,
                         fg='white',
                         pady=15)
        titulo.pack(fill='x')
        
        # Formulario
        form_frame = tk.Frame(ventana, bg='white', padx=30, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        # Nombre
        tk.Label(form_frame, text="Nombre Completo:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        entry_nombre = tk.Entry(form_frame, font=('Arial', 12), width=30)
        entry_nombre.pack(fill='x')
        if modo == 'editar':
            entry_nombre.insert(0, datos[0])
        
        # Código NFC
        tk.Label(form_frame, text="Código NFC:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))

        nfc_frame = tk.Frame(form_frame, bg='white')
        nfc_frame.pack(fill='x', pady=(0, 5))

        entry_nfc = tk.Entry(nfc_frame, font=('Arial', 12), width=30, state='readonly')
        entry_nfc.pack(side='left', fill='x', expand=True)
        if modo == 'editar' and datos[1]:
            entry_nfc.config(state='normal')
            entry_nfc.insert(0, datos[1])
            entry_nfc.config(state='readonly')

        # Botón para leer NFC
        btn_leer_nfc = tk.Button(nfc_frame,
                                text="📱 Leer NFC",
                                font=('Arial', 10, 'bold'),
                                bg='#2196F3',
                                fg='white',
                                cursor='hand2',
                                command=lambda: self.abrir_lector_nfc(entry_nfc))
        btn_leer_nfc.pack(side='left', padx=(10, 0))
                
        # Rol
        tk.Label(form_frame, text="Rol:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        
        # Obtener roles desde la BD
        self.cursor.execute('SELECT id, nombre_rol FROM roles')
        roles = self.cursor.fetchall()
        
        # Variable para el rol seleccionado
        rol_var = tk.StringVar()
        if modo == 'editar':
            # Buscar el nombre del rol actual
            rol_actual = next((r[1] for r in roles if r[0] == datos[2]), roles[0][1])
            rol_var.set(rol_actual.capitalize())
        else:
            rol_var.set(roles[0][1].capitalize())
        
        # Dropdown de roles
        roles_dict = {r[1].capitalize(): r[0] for r in roles}
        combo_roles = tk.OptionMenu(form_frame, rol_var, *roles_dict.keys())
        combo_roles.config(font=('Arial', 12), width=25)
        combo_roles.pack(fill='x')
        
        # Mensaje de error/éxito
        msg_label = tk.Label(form_frame, text="", font=('Arial', 10), bg='white', fg='red')
        msg_label.pack(pady=10)
        
        # Función para guardar
        def guardar():
            nombre = entry_nombre.get().strip()
            codigo_nfc = entry_nfc.get().strip().upper()
            rol_nombre = rol_var.get()
            rol_id = roles_dict[rol_nombre]
            
            # Validaciones
            if not nombre:
                msg_label.config(text="⚠️ El nombre es obligatorio", fg='red')
                return
            
            if not codigo_nfc:
                msg_label.config(text="⚠️ El código NFC es obligatorio", fg='red')
                return
            
            try:
                if modo == 'nuevo':
                    self.cursor.execute('''
                        INSERT INTO mecanicos (nombre, codigo_nfc, rol_id)
                        VALUES (?, ?, ?)
                    ''', (nombre, codigo_nfc, rol_id))
                else:
                    self.cursor.execute('''
                        UPDATE mecanicos
                        SET nombre = ?, codigo_nfc = ?, rol_id = ?
                        WHERE id = ?
                    ''', (nombre, codigo_nfc, rol_id, mecanico_id))
                
                self.conexion.commit()
                msg_label.config(text="✅ Guardado correctamente", fg='green')
                ventana.after(1000, ventana.destroy)
                self.cargar_mecanicos()
                
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
    
    def volver_menu(self):
        """Vuelve al menú principal"""
        self.conexion.close()
        self.root.destroy()
        self.menu_principal.state('zoomed')
        self.menu_principal.deiconify()
    def abrir_lector_nfc(self, entry_destino):
        """Abre ventana para leer código NFC y escribirlo en el entry"""
        from nfc_reader import NFCReader
        import time
        
        # Crear ventana modal
        ventana = tk.Toplevel(self.root)
        ventana.title("Leer Código NFC")
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
                text="📱 LECTOR DE NFC",
                font=('Arial', 16, 'bold'),
                bg='#2196F3',
                fg='white',
                pady=15).pack(fill='x')
        
        # Frame principal
        main_frame = tk.Frame(ventana, bg='white', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Icono e instrucción
        tk.Label(main_frame,
                text="🔑",
                font=('Arial', 48),
                bg='white').pack(pady=10)
        
        tk.Label(main_frame,
                text="Acerca el llavero NFC al lector",
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
                
                msg_label.config(text=f"✅ Código leído correctamente", fg='green')
                
                # Mostrar código
                tk.Label(main_frame,
                        text=f"Código: {codigo_nfc}",
                        font=('Arial', 11, 'bold'),
                        bg='#E8F5E9',
                        fg='#2E7D32',
                        relief='solid',
                        borderwidth=2,
                        padx=15,
                        pady=10).pack(pady=10)
                
                # Escribir en el entry destino
                entry_destino.config(state='normal')
                entry_destino.delete(0, 'end')
                entry_destino.insert(0, codigo_nfc)
                entry_destino.config(state='readonly')
                
                # Cerrar ventana automáticamente
                ventana.after(1500, ventana.destroy)
                
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
if __name__ == "__main__":
    root = tk.Tk()
    app = GestionMecanicos(root, None)
    root.mainloop()