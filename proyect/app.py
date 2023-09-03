from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import mysql.connector



app = Flask(__name__)

#MySql Conexion
conexion = mysql.connector.connect(user="root", password="joseph234", host="localhost", database="students", port="3306")
#Configuración
app.secret_key = "topsecret"

@app.route('/')
def Index():
    miCursor = conexion.cursor()
    miCursor.execute("SELECT * FROM students")
    consulta = miCursor.fetchall()
    return render_template('index.html', students = consulta)

@app.route('/add_student', methods=['POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        code = request.form['code']
        dieta = request.form['dieta']
        """ cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students")
        mysql.connect.commit() """
        miCursor = conexion.cursor()
        miCursor.execute(f'INSERT INTO students (code_student, firstName, lastName, diet) values ({code},"{name}", "{lastname}", "{dieta}")')
        conexion.commit()
        flash("Estudiante añadido exitosamente")
        return redirect(url_for("Index"))

@app.route('/edit/<id>')
def get_student(id):
    miCursor = conexion.cursor()
    miCursor.execute('SELECT * FROM students WHERE code_student = {0}'.format(id))
    data = miCursor.fetchall()
    return render_template('edit-student.html', student = data[0])

@app.route('/update/<id>', methods=['POST'])
def update_student(id):
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        code = request.form['code']
        dieta = request.form['dieta']
        miCursor = conexion.cursor()
        miCursor.execute("""
            UPDATE students
            SET firstName = %s,
                lastName = %s,
                diet = %s
            WHERE code_student = %s
        """, (name, lastname, dieta, code))
        conexion.commit()
        flash("Actualización concretada")
        return redirect(url_for("Index"))

@app.route('/delete/<string:id>')
def delete_student(id):
    miCursor = conexion.cursor()
    miCursor.execute('DELETE FROM students WHERE code_student = {0}'.format(id))
    conexion.commit()
    flash('Estudiante eliminado')
    return redirect(url_for('Index'))

if __name__ == '__main__':
    app.run(port=5000, debug=True)