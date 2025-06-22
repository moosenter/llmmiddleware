import pandas as pd
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine
from sqlalchemy import create_engine, MetaData
from langchain_community.agent_toolkits import create_sql_agent
from langchain.chains import create_sql_query_chain
from langchain_core.runnables import RunnablePassthrough
import aisuite as ai
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from operator import itemgetter
import re
import ast
from datetime import time

def convert_time_columns(df):
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, time)).any():
            df[col] = df[col].apply(lambda x: x.strftime('%H:%M:%S') if isinstance(x, time) else x)
    return df

def clean_column_names(name: str) -> str:
    # Remove leading/trailing single quotes from column names
    return name.strip("'")

def getcsv2sql():
    # df1 = pd.read_csv("data_storage/customers.csv")
    # df2 = pd.read_csv("data_storage/orders.csv")
    # df3 = pd.read_csv("data_storage/products.csv")

    engine = create_engine("sqlite:///data_storage/demosales.db")
    metadata = MetaData()
    metadata.reflect(bind=engine)
    metadata.drop_all(bind=engine)

    # Read all sheets into a dictionary of DataFrames
    excel_file = "/Users/visarutt/Downloads/POS_Datasource.xlsx"
    sheet_dict = pd.read_excel(excel_file, sheet_name=None, engine="openpyxl")

    # Loop over each sheet and write to SQL
    for sheet_name, df in sheet_dict.items():

        df.columns = [clean_column_names(col) for col in df.columns]
        # Clean the sheet name to use as table name
        df = convert_time_columns(df)
        table_name = sheet_name.lower().replace(" ", "_")
        
        # Write to SQL (append=False will overwrite if exists)
        df.to_sql(table_name, engine, if_exists="replace", index=False)

        print(f"Imported sheet '{sheet_name}' into table '{table_name}'")

    # df1.to_sql("customers", engine, index=False)
    # df2.to_sql("orders", engine, index=False)
    # df3.to_sql("products", engine, index=False)

    db = SQLDatabase(engine=engine)

    return db

if __name__ == "__main__":
    db = getcsv2sql()
    print(db.get_usable_table_names())

    load_dotenv()

    groq_api_key = os.environ['GROQ_API_KEY']
    model = 'llama3-70b-8192'
    # Initialize Groq Langchain chat object and conversation
    groq_chat = ChatGroq(
            groq_api_key=groq_api_key, 
            model_name=model
    )

    llm = groq_chat

    query_chain = create_sql_query_chain(llm, db)
    query = query_chain.invoke(
        # {"question": "What is the most recent orders and the product names"}
        {"question":"What are the top 10 customers by sales?"}
    )

    match = re.search(r"SQLQuery:\s*(.+)", query, re.DOTALL)
    if match:
        query = match.group(1).strip()
        print(query)

    print(db.run(query))

    
