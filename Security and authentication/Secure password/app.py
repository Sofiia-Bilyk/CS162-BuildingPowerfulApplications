"""
This codefixes three major security flaws from the original
requires_authorization.py:

1. Credentials are no longer hardcoded in source code — they live in a SQLite database.
2. Passwords are never stored in plain text — only bcrypt hashes are stored.
3. Each password hash uses a unique, randomly generated salt — this prevents
   rainbow table attacks and ensures that two users with the same password
   will have completely different hashes in the database.

How bcrypt works:
- bcrypt.gensalt() generates a random salt (e.g. "$2b$12$abcdef...")
- bcrypt.hashpw(password, salt) combines the salt + password and produces
  a fixed-length hash. The salt is embedded in the output, so no separate
  salt column is needed.
- bcrypt.checkpw(password, stored_hash) extracts the salt from the stored
  hash, re-hashes the candidate password with that same salt, and compares.
"""

# sqlite3: Python's built-in module for interacting with SQLite databases
import sqlite3
# functools: provides @functools.wraps to preserve the original function's
# metadata (name, docstring) when wrapping it with a decorator
import functools
# bcrypt: a password hashing library designed to be slow on purpose,
# making brute-force attacks computationally expensive
import bcrypt
# Flask utilities for building the web app and handling HTTP requests
from flask import Flask, request, jsonify

# Path to the SQLite database file that stores user credentials
DATABASE = "users.db"


def get_db():
    """Get a database connection.

    Uses sqlite3.Row as the row factory so that columns can be accessed
    by name (e.g. row["password_hash"]) instead of by index (row[0]).
    """
    conn = sqlite3.connect(DATABASE)
    # sqlite3.Row allows dictionary-style access to columns by name
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the users table and populate it with initial users.

    This function is called once at startup. It creates the table if it
    doesn't exist, then inserts each user with a uniquely salted bcrypt
    hash of their password. The plain-text passwords here are only used
    for this initial seeding and are never stored.
    """
    conn = get_db()

    # Create the users table. We store only the hash, not the plain password.
    # The password_hash column contains the salt embedded within it (bcrypt
    # format: "$2b$<cost>$<22-char salt><31-char hash>").
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    # These plain-text passwords are used ONLY for initial seeding.
    # In production, users would register through a sign-up form and
    # their passwords would be hashed immediately upon receipt.
    initial_users = {
        "Booker": "password",
        "Annabel": "password",
        "Steve": "password",
        "Tawny": "password",
        "Kasha": "password",
        "Tameika": "password",
        "Marie": "password",
        "Samual": "password",
        "Cyrus": "password",
        "Joya": "password",
    }

    for username, password in initial_users.items():
        # bcrypt.gensalt() generates a unique random salt each time it's called.
        # This means even though all users here have the same password ("password"),
        # each will have a completely different hash stored in the database.
        # The default cost factor is 12, meaning 2^12 = 4096 hashing rounds.
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        try:
            # Use parameterized queries (?) to prevent SQL injection.
            # The hash is stored as a UTF-8 string in the database.
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashed.decode("utf-8")),
            )
        except sqlite3.IntegrityError:
            # UNIQUE constraint on username — skip if user already exists
            pass

    conn.commit()
    conn.close()


def ok_user_and_password(username, password):
    """Check supplied credentials against the hashed password in the database.

    Steps:
    1. Query the database for the stored hash matching the given username.
       Uses a parameterized query (?) to prevent SQL injection.
    2. If the user doesn't exist, return False.
    3. Use bcrypt.checkpw() to verify the password. bcrypt extracts the salt
       from the stored hash, re-hashes the candidate password with that salt,
       and compares the result to the stored hash.

    Returns True if credentials are valid, False otherwise.
    """
    conn = get_db()
    # Parameterized query — the ? placeholder ensures the username value
    # is safely escaped, preventing SQL injection attacks
    row = conn.execute(
        "SELECT password_hash FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    # If no user with that username exists, authentication fails
    if row is None:
        return False

    # bcrypt.checkpw() handles the comparison securely:
    # - Extracts the salt from the stored hash
    # - Hashes the candidate password with that same salt
    # - Compares the two hashes in constant time (prevents timing attacks)
    return bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8"))


def authenticate():
    """Return a 401 response requesting authentication.

    The WWW-Authenticate header tells the browser to show a login dialog
    using HTTP Basic Authentication. The 'realm' is a label displayed to
    the user describing which area they are authenticating for.
    """
    resp = jsonify({"message": "Authenticate."})
    resp.status_code = 401  # 401 Unauthorized
    # This header triggers the browser's built-in login prompt
    resp.headers["WWW-Authenticate"] = 'Basic realm="Main"'
    return resp


def requires_authorization(f):
    """A decorator which requires HTTP basic authentication.

    When applied to a Flask route, this decorator:
    1. Checks if the request includes Basic Auth credentials
       (request.authorization is populated by Flask from the
       Authorization header).
    2. Validates the credentials against the database using
       ok_user_and_password().
    3. If valid, calls the original route function.
    4. If invalid or missing, returns a 401 response prompting login.

    @functools.wraps(f) preserves the original function's __name__ and
    __doc__, which Flask needs to correctly register routes.
    """

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        # Flask parses the Authorization header and provides .username
        # and .password attributes. If no header is present, auth is None.
        auth = request.authorization
        if not auth or not ok_user_and_password(auth.username, auth.password):
            return authenticate()
        # Credentials are valid — proceed to the actual route handler
        return f(*args, **kwargs)

    return decorated


# --- Flask App ---

app = Flask(__name__)


@app.route("/")
def index():
    """Public route — no authentication required."""
    return jsonify({"message": "Welcome! Try /secret for a protected route."})


@app.route("/secret")
@requires_authorization  # This decorator protects the route — only authenticated users can access it
def secret():
    """Protected route — requires valid Basic Auth credentials."""
    return jsonify({"message": f"Hello {request.authorization.username}, you are authenticated!"})


if __name__ == "__main__":
    # Initialize the database (create table + seed users) before starting the server
    init_db()
    # debug=True enables auto-reload on code changes and detailed error pages
    # NOTE: never use debug=True in production!
    app.run(debug=True)
