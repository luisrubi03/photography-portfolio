from flask import Flask, session, redirect, request, jsonify
import sqlite3 as sql
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import timedelta, datetime
import uuid
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = "users.db"

app.config["SESSION_TYPE"] = "filesystem"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
Session(app)

app.config['UPLOAD_POSTS'] = 'static/uploads/posts'
app.config['UPLOAD_PROFILE'] = 'static/uploads/profile_pic'
CORS(app, supports_credentials=True)


# ---------------- DB ---------------- #

def create_tables():
    connection = sql.connect(DATABASE)
    cur = connection.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users_data(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            profile_picture TEXT DEFAULT 'default.png'
        )
    ''')
    connection.commit()
    connection.close()


def create_posts_table():
    connection = sql.connect(DATABASE)
    cur = connection.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS posts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            description TEXT NOT NULL
        )
    ''')
    connection.commit()
    connection.close()


# ---------------- INDEX ---------------- #

@app.route("/")
def index():
    if not session.get("username"):
        return jsonify({"redirect": "/login"})

    carpeta = app.config['UPLOAD_POSTS']

    connection = sql.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("SELECT filename, username, description FROM posts ORDER BY id DESC")
    posts = cursor.fetchall()

    posts_validos = []
    for post in posts:
        ruta = os.path.join(carpeta, post[0])
        if os.path.exists(ruta):
            posts_validos.append({
                "filename": post[0],
                "username": post[1],
                "description": post[2]
            })

    return jsonify(posts_validos)


# ---------------- LOGIN ---------------- #

@app.route("/login", methods=['POST'])
def login():
    create_tables()
    create_posts_table()

    data = request.json

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    connection = sql.connect(DATABASE)
    c = connection.cursor()
    c.execute("SELECT * FROM users_data WHERE username = ?", (username,))
    user = c.fetchone()
    connection.close()

    if user and check_password_hash(user[5], password):
        session["user_id"] = user[0]
        session["username"] = user[3]
        return jsonify({"success": True})

    return jsonify({"error": "Credenciales incorrectas"}), 401


# ---------------- REGISTER ---------------- #

@app.route('/register', methods=['POST'])
def register():
    data = request.json

    firstname = data.get('firstname')
    lastname = data.get('lastname')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirmation = data.get('confirmation')

    if not all([firstname, lastname, username, email, password, confirmation]):
        return jsonify({"error": "Datos incompletos"}), 400

    if password != confirmation:
        return jsonify({"error": "Contraseñas no coinciden"}), 400

    conn = sql.connect(DATABASE)
    c = conn.cursor()

    c.execute("SELECT * FROM users_data WHERE username = ?", (username,))
    if c.fetchone():
        return jsonify({"error": "Usuario ya existe"}), 400

    passwordHash = generate_password_hash(password)

    c.execute("""
        INSERT INTO users_data (firstname, lastname, username, email, password)
        VALUES (?, ?, ?, ?, ?)
    """, (firstname, lastname, username, email, passwordHash))

    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ---------------- LOGOUT ---------------- #

@app.route("/logout", methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})


# ---------------- UPLOAD ---------------- #

@app.route("/upload", methods=['POST'])
def upload():
    if not session.get("username"):
        return jsonify({"error": "No autenticado"}), 401

    file = request.files.get('imagen')
    description = request.form.get('descripcion')

    if not file or not description:
        return jsonify({"error": "Datos incompletos"}), 400

    filename = secure_filename(file.filename)
    ruta = os.path.join(app.config['UPLOAD_POSTS'], filename)

    file.save(ruta)

    connection = sql.connect(DATABASE)
    c = connection.cursor()

    c.execute('''
        INSERT INTO posts (filename, user_id, username, date_time, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (filename, session["user_id"], session["username"], datetime.now(), description))

    connection.commit()

    return jsonify({"success": True})


# ---------------- PROFILE ---------------- #

@app.route("/profile")
def profile():
    if not session.get("username"):
        return jsonify({"error": "No autenticado"}), 401

    connection = sql.connect(DATABASE)
    connection.row_factory = sql.Row
    c = connection.cursor()

    c.execute("SELECT username, profile_picture FROM users_data WHERE user_id = ?", (session["user_id"],))
    user = c.fetchone()

    return jsonify({
        "username": user["username"],
        "profile_picture": user["profile_picture"] or "default.png"
    })


# ---------------- EDIT PROFILE ---------------- #

@app.route("/profile/edit", methods=['POST'])
def profile_edit():
    if "user_id" not in session:
        return jsonify({"error": "No autenticado"}), 401

    file = request.files.get('imagen')

    if not file:
        return jsonify({"error": "No file"}), 400

    filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)

    os.makedirs(app.config['UPLOAD_PROFILE'], exist_ok=True)
    ruta = os.path.join(app.config['UPLOAD_PROFILE'], filename)
    file.save(ruta)

    connection = sql.connect(DATABASE)
    c = connection.cursor()

    c.execute('''
        UPDATE users_data SET profile_picture = ?
        WHERE user_id = ?
    ''', (filename, session["user_id"]))

    connection.commit()

    return jsonify({"success": True})


# ---------------- BUSQUEDA ---------------- #

@app.route("/busqueda", methods=['POST'])
def buscar():
    data = request.json
    busqueda = data.get("busqueda")

    connection = sql.connect(DATABASE)
    c = connection.cursor()

    c.execute("SELECT username FROM users_data WHERE username = ?", (busqueda,))
    resultado = c.fetchone()

    connection.close()

    if resultado:
        return jsonify({"user": busqueda})

    return jsonify({"error": "No encontrado"}), 404


@app.route("/user/<user>")
def search_profile(user):
    return jsonify({"user": user})


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    create_tables()
    create_posts_table()
    app.run(debug=True)