from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from opensearchpy import OpenSearch
import os
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Search Service")

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

OPENSEARCH_ENDPOINT = os.getenv("OPENSEARCH_ENDPOINT", "localhost")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", "443"))
USE_SSL = os.getenv("OPENSEARCH_USE_SSL", "true").lower() == "true"

# OpenSearch client
opensearch_client = OpenSearch(
    hosts=[{"host": OPENSEARCH_ENDPOINT, "port": OPENSEARCH_PORT}],
    http_compress=True,
    use_ssl=USE_SSL,
    verify_certs=False,  # In production, set to True with proper certificates
    ssl_assert_hostname=False,
    ssl_show_warn=False
)

@app.get("/")
def health():
    return {"status": "healthy", "service": "search"}

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/search")
def search(q: str):
    start_time = time.time()
    try:
        if not q or len(q.strip()) == 0:
            REQUEST_COUNT.labels(method='GET', endpoint='/search', status='400').inc()
            raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
        
        # Search in OpenSearch
        try:
            search_body = {
                "query": {
                    "multi_match": {
                        "query": q,
                        "fields": ["name^2", "description"]
                    }
                }
            }
            
            response = opensearch_client.search(
                index="products",
                body=search_body
            )
            
            results = [
                {
                    "id": hit["_source"].get("id"),
                    "name": hit["_source"].get("name"),
                    "price": hit["_source"].get("price"),
                    "description": hit["_source"].get("description"),
                    "score": hit["_score"]
                }
                for hit in response["hits"]["hits"]
            ]
            
        except Exception as os_error:
            logger.warning(f"OpenSearch error, falling back to mock data: {os_error}")
            # Fallback to mock data if OpenSearch is not available
            mock_products = [
                {"id": 1, "name": "Laptop", "price": 999.99, "description": "High-performance laptop"},
                {"id": 2, "name": "Mouse", "price": 29.99, "description": "Wireless mouse"},
                {"id": 3, "name": "Keyboard", "price": 79.99, "description": "Mechanical keyboard"},
                {"id": 4, "name": "Monitor", "price": 299.99, "description": "27-inch 4K monitor"},
                {"id": 5, "name": "Headphones", "price": 149.99, "description": "Noise-cancelling headphones"}
            ]
            results = [p for p in mock_products if q.lower() in p["name"].lower() or q.lower() in p["description"].lower()]
        
        REQUEST_COUNT.labels(method='GET', endpoint='/search', status='200').inc()
        REQUEST_DURATION.labels(method='GET', endpoint='/search').observe(time.time() - start_time)
        
        return {"query": q, "results": results, "count": len(results)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching: {e}")
        REQUEST_COUNT.labels(method='GET', endpoint='/search', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/index")
def index_product(product: dict):
    """Index a product in OpenSearch"""
    start_time = time.time()
    try:
        if not product.get("id"):
            raise HTTPException(status_code=400, detail="Product ID required")
        
        opensearch_client.index(
            index="products",
            id=product["id"],
            body=product
        )
        
        REQUEST_COUNT.labels(method='POST', endpoint='/search/index', status='200').inc()
        REQUEST_DURATION.labels(method='POST', endpoint='/search/index').observe(time.time() - start_time)
        
        return {"message": "Product indexed", "productId": product["id"]}
    except Exception as e:
        logger.error(f"Error indexing product: {e}")
        REQUEST_COUNT.labels(method='POST', endpoint='/search/index', status='500').inc()
        raise HTTPException(status_code=500, detail=str(e))