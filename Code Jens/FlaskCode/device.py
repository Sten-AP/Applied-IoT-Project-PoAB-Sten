import app
import datetime
import influxdb
import json


class SensorData:
    def __init__(self):
        self.device_id = 0
        self.aan_uit = 0
        self.lamp1 = 0
        self.lamp2 = 0
        self.lamp3 = 0
        self.lichtdetectie = 0
        self.autoset = 0
        self.temp = 0
        self.pressure = 0
        self.last = 0
        self.status = ""


class SensorDataEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SensorData):
            # Convert the SensorData object to a dictionary
            return {
                "device_id": obj.device_id,
                "aan_uit": obj.aan_uit,
                "lamp1": obj.lamp1,
                "lamp2": obj.lamp2,
                "lamp3": obj.lamp3,
                "lichtdetectie": obj.lichtdetectie,
                "autoset": obj.autoset,
                "temp": obj.temp,
                "pressure": obj.pressure,
                "last": obj.last,
                "status": obj.status,
            }
        return super().default(obj)


def get_all_devices_data():
    print("Loading devices...")
    devices = []
    query = f'from(bucket: "{influxdb.bucket}")\
        |> range(start: 0)\
        |> filter(fn: (r) => r["_measurement"] == "bakens")\
        |> filter(fn: (r) => r["_field"] == "autoset" )\
        |> last()'

    resultIds = influxdb.read_api.query(org=influxdb.org, query=query)
    for i in range(len(resultIds)):
        device = SensorData()
        for record in resultIds[i].records:
            device.device_id = record.values.get("id")

            query = f'from(bucket: "{influxdb.bucket}")\
                            |> range(start: 0)\
                            |> filter(fn: (r) => r["_measurement"] == "bakens" and r["id"] == "{device.device_id}")\
                            |> last()'

            resultAllFields = influxdb.read_api.query(org=influxdb.org, query=query)
            for r in range(len(resultAllFields)):
                field = resultAllFields[r].records[0].get_field()
                value = resultAllFields[r].records[0].get_value()
                if field == "aan_uit":
                    device.aan_uit = value
                elif field == "lamp1":
                    device.lamp1 = value
                elif field == "lamp2":
                    device.lamp2 = value
                elif field == "lamp3":
                    device.lamp3 = value
                elif field == "lichtdetectie":
                    device.lichtdetectie = value
                elif field == "autoset":
                    device.autoset = value
                elif field == "temp":
                    device.temp = value
                elif field == "pressure":
                    device.pressure = value
                elif field == "last":
                    device.last = value
                elif field == "status":
                    device.status = value

            if not device.lamp1 == device.lamp2 or not device.lamp1 == device.lamp3:
                device.status = str(device.status) + "ERROR"

        devices.append(device)

    for device in devices:
        if device.last:
            print(device.last)
            modified_time = getTime(device.last)
            device.last = modified_time
    print(json.dumps(devices, cls=SensorDataEncoder))

    print("All devices have been loaded")
    return devices


def getTime(time):
    try:
        if time:
            timestamp = int(time)
            dt_object = datetime.datetime.fromtimestamp(timestamp)
            formatted_date = dt_object.strftime('%d/%m/%Y %H:%M:%S')
            return formatted_date
        else:
            return "Timestamp Missing"
    except (ValueError, OSError):
        return "Invalid Timestamp"
