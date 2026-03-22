from flask import Flask, session, render_template, url_for, redirect, request
import requests
from flask_session import Session
import sqlite3 as sql
app = Flask(__name__)
app_secret_key = "Santiago2015#"
DATABASE= "database.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE

def create_tables():
    connection= sql.connect(DATABASE)
    cur = connection.cursor()
    cur.execute(''' CREATE TABLE IF NOT EXISTS credentials(
                    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,username VARCHAR(40) NOT NULL,email VARCHAR(100)NOT NULL,
        password VARCHAR(40) NOT NULL, FOREIGN KEY(id))''')
    connection.commit()
    connection.close()
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
        if username:
            session["user"] = username
            return redirect(url_for('index'))
    return render_template('login.html')

if __name__ == "__main__":
    create_tables()
    app.run(debug=True)