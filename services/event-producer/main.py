from fastapi import FastAPI
from confluent_kafka import Producer
import json
import os

app = FastAPI(title="Events Producer")

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "b-1.msk:9092")

producer = Producer({
    "bootstrap.servers": KAFKA_BROKER
})

@app.post("/events")
def publish_event(event: dict):
    producer.produce("user-events", json.dumps(event).encode("utf-8"))
    producer.flush()
    return {"status": "event published"}
