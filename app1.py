from flask import Flask, session, request, jsonify
import sqlite3 as sql
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import timedelta, datetime
import uuid
from flask_cors import CORS

app = Flask(__name__)

# 🔐 IMPORTANTE: clave fija (NO random en dev con sesiones)
app.secret_key = "rubi911426"

DATABASE = "users.db"



app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session"
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

Session(app)


app.config['UPLOAD_POSTS'] = 'frontend/public/uploads/posts'
app.config['UPLOAD_PROFILE'] = 'frontend/public/uploads/profile_pic'

# ---------------- CORS (CRÍTICO PARA REACT) ---------------- #

CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5173"],
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"]
)

# ---------------- DB ---------------- #

def create_tables():
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
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
    conn.commit()
    conn.close()


def create_posts_table():
    conn = sql.connect(DATABASE)
    cur = conn.cursor()
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
    conn.commit()
    conn.close()


# ---------------- INDEX ---------------- #

@app.route("/")
def index():
    if not session.get("user_id"):
        return jsonify({"redirect": "/login"})

    carpeta = app.config['UPLOAD_POSTS']

    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT filename, username, description FROM posts ORDER BY id DESC")
    posts = cur.fetchall()
    conn.close()

    result = []
    for post in posts:
        ruta = os.path.join(carpeta, post[0])
        if os.path.exists(ruta):
            result.append({
                "filename": post[0],
                "username": post[1],
                "description": post[2]
            })

    return jsonify(result)


# ---------------- USER SESSION ---------------- #

@app.route("/api/user")
def api_user():
    if not session.get("user_id"):
        return jsonify({"error": "No auth"}), 401

    conn = sql.connect(DATABASE)
    conn.row_factory = sql.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT username, profile_picture
        FROM users_data
        WHERE user_id = ?
    """, (session["user_id"],))

    user = cur.fetchone()
    conn.close()

    return jsonify({
        "username": user["username"],
        "profile_picture": user["profile_picture"] or "default.png"
    })

# ---------------- LOGIN ---------------- #

@app.route("/api/login", methods=["POST"])
def login():
    create_tables()
    create_posts_table()

    data = request.json

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    conn = sql.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users_data WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()

    if user and check_password_hash(user[5], password):

        session.clear()
        session["user_id"] = user[0]
        session["username"] = user[3]
        session.permanent = True

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
    cur = conn.cursor()

    cur.execute("SELECT * FROM users_data WHERE username = ?", (username,))
    if cur.fetchone():
        return jsonify({"error": "Usuario ya existe"}), 400

    hashed = generate_password_hash(password)

    cur.execute("""
        INSERT INTO users_data (firstname, lastname, username, email, password)
        VALUES (?, ?, ?, ?, ?)
    """, (firstname, lastname, username, email, hashed))

    conn.commit()
    conn.close()

    return jsonify({"success": True})


# logout

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})




@app.route("/api/upload", methods=["POST"])
def upload():
    if not session.get("user_id"):
        return jsonify({"error": "No autenticado"}), 401

    file = request.files.get("imagen")
    description = request.form.get("descripcion")

    if not file or not description:
        return jsonify({"error": "Datos incompletos"}), 400

    filename = secure_filename(file.filename)
    ruta = os.path.join(app.config['UPLOAD_POSTS'], filename)

    file.save(ruta)

    conn = sql.connect(DATABASE)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO posts (filename, user_id, username, date_time, description)
        VALUES (?, ?, ?, ?, ?)
    """, (filename, session["user_id"], session["username"], datetime.now(), description))

    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ---------------- PROFILE ---------------- #

@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return jsonify({"error": "No autenticado"}), 401

    conn = sql.connect(DATABASE)
    conn.row_factory = sql.Row
    cur = conn.cursor()

    cur.execute("SELECT username, profile_picture FROM users_data WHERE user_id = ?", (session["user_id"],))
    user = cur.fetchone()
    conn.close()

    return jsonify({
        "user": user["username"],
        "profile_picture": user["profile_picture"] or "default.png"
    })


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    create_tables()
    create_posts_table()
    app.run(debug=True)