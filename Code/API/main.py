from typing import Union
from fastapi import FastAPI
from cbaken import Baken
from influxdb import db_write, db_read, BUCKET
import json
import pandas as pd
from datetime import datetime
import random as r
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

NOW = pd.Timestamp.now(tz='UCT').floor('ms')

app = FastAPI()


class CBaken(BaseModel):
    id: str
    status: str = False
    lamp1: bool = False
    lamp2: bool = False
    lamp3: bool = False
    licht: int = None
    luchtdruk: int = None
    temp: float = None
    lat: float = None
    lon: float = None
    time: datetime


@app.get("/")
def read_root():
    return {"Hello": "World"}


# @app.get("/baken")
# def get_baken_list():
#     query = f"""from (bucket: "{BUCKET}")
#         |> range(start: 0)
#         |> filter(fn: (r) => r["id"] == "eui-a8610a30373d9301")
#         |> last()"""

#     results = []
#     for table in read(query):
#         for record in table.records:
#             results.append(record)
#     return {json.dumps(results)}


@app.post("/aanmaken/baken/{id}")
async def post_baken(id: int, baken: CBaken):
    baken_dict = baken.dict()
    baken_dict.update(id=f'baken{id}')
    baken_dict.update(status=True)
    baken_dict.update(lamp1=False)
    baken_dict.update(lamp3=True)
    baken_dict.update(licht=300)
    baken_dict.update(luchtdruk=5)
    baken_dict.update(temp=20.5)
    baken_dict.update(lat=45.5)
    baken_dict.update(lon=4.1)
    return baken_dict
    # return baken
    # testbaken = {
    #     'id': f'baken{id}',
    #     'status': True,
    #     'lamp1': True,
    #     'lamp2': True,
    #     'lamp3': True,
    #     'licht': 300,
    #     'luchtdruk': 5,
    #     'temp': 20,
    #     'lat': 45,
    #     'lon': 4,
    #     'time': NOW
    # }

    # testbaken_df = pd.DataFrame(testbaken).set_index('time')
    # db_write.write(testbaken_df, data_frame_measurement_name='baken',
    #                data_frame_tag_columns=['id'])

    # uvicorn main:app --reload --host 0.0.0.0
