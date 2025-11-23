from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from confluent_kafka import Producer
import os
import json
import logging
import time
import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Order Service")

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME", "ecommerce")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

producer = Producer({
    "bootstrap.servers": KAFKA_BOOTSTRAP,
    "client.id": "order-service"
})

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

@app.get("/")
def health():
    return {"status": "healthy", "service": "order"}

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/order/checkout")
def checkout(order: dict):
    start_time = time.time()
    try:
        if not order.get("userId"):
            REQUEST_COUNT.labels(method='POST', endpoint='/order/checkout', status='400').inc()
            raise HTTPException(status_code=400, detail="userId required")
        
        # Save order to database
        conn = get_conn()
        cur = conn.cursor()
        
        total_amount = sum(item.get('price', 0) * item.get('quantity', 1) for item in order.get('items', []))
        
        cur.execute(
            "INSERT INTO orders (user_id, total_amount, status) VALUES (%s, %s, %s) RETURNING id",
            (order['userId'], total_amount, 'pending')
        )
        order_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        # Publish to Kafka
        order_event = {
            "orderId": order_id,
            "userId": order["userId"],
            "items": order.get("items", []),
            "totalAmount": total_amount,
            "timestamp": int(time.time())
        }
        
        producer.produce("orders", value=json.dumps(order_event).encode("utf-8"))
        producer.flush()
        
        REQUEST_COUNT.labels(method='POST', endpoint='/order/checkout', status='200').inc()
        REQUEST_DURATION.labels(method='POST', endpoint='/order/checkout').observe(time.time() - start_time)
        
        return {"status": "order placed", "orderId": order_id, "order": order_event}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing checkout: {e}")
        REQUEST_COUNT.labels(method='POST', endpoint='/order/checkout', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))
