from os import getenv

from flask import Flask, session, request, jsonify
import sqlite3 as sql
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_cors import CORS
from dotenv import load_dotenv
import os
import uuid
import sqlalchemy

from datetime import timedelta, datetime

app = Flask(__name__)
load_dotenv()

app.secret_key = os,getenv("SECRET_KEY")

DATABASE = "users.db"

# ---------------- SESSION ---------------- #

app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flask_session"
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

Session(app)

# ---------------- UPLOADS ---------------- #

app.config['UPLOAD_POSTS'] = 'frontend/public/uploads/posts'
app.config['UPLOAD_PROFILE'] = 'frontend/public/uploads/profile_pic'

# crear carpetas automáticamente
os.makedirs(app.config['UPLOAD_POSTS'], exist_ok=True)
os.makedirs(app.config['UPLOAD_PROFILE'], exist_ok=True)

# extensiones permitidas
ALLOWED_EXTENSIONS = {
    'png',
    'jpg',
    'jpeg',
    'gif',
    'webp'
}

# ---------------- CORS ---------------- #

CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5173"],
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)



def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def get_db_connection():
    conn = sql.connect(DATABASE)
    conn.row_factory = sql.Row
    return conn



def create_tables():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users_data(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            profile_picture TEXT DEFAULT 'default.png'
        )
    ''')

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



@app.route("/")
def index():

    if not session.get("user_id"):
        return jsonify({"redirect": "/login"}), 401

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT filename, username, description, date_time
        FROM posts
        ORDER BY id DESC
    """)

    posts = cur.fetchall()

    conn.close()

    result = []

    for post in posts:

        ruta = os.path.join(
            app.config['UPLOAD_POSTS'],
            post["filename"]
        )

        # verificar que el archivo exista
        if os.path.exists(ruta):

            result.append({
                "filename": post["filename"],
                "username": post["username"],
                "description": post["description"],
                "date_time": post["date_time"]
            })

    return jsonify(result)



@app.route("/api/user")
def api_user():

    if not session.get("user_id"):
        return jsonify({"error": "No auth"}), 401

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT username, profile_picture
        FROM users_data
        WHERE user_id = ?
    """, (session["user_id"],))

    user = cur.fetchone()

    conn.close()

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "username": user["username"],
        "profile_picture": user["profile_picture"] or "default.png"
    })

# =========================================================
# LOGIN
# =========================================================

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({
            "error": "Usuario y contraseña requeridos"
        }), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM users_data
        WHERE username = ?
    """, (username,))

    user = cur.fetchone()

    conn.close()

    if not user:
        return jsonify({
            "error": "Usuario no encontrado"
        }), 404

    if not check_password_hash(user["password"], password):
        return jsonify({
            "error": "Contraseña incorrecta"
        }), 401

    # iniciar sesión
    session.clear()

    session["user_id"] = user["user_id"]
    session["username"] = user["username"]

    session.permanent = True

    return jsonify({
        "success": True,
        "username": user["username"]
    })

# =========================================================
# REGISTER
# =========================================================

@app.route('/register', methods=['POST'])
def register():

    data = request.get_json()

    firstname = data.get('firstname', '').strip()
    lastname = data.get('lastname', '').strip()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    confirmation = data.get('confirmation', '').strip()

    # validar campos
    if not all([
        firstname,
        lastname,
        username,
        email,
        password,
        confirmation
    ]):
        return jsonify({
            "error": "Datos incompletos"
        }), 400

    if password != confirmation:
        return jsonify({
            "error": "Contraseñas no coinciden"
        }), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # verificar username
    cur.execute("""
        SELECT user_id
        FROM users_data
        WHERE username = ?
    """, (username,))

    if cur.fetchone():
        conn.close()

        return jsonify({
            "error": "Usuario ya existe"
        }), 400

    # verificar email
    cur.execute("""
        SELECT user_id
        FROM users_data
        WHERE email = ?
    """, (email,))

    if cur.fetchone():
        conn.close()

        return jsonify({
            "error": "Correo ya registrado"
        }), 400

    hashed = generate_password_hash(password)

    cur.execute("""
        INSERT INTO users_data(
            firstname,
            lastname,
            username,
            email,
            password
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        firstname,
        lastname,
        username,
        email,
        hashed
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True
    })

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "success": True
    })

# =========================================================
# UPLOAD POSTS
# =========================================================

@app.route("/api/upload", methods=["POST"])
def upload():

    if not session.get("user_id"):
        return jsonify({
            "error": "No autenticado"
        }), 401

    file = request.files.get("imagen")
    description = request.form.get("descripcion", "").strip()

    if not file:
        return jsonify({
            "error": "No se envió imagen"
        }), 400

    if not description:
        return jsonify({
            "error": "Descripción requerida"
        }), 400

    # validar extensión
    if not allowed_file(file.filename):
        return jsonify({
            "error": "Formato de imagen inválido"
        }), 400

    # nombre seguro
    original_filename = secure_filename(file.filename)

    # obtener extensión
    ext = os.path.splitext(original_filename)[1].lower()

    # generar nombre único
    filename = f"{uuid.uuid4()}{ext}"

    ruta = os.path.join(
        app.config['UPLOAD_POSTS'],
        filename
    )

    try:

        file.save(ruta)

    except Exception as e:

        return jsonify({
            "error": f"Error guardando imagen: {str(e)}"
        }), 500

    # guardar en DB
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO posts(
            filename,
            user_id,
            username,
            date_time,
            description
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        filename,
        session["user_id"],
        session["username"],
        datetime.now(),
        description
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "filename": filename
    })

# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
def profile():

    if not session.get("user_id"):
        return jsonify({
            "error": "No autenticado"
        }), 401

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT username, profile_picture
        FROM users_data
        WHERE user_id = ?
    """, (session["user_id"],))

    user = cur.fetchone()

    conn.close()

    if not user:
        return jsonify({
            "error": "Usuario no encontrado"
        }), 404

    return jsonify({
        "user": user["username"],
        "profile_picture": user["profile_picture"] or "default.png"
    })

@app.route("/profile/edit", methods=["POST"])
def edit_profile():

    if not session.get("user_id"):
        return jsonify({
            "error": "No autenticado"
        }), 401

    file = request.files.get("imagen")

    if not file:
        return jsonify({
            "error": "No se envió imagen"
        }), 400

    # validar extensión
    if not allowed_file(file.filename):
        return jsonify({
            "error": "Formato inválido"
        }), 400

    # nombre seguro
    original_filename = secure_filename(file.filename)

    # extensión
    ext = os.path.splitext(original_filename)[1].lower()

    # nombre único
    filename = f"{uuid.uuid4()}{ext}"

    # ruta
    ruta = os.path.join(
        app.config['UPLOAD_PROFILE'],
        filename
    )

    try:

        file.save(ruta)

    except Exception as e:

        return jsonify({
            "error": f"Error guardando archivo: {str(e)}"
        }), 500

    # actualizar DB
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users_data
        SET profile_picture = ?
        WHERE user_id = ?
    """, (
        filename,
        session["user_id"]
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "filename": filename
    })

if __name__ == "__main__":

    create_tables()

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )