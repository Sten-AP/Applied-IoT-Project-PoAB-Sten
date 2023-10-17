import base64
import datetime

import certifi
import paho.mqtt.client as mqtt
import json


import influxdb

APPID = "portofantwerp-2023@ttn"
PSW = 'NNSXS.2F7ZVD6AVRIBI4O7WOYSTPKDWMPG66NL2L6CARI.K3EHQPN5FLRTSTBF6NBJ4LPKF7V4Z2QVZQ5LMTBMGGPLMUN44EIA'

client = mqtt.Client()


def on_connect(_client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    topic = "#"
    _client.subscribe(topic, 0)


def on_message(_client, userdata, msg):
    x = json.loads(msg.payload.decode('utf-8'))

    device_id = x["end_device_ids"]["device_id"]

    if "uplink_message" in x and device_id == "eui-a8610a30373d9301":
        print(x)
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

        print(converted_data)
        print(payload_data)

        query = f'from(bucket: "{influxdb.bucket}")\
                |> range(start: 0)\
                |> filter(fn: (r) => r["_measurement"] == "bakens")\
                |> filter(fn: (r) => r["id"] == "{device_id}")'

        result = influxdb.read_api.query(org=influxdb.org, query=query)
        if result:
            data = influxdb.influxdb_client.Point("bakens").tag("id", device_id)\
                .field("aan_uit", int(payload_data[0]))\
                .field("lamp1", int(payload_data[1]))\
                .field("lamp2", int(payload_data[2]))\
                .field("lamp3", int(payload_data[3]))\
                .field("lichtdetectie", int(payload_data[4])) \
                .field("latitude", payload_data[5]) \
                .field("longitude", payload_data[6]) \
                .field("temp", payload_data[7]) \
                .field("pressure", payload_data[8]) \
                .field("last", int(datetime.datetime.now().timestamp()))
        else:  # Nieuwe baken + dataset
            data = influxdb.influxdb_client.Point("bakens").tag("id", device_id) \
                .field("aan_uit", int(payload_data[0])) \
                .field("lamp1", int(payload_data[1])) \
                .field("lamp2", int(payload_data[2])) \
                .field("lamp3", int(payload_data[3])) \
                .field("lichtdetectie", payload_data[4]) \
                .field("latitude", payload_data[5]) \
                .field("longitude", payload_data[6]) \
                .field("temp", payload_data[7]) \
                .field("pressure", payload_data[8]) \
                .field("autoset", 0) \
                .field("last", int(datetime.datetime.now().timestamp()))

        influxdb.write_api.write(bucket=influxdb.bucket, org=influxdb.org, record=data)

        query = f'from(bucket: "{influxdb.bucket}")\
        |> range(start: 0)\
        |> filter(fn: (r) => r["_measurement"] == "bakens")\
        |> filter(fn: (r) => r["_field"] == "autoset" or r["_field"] == "lichtdetectie")\
        |> last()'

        result = influxdb.read_api.query(org=influxdb.org, query=query)
        avg = [0, 0]  # Result + count
        for i in range(0, len(result), 2):
            for record in result[i].records:
                if record.get_value() == 1:
                    avg[0] += result[i + 1].records[0].get_value()
                    avg[1] += 1

        if avg[0] != 0:
            avg[0] = int(avg[0] / avg[1])
        else:
            avg[0] == None

        if avg[0] is not None:
            print(f"Het licht gemidelde: {avg[0]}, aantal autoset: {avg[1]}")

            if avg[0] < 400:
                print("lamp aan door gemidelde")
                create_downlink_all("LA1")

            if avg[0] > 600:
                print("lampen uit door gemidelde")
                create_downlink_all("LA0")


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

    query = f'from(bucket: "{influxdb.bucket}")\
    |> range(start: 0)\
    |> filter(fn: (r) => r["_measurement"] == "bakens")\
    |> filter(fn: (r) => r["_field"] == "autoset" and r["_value"] == 1)\
    |> last()'

    result = influxdb.read_api.query(org=influxdb.org, query=query)
    idlist = []
    for i in range(0, len(result)):
        for record in result[i].records:
            idlist.append(record.values.get("id"))

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
    cafile = certifi.where()

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish

    client.enable_logger()
    client.tls_set(ca_certs=certifi.where())
    client.username_pw_set(APPID, PSW)
    client.connect("eu1.cloud.thethings.network", 8883, 60)

    client.loop_start()
