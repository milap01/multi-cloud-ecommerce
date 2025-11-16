from fastapi import FastAPI

app = FastAPI(title="Search Service")

# Demo search index
PRODUCTS = [
    {"id": 1, "name": "Laptop"},
    {"id": 2, "name": "Phone"},
    {"id": 3, "name": "Headphones"}
]

@app.get("/search")
def search(q: str):
    results = [p for p in PRODUCTS if q.lower() in p["name"].lower()]
    return {"results": results}
