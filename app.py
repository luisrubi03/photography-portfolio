from flask import Flask, session, render_template, url_for, redirect, request
import requests
from flask_session import Session
import sqlite3 as sql
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app_secret_key = "secretkey123"
DATABASE= "users.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE


def create_tables():
    connection= sql.connect(DATABASE)
    cur = connection.cursor()
    cur.execute(''' CREATE TABLE IF NOT EXISTS users_data(
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,firstname TEXT NOT NULL, lastname TEXT NOT NULL,username TEXT NOT NULL,
                    email TEXT NOT NULL,password TEXT NOT NULL, creation_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
    connection.commit()
    connection.close()
    print("Base de datos creada correctamente")

@app.route("/")
def index():
    not session.get("user")
    return redirect(url_for("login"))
    return render_template('index.html')

@app.route("/account")
def account():
    return render_template('account.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/load")
def load():
    return render_template('load.html')

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = sql.connect(DATABASE)
        c = connection.cursor()
        c.execute("SELECT * FROM users_data WHERE username = ?", (username,))
        user = c.fetchone()
        connection.close()


        if username:
            session["username"] = username
            return redirect(url_for('index'))
        else:
            return 'credenciales incorrectas'#hacer una pagina de errores comunes
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        # Validaciones de entrada de datos
        if not request.form.get('firstname'):
            return 'El primer nombre es necesario'
        elif not request.form.get('lastname'):
            return 'El apellido es necesario'
        elif not request.form.get('username'):
            return 'El nombre de usuario es necesario'
        elif not request.form.get('email'):
            return 'El correo es necesario'
        elif not request.form.get('password'):
            return 'La contraseña es necesaria'
        elif not request.form.get('confirmation'):
            return 'La confirmacion es necesaria'

        #variables de formularios
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        #verifica si la contrasena es igual a la confirmacion
        if password != confirmation:
            return 'contrasena o confirmacion no coinciden'

        conn = sql.connect(DATABASE)
        c = conn.cursor()

        # Verificar si ya existe
        c.execute("SELECT * FROM users_data WHERE username = ?", (username,))
        if c.fetchone():
            conn.close()
            return "Este nombre de usuario ya existe"

        # Genera el hash de la contrasena ingresada para aumentar la seguridad
        passwordHash = generate_password_hash(password)
        c.execute("""
            INSERT INTO users_data (firstname, lastname, username, email, password)
            VALUES (?, ?, ?, ?, ?)
        """, (firstname, lastname, username, email, passwordHash))

        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

#funcion para recuperar contrasenas, aun en proceso
@app.route("/recoverpassword", methods=['GET','POST'])
def recoverpassword():
    connection= sql.connect(DATABASE)
    cur = connection.cursor()
    return render_template('recoverpassword.html')

#comentario de linea: ruta de salir sesion
@app.route("/logout")
def logout():
    return redirect(url_for('login'))

if __name__ == "__main__":
    create_tables()
    connection = sql.connect(DATABASE)
    c = connection.cursor()
    #c.execute(''' -header -csv database.db "select * from credenciales;" > database.csv ''')
    app.run(debug=True)