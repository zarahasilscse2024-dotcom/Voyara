from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from app.database.connection import db, serialize

router = APIRouter(prefix="/packages", tags=["packages"])

def get_collection():
    try:
        names = db.list_collection_names()
        if "packages" in names and db.packages.count_documents({}) > 0:
            return db.packages
        if "trips" in names and db.trips.count_documents({}) > 0:
            return db.trips
        # Auto-seed if database is empty
        try:
            from seed import seed_if_empty
            seed_if_empty()
        except Exception:
            pass
    except Exception:
        pass
    return db.packages


def normalize_package(doc):
    if not doc:
        return None
    item = serialize(doc)
    if "name" not in item and "title" in item:
        item["name"] = item["title"]
    if "destination" not in item and "location" in item:
        item["destination"] = item["location"]
    if "images" not in item:
        if "image" in item:
            item["images"] = [item["image"]]
        elif "image_url" in item:
            item["images"] = [item["image_url"]]
        else:
            item["images"] = []
    return item

def package_query(destination="", category="", min_price=None, max_price=None, duration=None, operator="", min_rating=None, q=""):
    query = {"status": {"$ne": "Rejected"}}
    if destination:
        query["$or"] = [
            {"destination": {"$regex": destination, "$options": "i"}},
            {"location": {"$regex": destination, "$options": "i"}},
        ]
    if category:
        query["category"] = {"$regex": category, "$options": "i"}
    if operator:
        query["operator_name"] = {"$regex": operator, "$options": "i"}
    if min_rating is not None:
        try:
            query["rating"] = {"$gte": float(min_rating)}
        except (ValueError, TypeError):
            pass
    if min_price is not None or max_price is not None:
        price_cond = {}
        if min_price is not None:
            try:
                price_cond["$gte"] = float(min_price)
            except (ValueError, TypeError):
                pass
        if max_price is not None:
            try:
                price_cond["$lte"] = float(max_price)
            except (ValueError, TypeError):
                pass
        if price_cond:
            query["price"] = price_cond
    if duration:
        try:
            query["duration"] = {"$lte": int(duration)}
        except (ValueError, TypeError):
            pass
    if q:
        q_cond = [
            {"name": {"$regex": q, "$options": "i"}},
            {"title": {"$regex": q, "$options": "i"}},
            {"destination": {"$regex": q, "$options": "i"}},
            {"location": {"$regex": q, "$options": "i"}},
            {"category": {"$regex": q, "$options": "i"}},
            {"operator_name": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}}
        ]
        if "$or" in query:
            existing_or = query.pop("$or")
            query["$and"] = [{"$or": existing_or}, {"$or": q_cond}]
        else:
            query["$or"] = q_cond
    return query

@router.get("")
def list_packages(destination: str = "", category: str = "", min_price: float | None = None, max_price: float | None = None, duration: int | None = None, operator: str = "", min_rating: float | None = None, q: str = "", sort: str = "featured"):
    col = get_collection()
    ordering = {
        "price_low": [("price", 1)],
        "price_high": [("price", -1)],
        "rating": [("rating", -1), ("price", 1)],
        "duration": [("duration", 1)],
        "featured": [("rating", -1), ("price", 1)]
    }.get(sort, [("rating", -1), ("price", 1)])
    query = package_query(destination, category, min_price, max_price, duration, operator, min_rating, q)
    try:
        return [normalize_package(item) for item in col.find(query).sort(ordering)]
    except Exception:
        return []

@router.get("/search")
def search_packages(q: str = Query("", max_length=100)):
    col = get_collection()
    query = package_query(q=q)
    try:
        return [normalize_package(item) for item in col.find(query)]
    except Exception:
        return []

@router.get("/{package_id}")
def get_package(package_id: str):
    col = get_collection()
    item = None
    try:
        if ObjectId.is_valid(package_id):
            item = col.find_one({"_id": ObjectId(package_id)})
    except Exception:
        pass
    if not item:
        try:
            item = col.find_one({"id": package_id})
        except Exception:
            pass
    if not item or item.get("status") == "Rejected":
        raise HTTPException(404, "Package not found")
    item = normalize_package(item)
    try:
        item["reviews"] = [serialize(r) for r in db.reviews.find({"package_id": package_id}).sort("created_at", -1)]
    except Exception:
        item["reviews"] = []
    return item
