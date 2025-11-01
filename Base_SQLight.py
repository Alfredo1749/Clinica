import sqlite3
class ConexionBD:
    def __init__(self, nombrebd="Clinica.BD"):
        self.nombrebd = nombrebd
        self.conexion = None

    def conectar(self):
        self.conexion = sqlite3.connect(self.nombrebd)
        return self.conexion

    def crear_tablas(self):
        conexion = self.conectar()
        cursor = conexion.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS citas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                descripcion TEXT,
                fecha_registro TEXT,
                fecha_cita TEXT DEFAULT NULL,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
            )
        ''')

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

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reportes_medicos(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                diagnostico TEXT,
                cita TEXT,
                fecha TEXT,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
            )
        ''')

        conexion.commit()
        conexion.close()
        print("Base de datos y tablas creadas correctamente.")


#La estructura de este codigo en partes como: "cursor.execute("SELECT * FROM pacientes WHERE nombre=?", (nombre,))"
#Realiza no una biusqueda binaria sino mejor que interactua con la misma
        