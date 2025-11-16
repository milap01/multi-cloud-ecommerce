from fastapi import FastAPI
import boto3
import os

app = FastAPI(title="Cart Service")

TABLE_NAME = os.getenv("CART_TABLE", "cart-table")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

@app.post("/cart/add")
def add_item(item: dict):
    table.put_item(Item=item)
    return {"message": "added", "item": item}

@app.get("/cart/{user_id}")
def get_cart(user_id: str):
    res = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("user_id").eq(user_id)
    )
    return res.get("Items", [])
