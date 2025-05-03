import jwt
import sqlite3
import datetime
import secrets

# Secret key for token encoding/decoding
SECRET_KEY = secrets.token_urlsafe(32)

def create_database():
    """Initialize the SQLite database."""
    conn = sqlite3.connect("data_storage/user_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_user(username, password):
    """Add a new user to the database if they don't already exist."""
    conn = sqlite3.connect("data_storage/user_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        conn.close()
        return False  # User already exists
    else:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True  # User added successfully

def verify_user(username, password):
    """Verify user credentials."""
    conn = sqlite3.connect("data_storage/user_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def generate_token(username):
    """Generate a JWT token."""
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token):
    """Verify a JWT token."""
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded["username"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
