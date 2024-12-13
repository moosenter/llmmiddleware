from fastapi import FastAPI, Request
from sentence_transformers import SentenceTransformer
import faiss
import os
from dotenv import load_dotenv
# from openai import OpenAI
import aisuite as ai
import uvicorn
import time
import pandas as pd
import json
import numpy as np
from lib.database_processor_for_rag import database_demo
from lib.vectordatabase import VectorDB
load_dotenv()

client = ai.Client()
app = FastAPI()
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

t0 = time.time()
db = VectorDB(database_path='data_storage/democompany-vector.db')
db.getCollection()
print(f'database reading time: {time.time() - t0} s')

# def faiss_retrieve_context(query, top_k=2):
#     # Search FAISS index
#     query_embedding = embedding_model.encode(query)
#     distances, indices = index.search(query_embedding, k=top_k)
#     results = []
#     for idx in indices[0]:
#         if idx != -1:  # Ensure index is valid
#             retrieved_text = knowledge_texts[idx]
#             if "HR Record" in retrieved_text and "hr" in query.lower() or "who" in query.lower():
#                 results.append({"type": "HR", "content": retrieved_text})
#             elif "Sales Record" in retrieved_text and "sales" in query.lower():
#                 results.append({"type": "Sales", "content": retrieved_text})
#             else:
#                 results.append({"type": "General", "content": retrieved_text})

def retrieve_context(query, top_k=5):
    # Generate embedding for the query
    query_embedding = embedding_model.encode(query)
    retrieved_texts = db.query_topk(query_embedding, topk=top_k)
    return retrieved_texts

@app.post("/model")
async def generate_response(request: Request):
    global model
    body = await request.json()
    model = body.get("model")
    return {
            'statusCode' : 200,
            "response": model
    } 

# Middleware endpoint
@app.post("/generate")
async def generate_response(request: Request):
    body = await request.json()
    if isinstance(body, list):
        role = body[-1].get("role", "")
        user_prompt = body[-1].get("content", "")
    else:
        role = 'user'
        user_prompt = body.get("prompt", "")
        

    # Retrieve context
    context = retrieve_context(user_prompt)
    print('-----------------------------')
    print(f'Prompt: {user_prompt}')
    print(f'Context : {context}')
    print('-----------------------------')

    if isinstance(body, list):
        body.extend([{"role": "system", "content": f"Context: {context}"}])
        messages=body
    else:
        messages=[
                {"role": "system", "content": f"Context: {context}"},
                {"role": role, "content": user_prompt}
            ]
    print(messages)

    try:
        response = client.chat.completions.create(
            messages=messages,
            # model='groq:llama-3.2-3b-preview',
            model=model
        )
        
        return {
            'statusCode' : 200,
            "response": response.choices[0].message.content
        }
    except Exception as e:

        return {
            'statusCode' : 413,
            "response": str(e)
        }

if __name__ == "__main__":
    uvicorn.run("middleware:app", host="0.0.0.0",port=8000, log_level="info")