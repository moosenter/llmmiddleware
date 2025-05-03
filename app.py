import time
import streamlit as st
import uuid
import requests
import os
import yaml
import orjson
import pandas as pd
import plotly.io as pio
from llmmiddleware.frontend.login import login_page, register_page

# Use environment-aware paths
if os.path.exists("config/ModelConfig.yaml"):
    config_path = "config"
else:
    config_path = "llmmiddleware/config"

avatar_url = "llmmiddleware/frontend/assets/middleware_icon.png"
st.set_page_config(page_title="LLM Middleware", layout="wide")

def set_question(question):
    st.session_state["my_question"] = question
    
def reset_button():
    st.session_state["my_question"] = None
    st.session_state.chat_history_1 = []
    st.session_state.run_once_flag = False

def writeResults():
    for message in st.session_state.chat_history_1:
        if message["role"] == "assistant":
            with st.chat_message(message["role"], avatar=avatar_url,):
                st.markdown(message["content"])
            if 'table' in message:
                with st.chat_message(message["role"], avatar=avatar_url,):
                    df = message['table']
                    if len(df) > 10:
                        st.write("First 10 rows of data")
                        st.dataframe(df.head(10))
                    else:
                        st.dataframe(df)
            if 'chart' in message:
                with st.chat_message(message["role"], avatar=avatar_url,):
                    st.plotly_chart(message['chart'], key=f"chart_{str(uuid.uuid4())}")
        else:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

def stramlit_ui():
    with open(f"{config_path}/ModelConfig.yaml", "r") as file:
        config = yaml.safe_load(file)
    configured_llms = config["llms"]

    # Initialize session states
    if "chat_history_1" not in st.session_state:
        st.session_state.chat_history_1 = []
    if "use_comparison_mode" not in st.session_state:
        st.session_state.use_comparison_mode = False
    if "run_once_flag" not in st.session_state:
        st.session_state["run_once_flag"] = False

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

    st.sidebar.title("Output Settings")
    st.sidebar.checkbox("Show SQL", value=True, key="show_sql")
    st.sidebar.checkbox("Show Table", value=True, key="show_table")
    st.sidebar.checkbox("Show Plotly Code", value=True, key="show_plotly_code")
    st.sidebar.checkbox("Show Chart", value=True, key="show_chart")
    st.sidebar.checkbox("Show Summary", value=True, key="show_summary")
    st.sidebar.checkbox("Show Follow-up Questions", value=True, key="show_followup")
    st.sidebar.button("Reset", on_click=lambda: reset_button(), use_container_width=True)
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state["token"] = None
        st.rerun()

    st.title("LLM Middleware")
    st.sidebar.write(st.session_state)

    selected_model_1 = st.selectbox(
        "Choose LLM Model 1",
        [llm["name"] for llm in configured_llms],
        key="model_1",
        index=0 if configured_llms else 0,
    )
    model_config_1 = next(
        llm for llm in configured_llms if llm["name"] == selected_model_1
    )
    with open(f"{config_path}/AppConfig.yaml", "r") as file:
        configs = yaml.safe_load(file)
    configs = configs["vannaconf"]
    configs.update({'model':model_config_1["provider"] + ":" + model_config_1["model"]})

    if st.session_state["run_once_flag"] is False:
        st.session_state["run_once_flag"] = True
        try:
            questions = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/setup_vanna/', json={'configs': configs}, timeout=10).json()['response']
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend service: {str(e)}")
            questions = []
        except KeyError:
            st.error("Unexpected response format from backend")
            questions = []
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            questions = []

    assistant_message_suggested = st.chat_message(
        "assistant", avatar=avatar_url
    )
    if assistant_message_suggested.button("Click to show suggested questions"):
        st.session_state["my_question"] = None
        try:
            questions = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/generate_questions_cached/', json={'configs': configs}).json()['response']
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data: {e}")
            return None
        for i, question in enumerate(questions):
            time.sleep(0.05)
            button = st.button(
                question,
                on_click=set_question,
                args=(question,),
                key=str(uuid.uuid4())
            )

    my_question = st.session_state.get("my_question", default=None)
    if my_question is None:
        my_question = st.chat_input(
            "Ask me a question about your data",
        )

    if my_question:
        current_question = my_question  # Store the current question for processing
        st.session_state.chat_history_1.append({"role": "user", "content": current_question})
        
        # Clear the question from session state so next input will be fresh
        st.session_state["my_question"] = None
        
        # Process the current question
        # Add a loading spinner while waiting for SQL generation
        with st.spinner("Generating SQL..."):
            try:
                sql_response = requests.post(
                    os.getenv('API_URL', 'http://backend:8000')+'/api/v2/generate_sql_cached/', 
                    json={'question': current_question},
                    timeout=15
                ).json()
                
                if 'error' in sql_response:
                    st.error(f"Error generating SQL: {sql_response['error']}")
                    st.session_state.chat_history_1.append({
                        "role": "assistant", 
                        "content": f"I'm sorry, {sql_response['error']}"
                    })
                    writeResults()
                    return None
                    
                sql = sql_response['response']
                if not sql:
                    st.error("Generated SQL is empty")
                    st.session_state.chat_history_1.append({
                        "role": "assistant", 
                        "content": "I'm sorry, I couldn't understand your question. Please try asking a more specific data-related question, such as:\n\n- How many customers do we have?\n- What's our total revenue?\n- Which products have the highest sales?\n- What was our revenue last month?"
                    })
                    writeResults()
                    return None
            except requests.exceptions.Timeout:
                st.error("Request timed out. The server took too long to respond.")
                st.session_state.chat_history_1.append({
                    "role": "assistant", 
                    "content": "I'm sorry, the request timed out. Please try again later."
                })
                writeResults()
                return None
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to backend service: {str(e)}")
                st.session_state.chat_history_1.append({
                    "role": "assistant", 
                    "content": "I'm sorry, there was an error connecting to the backend service."
                })
                writeResults()
                return None
            except KeyError:
                st.error("Unexpected response format from backend")
                st.session_state.chat_history_1.append({
                    "role": "assistant", 
                    "content": "I'm sorry, I received an unexpected response format from the backend."
                })
                writeResults()
                return None
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
                st.session_state.chat_history_1.append({
                    "role": "assistant", 
                    "content": f"I'm sorry, an unexpected error occurred: {str(e)}"
                })
                writeResults()
                return None

        try:
            is_sql_valid = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/is_sql_valid_cached/', json={'sql': sql}, timeout=10).json()['response']
        except requests.exceptions.Timeout:
            st.error("Request timed out during SQL validation")
            st.session_state.chat_history_1.append({
                "role": "assistant", 
                "content": "I'm sorry, the request timed out during SQL validation. Please try again later."
            })
            writeResults()
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to backend service: {str(e)}")
            st.session_state.chat_history_1.append({
                "role": "assistant", 
                "content": "I'm sorry, there was an error connecting to the backend service during SQL validation."
            })
            writeResults()
            return None
        except KeyError:
            st.error("Unexpected response format from backend during SQL validation")
            st.session_state.chat_history_1.append({
                "role": "assistant", 
                "content": "I'm sorry, I received an unexpected response format during SQL validation."
            })
            writeResults()
            return None
        except Exception as e:
            st.error(f"Unexpected error during SQL validation: {str(e)}")
            st.session_state.chat_history_1.append({
                "role": "assistant", 
                "content": f"I'm sorry, an unexpected error occurred during SQL validation: {str(e)}"
            })
            writeResults()
            return None
        
        if sql and is_sql_valid:
            writeResults()

            st.session_state.chat_history_1.append({"role": "assistant", "content": f"SQL generated:\n```sql\n{sql}\n```"})

            # Add a loading spinner while executing SQL
            with st.spinner("Running SQL query..."):
                try:
                    df_response = requests.post(
                        os.getenv('API_URL', 'http://backend:8000')+'/api/v2/run_sql_cached/', 
                        json={'sql': orjson.dumps(sql, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8")},
                        timeout=20
                    ).json()
                    
                    if 'error' in df_response:
                        st.error(f"Error executing SQL: {df_response['error']}")
                        st.session_state.chat_history_1.append({
                            "role": "assistant", 
                            "content": f"I'm sorry, there was an error executing the SQL query: {df_response['error']}"
                        })
                        writeResults()
                        return None
                        
                    df = df_response['response']
                    try:
                        df = orjson.loads(df)
                    except orjson.JSONDecodeError as e:
                        st.error(f"Error decoding JSON response: {str(e)}")
                        st.session_state.chat_history_1.append({
                            "role": "assistant", 
                            "content": "I'm sorry, I couldn't decode the query results."
                        })
                        writeResults()
                        return None
                        
                    try:
                        df = pd.read_json(df)
                        if df.empty:
                            st.warning("The query returned no results")
                            st.session_state.chat_history_1.append({
                                "role": "assistant", 
                                "content": "The query executed successfully but returned no results."
                            })
                    except Exception as e:
                        st.error(f"Error converting results to DataFrame: {str(e)}")
                        st.session_state.chat_history_1.append({
                            "role": "assistant", 
                            "content": f"I'm sorry, I couldn't process the query results: {str(e)}"
                        })
                        writeResults()
                        return None
                except requests.exceptions.Timeout:
                    st.error("Request timed out during SQL execution")
                    st.session_state.chat_history_1.append({
                        "role": "assistant", 
                        "content": "I'm sorry, the request timed out during SQL execution. Please try again later or simplify your query."
                    })
                    writeResults()
                    return None
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to backend service: {str(e)}")
                    st.session_state.chat_history_1.append({
                        "role": "assistant", 
                        "content": "I'm sorry, there was an error connecting to the backend service during SQL execution."
                    })
                    writeResults()
                    return None
                except Exception as e:
                    st.error(f"Unexpected error during SQL execution: {str(e)}")
                    st.session_state.chat_history_1.append({
                        "role": "assistant", 
                        "content": f"I'm sorry, an unexpected error occurred during SQL execution: {str(e)}"
                    })
                    writeResults()
                    return None

            if df is not None:
                st.session_state["df"] = df

            if st.session_state.get("df") is not None:
                if st.session_state.get("show_table", True):
                    st.write("### Query Results")
                    if len(df) > 10:
                        st.write("First 10 rows of data")
                        st.dataframe(df.head(10))
                    else:
                        st.dataframe(df)
                    st.session_state.chat_history_1.append({"role": "assistant", "content": "### Query Table", 'table':df})

                try:
                    should_generate_chart = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/should_generate_chart_cached/', 
                                    json={
                                        'sql': orjson.dumps(sql, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                        'df': orjson.dumps(df.to_json(orient="records"), option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                        'question': orjson.dumps(current_question, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                    }).json()['response']
                except requests.exceptions.RequestException as e:
                    st.error(f"Error fetching data: {e}")
                    return None
        
                if should_generate_chart:
                    try:
                        plot_code = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/generate_plotly_code_cached/', 
                                        json={
                                            'sql': orjson.dumps(sql, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                            'df': orjson.dumps(df.to_json(orient="records"), option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                            'question': orjson.dumps(current_question, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                        }).json()['response']
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error fetching data: {e}")
                        return None
                    
                    if st.session_state.get("show_plotly_code", False):
                        st.code(plot_code, language="python")

                    try:
                        fig = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/generate_plot_cached/', 
                                        json={
                                            'code': orjson.dumps(plot_code, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                            'df': orjson.dumps(df.to_json(orient="records"), option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                        }).json()['response']
                        fig = pio.from_json(orjson.loads(fig))
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error fetching data: {e}")
                        return None
                    
                    if fig:
                        st.plotly_chart(fig, key=f"chart_{str(uuid.uuid4())}")
                        st.session_state.chat_history_1.append({"role": "assistant", "content": "### Query Chart", 'chart':fig})
                    else:
                        st.session_state.chat_history_1.append({"role": "assistant", "content": "I couldn't generate a chart"})

                if st.session_state.get("show_summary", True):
                    try:
                        summary = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/generate_summary_cached/', 
                                        json={
                                            'question': orjson.dumps(current_question, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                            'df': orjson.dumps(df.to_json(orient="records"), option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                        }).json()['response']
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error fetching data: {e}")
                        return None
                    if summary is not None:
                        assistant_message_summary = st.chat_message(
                            "assistant", avatar=avatar_url
                        )
                        assistant_message_summary.text(summary)
                        st.session_state.chat_history_1.append({"role": "assistant", "content": summary})
                    else:
                        st.session_state.chat_history_1.append({"role": "assistant", "content": "I couldn't summarize"})

                # Generate follow-up questions
                if st.session_state.get("show_followup", True):
                    try:
                        followup_questions = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/generate_followup_cached/', 
                                        json={
                                            'question': orjson.dumps(current_question, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                            'df': orjson.dumps(df.to_json(orient="records"), option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                            'sql': orjson.dumps(sql, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                        }).json()['response']
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error fetching data: {e}")
                        return None
                    if followup_questions:
                        st.write("### Follow-Up Questions")
                        for question in followup_questions[:5]:
                            unique_key = str(uuid.uuid4())
                            st.button(question, on_click=set_question, args=(question,), key=unique_key)
                        st.button("Others", on_click=set_question, args=(None,), key=str(uuid.uuid4()))

        else:
            # This path is taken when SQL generation or validation fails
            # Use predefined examples to help the user
            sample_questions = [
                "How many customers do we have?",
                "What's our total revenue?",
                "Which products have the highest sales?",
                "What was our revenue last month?",
                "Who are our top 5 customers?"
            ]
            
            try:
                qlist = []
                for message in st.session_state.chat_history_1:
                    qlist.append({'role': message['role'], 'content':message["content"]})
                answer = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/generate_answer_cached/', json={'question':  qlist}).json()['response']
            except requests.exceptions.RequestException as e:
                st.error(f"Error fetching data: {e}")
                # Provide a fallback message if the request fails
                answer = "I'm having trouble understanding that question. Please try one of the sample questions below."
            
            st.session_state.chat_history_1.append({"role": "assistant", "content": answer})
            writeResults()
            
            # Display predefined questions that are guaranteed to work
            st.write("### Try these sample questions:")
            for question in sample_questions:
                unique_key = str(uuid.uuid4())
                st.button(question, on_click=set_question, args=(question,), key=unique_key)

if __name__ == "__main__":
    # Router
    if "token" not in st.session_state:
        st.session_state["token"] = None

    if st.session_state["token"]:
        stramlit_ui()
    else:
        tab = st.sidebar.radio("Navigation", ["Login", "Register"])
        if tab == "Login":
            login_page()
        else:
            register_page()