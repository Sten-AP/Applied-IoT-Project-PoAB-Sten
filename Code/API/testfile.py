import requests

id = "eui-1"

query = {
    "id": f"{id}",
    "status": 1,
    "lamp_1": 1,
    "lamp_2": 1,
    "lamp_3": 1,
    "lichtsterkte": 926,
    "luchtdruk": 16.3,
    "temperatuur": 17.8,
    "latitude": 45.21,
    "longitude": 4.21,
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
queryResponse = requests.get(f"http://localhost:8000/baken/3/autoset").json()
print(queryResponse["autoset"])
