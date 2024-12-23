import streamlit as st
from .auth import create_database, add_user, verify_user, generate_token, verify_token
import streamlit.components.v1 as components

# Initialize the database
create_database()

# Dummy user for testing
# add_user("admin", "password")

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

# # Router
# if "token" not in st.session_state:
#     st.session_state["token"] = None

# if st.session_state["token"]:
#     app_page()
# else:
#     tab = st.sidebar.radio("Navigation", ["Login", "Register"])
#     if tab == "Login":
#         login_page()
#     else:
#         register_page()
