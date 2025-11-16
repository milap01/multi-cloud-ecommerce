from fastapi import FastAPI
import httpx

app = FastAPI(title="Frontend Service")

PRODUCT_SERVICE_URL = "http://product-service:8000"
CART_SERVICE_URL = "http://cart-service:8000"
ORDER_SERVICE_URL = "http://order-service:8000"

@app.get("/")
def health():
    return {"status": "frontend ok"}

@app.get("/products")
async def get_products():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{PRODUCT_SERVICE_URL}/products")
        return r.json()

@app.post("/cart/add")
async def add_to_cart(item: dict):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{CART_SERVICE_URL}/cart/add", json=item)
        return r.json()

@app.post("/order/checkout")
async def checkout(order: dict):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{ORDER_SERVICE_URL}/order/checkout", json=order)
        return r.json()
