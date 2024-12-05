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
from database_processor import database_demo
load_dotenv()

client = ai.Client(
    # api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)
# models = client.models.list()
# print(models)

# Initialize the app
app = FastAPI()

knowledge_texts = database_demo()

st_time = time.time()
# Initialize FAISS index
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embedding_model.encode(knowledge_texts, show_progress_bar=True)
embedding_matrix = np.array(embeddings)
dimension = embedding_matrix.shape[1]
print(f'dimension: {dimension}')
index = faiss.IndexFlatL2(dimension)
index.add(embedding_matrix)
print(f'faiss time: {time.time() - st_time} s')
print(f"Number of vectors in FAISS index: {index.ntotal}")

def retrieve_context(query, top_k=1):
    # Generate embedding for the query
    query_embedding = embedding_model.encode([query])
    top_k =8

    # Search FAISS index
    distances, indices = index.search(query_embedding, k=top_k)

    # Retrieve matching content
    results = []
    for idx in indices[0]:
        if idx != -1:  # Ensure index is valid
            retrieved_text = knowledge_texts[idx]
            if "HR Record" in retrieved_text and "hr" in query.lower() or "who" in query.lower():
                results.append({"type": "HR", "content": retrieved_text})
            elif "Sales Record" in retrieved_text and "sales" in query.lower():
                results.append({"type": "Sales", "content": retrieved_text})
            else:
                results.append({"type": "General", "content": retrieved_text})
    return results

# Middleware endpoint
@app.post("/generate")
async def generate_response(request: Request):
    body = await request.json()
    if isinstance(body, list):
        role = body[-1].get("role", "")
        user_prompt = body[-1].get("content", "")
    else:
        role = 'user'
        user_prompt = body.get("top_k", "")
        

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

    response = client.chat.completions.create(
        messages=messages,
        model='groq:llama-3.2-3b-preview'
    )
    
    # Return response
    return {
        'statusCode' : 200,
        "response": response.choices[0].message.content
    }

if __name__ == "__main__":
    uvicorn.run("middleware:app", host="0.0.0.0",port=8000, log_level="info")