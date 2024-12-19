import numpy as np
import pandas as pd
import json
try:
    from .vectordatabase import VectorDB
except:
    from vectordatabase import VectorDB
from sentence_transformers import SentenceTransformer
import time
import random

def database_demo():

    SCHEMA = {
        "customers": ['customer_id','name','email','address'],
        "orders": ['order_id','product_id','customer_id','order_date'],
        "products": ['product_id','name','description','price','stock_quantity'],
    }

    QUESTIONS = [
        ("List all {} from the {} table", "SELECT {} FROM {};"),
        ("Find all {} where {} = '{}'", "SELECT * FROM {} WHERE {} = '{}';"),
        ("Show the total {} grouped by {} in the {} table", "SELECT {}, SUM({}) AS total_{} FROM {} GROUP BY {};"),
        ("Get the {} of orders made by customers from {}", "SELECT {} FROM orders INNER JOIN customers ON orders.customer_id = customers.customer_id;"),
        ("Retrieve {} sorted by {} in the {} table", "SELECT {} FROM {} ORDER BY {};"),
    ]

    # Function to randomly generate a question and SQL answer
    def generate_random_question_and_answer():
        # Randomly choose a table and columns
        table = random.choice(list(SCHEMA.keys()))
        columns = SCHEMA[table]
        column1 = random.choice(columns)
        column2 = random.choice(columns)

        # Randomly choose a question pattern
        question_template, sql_template = random.choice(QUESTIONS)

        # Fill placeholders in the question
        placeholder_count = question_template.count("{}")
        if placeholder_count == 2:
            question = question_template.format(column1, table)
        elif placeholder_count == 3:
            question = question_template.format(column1, column2, table)
        else:
            question = question_template

        # Fill placeholders in the SQL query
        sql_placeholder_count = sql_template.count("{}")
        if "GROUP BY" in sql_template and sql_placeholder_count == 5:
            sql = sql_template.format(column2, column1, column1, table, column2)
        elif sql_placeholder_count == 3:
            sql = sql_template.format(column1, table, column2)
        elif sql_placeholder_count == 2:
            sql = sql_template.format(column1, table)
        else:
            sql = sql_template

        return question, sql
    
    def split_question_sql(input_string):
        # Split the input into parts using "," as the delimiter
        parts = input_string.split('", ')
        
        # Clean and extract the "Question" and "SQL" parts
        question = parts[0].replace('f"Question: ', '').strip('"')
        sql = parts[1].replace('f"SQL: ', '').strip('}"')
        
        # Organize into a dictionary
        result = {
            "Question": question,
            "SQL": sql
        }
        return result

    # Example usage
    knowledge_sql = []
    for _ in range(10):  # Generate 3 random questions
        question, sql = generate_random_question_and_answer()
        knowledge_sql.append(
            split_question_sql(f'"Question: {question}", "SQL: {sql}"')
        )

    print(knowledge_sql)
        
    # Load data for retrieval
    knowledge_base = [
        {"title": "How do I reset my email password?", "content": "Visit the IT portal and click 'Forgot Password.'"},
        {"title": "What is the reimbursement process?", "content": "Submit receipts on the Finance portal under 'Reimbursements'."},
        {"title": "Password Reset", "content": "To reset your password, go to the IT portal and click 'Forgot Password'."},
        {"title": "Reimbursement Process", "content": "Submit your receipts on the Finance portal under 'Reimbursements'."},
        {"title": "Leave Policy", "content": "The company offers 20 days of paid leave per year."}
    ]

    sales_df = pd.read_csv("data_storage/customers.csv")
    info1 = []
    for _, row in sales_df.iterrows():
        row_txt = 'Customer Record: '
        for key in row.keys():
            row_txt = row_txt + f'{key} - {row[key]}, '
        info1.append(row_txt)

    sales_df = pd.read_csv("data_storage/orders.csv")
    info2 = []
    for _, row in sales_df.iterrows():
        row_txt = 'Order Record: '
        for key in row.keys():
            row_txt = row_txt + f'{key} - {row[key]}, '
        info2.append(row_txt)

    sales_df = pd.read_csv("data_storage/products.csv")
    info3 = []
    for _, row in sales_df.iterrows():
        row_txt = 'Product Record: '
        for key in row.keys():
            row_txt = row_txt + f'{key} - {row[key]}, '
        info3.append(row_txt)

    # hr_texts = []
    # with open("data_storage/hr_database.jsonl", "r") as file:
    #     for line in file:
    #         record = json.loads(line)
    #         row_txt = 'HR Record: '
    #         for key in record.keys():
    #             row_txt = row_txt + f'{key} - {record[key]}, '
    #         hr_texts.append(row_txt)

    knowledge_texts = [f"title : {item['title']}, content : {item['content']}" for item in knowledge_base] + info1 + info2 + info3
    # knowledge_texts = [q for q in knowledge_sql]
    print(knowledge_texts)
    print(f"Total Entries: {len(knowledge_texts)}")

    return knowledge_texts

if __name__ == "__main__":
    knowledge_texts = database_demo()
    st_time = time.time()
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = embedding_model.encode(knowledge_texts, show_progress_bar=True)
    print(f'encoding time: {time.time() - st_time} s')

    db = VectorDB(database_path= "data_storage/democompany-vector.db")
    db.drop_collection()
    db.create_db()
    db.insert_data(embeddings, knowledge_texts, sql)
    db.getAllData()
    vector = embedding_model.encode('Who is top spender?')
    queries = db.query_topk(vector, topk=2)
    print(queries)