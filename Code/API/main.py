from fastapi import FastAPI, Form
import pandas as pd
from datetime import datetime
from pydantic import BaseModel
from influxdb_client_3 import InfluxDBClient3
from influxdb_client import InfluxDBClient
import requests

BUCKET = "FastAPItest"
TOKEN = "19qF67GYbA-oxNwBoUbdgqtxZU7RwJ_AYStxdDCPecdfPWu6wdYKZ4_bmpnqvBF0Y_0_agG1BnqSo1MzhP5GzQ=="
URL = "http://168.119.186.250:8086"
ORG = "AP"

read_client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_client = InfluxDBClient3(host=URL, token=TOKEN, org=ORG, database=BUCKET)
read_api = read_client.query_api()

app = FastAPI()


class Baken(BaseModel):
    id: str
    status: int
    lamp_1: int = -999
    lamp_2: int = -999
    lamp_3: int = -999
    lichtsterkte: int = -999
    luchtdruk: int = -999
    temperatuur: float = -999
    latitude: float = -999
    longitude: float = -999
    autoset: int = 0
    time: datetime = pd.Timestamp.now(tz='UCT').floor('ms')


class Status(BaseModel):
    status: int


@app.post("/baken/aanmaken")
async def baken_aanmaken(baken: Baken):
    try:
        baken_df = pd.DataFrame([dict(baken)]).set_index("time")
        write_client.write(baken_df, data_frame_measurement_name='baken',
                           data_frame_tag_columns=['id'])
        return {"message": f"Baken {baken.id} is succesvol aangemaakt."}
    except Exception as e:
        return {"message": f"Fout bij het aanmaken van baken {baken.id}: {e}"}


@app.post("/baken/{id}/status")
async def baken_status_aanpassen(id: str, status: str):
    try:
        get_query = f"""from(bucket: "{BUCKET}")
                |> range(start: 0)
                |> filter(fn: (r) => r["_measurement"] == "baken")
                |> filter(fn: (r) => r["id"] == "{id}")
                """

        response = read_api.query(get_query, org=ORG)
        gegevens = records(response)

        post_query = {
            "id": f"{id}",
            "status": {status},
            "lamp_1": gegevens["lamp_1"],
            "lamp_2": gegevens["lamp_2"],
            "lamp_3": gegevens["lamp_3"],
            "lichtsterkte": gegevens["lichtsterkte"],
            "luchtdruk": gegevens["luchtdruk"],
            "temperatuur": gegevens["temperatuur"],
            "latitude": gegevens["latitude"],
            "longitude": gegevens["longitude"],
        }

        # requests.post(f"{URL}/aanmaken/baken", json=post_query)
        return post_query
    except Exception as e:
        return {"error": str(e)}


@app.get("/baken")
async def alle_bakens_oplijsten():
    try:
        query = f"""from(bucket: "{BUCKET}")
                |> range(start: 0)
                |> filter(fn: (r) => r["_measurement"] == "baken")
                """
        response = read_api.query(query, org=ORG)

        records = []
        baken_ids = []
        for table in response:
            for record in table.records:
                records.append(record)
                if record.values["id"] not in baken_ids:
                    baken_ids.append(record.values["id"])

        gegevens = []
        for id in baken_ids:
            baken = {}
            for record in records:
                baken.update({"id": id})
                if id == record.values["id"]:
                    baken.update({record.get_field(): record.get_value()})
            gegevens.append(baken)

        return gegevens
    except Exception as e:
        return {"error": str(e)}


@app.get("/baken/{id}")
async def baken_gegevens(id: str):
    try:
        query = f"""from(bucket: "{BUCKET}")
                |> range(start: 0)
                |> filter(fn: (r) => r["_measurement"] == "baken")
                |> filter(fn: (r) => r["id"] == "{id}")
                """
        response = read_api.query(query, org=ORG)

        return records(response)
    except Exception as e:
        return {"error": str(e)}


@app.get("/baken/{id}/{data}")
async def specifieke_gegevens_per_baken(id: str, data: str):
    try:
        query = f"""from(bucket: "{BUCKET}")
                |> range(start: 0)
                |> filter(fn: (r) => r["_measurement"] == "baken")
                |> filter(fn: (r) => r["_field"] == "{data}")
                |> filter(fn: (r) => r["id"] == "{id}")
                """

        if data == "locatie":
            query = f"""from(bucket: "{BUCKET}")
                |> range(start: 0)
                |> filter(fn: (r) => r["_measurement"] == "baken")
                |> filter(fn: (r) => r["_field"] == "longitude" or r["_field"] == "latitude")
                |> filter(fn: (r) => r["id"] == "{id}")
                """

        if data == "lampen":
            query = f"""from(bucket: "{BUCKET}")
                |> range(start: 0)
                |> filter(fn: (r) => r["_measurement"] == "baken")
                |> filter(fn: (r) => r["_field"] == "lamp_1" or r["_field"] == "lamp_2" or r["_field"] == "lamp_3")
                |> filter(fn: (r) => r["id"] == "{id}")
                """

        response = read_api.query(query, org=ORG)

        return records(response)
    except Exception as e:
        return {"error": str(e)}


def records(response):
    gegevens = {}
    for table in response:
        for record in table.records:
            gegevens.update({record.get_field(): record.get_value()})
    return gegevens
