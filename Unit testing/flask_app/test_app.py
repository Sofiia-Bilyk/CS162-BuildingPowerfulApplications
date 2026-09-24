"""
Unit tests for the Flask app.

Covers:
  - Login (valid, wrong password, unknown email)
  - Logout
  - Math expression evaluation (parser.py)
  - History endpoint (/dashboard)

Run:  pytest test_app.py -v
"""

import os
import tempfile
import pytest

# Point the app at a fresh, temporary database for every test session.
# Must be set BEFORE importing app so the DATABASE path is set correctly.
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")

import app as flask_app          # the Flask application module
import parser as expr_parser     # the expression parser module


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    """
    Create a test client that uses a temporary, isolated database.
    The DB is initialised once for the whole module, then torn down.
    """
    flask_app.DATABASE = _db_path
    flask_app.app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
    })

    with flask_app.app.test_client() as client:
        with flask_app.app.app_context():
            flask_app.init_db()
        yield client

    # Cleanup: close and delete the temp DB file
    os.close(_db_fd)
    os.unlink(_db_path)


def register_user(client, email="test@example.com", password="password123"):
    """Helper: POST to /register."""
    return client.post("/register", data={"email": email, "password": password},
                       follow_redirects=True)


def login_user(client, email="test@example.com", password="password123"):
    """Helper: POST to /login."""
    return client.post("/login", data={"email": email, "password": password},
                       follow_redirects=True)


def logout_user(client):
    """Helper: POST to /logout."""
    return client.post("/logout", follow_redirects=True)


# ---------------------------------------------------------------------------
# Login tests
# ---------------------------------------------------------------------------

class TestLogin:

    def test_login_valid_credentials(self, client):
        """A registered user can log in successfully."""
        register_user(client)
        resp = login_user(client)
        assert resp.status_code == 200
        # After login we land on the dashboard
        assert b"Dashboard" in resp.data

    def test_login_wrong_password(self, client):
        """Wrong password shows an error and stays on the login page."""
        resp = login_user(client, password="wrongpassword")
        assert b"Invalid email or password" in resp.data

    def test_login_unknown_email(self, client):
        """Unregistered email shows an error."""
        resp = login_user(client, email="nobody@example.com")
        assert b"Invalid email or password" in resp.data

    def test_login_get_returns_form(self, client):
        """GET /login returns the login form."""
        resp = client.get("/login")
        assert resp.status_code == 200
        assert b"Login" in resp.data


# ---------------------------------------------------------------------------
# Logout tests
# ---------------------------------------------------------------------------

class TestLogout:

    def test_logout_redirects_to_login(self, client):
        """After logout the user is redirected to the login page."""
        register_user(client, email="logout@example.com")
        login_user(client, email="logout@example.com")
        resp = logout_user(client)
        assert resp.status_code == 200
        assert b"Login" in resp.data

    def test_dashboard_inaccessible_after_logout(self, client):
        """Visiting /dashboard after logout redirects back to login."""
        logout_user(client)
        resp = client.get("/dashboard", follow_redirects=True)
        assert b"Login" in resp.data

    def test_logout_shows_confirmation(self, client):
        """Logout flash message is displayed."""
        login_user(client)
        resp = logout_user(client)
        assert b"Logged out" in resp.data


# ---------------------------------------------------------------------------
# Expression parser tests
# ---------------------------------------------------------------------------

class TestParser:
    """Tests for the recursive descent parser (no Flask needed)."""

    # --- basic operations ---
    def test_addition(self):
        assert expr_parser.evaluate("1 + 2") == 3

    def test_subtraction(self):
        assert expr_parser.evaluate("10 - 4") == 6

    def test_multiplication(self):
        assert expr_parser.evaluate("3 * 4") == 12

    def test_division(self):
        assert expr_parser.evaluate("10 / 4") == 2.5

    def test_exponentiation(self):
        assert expr_parser.evaluate("2 ^ 10") == 1024

    # --- precedence and associativity ---
    def test_operator_precedence(self):
        # 2 + 3 * 4 = 14, not 20
        assert expr_parser.evaluate("2 + 3 * 4") == 14

    def test_parentheses_override_precedence(self):
        assert expr_parser.evaluate("(2 + 3) * 4") == 20

    def test_exponentiation_is_right_associative(self):
        # 2^3^2 = 2^(3^2) = 2^9 = 512
        assert expr_parser.evaluate("2 ^ 3 ^ 2") == 512

    # --- unary minus ---
    def test_unary_minus(self):
        assert expr_parser.evaluate("-5") == -5

    def test_unary_minus_in_expression(self):
        assert expr_parser.evaluate("10 + -3") == 7

    # --- decimals ---
    def test_decimal_numbers(self):
        assert expr_parser.evaluate("1.5 + 2.5") == 4.0

    # --- edge cases ---
    def test_division_by_zero_raises(self):
        with pytest.raises(expr_parser.ParseError):
            expr_parser.evaluate("5 / 0")

    def test_empty_expression_raises(self):
        with pytest.raises(expr_parser.ParseError):
            expr_parser.evaluate("")

    def test_invalid_characters_raise(self):
        with pytest.raises(expr_parser.ParseError):
            expr_parser.evaluate("2 + x")

    def test_mismatched_parens_raise(self):
        with pytest.raises(expr_parser.ParseError):
            expr_parser.evaluate("(2 + 3")

    def test_nested_parentheses(self):
        assert expr_parser.evaluate("((2 + 3) * (1 + 1))") == 10


# ---------------------------------------------------------------------------
# History endpoint tests
# ---------------------------------------------------------------------------

class TestHistory:

    @pytest.fixture(autouse=True)
    def login_fresh_user(self, client):
        """Register a unique user and log in for each test in this class."""
        # Use a unique email per test to avoid state bleed
        email = f"hist_{id(self)}@example.com"
        register_user(client, email=email)
        login_user(client, email=email)
        yield
        logout_user(client)

    def test_empty_history_message(self, client):
        """Dashboard says 'No expressions evaluated yet' for a new user."""
        resp = client.get("/dashboard")
        assert resp.status_code == 200
        assert b"No expressions" in resp.data

    def test_evaluated_expression_appears_in_history(self, client):
        """After evaluating an expression it shows up in the history table."""
        client.post("/evaluate", data={"expression": "3 + 4"},
                    follow_redirects=True)
        resp = client.get("/dashboard")
        assert b"3 + 4" in resp.data
        assert b"7" in resp.data

    def test_multiple_expressions_all_visible(self, client):
        """All evaluated expressions appear in history."""
        client.post("/evaluate", data={"expression": "1 + 1"})
        client.post("/evaluate", data={"expression": "2 * 5"})
        resp = client.get("/dashboard")
        assert b"1 + 1" in resp.data
        assert b"2 * 5" in resp.data

    def test_history_requires_login(self, client):
        """Logged-out users are redirected away from /dashboard."""
        logout_user(client)
        resp = client.get("/dashboard", follow_redirects=True)
        assert b"Login" in resp.data

    def test_error_expression_saved_in_history(self, client):
        """Invalid expressions are still saved (with an error result)."""
        client.post("/evaluate", data={"expression": "5 / 0"},
                    follow_redirects=True)
        resp = client.get("/dashboard")
        assert b"5 / 0" in resp.data
        assert b"Error" in resp.data
