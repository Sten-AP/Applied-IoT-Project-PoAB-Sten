import requests

id = 3

query = {
    "id": f"{id}",
    "status": 0,
    "lamp_1": 0,
    "lamp_2": 0,
    "lamp_3": 0,
    "lichtsterkte": 350,
    "luchtdruk": 20.5,
    "temperatuur": 15.5,
    "latitude": 45.2,
    "longitude": 4.2,
}

status = {"status": 13.2}

# Aanmaken
queryResponse = requests.post(
    "http://localhost:7000/baken/aanmaken", json=query)
print(queryResponse.text)

# queryResponse = requests.post(
#     "http://localhost:7000/baken/4/temperatuur", params=status)
# print(queryResponse.text)

# Gegevens opvragen
# queryResponse = requests.get(f"http://localhost:8000/baken/3/autoset").json()
# print(queryResponse["autoset"])
