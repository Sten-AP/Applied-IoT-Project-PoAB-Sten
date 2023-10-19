from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pandas import DataFrame, Timestamp
from datetime import datetime
from pydantic import BaseModel
from influxdb_client_3 import InfluxDBClient3
from influxdb_client import InfluxDBClient
from mqtt import client, create_downlink_all, create_downlink
from uvicorn import run


# -----------Constants-----------
INFLUXDB_URL = "http://168.119.186.250:8086"
API_URL = "http://localhost:7000"
REACT_URL = "http://localhost:5173"

BUCKET = "bakens-poab"
TOKEN = "19qF67GYbA-oxNwBoUbdgqtxZU7RwJ_AYStxdDCPecdfPWu6wdYKZ4_bmpnqvBF0Y_0_agG1BnqSo1MzhP5GzQ=="
ORG = "AP"
BASE_QUERY = f"""from(bucket: "{BUCKET}") 
                |> range(start: 0)
                |> filter(fn: (r) => r["_measurement"] == "baken")"""


# -----------InfluxDB-settings-----------
read_client = InfluxDBClient(url=INFLUXDB_URL, token=TOKEN, org=ORG)
write_client = InfluxDBClient3(host=INFLUXDB_URL, token=TOKEN, org=ORG, database=BUCKET)
read_api = read_client.query_api()


# -----------App-settings-----------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=REACT_URL,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------Classes-----------
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


# -----------Functions-----------
def records(response):
    gegevens = {}
    for table in response:
        for record in table.records:
            gegevens.update({record.get_field(): record.get_value()})
    return gegevens

def nieuwe_tijd():
    return Timestamp.now(tz='UCT').floor('ms')

def nieuwe_baken(baken: Baken):
    try:
        baken.time = nieuwe_tijd()
        baken_df = DataFrame([dict(baken)]).set_index("time")
        write_client.write(baken_df, data_frame_measurement_name='baken',
                           data_frame_tag_columns=['id'])
        return {"message": f"baken {baken.id} is succesvol aangemaakt"}
    except Exception as e:
        return {"message": f"fout bij het aanmaken van baken {baken.id}: {e}"}

def enkele_baken_aansturen(id, status):
    if status == 1:
        create_downlink("LA1", id)
    if status == 0:
        create_downlink("LA0", id)

# def alle_baken_aansturen(bakens, status):
#     idlist = []
#     for baken in bakens:
#         idlist.append(baken["id"])

#     if status == 1:
#         create_downlink_all("LA1", idlist)
#     if status == 0:
#         create_downlink_all("LA0", idlist)


# -----------Routes-----------
@app.post("/baken/aanmaken/")
async def baken_aanmaken(baken: Baken):
    return nieuwe_baken(baken)

@app.post("/baken/{id}/{param}/")
async def baken_status_aanpassen(id: str, param: str, status: int | float):
    if param in ["status", "lamp_1", "lamp2", "lamp_3", "lichtsterkte", "luchtdruk", "temperatuur", "latitude", "longitude", "autoset"]:
        try:
            if param == "status":
                enkele_baken_aansturen(id, status)
                # bakens = await alle_bakens_oplijsten()
                # alle_baken_aansturen(bakens, status)
                
            query = BASE_QUERY + f"""|> filter(fn: (r) => r["id"] == "{id}")"""
            response = read_api.query(query, org=ORG)
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
        response = read_api.query(BASE_QUERY, org=ORG)

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
        query = BASE_QUERY + f"""|> filter(fn: (r) => r["id"] == "{id}")"""
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

        query = BASE_QUERY + filter +f"""|> filter(fn: (r) => r["id"] == "{id}")"""
        response = read_api.query(query, org=ORG)

        return records(response)
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    client.loop_start()
    run("main:app", port=7000, reload=True)