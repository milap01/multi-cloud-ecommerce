from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import psycopg2
import os
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Product Service")

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME", "ecommerce")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

@app.get("/")
def health():
    return {"status": "healthy", "service": "product"}

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/products")
def list_products():
    start_time = time.time()
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, price, description FROM products LIMIT 50;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        products = [
            {"id": r[0], "name": r[1], "price": float(r[2]), "description": r[3]} 
            for r in rows
        ]
        
        REQUEST_COUNT.labels(method='GET', endpoint='/products', status='200').inc()
        REQUEST_DURATION.labels(method='GET', endpoint='/products').observe(time.time() - start_time)
        
        return {"products": products, "count": len(products)}
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        REQUEST_COUNT.labels(method='GET', endpoint='/products', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products/{product_id}")
def get_product(product_id: int):
    start_time = time.time()
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, name, price, description FROM products WHERE id = %s;", (product_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if not row:
            REQUEST_COUNT.labels(method='GET', endpoint='/products/:id', status='404').inc()
            raise HTTPException(status_code=404, detail="Product not found")
        
        product = {"id": row[0], "name": row[1], "price": float(row[2]), "description": row[3]}
        REQUEST_COUNT.labels(method='GET', endpoint='/products/:id', status='200').inc()
        REQUEST_DURATION.labels(method='GET', endpoint='/products/:id').observe(time.time() - start_time)
        
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        REQUEST_COUNT.labels(method='GET', endpoint='/products/:id', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))
