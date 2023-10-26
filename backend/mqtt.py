import base64
import certifi
from paho.mqtt.client import Client
import json
import requests
from urls import API_URL

# -----------Constants-----------
APPID = "portofantwerp-2023@ttn"
PSW = 'NNSXS.2F7ZVD6AVRIBI4O7WOYSTPKDWMPG66NL2L6CARI.K3EHQPN5FLRTSTBF6NBJ4LPKF7V4Z2QVZQ5LMTBMGGPLMUN44EIA'

# -----------MQTT-settings-----------
client = Client()
client.enable_logger()
client.tls_set(ca_certs=certifi.where())
client.username_pw_set(APPID, PSW)
client.connect("eu1.cloud.thethings.network", 8883, 60)


# -----------Functions-----------
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("#", 0)

def on_message(client, userdata, msg):
    x = json.loads(msg.payload.decode('utf-8'))
    id = x["end_device_ids"]["device_id"]

    if "uplink_message" in x and id == "eui-a8610a30373d9301":
        payload = x["uplink_message"]["decoded_payload"]["payload"]
        payload_data = list(payload.split(":"))

        print(f"ID: {id}")
        print(f"Payload: {payload}")
        
        converted_data = []
        for item in payload_data:
            parts = item.split(".")
            integer_part = int(parts[0]) if parts[0].isdigit() else 0
            converted_data.append(integer_part)

        query = {
            "id": str(id),
            "status": int(payload_data[0]),
            "lamp_1": int(payload_data[1]),
            "lamp_2": int(payload_data[2]),
            "lamp_3": int(payload_data[3]),
            "lichtsterkte": int(payload_data[4]),
            "latitude": float(payload_data[5]),
            "longitude": float(payload_data[6]),
            "temperatuur": float(payload_data[7]),
            "luchtdruk": float(payload_data[8]),
        }
        
        print(requests.post(f"{API_URL}/baken/aanmaken/", json=query).json())

def on_disconnect(client, userdata, rc):
    print("Disconnected with result code " + str(rc))

def on_publish(client, userdata, mid):
    print("Message published with MID: " + str(mid))

def create_downlink(data, id):
    data = data.encode("ascii")
    data = base64.b64encode(data)
    data = data.decode("ascii")
    
    payload = {
        "downlinks": [
            {
                "f_port": 1,
                "frm_payload": str(data),
                "priority": "NORMAL"
            }
        ]
    }

    payload_json = json.dumps(payload)
    topic = f"v3/{APPID}/devices/{id}/down/push"
    client.publish(topic, payload_json)

def create_downlink_all(data, idlist):
    if idlist:
        for _id in idlist:
            create_downlink(data, _id)


# -----------MQTT-functions-----------
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
