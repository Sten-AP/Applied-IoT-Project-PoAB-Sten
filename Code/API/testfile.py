from cbaken import baken
from influxdb import write, read, BUCKET
import json
import time
import random as r
import pandas as pd

NOW = pd.Timestamp.now(tz='UCT').floor('ms')

query = f"""from (bucket: "{BUCKET}")
        |> range(start: 0)
        |> filter(fn: (r) => r["id"] == "eui-a8610a30373d9301")
        |> last()"""

results = []
# for table in read(query):
#     for record in table.records:
#         results.append(record)

# print(list(read(query))[8].records[0])

