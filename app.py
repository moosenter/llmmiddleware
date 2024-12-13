import streamlit as st
import requests
import yaml
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import os

# Function to display chat history
def display_chat_history(chat_history, model_name):
    for message in chat_history:
        role_display = "User" if message["role"] == "user" else model_name
        role = "user" if message["role"] == "user" else "assistant"
        if role == "user":
            with st.chat_message(role, avatar="👤"):
                st.write(message["content"])
        else:
            with st.chat_message(role, avatar="🤖"):
                st.write(message["content"])

# Helper function to query each LLM
def query_llm(model_config, chat_history):
    print(f"Querying {model_config['name']} with {chat_history}")
    try:
        model = model_config["provider"] + ":" + model_config["model"]
        try:
            model_response = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/model', json={'model':model}).json()['response']
            response = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/generate', json=chat_history).json()['response']
        except:
            model_response = requests.post('http://localhost:8000/model', json={'model':model}).json()['response']
            response = requests.post('http://localhost:8000/generate', json=chat_history).json()['response']
        print(
            f"Response from {model_config['name']}: {response}"
        )
        return response
    except Exception as e:
        st.error(f"Error querying {model_config['name']}: {e}")
        return "Error with LLM response."
    
def query_llm_and_append_to_history(model_config, chat_history):
    response = query_llm(model_config, chat_history)
    chat_history.append({"role": "assistant", "content": response})
    if str(chat_history) == "st.session_state.chat_history_1":
        st.session_state.chat_history_1.append(chat_history)
    if str(chat_history) == "st.session_state.chat_history_2":
        st.session_state.chat_history_2.append(chat_history)
    # Reset processing state
    return "Success"

def stramlit_ui():
    # configured_llms = [{'name':'LLAMA3.2', 'provider':'groq', 'model': 'llama-3.2-3b-preview'}]
    # Load configuration and initialize aisuite client
    with open("config/AppConfig.yaml", "r") as file:
        config = yaml.safe_load(file)
    configured_llms = config["llms"]
    # Configure Streamlit to use wide mode and hide the top streamlit menu
    st.set_page_config(layout="wide", menu_items={})
    # Add heading with padding
    # st.markdown(
    #     "<div style='padding-top: 1rem;'><h2 style='text-align: center; color: #ffffff;font-size:25px;'>Chat & Compare LLM responses</h2></div>",
    #     unsafe_allow_html=True,
    # )
    st.markdown(
        """
        <style>
            /* Apply default font size globally */
            html, body, [class*="css"] {
                font-size: 16px !important;
            }
            
            /* Style for Reset button focus */
            button[data-testid="stButton"][aria-label="Reset Chat"]:focus {
                border-color: red !important;
                box-shadow: 0 0 0 2px red !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <style>
            /* Hide Streamlit's default top bar */
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            
            /* Remove top padding/margin */
            .block-container {
                padding-top: 0rem;
                padding-bottom: 0rem;
                margin-top: 0rem;
            }

            /* Remove padding from the app container */
            .appview-container {
                padding-top: 0rem;
            }
            
            /* Custom CSS for scrollable chat container */
            .chat-container {
                height: 650px;
                overflow-y: auto !important;
                background-color: #1E1E1E;
                border: 1px solid #333;
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
            }
            
            /* Ensure the container takes full width */
            .stMarkdown {
                width: 100%;
            }
            
            /* Style for chat messages to ensure they're visible */
            .chat-message {
                margin: 10px 0;
                padding: 10px;
            }

            #text_area_1 {
                min-height: 20px !important;
            } 
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Initialize session states
    if "chat_history_1" not in st.session_state:
        st.session_state.chat_history_1 = []
    if "chat_history_2" not in st.session_state:
        st.session_state.chat_history_2 = []
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    if "use_comparison_mode" not in st.session_state:
        st.session_state.use_comparison_mode = False

    # Top Section - Controls
    col1, col2 = st.columns([1, 2])
    with col1:
        st.session_state.use_comparison_mode = st.checkbox("Comparison Mode", value=False)

    # Move LLM selection below comparison mode checkbox - now in columns
    llm_col1, llm_col2 = st.columns(2)
    with llm_col1:
        selected_model_1 = st.selectbox(
            "Choose LLM Model 1",
            [llm["name"] for llm in configured_llms],
            key="model_1",
            index=0 if configured_llms else 0,
        )
    with llm_col2:
        if st.session_state.use_comparison_mode:
            selected_model_2 = st.selectbox(
                "Choose LLM Model 2",
                [llm["name"] for llm in configured_llms],
                key="model_2",
                index=1 if len(configured_llms) > 1 else 0,
            )

    # Display Chat Histories first, always
    # Middle Section - Display Chat Histories
    if st.session_state.use_comparison_mode:
        col1, col2 = st.columns(2)
        with col1:
            chat_container = st.container(height=500)
            with chat_container:
                display_chat_history(st.session_state.chat_history_1, selected_model_1)
        with col2:
            chat_container = st.container(height=500)
            with chat_container:
                display_chat_history(st.session_state.chat_history_2, selected_model_2)
    else:
        chat_container = st.container(height=500)
        with chat_container:
            display_chat_history(st.session_state.chat_history_1, selected_model_1)

    # Bottom Section - User Input
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    if "query_input" not in st.session_state:
        st.session_state.query_input = ""

    col1, col2, col3 = st.columns([6, 1, 1])
    with col1:
        user_query = st.text_area(
            label="Enter your query",
            label_visibility="collapsed",
            placeholder="Enter your query...",
            key="query_input",
            height=100
        )

    # CSS for aligning buttons with the bottom of the text area
    st.markdown(
        """
        <style>
            /* Adjust the container of the buttons to align at the bottom */
            .stButton > button {
                margin-top: 5px !important; /* Adjust the margin to align */
            }

            /* Align buttons and "Processing..." text to the bottom of the text area */
            .button-container {
                margin-top: 5px !important;
                text-align: center; /* Center-aligns "Processing..." */
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with col2:
        send_button = False  # Initialize send_button
        if st.session_state.is_processing:
            st.markdown(
                "<div class='button-container'>Processing... ⏳</div>",
                unsafe_allow_html=True,
            )
        else:
            send_button = st.button("Send Query", use_container_width=True)

    with col3:
        if st.button("Reset Chat", use_container_width=True):
            st.session_state.chat_history_1 = []
            st.session_state.chat_history_2 = []
            st.session_state.is_processing = False
            st.rerun()

    # Handle send button click and processing
    if send_button and user_query and not st.session_state.is_processing:
        # Set processing state
        st.session_state.is_processing = True

        # Append user's message to chat histories first
        st.session_state.chat_history_1.append({"role": "user", "content": user_query})
        if st.session_state.use_comparison_mode:
            st.session_state.chat_history_2.append({"role": "user", "content": user_query})

        st.rerun()
    
    # Handle the actual processing
    if st.session_state.is_processing and user_query:
        # Query the selected LLM(s)
        with ThreadPoolExecutor() as executor:
            model_config_1 = next(
                llm for llm in configured_llms if llm["name"] == selected_model_1
            )
            future_1 = executor.submit(query_llm_and_append_to_history, model_config_1, st.session_state.chat_history_1)
            # response_1 = query_llm(model_config_1, st.session_state.chat_history_1)
            try:
                future_1.result(timeout=30)
                # st.session_state.chat_history_1.append({"role": "assistant", "content": response_1})
            except TimeoutError:
                st.error("Process stopped: It took too long to complete.")
                st.session_state.is_processing = False
                st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {e}")
                # Reset processing state
                st.session_state.is_processing = False
                st.rerun()
            
            if st.session_state.use_comparison_mode:
                model_config_2 = next(
                    llm for llm in configured_llms if llm["name"] == selected_model_2
                )
                future_2 = executor.submit(query_llm_and_append_to_history, model_config_2, st.session_state.chat_history_2)
                # response_2 = query_llm(model_config_2, st.session_state.chat_history_2)
                try:
                    future_2.result(timeout=30)
                except TimeoutError:
                    st.error("Process stopped: It took too long to complete.")
                    st.session_state.is_processing = False
                    st.rerun()
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    # Reset processing state
                    st.session_state.is_processing = False
                    st.rerun()

            st.session_state.is_processing = False
            st.rerun()
        

if __name__ == "__main__":
    stramlit_ui()

            

            

