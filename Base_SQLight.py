import sqlite3
class ConexionBD:
    def _init_(self, nombrebd= "Clinica.BD"):
        self.nombrebd = nombrebd
        self.conexion = None

    
    def conectar(self): #Permite crear una concexion en la base de datos y el archivo que se generara 
        self.conexion = sqlite3.connect(self.nombrebd)
        return  self.conexion
    
    def crear_tablas(self):
        conexion = self.conectar()
        cursor = conexion.cursor()

        #Tabla pacientes  #¿Que hace esta funcion?
        #Las bases deben siempre de estar en inlgles para darle un uso mas factible al programa
        cursor.execute ('''
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            )
        ''') 

        #Tabla Citas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS citas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                descripcion TEXT,
                fecha_registro TEXT,
                fecha_cita TEXT DEFAULT NULL,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
            )
        ''') #En Default Null de fehca_cita lo agregamos por si el paciente no tendra una proxima cita
       

        #Tabla Reportes Monetarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reportes_monetarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                monto REAL,
                descuento REAL,
                fecha TEXT,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
            )
        ''')

        #Tabla productos 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                cantidad INTEGER,
                precio REAL,
                categoria TEXT,
                codigo TEXT
            )
        ''')

        #Tabla Reportes Medicos 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reportes_medicos(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       paciente_id INTEGER,
                       diagnostico TEXT,
                       cita TEXT,
                       fecha TEXT,
                       FOREING KEY (paciente_id) REFERENCES pacientes (id)
                        )
        ''')

        conexion.commit()
        conexion.close()
        print("Base de datos y tablas creadas correctamente.")

#La estructura de este codigo en partes como: "cursor.execute("SELECT * FROM pacientes WHERE nombre=?", (nombre,))"
#Realiza no una biusqueda binaria sino mejor que interactua con la misma
        