from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from app.database.connection import db, serialize

router = APIRouter(prefix="/packages", tags=["packages"])

def package_query(destination="", category="", min_price=None, max_price=None, duration=None, operator="", min_rating=None, q=""):
    query = {"status": "Approved"}
    if destination: query["destination"] = {"$regex": destination, "$options": "i"}
    if category: query["category"] = {"$regex": category, "$options": "i"}
    if operator: query["operator_name"] = {"$regex": operator, "$options": "i"}
    if min_rating is not None: query["rating"] = {"$gte": min_rating}
    if min_price is not None or max_price is not None: query["price"] = {k: v for k, v in [("$gte", min_price), ("$lte", max_price)] if v is not None}
    if duration: query["duration"] = {"$lte": duration}
    if q: query["$or"] = [{"name": {"$regex": q, "$options": "i"}}, {"destination": {"$regex": q, "$options": "i"}}, {"category": {"$regex": q, "$options": "i"}}, {"operator_name": {"$regex": q, "$options": "i"}}]
    return query

@router.get("")
def list_packages(destination: str = "", category: str = "", min_price: float | None = None, max_price: float | None = None, duration: int | None = None, operator: str = "", min_rating: float | None = None, q: str = "", sort: str = "featured"):
    ordering = {"price_low": [("price", 1)], "price_high": [("price", -1)], "rating": [("rating", -1)], "duration": [("duration", 1)]}.get(sort, [("rating", -1)])
    return [serialize(item) for item in db.packages.find(package_query(destination, category, min_price, max_price, duration, operator, min_rating, q)).sort(ordering)]

@router.get("/search")
def search_packages(q: str = Query("", max_length=100)):
    query = package_query(q=q)
    return [serialize(item) for item in db.packages.find(query)]

@router.get("/{package_id}")
def get_package(package_id: str):
    try: item = db.packages.find_one({"_id": ObjectId(package_id)})
    except Exception: item = None
    if not item or item.get("status") != "Approved": raise HTTPException(404, "Package not found")
    item = serialize(item); item["reviews"] = [serialize(r) for r in db.reviews.find({"package_id": package_id}).sort("created_at", -1)]
    return item
