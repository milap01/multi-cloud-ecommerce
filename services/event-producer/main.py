from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from confluent_kafka import Producer
import json
import os
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Events Producer Service")

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")

producer = Producer({
    "bootstrap.servers": KAFKA_BOOTSTRAP,
    "client.id": "events-producer"
})

@app.get("/")
def health():
    return {"status": "healthy", "service": "events-producer"}

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/events/user")
def publish_user_event(event: dict):
    """Publish user activity events (login, logout, page views, etc.)"""
    start_time = time.time()
    try:
        if not event.get("userId") or not event.get("eventType"):
            REQUEST_COUNT.labels(method='POST', endpoint='/events/user', status='400').inc()
            raise HTTPException(status_code=400, detail="userId and eventType required")
        
        event["timestamp"] = int(time.time())
        
        producer.produce("user-events", value=json.dumps(event).encode("utf-8"))
        producer.flush()
        
        REQUEST_COUNT.labels(method='POST', endpoint='/events/user', status='200').inc()
        REQUEST_DURATION.labels(method='POST', endpoint='/events/user').observe(time.time() - start_time)
        
        return {"status": "event published", "topic": "user-events", "event": event}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing user event: {e}")
        REQUEST_COUNT.labels(method='POST', endpoint='/events/user', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events/analytics")
def publish_analytics_event(event: dict):
    """Publish analytics events for tracking"""
    start_time = time.time()
    try:
        event["timestamp"] = int(time.time())
        
        producer.produce("analytics-events", value=json.dumps(event).encode("utf-8"))
        producer.flush()
        
        REQUEST_COUNT.labels(method='POST', endpoint='/events/analytics', status='200').inc()
        REQUEST_DURATION.labels(method='POST', endpoint='/events/analytics').observe(time.time() - start_time)
        
        return {"status": "event published", "topic": "analytics-events", "event": event}
    except Exception as e:
        logger.error(f"Error publishing analytics event: {e}")
        REQUEST_COUNT.labels(method='POST', endpoint='/events/analytics', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events/custom")
def publish_custom_event(topic: str, event: dict):
    """Publish custom events to any topic"""
    start_time = time.time()
    try:
        if not topic:
            REQUEST_COUNT.labels(method='POST', endpoint='/events/custom', status='400').inc()
            raise HTTPException(status_code=400, detail="Topic name required")
        
        event["timestamp"] = int(time.time())
        
        producer.produce(topic, value=json.dumps(event).encode("utf-8"))
        producer.flush()
        
        REQUEST_COUNT.labels(method='POST', endpoint='/events/custom', status='200').inc()
        REQUEST_DURATION.labels(method='POST', endpoint='/events/custom').observe(time.time() - start_time)
        
        return {"status": "event published", "topic": topic, "event": event}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing custom event: {e}")
        REQUEST_COUNT.labels(method='POST', endpoint='/events/custom', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))
