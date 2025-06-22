import time
import streamlit as st
import uuid
import requests
import os
import yaml
import orjson
import pandas as pd
import plotly.io as pio
from frontend.login import login_page, register_page
import glob 
import io
import ujson

avatar_url = "frontend/assets/middleware_icon.png"
st.set_page_config(page_title="LLM Middleware", layout="wide")

def set_question(question):
    st.session_state["my_question"] = question
    
def reset_button():
    st.session_state["my_question"] = None
    st.session_state.chat_history_1 = []
    # st.session_state.chat_history_2 = []
    # st.session_state.is_processing = False
    st.session_state.run_once_flag = False
    # st.experimental_rerun()

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
    with open("config/ModelConfig.yaml", "r") as file:
        config = yaml.safe_load(file)
    configured_llms = config["llms"]

    with open("config/AppPredefinedQuestions.yaml", "r") as file:
        config = yaml.safe_load(file)
    predefinedqustions = config["predefinedqustions"]

    with open("config/AppPredefinedQuestions_thai.yaml", "r") as file:
        config = yaml.safe_load(file)
    predefinedqustions_thai = config["predefinedqustions"]

    # Initialize session states
    if "chat_history_1" not in st.session_state:
        st.session_state.chat_history_1 = []
    # if "chat_history_2" not in st.session_state:
    #     st.session_state.chat_history_2 = []
    # if "is_processing" not in st.session_state:
    #     st.session_state.is_processing = False
    if "sql_mode" not in st.session_state:
        st.session_state.sql_mode = True
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

    # st.sidebar.title("Output Settings")
    # st.sidebar.checkbox("Show SQL", value=True, key="show_sql")
    # st.sidebar.checkbox("Show Table", value=True, key="show_table")
    # st.sidebar.checkbox("Show Plotly Code", value=True, key="show_plotly_code")
    # st.sidebar.checkbox("Show Chart", value=True, key="show_chart")
    # st.sidebar.checkbox("Show Summary", value=True, key="show_summary")
    # st.sidebar.checkbox("Show Follow-up Questions", value=True, key="show_followup")
    st.sidebar.button("Reset", on_click=lambda: reset_button(), use_container_width=True)
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state["token"] = None
        st.rerun()

    st.sidebar.markdown("---")

    st.sidebar.subheader("📂 Select DB File from Server")
    db_files = glob.glob("data_storage/*.db")
    exceptionfiles = ['data_storage/user_database.db']
    db_files = [ x for x in db_files if x not in exceptionfiles ]
    db_files = [ x for x in db_files if 'vector' not in x ]
    selected_db = st.sidebar.selectbox("Choose a database file", db_files)

    if selected_db:
        try:
            with open("config/AppConfig.yaml", "r") as f:
                config_yaml = yaml.safe_load(f)
            config_yaml["vannaconf"]["sql_db"] = selected_db
            with open("config/AppConfig.yaml", "w") as f:
                yaml.safe_dump(config_yaml, f)
            st.sidebar.success(f"Updated Database to: {selected_db}")
            # st.session_state["run_once_flag"] = False
        except Exception as e:
            st.sidebar.error(f"Failed to update YAML: {e}")

    st.title("LLM Middleware")
    # st.sidebar.write(st.session_state)

    selected_model_1 = st.selectbox(
        "Choose LLM Model",
        [llm["name"] for llm in configured_llms],
        key="model_1",
        index=0 if configured_llms else 0,
    )
    model_config_1 = next(
        llm for llm in configured_llms if llm["name"] == selected_model_1
    )
    with open("config/AppConfig.yaml", "r") as file:
        configs = yaml.safe_load(file)
    configs = configs["vannaconf"]
    configs.update({'model':model_config_1["provider"] + ":" + model_config_1["model"]})

    col1, col2 = st.columns([1, 2])
    with col1:
        st.session_state.sql_mode = st.checkbox("Data Explanation Mode", value=True)

    if st.session_state["run_once_flag"] is False:
        st.session_state["run_once_flag"] = True
        with st.spinner("Calling LLM..."):
            try:
                questions = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/setup_vanna/', json={'configs': configs}).json()['response']
            except requests.exceptions.RequestException as e:
                # st.error(f"Error fetching data: {e}")
                st.error(f"[ERROR] Cannot connect to LLM, Please reload application or check the internet connections")
                return None

    assistant_message_suggested = st.chat_message(
        "assistant", avatar=avatar_url
    )
    if st.session_state.sql_mode:
        if assistant_message_suggested.button("Click to show suggested questions"):
            st.session_state["my_question"] = None
            # questions = generate_questions_cached(configs)
            # try:
            #     questions = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/generate_questions_cached/', json={'configs': configs}).json()['response']
            # except requests.exceptions.RequestException as e:
            #     st.error(f"Error fetching data: {e}")
            #     return None
            # questions = ['How has revenue trended over the last 12 months or fiscal years', 'What are the major fixed and variable costs?']
            questions = [ q['question'] for q in predefinedqustions] 
            for i, question in enumerate(questions):
                time.sleep(0.05)
                button = st.button(
                    question,
                    on_click=set_question,
                    args=(question,),
                    key=str(uuid.uuid4())
                )
        if assistant_message_suggested.button("คลิกเพื่อดูคำถามแนะนำ"):
            st.session_state["my_question"] = None
            questions = [ q['question'] for q in predefinedqustions_thai] 
            for i, question in enumerate(questions):
                time.sleep(0.05)
                button = st.button(
                    question,
                    on_click=set_question,
                    args=(question,),
                    key=str(uuid.uuid4())
                )
    else:
        st.session_state["my_question"] = None

    my_question = st.session_state.get("my_question", default=None)
    # if st.session_state.is_processing == False:
    if my_question is None:
        my_question = st.chat_input(
            "Ask me a question about your data",
        )

    if my_question:
        # st.session_state.is_processing = True
        st.session_state["my_question"] = my_question
        st.session_state.chat_history_1.append({"role": "user", "content": my_question})

        if st.session_state.sql_mode:
        # sql = generate_sql_cached(question=my_question)
            try:
                sql = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/generate_sql_cached/', json={'question': my_question}).json()['response']
            except requests.exceptions.RequestException as e:
                st.error(f"Error fetching data: {e}")
                print("sql was:", repr(sql))
                return None

            try:
                is_sql_valid = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/is_sql_valid_cached/', json={'sql': sql}).json()['response']
            except requests.exceptions.RequestException as e:
                st.error(f"Error fetching data: {e}")
                print("is_sql_valid was:", repr(is_sql_valid))
                return None
        else:
            sql = None
            is_sql_valid = None
        
        if sql and is_sql_valid and st.session_state.sql_mode:
            writeResults()

            # st.session_state.chat_history_1.append({"role": "assistant", "content": f"SQL generated:\n```sql\n{sql}\n```"})

            # df = run_sql_cached(sql=sql)
            try:
                df = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/run_sql_cached/', 
                                   json={'sql': orjson.dumps(sql, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8")}).json()['response']
                print(df)
                try:
                    df = orjson.loads(df)
                except orjson.JSONDecodeError as e:
                    print(f"JSON decoding failed: {e}")
                    print("run_sql_cached was:", repr(df))
                df = pd.read_json(io.StringIO(df), dtype=None, precise_float=True)
            except requests.exceptions.RequestException as e:
                # st.error(f"Error fetching data: {e}")
                st.error(f"[Error] LLM cannot query data correctly")
                return None

            if df is not None:
                st.session_state["df"] = df

            if st.session_state.get("df") is not None:
                if st.session_state.get("show_table", True):
                    st.write("### Query Results")
                    if len(df) > 10:

                        # cap only 100 rows
                        if len(df) > 100:
                            df = df.head(100)

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
                                        'question': orjson.dumps(my_question, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                    }).json()['response']
                except requests.exceptions.RequestException as e:
                    st.error(f"Error fetching data: {e}")
                    return None
        
                # if should_generate_chart_cached(question=my_question, sql=sql, df=df):
                if should_generate_chart:
                    # plot_code = generate_plotly_code_cached(question=my_question, sql=sql, df=df)
                    try:
                        plot_code = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/generate_plotly_code_cached/', 
                                        json={
                                            'sql': orjson.dumps(sql, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                            'df': orjson.dumps(df.to_json(orient="records"), option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                            'question': orjson.dumps(my_question, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
                                        }).json()['response']
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error fetching data: {e}")
                        return None
                    
                    if st.session_state.get("show_plotly_code", False):
                        st.code(plot_code, language="python")
                    # fig = generate_plot_cached(code=plot_code, df=df)

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

                try:
                    # st.session_state.chat_history_1.append({"role": "user", "content": my_question})
                    qlist = []
                    for message in st.session_state.chat_history_1:
                        qlist.append({'role': message['role'], 'content':message["content"]})
                    answer = requests.post(os.getenv('API_URL', 'http:/backend:8000')+'/api/v2/generate_answer_cached/', json={'question':  qlist}).json()['response']
                except requests.exceptions.RequestException as e:
                    st.error(f"Error fetching data: {e}")
                    return None
                if answer is not None:
                        assistant_message_answer = st.chat_message(
                            "assistant", avatar=avatar_url
                        )
                        assistant_message_answer.text(answer)
                st.session_state.chat_history_1.append({"role": "assistant", "content": answer})
                
                if st.session_state.get("show_summary", True):
                    st.write("### Conclusion")
                    # summary = generate_summary_cached(question=my_question, df=df)
                    try:
                        summary = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/generate_summary_cached/', 
                                        json={
                                            'question': orjson.dumps(my_question, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
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
                    # followup_questions = generate_followup_cached(question=my_question, sql=sql, df=df)
                    try:
                        followup_questions = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/generate_followup_cached/', 
                                        json={
                                            'question': orjson.dumps(my_question, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS).decode("utf-8"),
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
            try:
                # st.session_state.chat_history_1.append({"role": "user", "content": my_question})
                qlist = []
                for message in st.session_state.chat_history_1:
                    qlist.append({'role': message['role'], 'content':message["content"]})
                answer = requests.post(os.getenv('API_URL', 'http://backend:8000')+'/api/v2/generate_answer_cached/', json={'question':  qlist}).json()['response']
            except requests.exceptions.RequestException as e:
                st.error(f"Error fetching data: {e}")
                return None
            st.session_state.chat_history_1.append({"role": "assistant", "content": answer})

            writeResults()

            st.button("Others", on_click=set_question, args=(None,), key=str(uuid.uuid4()))

        # st.session_state.is_processing = False

if __name__ == "__main__":
    # stramlit_ui()
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