import requests

from pprint import pprint as pp
# from IPython.display import Markdown

# Set a custom width for pretty-printing
def pprint(data, width=80):
    """Pretty print data with a specified width."""
    pp(data, width=width)# List of model identifiers to query

url = "http://localhost:8000/generate"
data1 = {"prompt": "I forgot email password"}
data2 = {"prompt": "What product is the most profitable?"}
data3 = {"prompt": "Who can make the most sales?"}
data4 = {"prompt": "Tell then lastest sale product?"}
response = requests.post(url, json=data1)
pprint(response.json())
response = requests.post(url, json=data2)
pprint(response.json())
response = requests.post(url, json=data3)
pprint(response.json())
response = requests.post(url, json=data4)
pprint(response.json())