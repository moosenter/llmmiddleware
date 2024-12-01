import requests

from pprint import pprint as pp
# Set a custom width for pretty-printing
def pprint(data, width=80):
    """Pretty print data with a specified width."""
    pp(data, width=width)# List of model identifiers to query

url = "http://localhost:8000/generate"
data1 = {"prompt": "I forgot email password"}
data2 = {"prompt": "Who is responsible in the North region?"}
data3 = {"prompt": "Tell me about sales in Q1 2023 for the North region."}
data4 = {"prompt": "Tell me about sales in Q4 2024 for the South region."}
response = requests.post(url, json=data1)
pprint(response.json())
response = requests.post(url, json=data2)
pprint(response.json())
response = requests.post(url, json=data3)
pprint(response.json())
response = requests.post(url, json=data4)
pprint(response.json())