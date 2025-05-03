from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, List, Any, Union
import yaml
import orjson
import pandas as pd
import plotly.io as pio
import os
import uvicorn
import traceback
import logging

from llmmiddleware.flows.sql_flows import create_sql_generation_flow

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up API routes
@app.get("/")
async def root():
    return {"message": "LLM Middleware API"}

@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    last_message = data[-1]["content"] if data else ""
    last_message_lower = last_message.lower()
    
    # Generate response based on input
    if 'hi' in last_message_lower or 'hello' in last_message_lower or 'hey' in last_message_lower:
        response = "Hello! I'm the LLM Middleware chat assistant. How can I help you today?"
    elif 'help' in last_message_lower or 'what can you do' in last_message_lower:
        response = "I can help answer questions, provide information, and assist with various tasks. What would you like to know?"
    elif 'thank' in last_message_lower:
        response = "You're welcome! Is there anything else I can help with?"
    elif 'bye' in last_message_lower or 'goodbye' in last_message_lower:
        response = "Goodbye! Feel free to chat again if you need assistance."
    else:
        response = f"You said: '{last_message}'. I'm currently in development, so my responses are somewhat limited. Is there something specific about data analysis I can help with?"
    
    return {"response": response}

@app.post("/api/v2/setup_vanna/")
async def setup_vanna(request: Request):
    data = await request.json()
    configs = data.get("configs", {})
    
    # Initialize shared store
    shared = {
        "config": configs,
        "setup": True
    }
    
    # Create and run the flow
    flow = create_sql_generation_flow()
    flow.run(shared)
    
    # Return suggested questions if available
    questions = shared.get("suggested_questions", ["How many customers do we have?", "What's our total revenue?"])
    return {"response": questions}

@app.post("/api/v2/generate_questions_cached/")
async def generate_questions_cached(request: Request):
    data = await request.json()
    configs = data.get("configs", {})
    
    # For now return some sample questions
    questions = [
        "How many customers do we have?",
        "What's our total revenue?",
        "Which products have the highest sales?",
        "What was our revenue last month?",
        "Who are our top 5 customers?"
    ]
    
    return {"response": questions}

@app.post("/api/v2/generate_sql_cached/")
async def generate_sql_cached(request: Request):
    try:
        data = await request.json()
        question = data.get("question", "")
        
        if not question:
            logger.error("Empty question received in generate_sql_cached endpoint")
            return {"error": "Please provide a question related to your data."}
        
        logger.info(f"Generating SQL for question: {question}")
        
        # Initialize shared store
        shared = {
            "config": data.get("configs", {}),  # Include configs if provided
            "question": question,
            "sql": None
        }
        
        # Create and run the flow
        try:
            flow = create_sql_generation_flow()
            flow.run(shared)
            
            sql = shared.get("sql", "")
            if not sql:
                logger.warning(f"SQL generation returned empty for question: {question}")
                return {"error": "I couldn't generate SQL for this question. Please try a specific data-related question like 'How many sales were made in January?' or 'What is our total revenue?'"}
                
            logger.info(f"Successfully generated SQL: {sql}")
            return {"response": sql}
        except Exception as e:
            logger.error(f"Flow execution error: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": "An error occurred while processing your question. Please try a different data question."}
    except Exception as e:
        logger.error(f"Error in generate_sql_cached endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return {"error": "Server error occurred. Please try again later."}

@app.post("/api/v2/is_sql_valid_cached/")
async def is_sql_valid_cached(request: Request):
    data = await request.json()
    sql = data.get("sql", "")
    
    # Initialize shared store
    shared = {
        "sql": sql,
        "is_valid": False
    }
    
    # Create and run the flow
    flow = create_sql_generation_flow()
    flow.run(shared)
    
    return {"response": shared.get("is_valid", False)}

@app.post("/api/v2/run_sql_cached/")
async def run_sql_cached(request: Request):
    data = await request.json()
    sql = orjson.loads(data.get("sql", "{}"))
    
    # Initialize shared store
    shared = {
        "sql": sql,
        "results": None
    }
    
    # Create and run the flow
    flow = create_sql_generation_flow()
    flow.run(shared)
    
    # Convert results to JSON
    if shared.get("results") is not None:
        df = shared.get("results")
        return {"response": df.to_json()}
    
    return {"response": None}

@app.post("/api/v2/should_generate_chart_cached/")
async def should_generate_chart_cached(request: Request):
    data = await request.json()
    sql = orjson.loads(data.get("sql", "{}"))
    df_json = orjson.loads(data.get("df", "[]"))
    df = pd.read_json(df_json)
    question = orjson.loads(data.get("question", '""'))
    
    # Simple heuristic: If there are more than 1 column and data isn't too large, generate a chart
    should_chart = len(df.columns) > 1 and len(df) > 0 and len(df) < 1000
    
    return {"response": should_chart}

@app.post("/api/v2/generate_plotly_code_cached/")
async def generate_plotly_code_cached(request: Request):
    data = await request.json()
    sql = orjson.loads(data.get("sql", "{}"))
    df_json = orjson.loads(data.get("df", "[]"))
    question = orjson.loads(data.get("question", '""'))
    
    # Simple default plot code
    plot_code = """
    import plotly.express as px
    
    # Create a simple bar chart
    fig = px.bar(df, x=df.columns[0], y=df.columns[1] if len(df.columns) > 1 else None)
    fig.update_layout(title='Results Visualization')
    """
    
    return {"response": plot_code}

@app.post("/api/v2/generate_plot_cached/")
async def generate_plot_cached(request: Request):
    data = await request.json()
    code = orjson.loads(data.get("code", '""'))
    df_json = orjson.loads(data.get("df", "[]"))
    df = pd.read_json(df_json)
    
    try:
        # Create a local namespace for execution
        local_vars = {"df": df, "px": pio.plotly_mimetype}
        
        # Execute the code in the local namespace
        exec(code, globals(), local_vars)
        
        # Extract the figure from the namespace
        fig = local_vars.get("fig")
        
        if fig:
            return {"response": pio.to_json(fig)}
    except Exception as e:
        logger.error(f"Error generating plot: {str(e)}")
        traceback.print_exc()
    
    return {"response": None}

@app.post("/api/v2/generate_summary_cached/")
async def generate_summary_cached(request: Request):
    data = await request.json()
    question = orjson.loads(data.get("question", '""'))
    df_json = orjson.loads(data.get("df", "[]"))
    
    # Generate a simple summary
    summary = f"Here is a summary of the results for your question: '{question}'"
    
    return {"response": summary}

@app.post("/api/v2/generate_followup_cached/")
async def generate_followup_cached(request: Request):
    data = await request.json()
    question = orjson.loads(data.get("question", '""'))
    sql = orjson.loads(data.get("sql", "{}"))
    df_json = orjson.loads(data.get("df", "[]"))
    
    # Generate some follow-up questions
    followups = [
        f"Can you show me more details about {question}?",
        "How does this compare to last year?",
        "Can you break this down by category?",
        "What's the trend over time?",
        "Can you show this as a percentage?"
    ]
    
    return {"response": followups}

@app.post("/api/v2/generate_answer_cached/")
async def generate_answer_cached(request: Request):
    data = await request.json()
    question_data = data.get("question", [])
    
    # Get the latest user message
    latest_message = ""
    if question_data and len(question_data) > 0:
        for msg in reversed(question_data):
            if msg.get('role') == 'user':
                latest_message = msg.get('content', '').lower()
                break
    
    # Generate response based on input
    if 'hi' in latest_message or 'hello' in latest_message or 'hey' in latest_message:
        answer = "Hello! I can help you analyze your data. Try asking a question about your database."
    elif 'data' in latest_message or 'explore' in latest_message:
        answer = "I can help you explore your data. Try asking questions like 'How many customers do we have?' or 'What's our total revenue?'"
    elif 'help' in latest_message:
        answer = "I'm your data analysis assistant. I can run SQL queries, create charts, and summarize results. Try asking questions about your data in natural language."
    elif latest_message.strip() == '':
        answer = "Please provide a question or query about your data."
    else:
        # Provide more specific guidance instead of repeating the same unhelpful message
        answer = "I need more specific information to help you. Please try asking about:\n\n- Customer data (e.g., 'How many customers do we have?')\n- Sales information (e.g., 'What was our revenue last month?')\n- Product performance (e.g., 'Which products sell the most?')\n- Time-based analysis (e.g., 'Show sales trends for the past year')"
    
    return {"response": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)