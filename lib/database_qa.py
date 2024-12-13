import pandas as pd
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine
from sqlalchemy import create_engine, MetaData
from langchain_community.agent_toolkits import create_sql_agent
import aisuite as ai
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq


def getcsv2sql():
    df1 = pd.read_csv("data_storage/customers.csv")
    df2 = pd.read_csv("data_storage/orders.csv")
    df3 = pd.read_csv("data_storage/products.csv")

    engine = create_engine("sqlite:///data_storage/democompany.db")
    metadata = MetaData()
    metadata.reflect(bind=engine)
    metadata.drop_all(bind=engine)

    df1.to_sql("customers", engine, index=False)
    df2.to_sql("orders", engine, index=False)
    df3.to_sql("products", engine, index=False)

    db = SQLDatabase(engine=engine)

    return db

if __name__ == "__main__":
    db = getcsv2sql()
    print(db.get_usable_table_names())

    load_dotenv()

    groq_api_key = os.environ['GROQ_API_KEY']
    model = 'llama-3.2-3b-preview'
    # Initialize Groq Langchain chat object and conversation
    groq_chat = ChatGroq(
            groq_api_key=groq_api_key, 
            model_name=model
    )

    llm = groq_chat
    agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)
    agent_executor.invoke({"input": "what's the average product sales from products table"})