from fastapi import FastAPI
from confluent_kafka import Producer
import os
import json

app = FastAPI(title="Order Service")

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "b-1.msk:9092")

producer = Producer({
    "bootstrap.servers": KAFKA_BROKER
})

@app.post("/order/checkout")
def checkout(order: dict):
    data = json.dumps(order)
    producer.produce("orders", value=data.encode("utf-8"))
    producer.flush()

    return {"status": "order placed", "order": order}
