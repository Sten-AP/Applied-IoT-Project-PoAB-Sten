from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import pandas as pd
from datetime import datetime
from pydantic import BaseModel
from influxdb_client_3 import InfluxDBClient3
from influxdb_client import InfluxDBClient
import mqtt
import uvicorn

BUCKET = "FastAPItest"
TOKEN = "19qF67GYbA-oxNwBoUbdgqtxZU7RwJ_AYStxdDCPecdfPWu6wdYKZ4_bmpnqvBF0Y_0_agG1BnqSo1MzhP5GzQ=="
URL = "http://168.119.186.250:8086"
API_URL = "http://localhost:7000"
ORG = "AP"


read_client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_client = InfluxDBClient3(host=URL, token=TOKEN, org=ORG, database=BUCKET)
read_api = read_client.query_api()

app = FastAPI()

origins = [
    "http://localhost:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def records(response):
    gegevens = {}
    for table in response:
        for record in table.records:
            gegevens.update({record.get_field(): record.get_value()})
    return gegevens


def nieuwe_tijd():
    return pd.Timestamp.now(tz='UCT').floor('ms')


class Baken(BaseModel):
    id: str
    status: int
    lamp_1: int = -999
    lamp_2: int = -999
    lamp_3: int = -999
    lichtsterkte: int = -999
    luchtdruk: float = -999
    temperatuur: float = -999
    latitude: float = -999
    longitude: float = -999
    autoset: int = 0
    time: datetime = 0


def nieuwe_baken(baken: Baken):
    try:
        baken.time = nieuwe_tijd()
        baken_df = pd.DataFrame([dict(baken)]).set_index("time")
        write_client.write(baken_df, data_frame_measurement_name='baken',
                           data_frame_tag_columns=['id'])
        return {"message": f"baken {baken.id} is succesvol aangemaakt"}
    except Exception as e:
        return {"message": f"fout bij het aanmaken van baken {baken.id}: {e}"}


@app.post("/baken/aanmaken/")
async def baken_aanmaken(baken: Baken):
    return nieuwe_baken(baken)


@app.post("/baken/{id}/{param}/")
async def baken_status_aanpassen(id: str, param: str, status: int | float):
    if param == "status" and status == 1:
        mqtt.create_downlink("LA1", id)
    if param == "status" and status == 0:
        mqtt.create_downlink("LA0", id)
        
    if param in ["status", "lamp_1", "lamp2", "lamp_3", "lichtsterkte", "luchtdruk", "temperatuur", "latitude", "longitude", "autoset"]:
        try:
            get_query = f"""from(bucket: "{BUCKET}")
                    |> range(start: 0)
                    |> filter(fn: (r) => r["_measurement"] == "baken")
                    |> filter(fn: (r) => r["id"] == "{id}")
                    """

            response = read_api.query(get_query, org=ORG)
            gegevens = records(response)
            gegevens["id"] = id

            baken = Baken(**gegevens)

            setattr(baken, param, status)
            
            return nieuwe_baken(baken)
        except Exception as e:
            return {"error": str(e)}
    return {"error": f"{param} is niet aan te passen"}


@app.get("/baken/")
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


@app.get("/baken/{id}/")
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


@app.get("/baken/{id}/{data}/")
async def specifieke_gegevens_per_baken(id: str, data: str):
    try:
        filter = f"""|> filter(fn: (r) => r["_field"] == "{data}")"""
        if data == "locatie":
            filter = """|> filter(fn: (r) => r["_field"] == "latitude" or r["_field"] == "longitude")"""
        if data == "lampen":
            filter = """|> filter(fn: (r) => r["_field"] == "lamp_1" or r["_field"] == "lamp_2" or r["_field"] == "lamp_3")"""

        query = f"""from(bucket: "{BUCKET}")
            |> range(start: 0)
            |> filter(fn: (r) => r["_measurement"] == "baken")
            {filter}
            |> filter(fn: (r) => r["id"] == "{id}")
            """

        response = read_api.query(query, org=ORG)

        return records(response)
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mqtt.Init()
    uvicorn.run("main:app", port=7000, log_level="info", reload=True)
    
