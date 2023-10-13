from fastapi import FastAPI
from typing import Optional
import json
import pandas as pd
from datetime import datetime
import random as r
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from influxdb_client_3 import InfluxDBClient3

BUCKET = "FastAPItest"
TOKEN = "19qF67GYbA-oxNwBoUbdgqtxZU7RwJ_AYStxdDCPecdfPWu6wdYKZ4_bmpnqvBF0Y_0_agG1BnqSo1MzhP5GzQ=="
ORG = "AP"
URL = "http://poab.iot-ap.be:8086"

client = InfluxDBClient3(host=URL, token=TOKEN, org=ORG, database=BUCKET, enable_gzip=True)
app = FastAPI()


class Baken(BaseModel):
    id: str
    lamp1: int = 0
    lamp2: int = 0
    lamp3: int = 0
    licht: int = None
    luchtdruk: int = None
    temp: float = None
    lat: float = None
    lon: float = None
    time: datetime = pd.Timestamp.now(tz='UCT').floor('ms')

@app.get("/")
def read_root():
    return {"Hello": "World"}


# @app.get("/baken")
# def get_baken():
#     query = f"""from (bucket: "{BUCKET}")
#         |> range(start: 0)
#         |> filter(fn: (r) => r["id"] == "eui-a8610a30373d9301")
#         |> last()"""

#     results = []
#     for table in read(query):
#         for record in table.records:
#             results.append(record)
#     return {json.dumps(results)}


@app.post("/aanmaken/baken")
async def post_baken(baken: Baken):
    try:
        baken_df = pd.DataFrame([dict(baken)]).set_index("time")
        client.write(baken_df, data_frame_measurement_name='baken', data_frame_tag_columns=['id'], data_frame_field_columns=['lamp1, lamp2, lamp3, licht, luchtdruk, temp, lat, lon'])
        return {"message": f"{baken.id} is succesvol aangemaakt."}
    except:
        return {"message": "Baken is niet aangemaakt."}
