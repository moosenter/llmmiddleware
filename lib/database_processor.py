import numpy as np
import pandas as pd
import json
try:
    from .vectordatabase import VectorDB
except:
    from vectordatabase import VectorDB
from sentence_transformers import SentenceTransformer
import time

def database_demo():
    # Load data for retrieval
    knowledge_base = [
        {"title": "How do I reset my email password?", "content": "Visit the IT portal and click 'Forgot Password.'"},
        {"title": "What is the reimbursement process?", "content": "Submit receipts on the Finance portal under 'Reimbursements'."},
        {"title": "Password Reset", "content": "To reset your password, go to the IT portal and click 'Forgot Password'."},
        {"title": "Reimbursement Process", "content": "Submit your receipts on the Finance portal under 'Reimbursements'."},
        {"title": "Leave Policy", "content": "The company offers 20 days of paid leave per year."}
    ]

    sales_df = pd.read_csv("data_storage/sales_data.csv")
    sales_texts = []
    for _, row in sales_df.iterrows():
        row_txt = 'Sales Record: '
        for key in row.keys():
            row_txt = row_txt + f'{key} - {row[key]}, '
        sales_texts.append(row_txt)

    hr_texts = []
    with open("data_storage/hr_database.jsonl", "r") as file:
        for line in file:
            record = json.loads(line)
            row_txt = 'HR Record: '
            for key in record.keys():
                row_txt = row_txt + f'{key} - {record[key]}, '
            hr_texts.append(row_txt)

    knowledge_texts = [f"title : {item['title']}, content : {item['content']}" for item in knowledge_base] + sales_texts + hr_texts
    print(knowledge_texts)
    print(f"Total Entries: {len(knowledge_texts)}")

    return knowledge_texts

if __name__ == "__main__":
    knowledge_texts = database_demo()
    st_time = time.time()
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = embedding_model.encode(knowledge_texts, show_progress_bar=True)
    print(f'encoding time: {time.time() - st_time} s')

    db = VectorDB(database_path= "data_storage/democompany.db")
    db.drop_collection()
    db.create_db()
    db.insert_data(embeddings, knowledge_texts)
    db.getAllData()
    vector = embedding_model.encode('Who is responsible in the North region?')
    print(db.query_topk(vector, topk=2))