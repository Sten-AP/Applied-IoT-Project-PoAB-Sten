import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

BUCKET = "FastAPItest"
TOKEN = "19qF67GYbA-oxNwBoUbdgqtxZU7RwJ_AYStxdDCPecdfPWu6wdYKZ4_bmpnqvBF0Y_0_agG1BnqSo1MzhP5GzQ=="
ORG = "AP"
URL = "http://poab.iot-ap.be:8086"

client = influxdb_client.InfluxDBClient(url=URL, token=TOKEN, org=ORG)
db_write = client.write_api(write_options=SYNCHRONOUS)
db_read = client.query_api()
