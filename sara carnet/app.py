import tkinter as tk
import mysql.connector
from PIL import Image, ImageDraw, ImageFont, ImageOps
from tkinter import messagebox, filedialog
import qrcode

class Carnets(tk.Toplevel):
    def __init__(self, parent, data, db):
        self.baseData = db
        super().__init__(parent)
        self.info = data
        self.title("Generador de carnets")
        self.geometry("875x645+200+20") #595+50
        self.configure(bg="#fad02c")
        self.resizable(width=False, height=False)
        self.load()
    def load(self):
        self.lienzo = Image.open("./template-carnet.png")
        self.dibujo = ImageDraw.Draw(self.lienzo)

        self.qr = qrcode.QRCode(
            version=5,
            error_correction= qrcode.constants.ERROR_CORRECT_L,
        )
        self.qr.add_data(self.info[0])
        self.qr.make(fit=True)
        self.qrImg = self.qr.make_image(fill_color="black", back_color="white")
        self.qrImg = self.qrImg.resize((349,349))
        self.qrImg.save("./cache/qrStudent.png")

        self.fotoQR = Image.open("./cache/qrStudent.png")
        self.lienzo.paste(self.fotoQR, (38,146))

        self.fuente = ImageFont.truetype("arial.ttf", size=42, encoding="utf-8")
        self.name = str(self.baseData[0][1])
        self.code = str(self.baseData[0][0])
        self.lastName = str(self.baseData[0][2])
        self.grade = str(self.baseData[0][3])
        self.dibujo.text((420, 146), self.name, font=self.fuente, fill="black")
        self.dibujo.text((420, 240), self.lastName, font=self.fuente, fill="black")
        self.dibujo.text((420, 334), self.grade, font=self.fuente, fill="black")
        self.dibujo.text((420, 428), self.code, font=self.fuente, fill="black")
        self.nameIMG = f'{self.code}-carnet.png'
        self.lienzo.save(f'./export/{self.nameIMG}')

        self.img = tk.PhotoImage(file=f'./export/{self.nameIMG}')
        self.fondo = tk.Label(self, image=self.img)
        self.fondo.place(x=0, y=0, relwidth=1, relheight=0.922)
        self.btn = tk.Button(self, text="Guardar imagen", relief="flat", cursor="hand2", bg="#ffcb00", command=self.saveImg)
        self.btn.place(x=392.5, y=595, width=120, height=50)
    def saveImg(self):
        self.sourceIMG = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Imagenes sin fondo", "*.png")], 
            title="Guardar como",
            initialfile=f'{self.nameIMG}'
        )
        self.lienzo.save(self.sourceIMG)

class window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.conexion = mysql.connector.connect(user="root", password="joseph234", host="localhost", database="students", port="3306")
        self.geometry("1000x680+200+20")
        self.title("Bienvenido a SARA Scanner")
        self.resizable(width=False, height=False)
        self.img = tk.PhotoImage(file="SARA-CARNET.png")
        self.bg = "#fad02c"
        self.fondo = tk.Label(self, image=self.img).place(x=0, y=0, relwidth=1, relheight=1)
        self.load()
    def load(self):
        self.code = tk.Entry(self, text="Colegio", relief="flat", font=("Arial", 30, "bold"), bg=self.bg)
        self.code.place(x=284, y=250, width=432, height=80)
        self.code.bind("<Return>", self.pulsarBtn)
        self.name = tk.Entry(self, text="Laboratorio", relief="flat", font=("Arial", 30, "bold"), bg=self.bg)
        self.name.bind("<Return>", self.pulsarBtn)
        self.name.place(x=284, y=455, width=432, height=100)
        self.btn = tk.Button(self, text="Generar Qr", bg="#ffcb00", relief="flat", cursor="hand2", command=self.carnetMaker)
        self.btn.place(x=800, y=290, width=200, height=100)
    def pulsarBtn(self, event):
        self.carnetMaker()
    def carnetMaker(self):
        self.validar()
    def validar(self):
        if self.name.get() and self.code.get():
            miCursor = self.conexion.cursor()
            consulta = f'SELECT * FROM students WHERE firstName = "{self.name.get()}" AND code_student = {self.code.get()}'
            miCursor.execute(consulta)
            resultado = miCursor.fetchall()
            if resultado:
                subventana = Carnets(self, [self.code.get(), self.name.get()], resultado)
            else:
                messagebox.showinfo("Usuario no encontrado", "No lo encontramos en nuestros registros")
        else:
            messagebox.showinfo("Usuario no encontrado", "No lo encontramos en nuestros registros")

if __name__ == "__main__":
    app = window()
    app.mainloop()