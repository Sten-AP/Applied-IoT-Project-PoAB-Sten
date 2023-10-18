import requests
import mqtt

URL = "http://localhost:7000"

# print(requests.get(f"{URL}/baken/").json())

# mqtt.Init()

# id = "eui-1"
# query = {
#     "id": f"{id}",
#     "status": 1,
#     "lamp_1": 1,
#     "lamp_2": 1,
#     "lamp_3": 1,
#     "lichtsterkte": 926,
#     "luchtdruk": 16.3,
#     "temperatuur": 17.8,
#     "latitude": 45.21,
#     "longitude": 4.21,
# }

# status = {"status": 13.2}

# # Aanmaken
# queryResponse = requests.post(
#     "http://localhost:7000/baken/aanmaken", json=query)
# print(queryResponse.text)

# # queryResponse = requests.post(
# #     "http://localhost:7000/baken/4/temperatuur", params=status)
# # print(queryResponse.text)

# # Gegevens opvragen
bakens = requests.get(f"{URL}/baken/").json()

idlist = []
for baken in bakens:
    idlist.append(baken["id"])

autoset_en_lichtsterkte = []
for baken in bakens:
    autoset_en_lichtsterkte.append({'lichtsterkte': baken['lichtsterkte'], 'autoset': baken['autoset']})

avg = [0, 0]
for item in autoset_en_lichtsterkte:
    for param in item:
        if param == "lichtsterkte":
            avg[0] += item[param]
        if param == "autoset" and item[param] == 1:
            avg[1] += 1

if avg[0] != 0:
    avg[0] = int(avg[0] / avg[1])
else:
    avg[0] == None
    
if avg[0] is not None:
    print(f"Gemiddeld lichtsterkte: {avg[0]}, aantal autoset: {avg[1]}")
    if avg[0] < 400:
                print("lamp aan door gemidelde")
                create_downlink_all("LA1", idlist)

            if avg[0] > 600:
                print("lampen uit door gemidelde")
                create_downlink_all("LA0", idlist)