from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from app.config import MONGO_URI, DATABASE_NAME

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
db = client[DATABASE_NAME]

try:
    db.favorites.create_index([("user_id", 1), ("package_id", 1)], unique=True, name="user_package_favorite")
    db.bookings.create_index([("user_id", 1), ("created_at", -1)], name="user_bookings")
    db.bookings.create_index("package_id", name="package_bookings")
except Exception:
    pass


def check_connection():
    try:
        client.admin.command("ping")
        return True
    except ServerSelectionTimeoutError:
        return False

def serialize(document):
    if not document:
        return None
    document["id"] = str(document.pop("_id"))
    return document
