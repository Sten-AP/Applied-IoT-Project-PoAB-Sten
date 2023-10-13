import requests
from datetime import datetime
import pandas as pd
import json
from main import client

query = {
    "id": f"baken{4}",
    "lamp1": 0,
    "lamp2": 0,
    "lamp3": 0,
    "licht": 500,
    "luchtdruk": 5,
    "temp": 20.5,
    "lat": 45.5,
    "lon": 4.1,
}

queryResponse = requests.post("http://localhost:8000/aanmaken/baken", json=query)
baken = queryResponse.json()
print(queryResponse.text)