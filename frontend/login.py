import streamlit as st
from .auth import create_database, add_user, verify_user, generate_token, verify_token, get_all_users, delete_user, get_user_role
import streamlit.components.v1 as components

# # Initialize the database
# create_database()

# # Dummy user for testing
# add_user("admin", "P@ssw0rd!", "admin")

# Pages
def login_page():
    """Display the login page."""
    st.title("LLM Middleware")
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if verify_user(username, password):
            token = generate_token(username)
            st.session_state["token"] = token
            st.rerun()
        else:
            st.error("Invalid username or password.")

def app_page():
    """Display the main app page."""
    st.title("Welcome to the App")
    username = verify_token(st.session_state.get("token"))
    if not username:
        st.error("Session expired. Please log in again.")
        st.session_state["token"] = None
        st.rerun()

    st.write(f"Hello, {username}!")

    # App content
    st.write("This is your dashboard or app content.")

    # Logout button
    if st.button("Logout"):
        st.session_state["token"] = None
        st.rerun()

def register_page():
    """Display the registration page."""
    st.title("LLM Middleware")
    st.title("Register")
    username = st.text_input("Choose a username")
    password = st.text_input("Choose a password", type="password")
    register_button = st.button("Register")

    if register_button:
        success = add_user(username, password)
        if success:
            st.success("Registration successful! Please log in.")
        else:
            st.error("Username already exists. Please choose a different username.")


def admin_login_page():
    st.title("🛡️ Admin Login")
    username = st.text_input("Admin Username")
    password = st.text_input("Admin Password", type="password")
    login_button = st.button("Login as Admin")

    if login_button:
        if verify_user(username, password):
            role = get_user_role(username)
            if role == "admin":
                token = generate_token(username)
                st.session_state["admin_token"] = token
                st.success("Logged in as admin")
                st.rerun()
            else:
                st.error("This user is not an admin.")
        else:
            st.error("Invalid credentials.")

def admin_page():
    st.title("👤 Admin Dashboard")

    username = verify_token(st.session_state.get("admin_token"))
    if not username or get_user_role(username) != "admin":
        st.error("Unauthorized access.")
        st.stop()

    st.success(f"Welcome Admin: {username}")

    users = get_all_users()
    selected_user = st.selectbox("Select a user to delete", users)

    if selected_user == username:
        st.warning("You cannot delete yourself.")
    elif st.button("❌ Delete User"):
        delete_user(selected_user)
        st.success(f"User '{selected_user}' deleted successfully.")
        st.rerun()

    st.divider()
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")
    if st.button("➕ Add User"):
        if add_user(new_user, new_pass):
            st.success(f"User '{new_user}' added.")
            st.rerun()
        else:
            st.error("Username already exists.")