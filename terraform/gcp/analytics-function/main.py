import base64
import json
from google.cloud import bigquery

def main(event, context):
    data = base64.b64decode(event['data']).decode('utf-8')
    record = json.loads(data)

    client = bigquery.Client()
    table = f"{client.project}.{record['dataset']}.{record['table']}"
    
    errors = client.insert_rows_json(table, [record])
    if errors:
        print("Insertion errors:", errors)
