import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

bucket = "test"
token = "jUG6IvalPnGSNqBiTUxyf2w2Z21alUVsFnCCTVekgryUzI6GmIuDmnCn-KuqE2V8P4iefOCMSNRDFRbG8GQEtw=="
org = "AP"
url = "http://168.119.186.250:8086"
DBclient = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = DBclient.write_api(write_options=SYNCHRONOUS)
read_api = DBclient.query_api()
