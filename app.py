from fastapi import FastAPI
from fastapi import Request, Response, HTTPException, status
from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional
from dotenv import dotenv_values

app = FastAPI()
config = dotenv_values(".env")


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["MONGODB_URL"])
    app.database = app.mongodb_client[config["MONGODB_DB"]]


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


# Pydantic model for data validation
class Item(BaseModel):
    item_name: str = Field(...)
    placed_at: str = Field(...)
    use_by: str = Field(...)
    price: Optional[float] = None
    quantity: Optional[float] = None
    bought_on:  Optional[str] = None
    category: str = Field(...)
    status: str = Field(...)

    class Config:
        allow_population_by_field_name = True


# Create a new item
@app.post("/items/", status_code=status.HTTP_201_CREATED, response_model=None)
async def create_item(request: Request, item: Item):
    encoded_item = dict(item)
    new_item = request.app.database["Inventory"].insert_one(encoded_item)
    created_item = request.app.database["Inventory"].find_one(
        {"_id": new_item.inserted_id}
    )
    created_item["id"] = str(created_item["_id"])
    created_item.pop("_id")
    return created_item


# Get an item by ID
@app.get("/items/{item_id}", status_code=status.HTTP_200_OK, response_model=None)
async def read_item(request: Request, item_id: str):
    if (
        item := request.app.database["Inventory"].find_one({"_id": ObjectId(item_id)})
    ) is not None:
        item["id"] = str(item["_id"])
        item.pop("_id")
        return item
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Item with ID {item_id} not found",
    )


# API to get all items
@app.get("/", status_code=status.HTTP_200_OK, response_model=None)
async def list_items(request: Request):
    pipeline = [
        {
            "$project": {
                "id": {"$toString": "$_id"},
                "_id": 0,
                "item_name": 1,
                "placed_at": 1,
                "use_by": 1,
                "price": 1,
                "quantity": 1,
                "bought_on": 1,
                "category": 1,
                "status": 1,
            }
        }
    ]
    items = list(request.app.database["Inventory"].aggregate(pipeline))
    return items


# Update an item by ID
@app.put("/items/{item_id}", status_code=status.HTTP_200_OK, response_model=None)
async def update_item(request: Request, item_id: str, item: Item):
    item_dict = {k: v for k, v in item.dict().items() if v is not None}
    if len(item_dict) >= 1:
        update_result = request.app.database["Inventory"].update_one(
            {"_id": ObjectId(item_id)}, {"$set": item_dict}
        )
    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail=f"Item with ID {item_id} did not change",
        )

    if (
        existing_item := request.app.database["Inventory"].find_one(
            {"_id": ObjectId(item_id)}
        )
    ) is not None:
        existing_item["id"] = str(existing_item["_id"])
        existing_item.pop("_id")
        return existing_item

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Item with ID {item_id} not found",
    )


# Delete an item by ID
@app.delete("/items/{item_id}")
async def delete_item(item_id: str, request: Request, response: Response):
    delete_response = request.app.database["Inventory"].delete_one(
        {"_id": ObjectId(item_id)}
    )
    if delete_response.deleted_count == 1:
        response.body = {"message": "Item deleted successfully"}
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Book with ID {item_id} not found",
    )
