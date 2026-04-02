import tkinter as tk
from database import DatabaseManager

class MenuPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Talleres Camarina - Menú Principal")
        self.root.geometry("800x600")
        self.root.state('zoomed')
        self.root.configure(bg='#1e3a8a')
        
        self.crear_widgets()
        
        self.abrir_tablero() 
    
    def crear_widgets(self):
        # Frame contenedor principal
        main_frame = tk.Frame(self.root, bg='#1e3a8a')
        main_frame.pack(expand=True)
        
        # Logo/Título
        titulo = tk.Label(main_frame,
                         text="🚛 TALLERES CAMARINA",
                         font=('Arial', 48, 'bold'),
                         bg='#1e3a8a',
                         fg='#FFB800')
        titulo.pack(pady=30)
        
        subtitulo = tk.Label(main_frame,
                            text="Sistema de Gestión de Taller",
                            font=('Arial', 20),
                            bg='#1e3a8a',
                            fg='white')
        subtitulo.pack(pady=10)
        
        # Frame para los botones
        botones_frame = tk.Frame(main_frame, bg='#1e3a8a')
        botones_frame.pack(pady=50)
        
        # Botones del menú
        botones = [
            {
                "texto": "📊 TABLERO DE VEHÍCULOS",
                "color": "#4CAF50",
                "comando": self.abrir_tablero
            },
            {
                "texto": "🚛 GESTIÓN DE VEHÍCULOS",
                "color": "#2196F3",
                "comando": self.abrir_gestion_vehiculos
            },
            {
                "texto": "👨‍🔧 GESTIÓN DE MECÁNICOS",
                "color": "#FF9800",
                "comando": self.abrir_gestion_mecanicos
            },
            {
                "texto": "⚙️ GESTIÓN DE ESTADOS",
                "color": "#9C27B0",
                "comando": self.abrir_gestion_estados
            },
            {
                "texto": "👥 GESTIÓN DE CLIENTES",
                "color": "#3F51B5",
                "comando": self.abrir_gestion_clientes
            },
            {
                "texto": "❌ SALIR",
                "color": "#f44336",
                "comando": self.salir
            }
        ]
        
        for btn_config in botones:
            btn = tk.Button(botones_frame,
                           text=btn_config["texto"],
                           font=('Arial', 18, 'bold'),
                           bg=btn_config["color"],
                           fg='white',
                           width=30,
                           height=2,
                           command=btn_config["comando"],
                           cursor='hand2')
            btn.pack(pady=10)
            
            # Efecto hover
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=self.oscurecer_color(b.cget('bg'))))
            btn.bind('<Leave>', lambda e, b=btn, c=btn_config["color"]: b.config(bg=c))
    
    def oscurecer_color(self, color):
        """Oscurece un color hex para el efecto hover"""
        colores_hover = {
            "#4CAF50": "#45a049",
            "#2196F3": "#0b7dda",
            "#FF9800": "#e68900",
            "#9C27B0": "#7b1fa2",
            "#3F51B5": "#303F9F",
            "#f44336": "#da190b"
        }
        return colores_hover.get(color, color)
    
    def abrir_tablero(self):
        """Abre el tablero de vehículos"""
        self.root.withdraw()  # Oculta el menú
        
        # Crear ventana del tablero
        ventana_tablero = tk.Toplevel()
        ventana_tablero.state('zoomed')  # Maximizar la ventana del tablero
        from tablero_vehiculos import TableroVehiculos
        TableroVehiculos(ventana_tablero, self.root)
    
    def abrir_gestion_vehiculos(self):
        """Abre gestión de vehículos"""
        self.root.withdraw()
        
        ventana_gestion = tk.Toplevel()
        ventana_gestion.state('zoomed')
        from gestion_vehiculos import GestionVehiculos
        GestionVehiculos(ventana_gestion, self.root)
    
    def abrir_gestion_mecanicos(self):
        """Abre gestión de mecánicos"""
        self.root.withdraw()
        
        ventana_gestion = tk.Toplevel()
        ventana_gestion.state('zoomed')
        from gestion_mecanicos import GestionMecanicos
        GestionMecanicos(ventana_gestion, self.root)
        
    def abrir_gestion_estados(self):
        """Abre gestión de estados"""
        self.root.withdraw()
        
        ventana_gestion = tk.Toplevel()
        ventana_gestion.state('zoomed')
        from gestion_estados import GestionEstados
        GestionEstados(ventana_gestion, self.root)
        
    def abrir_gestion_clientes(self):
        """Abre gestión de clientes"""
        self.root.withdraw()
        
        ventana_gestion = tk.Toplevel()
        ventana_gestion.state('zoomed')
        from gestion_clientes import GestionClientes
        GestionClientes(ventana_gestion, self.root)
    
    def salir(self):
        """Cierra la aplicación"""
        self.root.quit()

if __name__ == "__main__":
    # Aquí inicializas la conexión a PostgreSQL. (Si omites los datos usa la de SQLite local)
    db = DatabaseManager(
        tipo_bd='postgres', 
        host='localhost', 
        port=5432, 
        dbname='taller_camarina', 
        user='postgres', 
        password='AlfinfBD24'
    )
    root = tk.Tk()
    app = MenuPrincipal(root)
    root.mainloop()