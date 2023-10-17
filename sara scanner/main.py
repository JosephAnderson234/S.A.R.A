import tkinter as tk
import time
import cv2
from tkinter import messagebox
import tkinter.scrolledtext as scrolledtext
from PIL import Image, ImageTk, ImageDraw, ImageGrab
from pyzbar.pyzbar import decode, ZBarSymbol
import mysql.connector
from datetime import datetime

conexion = mysql.connector.connect(user="root", password="joseph234", host="localhost", database="students", port="3306")
#miCursor = conexion.cursor()
#miCursor.execute('')
#conexion.commit()

class ScannerQR(tk.Toplevel):
    def __init__(self, parent, text, font_video=0):
        super().__init__(parent)
        # self.active_camera = False
        self.font_video=font_video
        self.category = text
        self.codelist = []
        self.logins = []
        self.title("Bienbenido al " + self.category)
        self.geometry("875x595+200+20")
        self.resizable(width=False, height=False)
        self.etiqueta = tk.Label(self, text="Esta es una subventana.")
        self.img = tk.PhotoImage(file="SCANNER.png")
        self.fondo = tk.Label(self, image=self.img).place(x=0, y=0, relwidth=1, relheight=1)
        self.etiqueta.pack()

        #cache
        self.cache = []

        #data from the dataBase
        self.name_label = tk.Label(self, text="", bg="#FAD02C", font=("Arial", 20))
        self.lastName_label = tk.Label(self, text="", bg="#FAD02C", font=("Arial", 20))
        self.grade_label = tk.Label(self, text="", bg="#FAD02C", font=("Arial", 20))
        self.name_label.place(x=442, y=195, width=350, height=30)
        self.lastName_label.place(x=442, y=316, width=350, height=30)
        self.grade_label.place(x=442, y=440, width=290, height=30)


        self.canvas=tk.Canvas(self, bg='#8148de', width=350, height=350)
        self.canvas.place(x=60, y=140)
        # self.display=scrolledtext.ScrolledText(self,width=86,background='snow3', height=4,padx=10, pady=10,font=('Arial', 10))
        # self.display.pack(side=tk.BOTTOM)
        self.start()
    def login(self, data):
        try: 
            logs = (str(data[0][0]), str(datetime.now().date()))
            if logs not in self.cache:
                self.cache.append(logs)
                self.name_label.config(text=str(data[0][1]))
                self.lastName_label.config(text=str(data[0][2]))
                self.grade_label.config(text=str(data[0][3]))
                hour = str(datetime.now().time())
                day = str(datetime.now().date())
                miCursor = conexion.cursor()
                if self.category == "Colegio":
                    miCursor.execute(f'INSERT INTO collegeacces (studentCode, dayData, hourData) VALUES ({data[0][0]}, "{day}", "{hour}");')
                    conexion.commit()
                elif self.category == "Laboratorio":
                    miCursor = conexion.cursor()
                    miCursor.execute(f'INSERT INTO laboratoryacces (studentCode, dayData, hourData) VALUES ({data[0][0]}, "{day}", "{hour}");')
                    conexion.commit()
            else:
                print("Ya está registrado")
        except NameError:
            print(NameError)
    def start(self):
        self.VideoCaptura()
        self.visor()
    def VideoCaptura(self):
        self.vid = cv2.VideoCapture(self.font_video)
        if self.vid.isOpened():
            print(str(cv2.CAP_PROP_FRAME_WIDTH)+"  "+str(cv2.CAP_PROP_FRAME_HEIGHT))
        else:
            messagebox.showwarning("CAMARA NO DISPONIBLE","El dispositivo está desactivado o no disponible")
            self.display.delete('1.0',tk.END)
            self.active_camera = False
    def visor(self):
        ret, frame=self.get_frame()
        if ret:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0,0,image=self.photo,anchor=tk.NW)
            self.after(15,self.visor)
    def capta(self,frm):
        self.info = decode(frm)
        cv2.putText(frm, "Muestre el codigo", (84, 37), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(frm, "frente a la camara", (80, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(frm, "para su lectura", (90, 83), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        if self.info != []:
            # self.display.delete('1.0', tk.END)
            for code in self.info:
                if code not in self.codelist:
                    self.codelist.append(code)
                    content = code[0].decode('utf-8')
                    if int(content):
                        try:
                            miCursor = conexion.cursor()
                            miCursor.execute('SELECT * FROM students WHERE code_student = {0}'.format(content))
                            data = miCursor.fetchall()
                            # print(data)
                            self.login(data)
                            # self.display.insert(tk.END,str(data)+'\n')
                        except NameError:
                            print("Error: " + NameError)
                    else:
                        print("No es un código legible")
                self.draw_rectangle(frm)
    def draw_rectangle(self,frm):
        codes = decode(frm)
        for code in codes:
            data = code.data.decode('ascii')
            x, y, w, h = code.rect.left, code.rect.top, \
                        code.rect.width, code.rect.height
            cv2.rectangle(frm, (x,y),(x+w, y+h),(255, 0, 0), 6)
            cv2.putText(frm, code.type, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 50, 255), 2)
    def get_frame(self):
        if self.vid.isOpened():
            verif,frame=self.vid.read()
            if verif:
                self.capta(frame)
                return(verif,cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                messagebox.showwarning("CAMARA NO DISPONIBLE","""La cámara está siendo utilizada por otra aplicación.
                Cierrela e intentelo de nuevo.""")
                self.active_cam()
                return(verif,None)
        else:
            verif=False
            return(verif,None)


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
        self.buttonCollege = tk.Button(self, text="Colegio", relief="flat", cursor="hand2", font=("Arial", 40, "bold"), bg=self.bg, command=self.scannerClg).place(x=388, y=270, width=220, height=100)
        self.buttonLaboratory = tk.Button(self, text="Laboratorio", relief="flat", cursor="hand2", font=("Arial", 30, "bold"), bg=self.bg, command=self.scannerLbt).place(x=388, y=465, width=220, height=100)
    def scannerClg(self):
        scanner = ScannerQR(self, "Colegio")
    def scannerLbt(self):
        scanner = ScannerQR(self, "Laboratorio")
        
if __name__ == "__main__":
    app = window()
    app.mainloop()
