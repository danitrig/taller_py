import tkinter as tk
from tkinter import ttk, messagebox, colorchooser 
import sqlite3

class GestionEstados:
    def __init__(self, root, menu_principal):
        self.root = root
        self.menu_principal = menu_principal
        self.root.title("Gestión de Estados")
        self.root.geometry("900x600")
        self.root.state('zoomed')
        self.root.configure(bg='#f0f0f0')
        
        # Conectar a la base de datos
        self.conexion = sqlite3.connect('taller_camarina.db')
        self.cursor = self.conexion.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        # Variables para ordenamiento (una por cada tabla)
        self.orden_camion = {'columna': 'nombre_estado', 'ascendente': True}
        self.orden_trabajador = {'columna': 'nombre_estado', 'ascendente': True}       
        self.crear_widgets()
        
        # Al cerrar, volver al menú
        self.root.protocol("WM_DELETE_WINDOW", self.volver_menu)
    
    def crear_widgets(self):
        # CABECERA
        header_frame = tk.Frame(self.root, bg='#9C27B0', height=70)
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
                         text="⚙️ GESTIÓN DE ESTADOS",
                         font=('Arial', 24, 'bold'),
                         bg='#9C27B0',
                         fg='white')
        titulo.pack(expand=True)
        
        # FRAME PRINCIPAL
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Pestañas para separar Estados de Camión y Trabajador
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # PESTAÑA 1: Estados de Camión
        tab_camion = tk.Frame(notebook, bg='white')
        notebook.add(tab_camion, text='🚛 Estados de Camión')
        self.crear_tabla_estados(tab_camion, 'camion')
        
        # PESTAÑA 2: Estados de Trabajador
        tab_trabajador = tk.Frame(notebook, bg='white')
        notebook.add(tab_trabajador, text='👨‍🔧 Estados de Trabajador')
        self.crear_tabla_estados(tab_trabajador, 'trabajador')
    
    def crear_tabla_estados(self, parent, tipo):
        """Crea la tabla de estados (camión o trabajador)"""
        
        # Frame para botones
        botones_frame = tk.Frame(parent, bg='white')
        botones_frame.pack(fill='x', pady=10, padx=10)
        
        # Botón Nuevo
        btn_nuevo = tk.Button(botones_frame,
                             text="➕ NUEVO ESTADO",
                             font=('Arial', 12, 'bold'),
                             bg='#4CAF50',
                             fg='white',
                             command=lambda: self.nuevo_estado(tipo))
        btn_nuevo.pack(side='left', padx=5)
        
        # Botón Editar
        btn_editar = tk.Button(botones_frame,
                              text="✏️ EDITAR",
                              font=('Arial', 12, 'bold'),
                              bg='#FF9800',
                              fg='white',
                              command=lambda: self.editar_estado(tipo))
        btn_editar.pack(side='left', padx=5)
        
        # Botón Eliminar (AÑADIR DESPUÉS DE btn_editar)
        btn_eliminar = tk.Button(botones_frame,
                                text="🗑️ ELIMINAR",
                                font=('Arial', 12, 'bold'),
                                bg='#f44336',  # Rojo
                                fg='white',
                                command=lambda: self.eliminar_estado(tipo))
        btn_eliminar.pack(side='left', padx=5)
        
        # Botón Refrescar
        btn_refrescar = tk.Button(botones_frame,
                                 text="🔄 REFRESCAR",
                                 font=('Arial', 12, 'bold'),
                                 bg='#607D8B',
                                 fg='white',
                                 command=lambda: self.cargar_estados(tipo))
        btn_refrescar.pack(side='left', padx=5)
        
        
        
        # Frame para la tabla
        tabla_frame = tk.Frame(parent, bg='white')
        tabla_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Crear Treeview (tabla)
        columnas = ('ID', 'Nombre Estado', 'Color')
        tabla = ttk.Treeview(tabla_frame,
                            columns=columnas,
                            show='headings',
                            yscrollcommand=scrollbar.set,
                            height=15)
        
        scrollbar.config(command=tabla.yview)
        
        # Configurar columnas
        # Configurar columnas con ordenamiento clickeable
        tabla.heading('ID', text='ID', command=lambda: self.ordenar_estados(tipo, 'id'))
        tabla.heading('Nombre Estado', text='Nombre Estado ▲', command=lambda: self.ordenar_estados(tipo, 'nombre_estado'))
        tabla.heading('Color', text='Color (HEX)', command=lambda: self.ordenar_estados(tipo, 'color'))
        
        tabla.column('ID', width=80, anchor='center')
        tabla.column('Nombre Estado', width=250, anchor='center')
        tabla.column('Color', width=150, anchor='center')
        
        tabla.pack(fill='both', expand=True)
        
        # Guardar referencia a la tabla
        if tipo == 'camion':
            self.tabla_camion = tabla
        else:
            self.tabla_trabajador = tabla
        
        # Cargar datos
        self.cargar_estados(tipo)
    def ordenar_estados(self, tipo, columna):
        """Ordena la tabla de estados por la columna seleccionada"""
        # Seleccionar el diccionario de orden correcto
        orden_dict = self.orden_camion if tipo == 'camion' else self.orden_trabajador
        
        # Si es la misma columna, invertir orden
        if orden_dict['columna'] == columna:
            orden_dict['ascendente'] = not orden_dict['ascendente']
        else:
            orden_dict['columna'] = columna
            orden_dict['ascendente'] = True
        
        # Seleccionar tabla correcta
        tabla = self.tabla_camion if tipo == 'camion' else self.tabla_trabajador
        
        # Actualizar indicador visual en encabezados
        flecha = ' ▲' if orden_dict['ascendente'] else ' ▼'
        
        tabla.heading('ID', text='ID' + (flecha if columna == 'id' else ''))
        tabla.heading('Nombre Estado', text='Nombre Estado' + (flecha if columna == 'nombre_estado' else ''))
        tabla.heading('Color', text='Color (HEX)' + (flecha if columna == 'color' else ''))
        
        # Recargar datos ordenados
        self.cargar_estados(tipo)
        
    def cargar_estados(self, tipo):
            """Carga los estados en la tabla correspondiente"""
            
            # Seleccionar la tabla correcta
            if tipo == 'camion':
                tabla = self.tabla_camion
                tabla_bd = 'estados_camion'
                orden_dict = self.orden_camion
            else:
                tabla = self.tabla_trabajador
                tabla_bd = 'estados_trabajador'
                orden_dict = self.orden_trabajador
            
            # Limpiar tabla
            for item in tabla.get_children():
                tabla.delete(item)
            
            # Determinar orden
            orden = 'ASC' if orden_dict['ascendente'] else 'DESC'
            columna_orden = orden_dict['columna']
            
            # Obtener datos de la BD ordenados
            query = f'SELECT id, nombre_estado, color FROM {tabla_bd} ORDER BY {columna_orden} {orden}'
            self.cursor.execute(query)
            estados = self.cursor.fetchall()
            
            # Insertar en la tabla
            for estado in estados:
                tabla.insert('', 'end', values=estado)
    
    def nuevo_estado(self, tipo):
        """Abre ventana para crear nuevo estado"""
        self.ventana_formulario(tipo, modo='nuevo')
    
    def editar_estado(self, tipo):
        """Abre ventana para editar estado"""
        # Seleccionar tabla correcta
        tabla = self.tabla_camion if tipo == 'camion' else self.tabla_trabajador
        
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un estado para editar")
            return
        
        item = tabla.item(seleccion[0])
        estado_id = item['values'][0]
        
        self.ventana_formulario(tipo, modo='editar', estado_id=estado_id)
        
    def eliminar_estado(self, tipo):
        """Elimina un estado seleccionado"""
        # 1. Seleccionar la tabla correcta (camion o trabajador)
        tabla = self.tabla_camion if tipo == 'camion' else self.tabla_trabajador
        
        # 2. Verificar que hay algo seleccionado
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Selecciona un estado para eliminar")
            return
        
        # 3. Obtener el ID del estado seleccionado
        item = tabla.item(seleccion[0])
        estado_id = item['values'][0]
        nombre_estado = item['values'][1]
        
        # 4. Confirmar eliminación (IMPORTANTE!)
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de eliminar el estado '{nombre_estado}'?\n\n" +
            "⚠️ ADVERTENCIA: Si hay vehículos o trabajadores usando este estado,\n" +
            "la eliminación no será posible."
        )
        
        if not respuesta:
            return
        
        # 5. Intentar eliminar de la base de datos
        try:
            # Determinar tabla de BD
            tabla_bd = 'estados_camion' if tipo == 'camion' else 'estados_trabajador'
            
            with self.conexion:
                # Ejecutar DELETE
                self.cursor.execute(f'DELETE FROM {tabla_bd} WHERE id = ?', (estado_id,))
            
            # Mensaje de éxito
            messagebox.showinfo("Éxito", f"Estado '{nombre_estado}' eliminado correctamente")
            
            # Recargar la tabla
            self.cargar_estados(tipo)
            
        except sqlite3.IntegrityError:
            # Error si hay referencias (FOREIGN KEY)
            messagebox.showerror(
                "Error de integridad",
                f"No se puede eliminar el estado '{nombre_estado}'.\n\n" +
                "Hay vehículos o trabajadores asignados con este estado.\n" +
                "Primero debes cambiarlos a otro estado."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
        
    def ventana_formulario(self, tipo, modo='nuevo', estado_id=None):
        """Ventana para crear/editar estado"""
        
        # Definir tabla de BD
        tabla_bd = 'estados_camion' if tipo == 'camion' else 'estados_trabajador'
        tipo_texto = 'Camión' if tipo == 'camion' else 'Trabajador'
        
        # Crear ventana
        ventana = tk.Toplevel(self.root)
        ventana.title(f"Nuevo Estado de {tipo_texto}" if modo == 'nuevo' else f"Editar Estado de {tipo_texto}")
        ventana.geometry("550x500")
        ventana.resizable(False, False)
        ventana.grab_set()
        ventana.transient(self.root)
        
        # Si es editar, cargar datos
        if modo == 'editar' and estado_id:
            self.cursor.execute(f'SELECT nombre_estado, color FROM {tabla_bd} WHERE id = ?', (estado_id,))
            datos = self.cursor.fetchone()
        
        # Título
        color_titulo = '#4CAF50' if modo == 'nuevo' else '#FF9800'
        titulo = tk.Label(ventana,
                         text=f"⚙️ {'NUEVO' if modo == 'nuevo' else 'EDITAR'} ESTADO DE {tipo_texto.upper()}",
                         font=('Arial', 16, 'bold'),
                         bg=color_titulo,
                         fg='white',
                         pady=15)
        titulo.pack(fill='x')
        
        # Formulario
        form_frame = tk.Frame(ventana, bg='white', padx=30, pady=20)
        form_frame.pack(fill='both', expand=True)
        
        # Nombre del Estado
        tk.Label(form_frame, text="Nombre del Estado:", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        entry_nombre = tk.Entry(form_frame, font=('Arial', 12), width=30)
        entry_nombre.pack(fill='x')
        if modo == 'editar':
            entry_nombre.insert(0, datos[0])
        
        # Color (HEX)
        tk.Label(form_frame, text="Color (formato HEX):", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(10, 5))
        
        color_frame = tk.Frame(form_frame, bg='white')
        color_frame.pack(fill='x')
        
        entry_color = tk.Entry(color_frame, font=('Arial', 12), width=20)
        entry_color.pack(side='left')
        if modo == 'editar':
            entry_color.insert(0, datos[1])
        else:
            entry_color.insert(0, '#90EE90')
        
        # Vista previa del color (clickeable)
        preview_frame = tk.Frame(color_frame, bg=entry_color.get(), width=50, height=30, relief='solid', borderwidth=2, cursor='hand2')
        preview_frame.pack(side='left', padx=10)
        
        # Hacer clickeable el cuadrado
        preview_frame.bind('<Button-1>', lambda e: abrir_selector_color())
        
        # Actualizar vista previa al escribir
        def actualizar_preview(event=None):
            try:
                color = entry_color.get()
                preview_frame.config(bg=color)
            except:
                pass
        
        entry_color.bind('<KeyRelease>', actualizar_preview)
        
        # Función para abrir el selector
        def abrir_selector_color():
            # Obtener color actual como predeterminado
            color_actual = entry_color.get()
            
            # Abrir selector de color
            color_elegido = colorchooser.askcolor(
                color=color_actual,
                title="Selecciona un color"
            )
            
            # color_elegido devuelve una tupla: ((R, G, B), '#HEXCOLOR')
            if color_elegido[1]:  # Si se eligió un color (no se canceló)
                entry_color.delete(0, 'end')
                entry_color.insert(0, color_elegido[1])
                actualizar_preview()
        
        # Mensaje
        msg_label = tk.Label(form_frame, text="", font=('Arial', 10), bg='white')
        msg_label.pack(pady=10)
        
        # Función guardar
        def guardar():
            nombre = entry_nombre.get().strip()
            color = entry_color.get().strip()
            
            if not nombre:
                msg_label.config(text="⚠️ El nombre es obligatorio", fg='red')
                return
            
            if not color or not color.startswith('#'):
                msg_label.config(text="⚠️ El color debe estar en formato HEX (#RRGGBB)", fg='red')
                return
            
            try:
                with self.conexion:
                    if modo == 'nuevo':
                        self.cursor.execute(f'''
                            INSERT INTO {tabla_bd} (nombre_estado, color)
                            VALUES (?, ?)
                        ''', (nombre, color))
                    else:
                        self.cursor.execute(f'''
                            UPDATE {tabla_bd}
                            SET nombre_estado = ?, color = ?
                            WHERE id = ?
                        ''', (nombre, color, estado_id))
                
                msg_label.config(text="✅ Guardado correctamente", fg='green')
                ventana.after(1000, ventana.destroy)
                self.cargar_estados(tipo)
                
            except sqlite3.IntegrityError:
                msg_label.config(text="❌ Error: Ya existe un estado con ese nombre", fg='red')
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
        if self.menu_principal:
            self.menu_principal.state('zoomed')
            self.menu_principal.deiconify()

if __name__ == "__main__":
    root = tk.Tk()
    app = GestionEstados(root, None)
    root.mainloop()