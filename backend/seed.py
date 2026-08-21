from datetime import datetime
from app.database.connection import db
from app.auth.security import hash_password

IMAGES = {
    "Ooty": "https://images.unsplash.com/photo-1593693411515-c20261bcad6e?auto=format&fit=crop&w=1200&q=80",
    "Goa": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1200&q=80",
    "Munnar": "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1200&q=80",
    "Manali": "https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=1200&q=80",
    "Kashmir": "https://images.unsplash.com/photo-1598091383021-15ddea10925d?auto=format&fit=crop&w=1200&q=80",
    "Rajasthan": "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1200&q=80",
    "Coorg": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
    "Kerala": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1200&q=80",
}

def seed():
    for collection in [db.users, db.operators, db.packages, db.reviews]: collection.delete_many({})
    operators = [
        {"name": "WanderNest Travels", "description": "Local, human-scale journeys with thoughtful guides.", "verified": True, "rating": 4.7, "contact": "hello@wandernest.example.com"},
        {"name": "ExploreX Holidays", "description": "Comfort-first itineraries for curious travelers.", "verified": True, "rating": 4.8, "contact": "trips@explorex.example.com"},
        {"name": "BlueSky Tours", "description": "Flexible adventures with transparent inclusions.", "verified": True, "rating": 4.5, "contact": "team@bluesky.example.com"},
    ]
    operator_result = db.operators.insert_many(operators)
    operator_ids = list(operator_result.inserted_ids)
    user_result = db.users.insert_many([
        {"full_name": "WanderNest Travels", "email": "operator@example.com", "phone": "9876543210", "role": "operator", "verified": True, "password_hash": hash_password("VoyaraDemo123")},
        {"full_name": "Voyara Admin", "email": "admin@example.com", "phone": "9876543211", "role": "admin", "verified": True, "password_hash": hash_password("VoyaraAdmin123")},
    ])
    db.users.update_one({"_id": user_result.inserted_ids[0]}, {"$set": {"operator_id": str(operator_ids[0])}})
    rows = [
        ("Ooty Budget Escape", "Ooty", 9999, 2, "Nature", 4.2, 0, ["Hotel", "Sightseeing"], "Budget hotel", "Shared cab", "Breakfast", ["Sightseeing"]),
        ("Ooty Premium Holiday", "Ooty", 16999, 4, "Nature", 4.8, 1, ["Hotel", "Meals", "Transport", "Sightseeing"], "Heritage resort", "Private car", "All meals", ["Sightseeing", "Trekking"]),
        ("Ooty Family Explorer", "Ooty", 12999, 3, "Family", 4.5, 2, ["Hotel", "Breakfast", "Guide"], "Family suite", "Private car", "Breakfast", ["Sightseeing", "Food"]),
        ("Goa Budget Adventure", "Goa", 11999, 3, "Adventure", 4.2, 0, ["Stay", "Breakfast", "Kayak"], "Beach hostel", "Scooter", "Breakfast", ["Beach", "Water"]),
        ("Goa Beach Escape", "Goa", 24999, 5, "Beach", 4.6, 1, ["Boutique stay", "Breakfast", "Scooter"], "Boutique stay", "Scooter", "Breakfast", ["Beach", "Food"]),
        ("Goa Luxury Retreat", "Goa", 47999, 6, "Beach", 4.9, 2, ["Resort", "All meals", "Private car"], "Five-star resort", "Private car", "All meals", ["Beach", "Wellness"]),
        ("Munnar Nature Trip", "Munnar", 14999, 3, "Nature", 4.4, 0, ["Hotel", "Breakfast", "Guide"], "Tea estate stay", "Shared cab", "Breakfast", ["Nature", "Hiking"]),
        ("Munnar Premium Escape", "Munnar", 28900, 5, "Nature", 4.9, 1, ["Boutique stay", "All meals", "Private car"], "Plantation resort", "Private car", "All meals", ["Nature", "Hiking", "Food"]),
        ("Munnar Couple Retreat", "Munnar", 21999, 4, "Couple", 4.7, 2, ["Cottage", "Breakfast", "Sunset tour"], "Private cottage", "Private car", "Breakfast", ["Nature", "Food"]),
        ("Manali Alpine Budget", "Manali", 13999, 3, "Adventure", 4.3, 0, ["Hotel", "Breakfast", "Sightseeing"], "Mountain hotel", "Shared cab", "Breakfast", ["Hiking", "Nature"]),
        ("Manali Snowline Premium", "Manali", 32999, 6, "Adventure", 4.9, 1, ["Resort", "All meals", "Private car"], "Snowline resort", "Private car", "All meals", ["Hiking", "Adventure"]),
        ("Manali Family Trail", "Manali", 23999, 5, "Family", 4.6, 2, ["Family room", "Breakfast", "Guide"], "Family hotel", "Private car", "Breakfast", ["Nature", "Sightseeing"]),
        ("Kashmir Valley Budget", "Kashmir", 18999, 4, "Nature", 4.4, 0, ["Hotel", "Breakfast", "Shikara ride"], "Valley hotel", "Shared cab", "Breakfast", ["Nature", "Water"]),
        ("Kashmir Houseboat Escape", "Kashmir", 39999, 6, "Culture", 4.9, 1, ["Houseboat", "All meals", "Private car"], "Dal Lake houseboat", "Private car", "All meals", ["Culture", "Nature"]),
        ("Kashmir Family Explorer", "Kashmir", 27999, 5, "Family", 4.6, 2, ["Hotel", "Breakfast", "Guide"], "Family suite", "Private car", "Breakfast", ["Nature", "Sightseeing"]),
        ("Rajasthan Craft Trail", "Rajasthan", 17999, 4, "Culture", 4.4, 0, ["Heritage hotel", "Breakfast", "Craft walk"], "Heritage hotel", "Shared cab", "Breakfast", ["Culture", "Craft"]),
        ("Rajasthan Desert Table", "Rajasthan", 34999, 6, "Culture", 4.8, 1, ["Camp", "All meals", "Private car"], "Desert camp", "Private car", "All meals", ["Culture", "Food"]),
        ("Rajasthan Royal Family", "Rajasthan", 26999, 5, "Family", 4.6, 2, ["Palace hotel", "Breakfast", "Guide"], "Palace hotel", "Private car", "Breakfast", ["Culture", "Food"]),
        ("Coorg Coffee Budget", "Coorg", 10999, 3, "Nature", 4.2, 0, ["Homestay", "Breakfast", "Plantation walk"], "Coffee homestay", "Shared cab", "Breakfast", ["Nature", "Food"]),
        ("Coorg Rainforest Retreat", "Coorg", 29999, 5, "Nature", 4.8, 1, ["Resort", "All meals", "Private car"], "Rainforest resort", "Private car", "All meals", ["Nature", "Hiking"]),
        ("Coorg Family Outdoors", "Coorg", 19999, 4, "Family", 4.5, 2, ["Villa", "Breakfast", "Guide"], "Family villa", "Private car", "Breakfast", ["Nature", "Adventure"]),
        ("Kerala Backwater Budget", "Kerala", 12999, 3, "Nature", 4.3, 0, ["Homestay", "Breakfast", "Canoe ride"], "Backwater homestay", "Shared cab", "Breakfast", ["Nature", "Water"]),
        ("Kerala Coastal Comfort", "Kerala", 24999, 5, "Beach", 4.7, 1, ["Boutique stay", "Breakfast", "Houseboat"], "Coastal boutique stay", "Private car", "Breakfast", ["Beach", "Food", "Water"]),
        ("Kerala Houseboat Escape", "Kerala", 42999, 6, "Culture", 4.9, 2, ["Houseboat", "All meals", "Private car"], "Private houseboat", "Private car", "All meals", ["Culture", "Food", "Water"]),
    ]
    packages = []
    for name, destination, price, duration, category, rating, operator_index, included, accommodation, transport, meals, activities in rows:
        operator = operators[operator_index]
        packages.append({"name": name, "destination": destination, "description": f"A considered {duration}-day {category.lower()} journey through {destination}.", "price": price, "duration": duration, "category": category, "operator_id": str(operator_ids[operator_index]), "operator_name": operator["name"], "operator_verified": True, "status": "Approved", "rating": rating, "review_count": 0, "images": [IMAGES[destination]], "itinerary": [{"title": "Arrive and settle in", "description": "Meet your local host and ease into the destination."}, {"title": "A day made for you", "description": "Explore with a balance of guided time and freedom."}], "included": included, "excluded": ["Flights", "Personal expenses"], "activities": activities, "accommodation": accommodation, "transport": transport, "meals": meals, "guide": "Local guide included", "insurance": "Optional travel insurance", "cancellation_policy": "Free cancellation up to 7 days before departure.", "created_at": datetime.utcnow()})
    db.packages.insert_many(packages)
    db.users.create_index("email", unique=True)
    for field in ["destination", "category", "price", "operator_id", "rating"]: db.packages.create_index(field)
    print("Seeded 3 verified operators and 24 cross-operator packages.")

