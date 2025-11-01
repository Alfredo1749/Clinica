import pywhatkit as kit
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from Base_SQLight import ConexionBD
import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

conexion = ConexionBD()
conexion.crear_tablas()

class Pacientes:
    def __init__(self, nombre):
        self.nombre = nombre
        pass

class Adm_Paciente(Pacientes):
    citas_progr = {}

    def __init__(self, nombre, cita=None):
        super().__init__(nombre)
        if nombre not in Adm_Paciente.citas_progr:
            Adm_Paciente.citas_progr[nombre] = []
        if cita:
            Adm_Paciente.citas_progr[self.nombre].append(cita)

    def añadir_cita(self, descripcion, fecha_cita=None):
        Adm_Paciente.citas_progr[self.nombre].append(descripcion)
        conexion = sqlite3.connect("Clinica.BD")
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM pacientes WHERE nombre=?", (self.nombre,))
        resultado = cursor.fetchone()
        if resultado:
            paciente_id = resultado[0]
        else:
            cursor.execute("INSERT INTO pacientes (nombre) VALUES (?)", (self.nombre,))
            paciente_id = cursor.lastrowid
        fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO citas (paciente_id, descripcion, fecha_registro, fecha_cita)
            VALUES (?, ?, ?, ?)
        """, (paciente_id, descripcion, fecha_registro, fecha_cita))
        conexion.commit()
        conexion.close()
        if fecha_cita:
            print(f"Cita guardada para {self.nombre}: {descripcion}(Proxima cita: {fecha_cita})")
        else:
            print(f"Cita guardada para {self.nombre}: {descripcion} (Sin proxima cita)")

    def cancelar_cita(self):
        if self.nombre in Adm_Paciente.citas_progr and Adm_Paciente.citas_progr[self.nombre]:
            cancelada = Adm_Paciente.citas_progr[self.nombre].pop()
            print(f"Cita cancelada para {self.nombre}: {cancelada}")
            conexion = sqlite3.connect("Clinica.BD")
            cursor = conexion.cursor()
            cursor.execute("SELECT id FROM pacientes WHERE nombre=?", (self.nombre,))
            resultado = cursor.fetchone()
            if resultado:
                paciente_id = resultado[0]
            cursor.execute("""
                DELETE FROM citas 
                WHERE id=(
                    SELECT id FROM citas
                    WHERE paciente_id=? AND descripcion =?
                    ORDER BY id DESC
                    LIMIT 1
                )
            """, (paciente_id, cancelada))
            conexion.commit()
            conexion.close()
        else:
            print(f"No existen citas para {self.nombre}")

    def ultima_visita(self):
        if Adm_Paciente.citas_progr[self.nombre]:
            ultima = Adm_Paciente.citas_progr[self.nombre][-1]
            print(f"Ultoma cita registrada de {self.nombre}: {ultima}")
        else:
            print("No hay citas registradas")

    def historial_paciente(self):
        historial = Adm_Paciente.citas_progr[self.nombre]
        if historial:
            print(f"Hiostorial de {self.nombre}: {historial}")
        else:
            print(f"No hay citas registradas para {self.nombre}")
        return historial

    def recordatorio(self, numero, mensaje):
        if numero:
            kit.sendwhatmsg_instantly(
                phone_no=f"+502 {numero}",
                message=f"{mensaje}",
                wait_time=10,
                tab_close=True,
                close_time=3)
            print(f"Recordatorio enviado a {self.nombre} al número {numero}")
        else:
            print("No exsite un numero para enviar el recordatorio")

    def guardar_en_bd(self, descripcion, fecha_cita):
        conexion = sqlite3.connect("Clinica.BD")
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM pacientes WHERE nombre=?", (self.nombre,))
        resultado = cursor.fetchone()
        if resultado:
            paciente_id = resultado[0]
        else:
            cursor.execute("INSERT INTO pacientes (nombre) VALUES (?)", (self.nombre,))
            paciente_id = cursor.lastrowid
        fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO citas (paciente_id, descripcion, fecha_registro, fecha_cita)
            VALUES (?, ?, ?, ?)
        """, (paciente_id, descripcion, fecha_registro, fecha_cita))
        conexion.commit()
        conexion.close()
        if fecha_cita:
            print(f"Cita guardada para {self.nombre}: {descripcion}(Proxima cita: {fecha_cita})")
        print(f"Cita guardada para {self.nombre}: {descripcion} (Sin proxima cita)")

    def programar_recordatorio_whatsapp(self, mensaje):
        conexion = sqlite3.connect("clinica.db")
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT fecha_cita 
            FROM citas 
            WHERE paciente_id = (SELECT id FROM pacientes WHERE nombre = ?) 
            ORDER BY id DESC LIMIT 1
        """, (self.nombre,))
        resultado = cursor.fetchone()
        conexion.close()
        if not resultado or not resultado[0]:
            print("No hay próxima cita registrada para enviar un recordatorio.")
            return
        fecha_cita = datetime.strptime(resultado[0], "%Y-%m-%d")
        fecha_recordatorio = fecha_cita - datetime.timedelta(days=2)
        hora_envio = 9
        fecha_recordatorio = fecha_recordatorio.replace(hour=hora_envio, minute=0, second=0)
        if datetime.now() >= fecha_recordatorio:
            print("Ya pasó la fecha de recordatorio.")
            return
        print(f"Recordatorio de WhatsApp programado para {fecha_recordatorio.strftime('%Y-%m-%d %H:%M')}")
        while True:
            ahora = datetime.now()
            if ahora >= fecha_recordatorio:
                try:
                    kit.sendwhatmsg_instantly(self.telefono, mensaje, wait_time=10)
                    print(f"Mensaje de WhatsApp enviado a {self.telefono}")
                except Exception as e:
                    print(f"Error al enviar mensaje de WhatsApp: {e}")
                break
            time.sleep(60)

class Generar_Report(Pacientes):
    def __init__(self, nombre):
        super().__init__(nombre)
        pass

class Reporte_monetario(Generar_Report):
    dinero_obtenido = {}

    def __init__(self, nombre, money, descuento=0):
        super().__init__(nombre)
        self.money = money
        self.descuento = descuento
        Reporte_monetario.dinero_obtenido[self.nombre] = money
        self.guardar_en_bd()

    def aplicar_descuentos(self, descuento, total):
        if descuento:
            pago = total - (descuento * total / 100)
            print(f"Descuento del {descuento}% aplicado a {self.nombre} dando el total de: {pago}")
        else:
            pass

    def registro_dinero(self):
        if self.nombre in Reporte_monetario.dinero_obtenido:
            print(f"Dinero obtenido por {self.nombre}: Q {self.money}")
        else:
            print(f"Aún no se registra un pago obtenido por {self.nombre}")

    def guardar_en_bd(self):
        conexion = sqlite3.connect("Clinica.BD")
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM pacientes WHERE nombre=?", (self.nombre,))
        resultado = cursor.fetchone()
        if resultado:
            paciente_id = resultado[0]
        else:
            cursor.execute("INSERT INTO pacientes (nombre) VALUES (?)", (self.nombre,))
            paciente_id = cursor.lastrowid
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO reportes_monetarios (paciente_id, monto, descuento, fecha)
            VALUES (?, ?, ?, ?)
        """, (paciente_id, self.money, self.descuento, fecha))
        conexion.commit()
        conexion.close()
        print(f"Pago registrado en la BD para {self.nombre}: Q{self.money} (Descuento: {self.descuento}%)")

class Reporte_consulta(Generar_Report):
    def __init__(self, nombre, cita=None, diagnostico=None):
        super().__init__(nombre)
        self.cita = cita
        self.diagnostico = diagnostico
        self.fecha = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
        self.guardar_en_bd()
        self.generar_reporte_receta()

    def guardar_info(self):
        with open(f"Reporte {self.nombre}.txt", "w", encoding="utf_8") as archivo:
            archivo.write(f"Paciente {self.nombre}\n")
            archivo.write(f"Cita: {self.cita}\n")
            archivo.write(f"Diagnostico: {self.diagnostico}")
            archivo.write(f"Fecha de Reporte: {self.fecha}")
        print(f" Reporte generado: reporte {self.nombre}.txt  ")

    def generar_reporte_receta(self):
        nombre_pdf = f"reporte {self.nombre}.pdf"
        c = canvas.Canvas(nombre_pdf, pagesize=letter)
        width, height = letter
        c.setFont("Times New Roman", 16)
        c.drawString(200, height - 80, "REPORTE MÉDICO")
        c.setFont("Times New Roman", 12)
        c.drawString(50, height - 130, f"Paciente: {self.nombre}")
        c.drawString(50, height - 150, f"Cita: {self.cita}")
        c.drawString(50, height - 170, f"Diagnostico: {self.diagnostico}")
        c.drawString(50, height - 190, f"Fecha del reporte: {self.fecha}")
        c.line(50, height - 210, width - 50, height - 210)
        c.drawString(50, height - 230, "Reporte generado por el Sistema")
        c.save()
        print(f"Reporet PDF generado correctamente: {nombre_pdf}")

    def guardar_en_bd(self):
        conexion = sqlite3.connect("Clinica.BD")
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM pacientes WHERE nombre=?", (self.nombre,))
        resultado = cursor.fetchone()
        if resultado:
            paciente_id = resultado[0]
        else:
            cursor.execute("INSERT INTO pacientes (nombre) VALUES (?)", (self.nombre,))
            paciente_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO reportes_medicos (paciente_id, diagnostico, cita, fecha)
            VALUES (?, ?, ?, ?)
        """, (paciente_id, self.diagnostico, self.cita, self.fecha))
        conexion.commit()
        conexion.close()
        print(f"Diagnostico registrado en la BD para {self.nombre}: {self.diagnostico}")

    def imprimir_pdf(self, nombre_pdf=None):
        if nombre_pdf is None:
            nombre_pdf = f"Reporte {self.nombre}.pdf"
        if os.path.exists(nombre_pdf):
            os.startfile(nombre_pdf, "print")
            print(f"PDF enviado a la impresora: {nombre_pdf}")
        else:
            print(f"Archivo no encontrado: {nombre_pdf}")

class Contabilidad_Productos(Pacientes):
    def __init__(self, nombre, producto):
        super().__init__(nombre)
        self.producto = producto
        self.productos = []
        self.inventario = {}

    def agregar_producto(self, nombre, cantidad, precio, categoria="General", codigo=None):
        conexion = sqlite3.connect("Clinica.BD")
        cursor = conexion.cursor()
        cursor.execute("SELECT id, cantidad FROM productos WHERE nombre=?", (nombre,))
        resultado = cursor.fetchone()
        if resultado:
            producto_id, cant_actual = resultado
            nueva_cant = cant_actual + cantidad
            cursor.execute("UPDATE productos SET cantidad=?, precio=?, categoria=?, codigo=? WHERE id=?",
                           (nueva_cant, precio, categoria, codigo, producto_id))
        else:
            cursor.execute("INSERT INTO productos (nombre, cantidad, precio, categoria, codigo) VALUES (?, ?, ?, ?, ?)",
                           (nombre, cantidad, precio, categoria, codigo))
        conexion.commit()
        conexion.close()
        print(f"Producto {nombre} agregado/actualizado en la BD: {cantidad} unidades, Q{precio}")

    def eliminar_producto(self, nombre):
        conexion = sqlite3.connect("Clinica.BD")
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE nombre=?", (nombre,))
        conexion.commit()
        conexion.close()
        print(f"Producto {nombre} eliminado de la BD")
