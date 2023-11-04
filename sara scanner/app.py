import tkinter as tk
import cv2
from tkinter import messagebox
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
import mysql.connector
from datetime import datetime

# Establecer una conexión con la base de datos
conexion = mysql.connector.connect(user="root", password="joseph234", host="localhost", database="students", port="3306")

class ScannerQR(tk.Toplevel):
    def __init__(self, parent, text, font_video=0):
        super().__init__(parent)
        self.font_video = font_video
        self.category = text
        self.codelist = []
        self.title("Bienvenido al " + self.category)
        self.geometry("875x595+200+20")
        self.resizable(width=False, height=False)
        self.img = tk.PhotoImage(file="SCANNER.png")
        self.fondo = tk.Label(self, image=self.img).place(x=0, y=0, relwidth=1, relheight=1)

        # Cache
        self.cache = []

        # Labels
        self.name_label = tk.Label(self, text="", bg="#FAD02C", font=("Arial", 20))
        self.lastName_label = tk.Label(self, text="", bg="#FAD02C", font=("Arial", 20))
        self.grade_label = tk.Label(self, text="", bg="#FAD02C", font=("Arial", 20))
        self.name_label.place(x=442, y=195, width=350, height=30)
        self.lastName_label.place(x=442, y=316, width=350, height=30)
        self.grade_label.place(x=442, y=440, width=290, height=30)

        self.canvas = tk.Canvas(self, bg='#8148de', width=350, height=350)
        self.canvas.place(x=60, y=140)
        self.start()

    def login(self, data):
        student_code = str(data[0][0])
        if student_code not in self.cache:
            self.cache.append(student_code)
            self.name_label.config(text=str(data[0][1]))
            self.lastName_label.config(text=str(data[0][2]))
            self.grade_label.config(text=str(data[0][3]))
            current_time = datetime.now().strftime("%H:%M:%S")
            current_date = datetime.now().strftime("%Y-%m-%d")
            cursor = conexion.cursor()

            if self.category == "Colegio":
                cursor.execute(f'INSERT INTO collegeacces (studentCode, dayData, hourData) VALUES ({student_code}, "{current_date}", "{current_time}");')
                conexion.commit()
            elif self.category == "Laboratorio":
                cursor.execute(f'INSERT INTO laboratoryacces (studentCode, dayData, hourData) VALUES ({student_code}, "{current_date}", "{current_time}");')
                conexion.commit()
        else:
            print("El estudiante ya está registrado")

    def start(self):
        self.VideoCaptura()
        self.visor()

    def VideoCaptura(self):
        self.vid = cv2.VideoCapture(self.font_video)
        if self.vid.isOpened():
            print(f"Resolución: {self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)} x {self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        else:
            messagebox.showwarning("CÁMARA NO DISPONIBLE", "El dispositivo está desactivado o no disponible")
            self.active_camera = False

    def visor(self):
        ret, frame = self.get_frame()
        if ret:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.after(15, self.visor)

    def capta(self, frm):
        self.info = decode(frm)
        cv2.putText(frm, "Muestre el codigo", (84, 37), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(frm, "frente a la camara", (80, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(frm, "para su lectura", (90, 83), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        if self.info:
            for code in self.info:
                if code not in self.codelist:
                    self.codelist.append(code)
                    content = code.data.decode('utf-8')
                    if content.isnumeric():
                        try:
                            cursor = conexion.cursor()
                            cursor.execute(f'SELECT * FROM students WHERE code_student = {content}')
                            data = cursor.fetchall()
                            self.login(data)
                        except mysql.connector.Error as e:
                            print("Error en la consulta:", e)
                    else:
                        print("El código no es legible")
                self.draw_rectangle(frm)

    def draw_rectangle(self, frm):
        codes = decode(frm)
        for code in codes:
            data = code.data.decode('ascii')
            x, y, w, h = code.rect.left, code.rect.top, code.rect.width, code.rect.height
            cv2.rectangle(frm, (x, y), (x + w, y + h), (255, 0, 0), 6)
            cv2.putText(frm, code.type, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 50, 255), 2)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                self.capta(frame)
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                messagebox.showwarning("CÁMARA NO DISPONIBLE", "La cámara está siendo utilizada por otra aplicación. Cierre la aplicación e inténtelo de nuevo.")
                self.active_cam()
                return ret, None
        else:
            return False, None


class window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1000x680+200+20")
        self.title("Bienvenido a SARA Scanner")
        self.resizable(width=False, height=False)
        self.img = tk.PhotoImage(file="SARA-SCANNER.png")
        self.bg = "#fdfee9"
        self.fondo = tk.Label(self, image=self.img).place(x=0, y=0, relwidth=1, relheight=1)
        self.load()

    def load(self):
        tk.Button(self, text="Colegio", relief="flat", cursor="hand2", font=("Arial", 40, "bold"), bg=self.bg, command=self.scannerClg).place(x=388, y=270, width=220, height=100)
        tk.Button(self, text="Laboratorio", relief="flat", cursor="hand2", font=("Arial", 30, "bold"), bg=self.bg, command=self.scannerLbt).place(x=388, y=465, width=220, height=100)

    def scannerClg(self):
        scanner = ScannerQR(self, "Colegio")

    def scannerLbt(self):
        scanner = ScannerQR(self, "Laboratorio")

if __name__ == "__main__":
    app = window()
    app.mainloop()
