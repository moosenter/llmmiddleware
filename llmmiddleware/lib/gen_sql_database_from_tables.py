import random
import json
import sqlite3
import pandas as pd

conn = sqlite3.connect(
    database='data_storage/democompany.db',
    check_same_thread=False,
)

def generate_random_question_and_answer():
    """
    Generate a random question and its corresponding SQL query based on the schema and question templates.
    """
    try:
        # Randomly select a table and columns
        table = random.choice(list(SCHEMA.keys()))
        columns = SCHEMA[table]
        column1 = random.choice(columns)
        column2 = random.choice(columns)
        column3 = random.choice(['name','email','address'])

        # Randomly select a question and SQL template
        question_template, sql_template = random.choice(QUESTIONS)

        # Ensure the placeholders match the schema
        if sql_template.count("{}") == 1:
            question = question_template.format(column3)
        elif sql_template.count("{}") == 2:
            question = question_template.format(column1, table)
        elif sql_template.count("{}") == 3 and 'Find all rows where' in question_template:
            question = question_template.format(column1, column2, table)
        elif question_template.count("{}") == 3:
            question = question_template.format(column1, column2, table)
        else:
            question = question_template

        # Generate SQL query
        if "JOIN" in sql_template:
            sql = sql_template.format(column3)
        elif sql_template.count("{}") == 2:
            sql = sql_template.format(column1, table)
        elif sql_template.count("{}") == 3 and 'SELECT * FROM' in sql_template:
            sql = sql_template.format(table, column1, column2)
        elif sql_template.count("{}") == 3:
            sql = sql_template.format(column1, table, column2)
        elif "GROUP BY" in sql_template:
            sql = sql_template.format(column2, column1, column1, table, column2)
        else:
            sql = sql_template

        # Validate that the table exists in the schema
        # if table not in SCHEMA:
        #     raise ValueError(f"Invalid table name: {table}")

        return question, sql

    except Exception as e:
        return f"Error generating question and SQL: {e}", ""


def split_question_sql(input_string):
    # Split the input into parts using "," as the delimiter
    parts = input_string.split('", ')
    
    # Clean and extract the "Question" and "SQL" parts
    question = parts[0].replace('"Question: ', '').strip('"')
    sql = parts[1].replace('"SQL: ', '').strip('}"')
    
    # Organize into a dictionary
    result = {
        "question": question,
        "answer": sql
    }
    return result

if __name__ == "__main__":
    SCHEMA = {
        "customers": ['customer_id','name','email','address'],
        "orders": ['order_id','product_id','customer_id','order_date'],
        "products": ['product_id','name','description','price','stock_quantity'],
    }

    QUESTIONS = [
        # Basic listing
        ("List all {} from the {} table", "SELECT {} FROM {};"),
        # Conditional retrieval
        ("Find all rows where {} is '{}' in the {} table", "SELECT * FROM {} WHERE {} = '{}';"),
        # Aggregation and grouping
        ("Show the total {} grouped by {} in the {} table", "SELECT {}, SUM({}) AS total_{} FROM {} GROUP BY {};"),
        # Joining two tables
        ("Get the {} of orders made by customers", 
        "SELECT {} FROM orders INNER JOIN customers ON orders.customer_id = customers.customer_id;"),
        # Sorting results
        ("Retrieve all {} sorted by {} in the {} table", "SELECT {} FROM {} ORDER BY {};"),
    ]

    # Example usage
    knowledge_sql = []
    for _ in range(100):  # Generate 3 random questions
        question, sql = generate_random_question_and_answer()
        qsql = split_question_sql(f'"Question: {question}", "SQL: {sql}"')
        if sql != '' and qsql not in knowledge_sql:
            knowledge_sql.append(
                qsql
            )

    print(knowledge_sql)

    i = 0
    for sql in knowledge_sql:
        try:
            pd.read_sql_query(sql['answer'], conn)
            i+=1
            print(f'pass: {i}')
            print(sql['question']+'\n')
        except Exception as e:
            print('------------------------------------')
            print(sql['question']+'\n')
            print(sql['answer']+'\n')
            print(str(e)+'\n')
            print('------------------------------------')

    try:
        with open("data_storage/questions.json", "w") as json_file:
            json.dump(knowledge_sql, json_file, indent=4)
        print("JSON file saved successfully.")
    except Exception as e:
        print(f"Error saving JSON file: {e}")