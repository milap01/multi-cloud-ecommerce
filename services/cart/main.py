from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from confluent_kafka import Producer
import boto3
from boto3.dynamodb.conditions import Attr
import os
import logging
import time
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cart Service")

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

TABLE_NAME = os.getenv("DYNAMODB_TABLE", "mce-cart-local")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")  # Important!

# Configure DynamoDB client
dynamodb_config = {
    "region_name": AWS_REGION
}

# Add endpoint_url if DYNAMODB_ENDPOINT is set (for local testing)
if DYNAMODB_ENDPOINT:
    logger.info(f"Using local DynamoDB at {DYNAMODB_ENDPOINT}")
    dynamodb_config["endpoint_url"] = DYNAMODB_ENDPOINT
    dynamodb_config["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID", "test")
    dynamodb_config["aws_secret_access_key"] = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
else:
    logger.info("Using AWS DynamoDB")

dynamodb = boto3.resource("dynamodb", **dynamodb_config)
table = dynamodb.Table(TABLE_NAME)

# Kafka producer
try:
    producer = Producer({
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "client.id": "cart-service",
        "security.protocol": "SSL"
    })
    logger.info(f"Kafka producer initialized with {KAFKA_BOOTSTRAP}")
except Exception as e:
    logger.warning(f"Kafka producer initialization failed: {e}")
    producer = None

@app.get("/")
def health():
    return {"status": "healthy", "service": "cart"}

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/cart/add")
def add_item(item: dict):
    start_time = time.time()
    try:
        if not item.get("userId") or not item.get("productId"):
            REQUEST_COUNT.labels(method='POST', endpoint='/cart/add', status='400').inc()
            raise HTTPException(status_code=400, detail="userId and productId required")
        
        cart_item = {
            "cartId": f"{item['userId']}#{item['productId']}",
            "userId": item["userId"],
            "productId": str(item["productId"]),
            "quantity": int(item.get("quantity", 1)),
            "timestamp": int(time.time())
        }
        
        table.put_item(Item=cart_item)
        logger.info(f"Added item to cart: {cart_item}")
        
        # Publish cart event to Kafka
        if producer:
            event = {
                "eventType": "cart_item_added",
                "userId": item["userId"],
                "productId": item["productId"],
                "quantity": item.get("quantity", 1),
                "timestamp": int(time.time())
            }
            try:
                producer.produce("cart-events", value=json.dumps(event).encode("utf-8"))
                producer.flush()
            except Exception as kafka_error:
                logger.warning(f"Kafka publish failed: {kafka_error}")
        
        REQUEST_COUNT.labels(method='POST', endpoint='/cart/add', status='200').inc()
        REQUEST_DURATION.labels(method='POST', endpoint='/cart/add').observe(time.time() - start_time)
        
        return {"message": "Item added to cart", "item": cart_item}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        REQUEST_COUNT.labels(method='POST', endpoint='/cart/add', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cart/{user_id}")
def get_cart(user_id: str):
    start_time = time.time()
    try:
        response = table.scan(
            FilterExpression=Attr('userId').eq(user_id)
        )
        items = response.get("Items", [])
        
        logger.info(f"Retrieved {len(items)} items for user {user_id}")
        
        REQUEST_COUNT.labels(method='GET', endpoint='/cart/:userId', status='200').inc()
        REQUEST_DURATION.labels(method='GET', endpoint='/cart/:userId').observe(time.time() - start_time)
        
        return {"userId": user_id, "items": items, "count": len(items)}
    except Exception as e:
        logger.error(f"Error fetching cart for {user_id}: {e}")
        REQUEST_COUNT.labels(method='GET', endpoint='/cart/:userId', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/cart/{user_id}/{product_id}")
def remove_item(user_id: str, product_id: str):
    start_time = time.time()
    try:
        cart_id = f"{user_id}#{product_id}"
        table.delete_item(Key={"cartId": cart_id})
        
        logger.info(f"Removed item {cart_id} from cart")
        
        REQUEST_COUNT.labels(method='DELETE', endpoint='/cart/:userId/:productId', status='200').inc()
        REQUEST_DURATION.labels(method='DELETE', endpoint='/cart/:userId/:productId').observe(time.time() - start_time)
        
        return {"message": "Item removed from cart", "cartId": cart_id}
    except Exception as e:
        logger.error(f"Error removing item: {e}")
        REQUEST_COUNT.labels(method='DELETE', endpoint='/cart/:userId/:productId', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))
# docker run -d \
#   --name cart-service \
#   --network mce-network \
#   -p 8002:8000 \
#   -e DYNAMODB_TABLE=mce-cart-local \
#   -e AWS_REGION=us-east-1 \
#   -e AWS_ACCESS_KEY_ID=test \
#   -e AWS_SECRET_ACCESS_KEY=test \
#   -e DYNAMODB_ENDPOINT=http://dynamodb-local:8000 \
#   -e KAFKA_BOOTSTRAP=kafka:9092 \
#   mce-cart:latest        raise HTTPException(status_code=500, detail=str(e))


