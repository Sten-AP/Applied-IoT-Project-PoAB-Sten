import base64
import certifi
from paho.mqtt.client import Client
import json
import requests


APPID = "portofantwerp-2023@ttn"
PSW = 'NNSXS.2F7ZVD6AVRIBI4O7WOYSTPKDWMPG66NL2L6CARI.K3EHQPN5FLRTSTBF6NBJ4LPKF7V4Z2QVZQ5LMTBMGGPLMUN44EIA'
URL = "http://localhost:7000"

client = Client()


def on_connect(_client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    topic = "#"
    _client.subscribe(topic, 0)


def on_message(_client, userdata, msg):
    x = json.loads(msg.payload.decode('utf-8'))

    device_id = x["end_device_ids"]["device_id"]

    if "uplink_message" in x and device_id == "eui-a8610a30373d9301":
        print(f"device id is {device_id}")
        payload = x["uplink_message"]["decoded_payload"]["payload"]
        print(f"de payload is {payload}")

        payload_data = list(payload.split(":"))

        converted_data = []
        for item in payload_data:
            # Split each item by '.' to separate integer and decimal parts
            parts = item.split(".")

            # Convert the integer part to an integer (if it's a valid integer)
            integer_part = int(parts[0]) if parts[0].isdigit() else 0
            converted_data.append(integer_part)

        # print(converted_data)
        # print(payload_data)

        query = {
            "id": str(device_id),
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

        # Aanmaken van de baken
        response = requests.post(f"{URL}/baken/aanmaken", json=query).json()
        print(response)

        # Lichtsterkte & autoset
        # response = requests.get(
        #     f"{URL}/baken/{device_id}/autoset").json()
        # if response["autoset"]:
        #     if int(payload_data[4]) < 400:
        #         create_downlink_all("LA1")
        #     if int(payload_data[4]) > 600:
        #         create_downlink_all("LA0")


def on_disconnect(_client, userdata, rc):
    print("Disconnected with result code " + str(rc))


def create_downlink(data, device_id):
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
    topic = "v3/{}/devices/{}/down/push".format(APPID, device_id)
    client.publish(topic, payload_json)


def create_downlink_all(data):
    data = data.encode("ascii")
    data = base64.b64encode(data)
    data = data.decode("ascii")
    print(f"data naar alle devices: {data}")

    idlist = []
    bakens = requests.get(f"{URL}/baken").json()
    for baken in bakens:
        if baken["autoset"]:
            idlist.append(baken["id"])

    print(idlist)
    if idlist:
        for _id in idlist:
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
            topic = "v3/{}/devices/{}/down/push".format(APPID, _id)
            client.publish(topic, payload_json)
    else:
        print("Geen devices met autoset 1")


def on_publish(_client, userdata, mid):
    print("Message published with MID: " + str(mid))


def Init():
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish

    client.enable_logger()
    client.tls_set(ca_certs=certifi.where())
    client.username_pw_set(APPID, PSW)
    client.connect("eu1.cloud.thethings.network", 8883, 60)

    client.loop_start()

