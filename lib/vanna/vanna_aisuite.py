from vanna.base import VannaBase
import aisuite as ai
from dotenv import load_dotenv
import json
import dataclasses
from dataclasses import dataclass
import requests
import os
from abc import ABC, abstractmethod
from io import StringIO
import re
import pandas as pd
from pydantic import ValidationError

from pprint import pprint as pp
def pprint(data, width=80):
    pp(data, width=width)

from .milvus_vector import Milvus_VectorStore

def sanitize_model_name(model_name):
    try:
        model_name = model_name.lower()

        # Replace spaces with a hyphen
        model_name = model_name.replace(" ", "-")

        if '-' in model_name:

            # remove double hyphones
            model_name = re.sub(r"-+", "-", model_name)
            if '_' in model_name:
                # If name contains both underscores and hyphen replace all underscores with hyphens
                model_name = re.sub(r'_', '-', model_name)

        # Remove special characters only allow underscore
        model_name = re.sub(r"[^a-zA-Z0-9-_]", "", model_name)

        # Remove hyphen or underscore if any at the last or first
        if model_name[-1] in ("-", "_"):
            model_name = model_name[:-1]
        if model_name[0] in ("-", "_"):
            model_name = model_name[1:]

        return model_name
    except Exception as e:
        raise ValidationError(e)

class aisuite_Chat(Milvus_VectorStore):
    def __init__(self, client=None, config={'milvus_client':'data_storage/vanna-democompany-vector.db','model':'groq:llama-3.2-3b-preview'}):
        VannaBase.__init__(self, config=config)
        Milvus_VectorStore.__init__(self, config=config)

        load_dotenv()

        if config is None:
            self._model = 'groq:llama-3.2-3b-preview'
        else:
            self._model = config['model']
        self._api_key = os.getenv('GROQ_API_KEY')

        if client is not None:
            self.client = client
            return

        else:
            self.client = ai.Client()
            return

    def system_message(self, message: str) -> any:
        return {"role": "system", "content": message}

    def user_message(self, message: str) -> any:
        return {"role": "user", "content": message}

    def assistant_message(self, message: str) -> any:
        return {"role": "assistant", "content": message}
    
    def submit_prompt(self, prompt, **kwargs) -> str:
        if prompt is None:
            raise Exception("Prompt is None")

        if len(prompt) == 0:
            raise Exception("Prompt is empty")
        
        # Count the number of tokens in the message log
        # Use 4 as an approximation for the number of characters per token
        # num_tokens = 0
        # for message in prompt:
        #     num_tokens += len(message["content"]) / 4
        response = self.client.chat.completions.create(
            messages=prompt,
            # model='groq:llama-3.2-3b-preview',
            model=self._model
        )

        return response.choices[0].message.content

# def test_vn_milvus():
#     existing_training_data = vn_milvus.get_training_data()
#     if len(existing_training_data) > 0:
#         for _, training_data in existing_training_data.iterrows():
#             vn_milvus.remove_training_data(training_data['id'])

#     df_ddl = vn_milvus.run_sql("SELECT type, sql FROM sqlite_master WHERE sql is not null")

#     for ddl in df_ddl['sql'].to_list():
#         vn_milvus.train(ddl=ddl)

#     # sql = vn_milvus.generate_sql("what is the most sales order?")
#     sql = vn_milvus.generate_sql("who buy Laptop? give name and email")
#     df = vn_milvus.run_sql(sql)
#     print(df)

# class VannaMilvus(Milvus_VectorStore, aisuite_Chat):
#     def __init__(self, config={}):
#         Milvus_VectorStore.__init__(self, config=config)
#         aisuite_Chat.__init__(self, config=config)

# if __name__ == "__main__":
#     vn_milvus = VannaMilvus(config={'model': 'groq:llama-3.2-3b-preview'})
#     vn_milvus.connect_to_sqlite('data_storage/democompany.db')

#     test_vn_milvus()