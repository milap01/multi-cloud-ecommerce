from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import httpx
import os
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Frontend Service")

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

# Service URLs from environment
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product.mce.svc.cluster.local")
CART_SERVICE_URL = os.getenv("CART_SERVICE_URL", "http://cart.mce.svc.cluster.local")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order.mce.svc.cluster.local")
SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL", "http://search.mce.svc.cluster.local")

app = FastAPI(title="Frontend Service")

# FIX: Read from Environment Variables (injected by Kubernetes)
# Fallback to defaults only if env vars are missing
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8000")
CART_SERVICE_URL = os.getenv("CART_SERVICE_URL", "http://cart-service:8000")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8000")

@app.get("/")
def health():
    return {"status": "healthy", "service": "frontend"}

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/products")
async def get_products():
    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{PRODUCT_SERVICE_URL}/products")
            response.raise_for_status()
            
            REQUEST_COUNT.labels(method='GET', endpoint='/products', status='200').inc()
            REQUEST_DURATION.labels(method='GET', endpoint='/products').observe(time.time() - start_time)
            
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error fetching products: {e}")
        REQUEST_COUNT.labels(method='GET', endpoint='/products', status='500').inc()
        raise HTTPException(status_code=500, detail=f"Product service error: {str(e)}")

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
            response.raise_for_status()
            
            REQUEST_COUNT.labels(method='GET', endpoint='/products/:id', status='200').inc()
            REQUEST_DURATION.labels(method='GET', endpoint='/products/:id').observe(time.time() - start_time)
            
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            REQUEST_COUNT.labels(method='GET', endpoint='/products/:id', status='404').inc()
            raise HTTPException(status_code=404, detail="Product not found")
        raise
    except httpx.HTTPError as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        REQUEST_COUNT.labels(method='GET', endpoint='/products/:id', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))
    async with httpx.AsyncClient() as client:
        # Use the variable, which now contains the correct K8s URL
        r = await client.get(f"{PRODUCT_SERVICE_URL}/products")
        return r.json()

@app.post("/cart/add")
async def add_to_cart(item: dict):
    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{CART_SERVICE_URL}/cart/add", json=item)
            response.raise_for_status()
            
            REQUEST_COUNT.labels(method='POST', endpoint='/cart/add', status='200').inc()
            REQUEST_DURATION.labels(method='POST', endpoint='/cart/add').observe(time.time() - start_time)
            
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error adding to cart: {e}")
        REQUEST_COUNT.labels(method='POST', endpoint='/cart/add', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cart/{user_id}")
async def get_cart(user_id: str):
    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{CART_SERVICE_URL}/cart/{user_id}")
            response.raise_for_status()
            
            REQUEST_COUNT.labels(method='GET', endpoint='/cart/:userId', status='200').inc()
            REQUEST_DURATION.labels(method='GET', endpoint='/cart/:userId').observe(time.time() - start_time)
            
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error fetching cart: {e}")
        REQUEST_COUNT.labels(method='GET', endpoint='/cart/:userId', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/order/checkout")
async def checkout(order: dict):
    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{ORDER_SERVICE_URL}/order/checkout", json=order)
            response.raise_for_status()
            
            REQUEST_COUNT.labels(method='POST', endpoint='/order/checkout', status='200').inc()
            REQUEST_DURATION.labels(method='POST', endpoint='/order/checkout').observe(time.time() - start_time)
            
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error during checkout: {e}")
        REQUEST_COUNT.labels(method='POST', endpoint='/order/checkout', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search(q: str):
    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{SEARCH_SERVICE_URL}/search?q={q}")
            response.raise_for_status()
            
            REQUEST_COUNT.labels(method='GET', endpoint='/search', status='200').inc()
            REQUEST_DURATION.labels(method='GET', endpoint='/search').observe(time.time() - start_time)
            
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error searching: {e}")
        REQUEST_COUNT.labels(method='GET', endpoint='/search', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{ORDER_SERVICE_URL}/order/checkout", json=order)
        return r.json()

@app.post("/products", status_code=201)
async def create_product(product: dict):
    start_time = time.time()
    try:
        # Forward the request to the Product Service
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{PRODUCT_SERVICE_URL}/products", json=product)
            response.raise_for_status()
            
            REQUEST_COUNT.labels(method='POST', endpoint='/products', status='201').inc()
            REQUEST_DURATION.labels(method='POST', endpoint='/products').observe(time.time() - start_time)
            
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Error creating product: {e}")
        REQUEST_COUNT.labels(method='POST', endpoint='/products', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))