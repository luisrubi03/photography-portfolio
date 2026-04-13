import sqlite3

from flask import Flask, session, render_template, url_for, redirect, request
import requests
from flask_session import Session
import sqlite3 as sql
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import timedelta, datetime
app = Flask(__name__)
app.secret_key = os.urandom(24)
DATABASE= "users.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE


app.config['UPLOAD_POSTS'] = 'static/uploads/posts'
app.config['UPLOAD_PROFILE'] = 'static/uploads/profile_pic'

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)


def create_tables():
    connection= sql.connect(DATABASE)
    cur = connection.cursor()
    cur.execute(''' CREATE TABLE IF NOT EXISTS users_data(
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,firstname TEXT NOT NULL, lastname TEXT NOT NULL,username TEXT NOT NULL,
                    email TEXT NOT NULL,password TEXT NOT NULL, creation_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, profile_picture TEXT DEFAULT 'default.png')''')
    connection.close()

    print("Base de datos creada correctamente")

def create_posts_table():
    connection2 = sql.connect(DATABASE)
    cur2 = connection2.cursor()
    cur2.execute(''' CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT NOT NULL, user_id INTEGER NOT NULL, username TEXT NOT NULL, date_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP NOT NULL, description TEXT NOT NULL)''')
    connection2.close()
    print("tabla posts creada correctamente")

@app.route("/")
def index():
    if not session.get("username"):
        return redirect(url_for('login'))

    carpeta = app.config['UPLOAD_POSTS']

    connection = sql.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("SELECT filename, username, description FROM posts ORDER BY id DESC")
    posts = cursor.fetchall()

    posts_validos = []

    for post in posts:
        ruta = os.path.join(carpeta, post[0])
        if os.path.exists(ruta):
            posts_validos.append(post)

    return render_template('index.html', show_navbar=True, posts=posts_validos)

@app.route("/account")
def account():
    return render_template('account.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/error_handler")
def error_handler():
    return render_template("error_handler.html", Show_navbar=True)


@app.route("/login", methods=['GET','POST'])
def login():
    create_tables()
    create_posts_table()

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        connection = sql.connect(DATABASE)
        c = connection.cursor()
        c.execute("SELECT * FROM users_data WHERE username = ?", (username,))
        user = c.fetchone()
        connection.close()
        #print(user)
        print(session.get("username"))
        if user and check_password_hash(user[5], password):
            session["user_id"] = user[0]  # ID
            session["username"] = user[3]  # username (mejor usar el de la BD)

            return redirect(url_for('index'))
        else:
            return 'Credenciales incorrectas, intenta de nuevo'#hacer una pagina de errores comunes

    return render_template('login.html', show_navbar=False)


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
        firstname = request.form.get('firstname').strip().title()
        lastname = request.form.get('lastname').strip().title()
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()
        confirmation = request.form.get('confirmation').strip()

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

    return render_template('register.html', show_navbar=False)

#funcion para recuperar contrasenas, aun en proceso
@app.route("/recoverpassword", methods=['GET','POST'])
def recoverpassword():
    connection= sql.connect(DATABASE)
    cur = connection.cursor()
    return render_template('recoverpassword.html')

#comentario de linea: ruta de salir sesion
@app.route("/logout", methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if not session.get("username"):
        return redirect(url_for('login'))

    print("SESSION:", session)

    if request.method == 'POST':

        if "user_id" not in session:
            return redirect(url_for("login"))

        if 'imagen' not in request.files:
            return "No file"

        file = request.files['imagen']
        description = request.form['descripcion']

        if description == '':
            return "deberias poner una descripcion"
        if file.filename == '':
            return "Ningun archivo se ha seleccionado"

        filename = secure_filename(file.filename)

        ruta = os.path.join(app.config['UPLOAD_POSTS'], filename)
        file.save(ruta)

        connection = sql.connect(DATABASE)
        c = connection.cursor()
        if os.path.exists(ruta):
            c.execute('''
                      INSERT INTO posts (filename, user_id, username, date_time, description)
                      VALUES (?, ?, ?, ?, ?)
                      ''', (filename, session["user_id"], session["username"], datetime.now(), description))

            connection.commit()
        else:
            return "Error al guardar la imagen"

        return redirect(url_for('upload'))

    return render_template("upload.html", show_navbar= True)

@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if not session.get("username"):
        return redirect(url_for('login'))

    connection = sql.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()
    user = cur.execute("SELECT username FROM users_data WHERE user_id = ?", (session["user_id"],)).fetchone()

    connection = sql.connect(DATABASE)
    connection.row_factory = sql.Row
    c = connection.cursor()

    c.execute("SELECT username, profile_picture FROM users_data WHERE user_id = ?", (session["user_id"],))
    user = c.fetchone()

    c.close()

    # manejar default
    profile_picture = user["profile_picture"] or "default.png"

    return render_template(
        "profile.html",
        show_navbar=True,
        profile_username=user["username"],
        imagen=profile_picture
    )

@app.route("/profile/edit", methods=['GET', 'POST'])
def profile_edit():
    if "user_id" not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'imagen' not in request.files:
            return "No file"

        file = request.files['imagen']

        if file.filename == '':
            return "Ningun archivo se ha seleccionado"

        import uuid
        filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)

        os.makedirs(app.config['UPLOAD_PROFILE'], exist_ok=True)
        ruta = os.path.join(app.config['UPLOAD_PROFILE'], filename)
        file.save(ruta)

        if not os.path.exists(ruta):
            return "Error al guardar la imagen"

        connection = sql.connect(DATABASE)
        c = connection.cursor()

        c.execute('''
            UPDATE users_data 
            SET profile_picture = ? 
            WHERE user_id = ?
        ''', (filename, session["user_id"]))

        connection.commit()

        return redirect(url_for('profile'))

@app.context_processor
def inject_user():
    if "user_id" in session:
        connection = sql.connect(DATABASE)
        connection.row_factory = sql.Row
        c = connection.cursor()

        c.execute("SELECT username, profile_picture FROM users_data WHERE user_id = ?", (session["user_id"],))
        user = c.fetchone()

        return dict(current_user=user)

    return dict(current_user=None)



if __name__ == "__main__":
    create_tables()
    create_posts_table()
    connection = sql.connect(DATABASE)
    c = connection.cursor()
    #c.execute(''' -header -csv database.db "select * from credenciales;" > database.csv ''')
    app.run(debug=True)