import jwt
import sqlite3
import datetime
import secrets

# Secret key for token encoding/decoding
SECRET_KEY = secrets.token_urlsafe(32)

def create_database():
    """Initialize the SQLite database with role support."""
    conn = sqlite3.connect("data_storage/user_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    """)
    conn.commit()
    conn.close()

def add_user(username, password, role='user'):
    """Add a new user with optional role."""
    conn = sqlite3.connect("data_storage/user_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        conn.close()
        return False
    else:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )
        conn.commit()
        conn.close()
        return True
    
def get_all_users():
    """Return a list of all usernames in the DB."""
    conn = sqlite3.connect("data_storage/user_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

def delete_user(username):
    """Delete a user from the DB."""
    conn = sqlite3.connect("data_storage/user_database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def verify_user(username, password):
    """Verify user credentials."""
    conn = sqlite3.connect("data_storage/user_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def get_user_role(username):
    """Return the user's role."""
    conn = sqlite3.connect("data_storage/user_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def generate_token(username):
    """Generate a JWT token."""
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token):
    """Verify a JWT token and check if the user still exists in DB."""
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = decoded.get("username")
        
        # Check if user still exists in the database
        conn = sqlite3.connect("data_storage/user_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        user_exists = cursor.fetchone() is not None
        conn.close()

        if not user_exists:
            return None  # User revoked/deleted

        return username
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
