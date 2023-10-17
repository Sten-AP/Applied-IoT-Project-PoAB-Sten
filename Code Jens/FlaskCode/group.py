from datetime import datetime

import app
import influxdb
import json


class GroupData:
    def __init__(self):
        self.group_id = 0
        self.device_ids = ""
        self.time = None


class GroupDataEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, GroupData):
            return {
                "group_id": obj.group_id,
                "devices": obj.device_ids,
                "time": obj.time,
            }
        return super().default(obj)


def get_all_group_data(showAll):
    print("Loading groups...")
    groups = []
    query = f'from(bucket: "{influxdb.bucket}")\
            |> range(start: 0)\
            |> filter(fn: (r) => r["_measurement"] == "groups")\
            |> filter(fn: (r) => r["_field"] == "devices" )\
            |> last()'

    resultIds = influxdb.read_api.query(org=influxdb.org, query=query)
    for i in range(len(resultIds)):
        group = GroupData()
        removed = False
        for record in resultIds[i].records:
            if "removed" in str(record.values.get("id")):
                if not showAll:
                    continue

                print(record)

            group.group_id = record.values.get("id")
            group.time = record.values.get("_time").strftime("%Y-%m-%d %H:%M:%S.%f%z")
            group.device_ids = record.values.get("devices")

            query = f'from(bucket: "{influxdb.bucket}")\
                                |> range(start: 0)\
                                |> filter(fn: (r) => r["_measurement"] == "groups" and r["id"] == "{group.group_id}")\
                                |> last()'

            resultAllFields = influxdb.read_api.query(org=influxdb.org, query=query)
            for r in range(len(resultAllFields)):
                field = resultAllFields[r].records[0].get_field()
                value = resultAllFields[r].records[0].get_value()
                if field == "removed":
                    if value == "yes":
                        removed = True

        if not showAll:
            if group.time is not None and not removed:
                groups.append(group)
        else:
            groups.append(group)

    print(json.dumps(groups, cls=GroupDataEncoder))
    print("All groups have been loaded")

    return groups


def DeleteGroup(_id):
    print("Trying to delete group " + str(_id))
    _groups = get_all_group_data(False)
    for group in _groups:
        if group.group_id == str(_id):
            data = influxdb.influxdb_client.Point("groups").tag("id", str(_id)).field("devices", "").field(
                "removed", "yes").time(datetime.strptime(group.time, "%Y-%m-%d %H:%M:%S.%f%z"))
            influxdb.write_api.write(bucket=influxdb.bucket, org=influxdb.org, record=data)
            break


def NewGroup():
    print("Creating new group...")

    _id = 1
    for _ in get_all_group_data(True):
        _id += 1

    data = influxdb.influxdb_client.Point("groups").tag("id", _id).field("devices", "")
    influxdb.write_api.write(bucket=influxdb.bucket, org=influxdb.org, record=data)
    print("New group has been created with id " + str(_id))
