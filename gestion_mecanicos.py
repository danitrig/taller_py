import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DatabaseManager

class GestionMecanicos:
    def __init__(self, root, menu_principal):
        self.root = root
        self.menu_principal = menu_principal
        self.root.title("Gestión de Mecánicos")
        self.root.geometry("1200x700")
        self.root.state('zoomed')
        self.root.configure(bg='#f0f0f0')
        
        # Conectar a la base de datos
        self.db_manager = DatabaseManager()
        self.conexion = self.db_manager.get_connection()
        self.cursor = self.conexion.cursor()
        if self.db_manager.tipo_bd == 'sqlite':
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
        
        btn_leer_nfc = tk.Button(botones_frame,
                                text="📻 ASIGNAR NFC",
                                font=('Arial', 12, 'bold'),
                                bg='#2196F3',
                                fg='white',
                                command=self.asignar_nfc_a_mecanico)
        btn_leer_nfc.pack(side='left', padx=5)
        
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
        columnas = ('ID', 'Nombre Completo', 'Nombre', 'Código NFC', 'Rol')
        self.tabla = ttk.Treeview(tabla_frame,
                                  columns=columnas,
                                  show='headings',
                                  yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tabla.yview)
        
        # Configurar columnas con ordenamiento clickeable
        self.tabla.heading('ID', text='ID ▼', command=lambda: self.ordenar_por('id'))
        self.tabla.heading('Nombre Completo', text='Nombre Completo ▼', command=lambda: self.ordenar_por('nombrecompleto'))
        self.tabla.heading('Nombre', text='Nombre a mostrar ▼', command=lambda: self.ordenar_por('nombre'))
        self.tabla.heading('Código NFC', text='Código NFC', command=lambda: self.ordenar_por('codigo_nfc'))
        self.tabla.heading('Rol', text='Rol', command=lambda: self.ordenar_por('rol'))

        self.tabla.column('ID', width=50, anchor='center')
        self.tabla.column('Nombre Completo', width=250, anchor='w')
        self.tabla.column('Nombre', width=150, anchor='w')
        self.tabla.column('Código NFC', width=150, anchor='center')
        self.tabla.column('Rol', width=150, anchor='center')
        
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
            
            self.tabla.heading('ID', text='ID' + (flecha if columna == 'id' else ''))
            self.tabla.heading('Nombre Completo', text='Nombre Completo' + (flecha if columna == 'NombreCompleto' else ''))
            self.tabla.heading('Nombre', text='Nombre a mostrar' + (flecha if columna == 'nombre' else ''))
            self.tabla.heading('Código NFC', text='Código NFC' + (flecha if columna == 'codigo_nfc' else ''))
            self.tabla.heading('Rol', text='Rol' + (flecha if columna == 'rol' else ''))
            
            self.cargar_mecanicos()
    
    def cargar_mecanicos(self):
        """Carga los mecánicos en la tabla"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Mapear columnas para SQL
        columna_sql = {
            'id': 'm.id',
            'nombrecompleto': 'm."NombreCompleto"',
            'nombre': 'm.nombre',
            'codigo_nfc': 'm.codigo_nfc',
            'rol': 'r.nombre_rol'
        }
        
        # Determinar orden
        orden = 'ASC' if self.orden_ascendente else 'DESC'
        columna_orden = columna_sql.get(self.orden_columna, 'm.id')
        
        # Obtener datos ordenados
        query = f'''
            SELECT m.id, m."NombreCompleto", m.nombre, m.codigo_nfc, r.nombre_rol
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
            mecanico_lista[4] = mecanico_lista[4].capitalize()
            self.tabla.insert('', 'end', values=mecanico_lista, tags=(tag,))

    
    def asignar_nfc_a_mecanico(self):
        """Prepara el lector NFC para el mecánico seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un mecánico de la lista primero")
            return
            
        item = self.tabla.item(seleccion[0])
        mecanico_id = item['values'][0]
        nombre_completo = item['values'][1]
        
        self.abrir_lector_nfc(mecanico_id, nombre_completo)
    
    def volver_menu(self):
        """Vuelve al menú principal"""
        self.conexion.close()
        self.root.destroy()
        if self.menu_principal:
            self.menu_principal.state('zoomed')
            self.menu_principal.deiconify()
    def abrir_lector_nfc(self, mecanico_id, nombre_mecanico):
        """Abre ventana para leer código NFC y lo asocia al mecánico en la BD"""
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
                text=f"Asignando NFC a:\n{nombre_mecanico}",
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
                
                # Guardar el NFC en base de datos
                try:
                    with self.conexion:
                        self.cursor.execute('''
                            UPDATE mecanicos
                            SET codigo_nfc = ?
                            WHERE id = ?
                        ''', (codigo_nfc, mecanico_id))
                    
                    self.cargar_mecanicos()
                except Exception as e:
                    if "UNIQUE constraint" in str(e) or "unique constraint" in str(e).lower():
                        msg_label.config(text=f"❌ Error: El código ya pertenece a otro mecánico", fg='red')
                        lectura_exitosa[0] = False
                        ventana.after(2000, intentar_lectura)
                        return
                    else:
                        messagebox.showerror("Error", str(e))
                
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