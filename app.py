from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"   # change this in production

DATABASE = "users.db"


# -------------------------------
# DATABASE SETUP
# -------------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# -------------------------------
# HOME
# -------------------------------
@app.route('/')
def home():
    if "user" in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# -------------------------------
# LOGIN
# -------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[3], password):
            session['user'] = user[1]  # store name
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password", "error")

    return render_template('login.html')


# -------------------------------
# SIGNUP
# -------------------------------
@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    hashed_password = generate_password_hash(password)

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_password)
        )

        conn.commit()
        conn.close()

        flash("Account created successfully!", "success")
    except sqlite3.IntegrityError:
        flash("Email already exists!", "error")

    return redirect(url_for('login'))


# -------------------------------
# DASHBOARD (AFTER LOGIN)
# -------------------------------
@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        return redirect(url_for('login'))

    return f"""
    <h1>Welcome {session['user']} 🎉</h1>
    <a href="/logout">Logout</a>
    """


# -------------------------------
# LOGOUT
# -------------------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully", "info")
    return redirect(url_for('login'))


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)