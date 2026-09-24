"""
Flask app: user auth + arithmetic expression evaluator.

Routes:
  GET  /              → redirect to dashboard or login
  GET  /register      → registration form
  POST /register      → create account
  GET  /login         → login form
  POST /login         → authenticate
  POST /logout        → clear session
  GET  /dashboard     → show history form (login required)
  POST /evaluate      → evaluate expression, save to history (login required)
"""

import sqlite3
import os
from flask import (Flask, g, session, redirect, url_for,
                   render_template_string, request, flash)
from werkzeug.security import generate_password_hash, check_password_hash
from parser import evaluate, ParseError

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# Path to the SQLite database file (sits next to app.py)
DATABASE = os.path.join(os.path.dirname(__file__), "app.db")


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    """Return a database connection, opening one if not already open."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # rows behave like dicts
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables if they don't exist yet."""
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            email    TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id),
            expression TEXT    NOT NULL,
            result     TEXT    NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    db.commit()


# Initialise the DB the first time a request comes in (avoids app-context issues
# when importing the module in tests).
@app.before_request
def ensure_db():
    init_db()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def current_user_id():
    """Return the logged-in user's id, or None."""
    return session.get("user_id")


def login_required(f):
    """Simple decorator: redirect to login if not authenticated."""
    from functools import wraps

    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user_id():
            flash("Please log in first.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return wrapper


# ---------------------------------------------------------------------------
# HTML templates (inline for simplicity — no separate template files needed)
# ---------------------------------------------------------------------------

BASE = """
<!doctype html>
<html>
<head><title>MathApp</title></head>
<body>
<nav>
  {% if session.user_id %}
    <a href="{{ url_for('dashboard') }}">Dashboard</a> |
    <form method="post" action="{{ url_for('logout') }}" style="display:inline">
      <button type="submit">Log out</button>
    </form>
  {% else %}
    <a href="{{ url_for('login') }}">Login</a> |
    <a href="{{ url_for('register') }}">Register</a>
  {% endif %}
</nav>
<hr>
{% with messages = get_flashed_messages() %}
  {% for m in messages %}<p style="color:red">{{ m }}</p>{% endfor %}
{% endwith %}
{% block body %}{% endblock %}
</body>
</html>
"""

REGISTER_TMPL = BASE.replace("{% block body %}{% endblock %}", """
{% block body %}
<h2>Register</h2>
<form method="post">
  Email: <input name="email" type="email" required><br>
  Password: <input name="password" type="password" required><br>
  <button type="submit">Register</button>
</form>
{% endblock %}
""")

LOGIN_TMPL = BASE.replace("{% block body %}{% endblock %}", """
{% block body %}
<h2>Login</h2>
<form method="post">
  Email: <input name="email" type="email" required><br>
  Password: <input name="password" type="password" required><br>
  <button type="submit">Login</button>
</form>
{% endblock %}
""")

DASHBOARD_TMPL = BASE.replace("{% block body %}{% endblock %}", """
{% block body %}
<h2>Dashboard</h2>
<form method="post" action="{{ url_for('do_evaluate') }}">
  Expression: <input name="expression" required>
  <button type="submit">Evaluate</button>
</form>
{% if result is not none %}
  <p>Result: <strong>{{ result }}</strong></p>
{% endif %}
<h3>History</h3>
{% if history %}
  <table border="1" cellpadding="4">
    <tr><th>Expression</th><th>Result</th><th>Time</th></tr>
    {% for row in history %}
      <tr><td>{{ row['expression'] }}</td><td>{{ row['result'] }}</td><td>{{ row['created_at'] }}</td></tr>
    {% endfor %}
  </table>
{% else %}
  <p>No expressions evaluated yet.</p>
{% endif %}
{% endblock %}
""")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    if current_user_id():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not email or not password:
            flash("Email and password are required.")
            return render_template_string(REGISTER_TMPL)

        db = get_db()
        # Check for duplicate email
        if db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
            flash("That email is already registered.")
            return render_template_string(REGISTER_TMPL)

        db.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, generate_password_hash(password)),
        )
        db.commit()
        flash("Account created! Please log in.")
        return redirect(url_for("login"))

    return render_template_string(REGISTER_TMPL)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        if user is None or not check_password_hash(user["password"], password):
            flash("Invalid email or password.")
            return render_template_string(LOGIN_TMPL)

        session.clear()
        session["user_id"] = user["id"]
        return redirect(url_for("dashboard"))

    return render_template_string(LOGIN_TMPL)


@app.post("/logout")
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    history = db.execute(
        "SELECT expression, result, created_at FROM history "
        "WHERE user_id = ? ORDER BY created_at DESC",
        (current_user_id(),),
    ).fetchall()
    return render_template_string(DASHBOARD_TMPL, history=history, result=None)


@app.post("/evaluate")
@login_required
def do_evaluate():
    expression = request.form.get("expression", "").strip()
    db = get_db()

    try:
        value = evaluate(expression)
        # Format cleanly: drop the decimal point for whole numbers
        result = str(int(value)) if value == int(value) else str(value)
    except ParseError as e:
        result = f"Error: {e}"
    except Exception:
        result = "Error: could not evaluate expression"

    # Save every attempt (including errors) to history
    db.execute(
        "INSERT INTO history (user_id, expression, result) VALUES (?, ?, ?)",
        (current_user_id(), expression, result),
    )
    db.commit()

    history = db.execute(
        "SELECT expression, result, created_at FROM history "
        "WHERE user_id = ? ORDER BY created_at DESC",
        (current_user_id(),),
    ).fetchall()
    return render_template_string(DASHBOARD_TMPL, history=history, result=result)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
