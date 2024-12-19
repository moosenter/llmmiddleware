import streamlit as st
from lib.vanna.vanna_aisuite import aisuite_Chat
from fastapi import FastAPI, Request
import uvicorn
import orjson
import re
import pandas as pd
import json

app = FastAPI()

def merged_decorator_with_args(bar, baz):
    deco2 = st.cache_data(show_spinner=bar)
    deco1 = app.post(baz)
    def real_decorator(func):
        return deco2(deco1(func))
    return real_decorator

@app.get("/")
async def read_root():
    return {"message": "Hello, world!"}

def clean_sql(sql):
    sql = sql.strip('"').strip()
    sql = sql.replace(r"\n", " ")
    sql = re.sub(r";", "", sql)
    return sql

# @app.post("/api/v2/setup_vanna")
@st.cache_resource(ttl=3600)
def setup_vanna(config):
    # config={
    #     'milvus_client':'data_storage/vanna-democompany-vector.db',
    #     'model':'groq:llama-3.2-3b-preview', 
    #     'sql_db':'data_storage/democompany.db'
    # }
    vn = aisuite_Chat(config=config)
    vn.connect_to_sqlite(config['sql_db'])

    existing_training_data = vn.get_training_data()
    if len(existing_training_data) > 0:
        for _, training_data in existing_training_data.iterrows():
            vn.remove_training_data(training_data['id'])
    df_ddl = vn.run_sql("SELECT type, sql FROM sqlite_master WHERE sql is not null")
    for ddl in df_ddl['sql'].to_list():
        vn.train(ddl=ddl)
    existing_training_data = vn.get_training_data()
    print(existing_training_data)
    
    return vn

# @merged_decorator_with_args("Genera/ting sample questions ...", "/api/v2/generate_questions_cached")
# @st.cache_data(show_spinner="Generating sample questions ...")
@app.post("/api/v2/generate_questions_cached")
async def generate_questions_cached(request: Request):
    body = await request.json()
    config = body.get('configs')
    global vn
    vn = setup_vanna(config)
    response = vn.generate_questions()
    return {
                'statusCode' : 200,
                "response": response
            }


# @st.cache_data(show_spinner="Generating SQL query ...")
@app.post("/api/v2/generate_sql_cached")
async def generate_sql_cached(request: Request):
    body = await request.json()
    question = body.get('question')
    response = vn.generate_sql(question=question, allow_llm_to_see_data=True)
    return {
                'statusCode' : 200,
                "response": response
            }

# @st.cache_data(show_spinner="Checking for valid SQL ...")
@app.post("/api/v2/is_sql_valid_cached")
async def is_sql_valid_cached(request: Request):
    body = await request.json()
    sql = body.get('sql')
    response = vn.is_sql_valid(sql=sql)
    return {
                'statusCode' : 200,
                "response": response
            }

# @st.cache_data(show_spinner="Running SQL query ...")
@app.post("/api/v2/run_sql_cached")
async def run_sql_cached(request: Request):
    body = await request.body()
    body = orjson.loads(body)
    sql = body.get('sql')
    sql = clean_sql(sql)
    response = vn.run_sql(sql=sql)
    return {
                'statusCode' : 200,
                "response": response.to_json(orient="records")
            }


# @st.cache_data(show_spinner="Checking if we should generate a chart ...")
@app.post("/api/v2/should_generate_chart_cached")
async def should_generate_chart_cached(request: Request):
    body = await request.body()
    body = orjson.loads(body)
    sql = body.get('sql')
    sql = clean_sql(sql)
    df = body.get('df')
    df = json.loads(df)
    df = pd.read_json(df)
    question = body.get('question')
    response = vn.should_generate_chart(df=df)
    return {
                'statusCode' : 200,
                "response": response
            }

# @st.cache_data(show_spinner="Generating Plotly code ...")
@app.post("/api/v2/generate_plotly_code_cached")
async def generate_plotly_code_cached(request: Request):
    body = await request.body()
    body = orjson.loads(body)
    sql = body.get('sql')
    sql = clean_sql(sql)
    df = body.get('df')
    df = json.loads(df)
    df = pd.read_json(df)
    question = body.get('question')
    code = vn.generate_plotly_code(question=question, sql=sql, df=df)
    response = code
    return {
                'statusCode' : 200,
                "response": response
            }



# @st.cache_data(show_spinner="Running Plotly code ...")
@app.post("/api/v2/generate_plot_cached")
async def generate_plot_cached(request: Request):
    body = await request.body()
    body = orjson.loads(body)
    df = body.get('df')
    df = json.loads(df)
    df = pd.read_json(df)
    code = body.get('code')
    response = vn.get_plotly_figure(plotly_code=code, df=df)
    return {
                'statusCode' : 200,
                "response": response
            }

# @st.cache_data(show_spinner="Generating followup questions ...")
@app.post("/api/v2/generate_followup_cached")
async def generate_followup_cached(request: Request):
    body = await request.body()
    body = orjson.loads(body)
    sql = body.get('sql')
    sql = clean_sql(sql)
    df = body.get('df')
    df = json.loads(df)
    df = pd.read_json(df)
    question = body.get('question')
    response = vn.generate_followup_questions(question=question, sql=sql, df=df)
    return {
                'statusCode' : 200,
                "response": response
            }

# @st.cache_data(show_spinner="Generating summary ...")
@app.post("/api/v2/generate_summary_cached")
async def generate_summary_cached(request: Request):
    body = await request.body()
    body = orjson.loads(body)
    df = body.get('df')
    df = json.loads(df)
    df = pd.read_json(df)
    question = body.get('question')
    response = vn.generate_summary(question=question, df=df)
    return {
                'statusCode' : 200,
                "response": response
            }

if __name__ == "__main__":
    uvicorn.run("vanna_calls:app", host="0.0.0.0",port=8000, log_level="info", reload=True)