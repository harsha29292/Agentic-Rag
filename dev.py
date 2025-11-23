import os
import requests
import json
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("SERP_API_KEY")

query = "renewable energy"

url = "https://serpapi.com/search"
params = {
    "engine": "google_patents",
    "q": query,
    "api_key": api_key,
}

resp = requests.get(url, params=params, timeout=30)
resp.raise_for_status()
data = resp.json()
patents=data.get("organic_results",[])
with open("files/patents.json", "w") as file:
    json.dump(patents, file, indent=4)

patent_url="https://serpapi.com/search.json?engine=google_patents_details&patent_id=patent%2FSA523442135B1%2Fen&api_key=" + api_key
patent_resp = requests.get(patent_url)
patent_data = patent_resp.json()
with open("files/patent_details.json", "w") as file:
    json.dump(patent_data, file, indent=4)
pprint(patent_data.get("abstract",""))
