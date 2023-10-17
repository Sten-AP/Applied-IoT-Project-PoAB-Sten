import requests

id = 3

query = {
    "id": f"{id}",
    "status": 1,
    "lamp_1": 1,
    "lamp_2": 1,
    "lamp_3": 1,
    "lichtsterkte": 350,
    "luchtdruk": 3,
    "temperatuur": 17.5,
    "latitude": 45.2,
    "longitude": 4.2,
}

status = {"status": 1}

# Aanmaken
queryResponse = requests.post(
    "http://localhost:8000/baken/3/status").json()
print(queryResponse)

# Gegevens opvragen
# queryResponse = requests.get(f"http://localhost:8000/baken/3/autoset").json()
# print(queryResponse["autoset"])
