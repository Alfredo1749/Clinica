import pywhatkit as kit 
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter #Dopcuemntar y conocer el porque de las funciones egragads
from reportlab.pdfgen import  canvas
from Base_SQLight import ConexionBD
import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os #Imprimir pdf en windows
conexion = ConexionBD() #Conexion de la base de datos al programa
conexion.crear_tablas() #Crea las tablas para la base de datos generada por el programa
#Especificar si la funcion es parte de los RF o RNF (Requerimientos funcionales/no funcionales)
 
class Pacientes:
    def _init_(self, nombre):
        self.nombre = nombre
        pass



class Adm_Paciente(Pacientes):
        
        citas_progr = {}
        def _init_(self, nombre, cita = None):
             super()._init_(nombre)
             if nombre not in Adm_Paciente.citas_progr:
                  Adm_Paciente.citas_progr[nombre] = [] #Convertimos los datos en una lista para interactuar con pilas y colas 
             if cita:
                  Adm_Paciente.citas_progr[self.nombre].append(cita)
                             
        def añadir_cita(self, descripcion,  fecha_cita= None):
              Adm_Paciente.citas_progr[self.nombre].append(descripcion) #Añadiomos la lista a la memoria 

              #Conectamos al sql
              conexion = sqlite3.connect("Clinica.BD")
              cursor = conexion.cursor()

              cursor.execute("SELECT id FROM pacientes WHERE nombre=?", (self.nombre,))
              #Verificacion si el paciente existe

              resultado = cursor.fetchone()
              if resultado:
                   paciente_id = resultado[0]
              else:
                   cursor.execute("INSERT INTO pacientes (nombre) VALUES (?)", (self.nombre,))
                   paciente_id = cursor.lastrowid #¡¿?


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
                 #Eliminamos la memoria de la cita en la estructura LIFO
                 cancelada = Adm_Paciente.citas_progr[self.nombre].pop()
                 print(f"Cita cancelada para {self.nombre}: {cancelada}")

                 conexion = sqlite3.connect("Clinica.BD")
                 cursor = conexion.cursor()

        # Obtenemos el id del paciente
                 cursor.execute("SELECT id FROM pacientes WHERE nombre=?", (self.nombre,))
                 resultado = cursor.fetchone()
                 if resultado:
                   paciente_id = resultado[0]

            # Eliminamos la cita de la BD usando paciente_id y descripción
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
                  ultima = Adm_Paciente.citas_progr[self.nombre][-1] ##LIFO
                  print(f"Ultoma cita registrada de {self.nombre}: {ultima}")
             else:
                  print("No hay citas registradas")

        def historial_paciente(self):
             historial = Adm_Paciente.citas_progr[self.nombre]
             if historial:
                  print(f"Hiostorial de {self.nombre}: {historial}")
             else:
                  print(F"No hay citas registradas para {self.nombre}")

             return historial
        
   
        def recordatorio(self, numero, mensaje): #Falta cambiarlo a correo y asignar una fecha especiofica
             if numero:
                  kit.sendwhatmsg_instantly(
                   phone_no = f"+502 {numero}",
                   message= f"{mensaje}",
                   wait_time = 10,
                   tab_close = True,
                   close_time= 3 )  
                  print(f"Recordatorio enviado a {self.nombre} al número {numero}")  
             else:
                  print("No exsite un numero para enviar el recordatorio")

                  #Falta agregar la funcion de ordenar pacientes por fecha

        
        def guardar_en_bd(self, descripcion, fecha_cita):
          conexion = sqlite3.connect("Clinica.BD")
          cursor = conexion.cursor()

        #Verificamos si el paciente ya existe
          cursor.execute("SELECT id FROM pacientes WHERE nombre=?", (self.nombre,))
          resultado = cursor.fetchone()

          if resultado:
              paciente_id = resultado[0]
          else:
              cursor.execute("INSERT INTO pacientes (nombre) VALUES (?)", (self.nombre,))
              paciente_id = cursor.lastrowid #¿?

          fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #Guardamos la cita
          cursor.execute("""
               INSERT INTO citas (paciente_id, descripcion, fecha_registro, fecha_cita)
               VALUES (?, ?, ?, ?)
           """, (paciente_id, descripcion, fecha_registro, fecha_cita)) #Por que colocamos ????

          conexion.commit()
          conexion.close()

          if fecha_cita:
               print(f"Cita guardada para {self.nombre}: {descripcion}(Proxima cita: {fecha_cita})")

          print(f"Cita guardada para {self.nombre}: {descripcion} (Sin proxima cita)")

        def programar_recordatorio_email(self, destinatario, mensaje):
   
    #Buscar la fecha de la próxima cita
         conexion = sqlite3.connect("clinica.db")
         cursor = conexion.cursor()
         cursor.execute("SELECT fecha_cita FROM citas WHERE paciente_id=(SELECT id FROM pacientes WHERE nombre=?) ORDER BY id DESC LIMIT 1", (self.nombre,))
         resultado = cursor.fetchone()
         conexion.close()

         if not resultado or not resultado[0]:
             print("No hay próxima cita registrada para enviar un recordatorio")
             return

         fecha_cita = datetime.datetime.strptime(resultado[0], "%Y-%m-%d")
         fecha_recordatorio = fecha_cita - datetime.timedelta(days=2) #El correo se enviara dos dias antes de la fecha de proxima cita
         hora_envio = 9  #9:00 AM
         fecha_recordatorio = fecha_recordatorio.replace(hour=hora_envio, minute=0, second=0) #Ajusta la hora de envio

         #Programar el correo
         EMAIL_REMITENTE = "tucuenta@gmail.com"
         CONTRASENA_APP = "tu_contraseña_de_aplicacion"

         if datetime.datetime.now() >= fecha_recordatorio:
             print("Ya pasó la fecha de recordatorio")
             return

         print(f"Recordatorio programado para {fecha_recordatorio.strftime('%Y-%m-%d %H:%M')}")

         while True:
             ahora = datetime.datetime.now()
             if ahora >= fecha_recordatorio:
                 try:
                     msg = MIMEMultipart()
                     msg["From"] = EMAIL_REMITENTE
                     msg["To"] = destinatario
                     msg["Subject"] = f"Recordatorio de cita médica"
                     msg.attach(MIMEText(mensaje, "plain"))

                     with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                         server.login(EMAIL_REMITENTE, CONTRASENA_APP)
                         server.send_message(msg)

                     print(f"Correo enviado a {destinatario}")
                 except Exception as e:
                     print(f"Error al enviar el correo: {e}")
                 break
             
             time.sleep(60)





class Generar_Report(Pacientes):
     def _init_(self, nombre):
          super()._init_(nombre)
          pass
      
class Reporte_monetario(Generar_Report):

    dinero_obtenido= {}#Guarda Nombre con la cantidad de dinero a pagar o que pago 
    def _init_(self, nombre, money, descuento=0):
          super()._init_(nombre)
          self.money = money
          self.descuento = descuento
          Reporte_monetario.dinero_obtenido[self.nombre] = money
          self.guardar_en_bd() #Integrar a la base de datos

    def aplicar_descuentos(self, descuento, total):
          if descuento:
               pago = total - (descuento * total / 100)
               print(f"Descuento del {descuento}% aplicado a {self.nombre} dando el total de: {pago}")

          else:
               pass
            


    def registro_dinero(self):
          if self.nombre in Reporte_monetario.dinero_obtenido:
               print( f"Dinero obtenido por {self.nombre}: Q {self.money}" )

          else:
               print(f"Aún no se registra un pago obtenido por {self.nombre} ")

    def guardar_en_bd(self):
         conexion = sqlite3.connect("Clinica.BD")
         cursor = conexion.cursor()

         cursor.execute("SELECT id FROM pacientes WHERE nombre=?", (self.nombre,))
         resultado = cursor.fetchone() #¿?
         if resultado:
              paciente_id = resultado[0]
         else:
              cursor.execute("INSERT INTO pacientes (nombre) VALUES (?)", (self.nombre,))#Porque se le agrega la coma en self.nombre
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
     #¿Se requiere alguna funcioon en especifico para que el archivo txt se convierta a pdf posterior a la generacion del reporte?
     #Necesito tambien en el reporte registrar en un epcio npequeña la fecha de la cita o la cita en si
     def _init_(self, nombre, cita = None, diagnostico = None ):
          super()._init_(nombre)
          self.cita = cita
          self.diagnostico = diagnostico
          self.fecha = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")#Fecha registrada en dias meses y años incluyenco su hora
          self.guardar_en_bd() #Se integra directamente en la BD
          self.generar_reporte_receta()#Obtenemos informacion de la funcion "generar reporte receta"
          


     def guardar_info(self):
          
          with open(f"Reporte {self.nombre}.txt", "w", encoding="utf_8") as archivo:
               archivo.write(f"Paciente {self.nombre}\n")
               archivo.write(f"Cita: {self.cita}\n")
               archivo.write(f"Diagnostico: {self.diagnostico}")
               archivo.write(f"Fecha de Reporte: {self.fecha}")

          print(f" Reporte generado: reporte {self.nombre}.txt  ")
     


     def generar_reporte_receta(self): #El codigo que se mostrara a continuacion se genero con ayuda de ChatGPT
          #Esto debido a que no se tenia conocimiento del comando y su correcta utilización
          nombre_pdf = f"reporte {self.nombre}.pdf"
          c = canvas.Canvas(nombre_pdf, pagesize=letter)
          width, height = letter #Grosor y altura de la letra

          #Encabezado
          c.setFont("Times New Roman", 16)
          c.drawString(200, height - 80, "REPORTE MÉDICO")

          #Datos paciente
          c.setFont("Times New Roman", 12)
          c.drawString(50, height - 130, f"Paciente: {self.nombre}") # El codigo "50, height - 130" es la representacion de la ubicacion en el eje Y y X en el que se colocara el texto
          c.drawString(50, height - 150, f"Cita: {self.cita}")
          c.drawString(50, height - 170, f"Diagnostico: {self.diagnostico}")
          c.drawString(50, height - 190, f"Fecha del reporte: {self.fecha}")

          #Linea Decorativa Final

          c.line(50, height - 210, width - 50, height - 210)
          c.drawString(50, height - 230, "Reporte generado por el Sistema")

          c.save()
          print(f"Reporet PDF generado correctamente: {nombre_pdf}")



     def guardar_en_bd(self):
         conexion = sqlite3.connect("Clinica.BD")
         cursor = conexion.cursor()

         # Obtener id del paciente
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

#Imprime el archivo pdf ya generado
     def imprimir_pdf(self, nombre_pdf = None):
          if nombre_pdf is None:
               nombre_pdf = f"Reporte {self.nombre}.pdf"

          if os.path.exists(nombre_pdf):
               os.startfile(nombre_pdf, "print")
               print(f"PDF enviado a la impresora: {nombre_pdf}")
          else:
               print(f"Archivo no encontrado: {nombre_pdf}")






class Contabilidad_Productos(Pacientes):
     
     def _init_(self, nombre, producto):
          super()._init_(nombre)
          self.producto = producto
          self.productos = []
          self.inventario = {}


#Def buscar producto

     def agregar_producto(self, nombre, cantidad, precio, categoria="General", codigo= None):
          #Agrega productos o actualia su cantidad si ya existe 
          if nombre in self.inventario:
               self.inventario[nombre]["cantidad"] += cantidad
          else:
               self.inventario[nombre] = {
                    "cantidad": cantidad,
                    "precio": precio,
                    "categoria": categoria,
                    "codigo": codigo
               }
               print(f"Producto {nombre} agregado o catualizado correctamente")




     def elmienar_producto(self, nombre):
          if nombre in self.inventario:
               del self.inventario[nombre] #Eliminamos al  producto
               print(f"Producto {nombre} eliminado del inventario")
          else:
               print(f"El producto {nombre} no existe ")




     def aviso_stock(self, minimo= 5):
          #La cantidad minima de procutos sera de 5, al pasar esat cnatidad se enviara un aviso
          print("Productos con Bajo Stck")
          for nombre, datos in self.inventario.items():
               if datos ["cantidad"] <= minimo:
                    print(f"{nombre}: {datos["cantidad"]} unidades restantes") #Aviso de stock minimo




     def mostrar_inventario(self):
          #Inventario ordenado alfabeticamente
          productos = list(self.inventario.keys())#Obtenemos informacion propia de inventario y la trasnformamos en lista
          productos_ordenados = self.merge_sort_productos(productos)
          print("\n Inventario Completo: ")
          for nombre in productos_ordenados:
               datos = self.inventario[nombre]
               print(f"{nombre}: {datos["cantidad"]} unidades |  Q{datos["precio"]| {datos["categoria"]}}")
               #Funcion no planificada: muesrtra precios y categoria



#Logistica del orden alfabeticos
     def merge_sort_productos(self, lista):
          
          if len(lista) <= 1:
               return lista
          
          mitad = len(lista)//2
          izquierda = Contabilidad_Productos.merge_sort_productos(self.productos[:mitad])
          derecha = Contabilidad_Productos.merge_sort_productos(self.productos[mitad:])
        
          return Contabilidad_Productos.fusionar(izquierda, derecha)
     



     @staticmethod #Usamos static debido a que fusionar no usa self, de esta manera lo podremos llamar desde otros metodos
     def fusionar(izquierda, derecha):
          resultado = []
          i = j = 0

          while i < len(izquierda) and j < len(derecha):
               if izquierda[i].lower()<= derecha[j].lower():
                    resultado.append(izquierda[i])
                    i+= 1
               else:
                    resultado.append(derecha[j])

               resultado.extend(izquierda[i:])
               resultado.extend(derecha[j:])

          return resultado


     def agregar_producto(self, nombre, cantidad, precio, categoria="General", codigo=None):
         conexion = sqlite3.connect("Clinica.BD")
         cursor = conexion.cursor()

         # Verificar si producto existe
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