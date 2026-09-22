from datetime import datetime
import hmac
import hashlib
from fastapi import APIRouter, Depends, HTTPException
from app.config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
from bson import ObjectId
from app.database.connection import db, serialize
from app.auth.security import current_user
from app.schemas.models import ReviewRequest, BookingRequest, PreferenceRequest, PaymentOrderRequest, PaymentVerifyRequest

router = APIRouter(tags=["features"])

@router.get("/favorites")
def favorites(user=Depends(current_user)):
    ids = [f["package_id"] for f in db.favorites.find({"user_id": user["id"]})]
    valid_ids = [ObjectId(item) for item in ids if ObjectId.is_valid(item)]
    return [serialize(p) for p in db.packages.find({"_id": {"$in": valid_ids}})]

@router.post("/favorites/{package_id}")
def add_favorite(package_id: str, user=Depends(current_user)):
    if not ObjectId.is_valid(package_id): raise HTTPException(422, "Invalid package id")
    if not db.packages.find_one({"_id": ObjectId(package_id)}): raise HTTPException(404, "Package not found")
    db.favorites.update_one({"user_id": user["id"], "package_id": package_id}, {"$set": {"user_id": user["id"], "package_id": package_id}}, upsert=True); return {"saved": True}

@router.delete("/favorites/{package_id}")
def remove_favorite(package_id: str, user=Depends(current_user)):
    if not ObjectId.is_valid(package_id): raise HTTPException(422, "Invalid package id")
    db.favorites.delete_one({"user_id": user["id"], "package_id": package_id}); return {"saved": False}

@router.post("/reviews")
def add_review(data: ReviewRequest, user=Depends(current_user)):
    booking = db.bookings.find_one({"package_id": data.package_id, "user_id": user["id"], "status": {"$in": ["Enquiry received", "Confirmed"]}})
    if not booking: raise HTTPException(403, "Complete a booking enquiry before reviewing this package")
    if db.reviews.find_one({"package_id": data.package_id, "user_id": user["id"]}): raise HTTPException(409, "You have already reviewed this package")
    review = {**data.model_dump(), "user_id": user["id"], "reviewer": user["full_name"], "created_at": datetime.utcnow()}; db.reviews.insert_one(review)
    ratings = [r["rating"] for r in db.reviews.find({"package_id": data.package_id})]
    db.packages.update_one({"_id": ObjectId(data.package_id)}, {"$set": {"rating": round(sum(ratings) / len(ratings), 1), "review_count": len(ratings)}})
    return review

@router.post("/bookings")
def booking(data: BookingRequest, user=Depends(current_user)):
    if data.travel_date <= datetime.utcnow().date(): raise HTTPException(422, "Travel date must be in the future")
    package = db.packages.find_one({"_id": ObjectId(data.package_id), "status": "Approved"})
    if not package: raise HTTPException(404, "Package is unavailable")
    item = {**data.model_dump(mode="json"), "user_id": user["id"], "package_name": package["name"], "destination": package["destination"], "operator_name": package.get("operator_name", ""), "unit_price": package["price"], "total_amount": package["price"] * data.travelers, "payment_status": "PENDING", "status": "Enquiry received", "created_at": datetime.utcnow()}; result = db.bookings.insert_one(item); item["_id"] = result.inserted_id
    return serialize(item)

@router.get("/bookings")
def bookings(user=Depends(current_user)):
    return [serialize(item) for item in db.bookings.find({"user_id": user["id"]}).sort("created_at", -1)]

@router.post("/payments/order")
def payment_order(data: PaymentOrderRequest, user=Depends(current_user)):
    booking = db.bookings.find_one({"_id": ObjectId(data.booking_id), "user_id": user["id"]})
    if not booking: raise HTTPException(404, "Booking not found")
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET: raise HTTPException(503, "Payment provider is not configured")
    try:
        import razorpay
        order = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)).order.create({"amount": int(booking["total_amount"] * 100), "currency": "INR", "receipt": data.booking_id})
    except Exception:
        raise HTTPException(503, "Unable to create payment order")
    db.bookings.update_one({"_id": booking["_id"]}, {"$set": {"razorpay_order_id": order["id"]}})
    return {"key_id": RAZORPAY_KEY_ID, "order_id": order["id"], "amount": order["amount"], "currency": "INR"}

@router.post("/payments/verify")
def payment_verify(data: PaymentVerifyRequest, user=Depends(current_user)):
    booking = db.bookings.find_one({"_id": ObjectId(data.booking_id), "user_id": user["id"], "razorpay_order_id": data.razorpay_order_id})
    if not booking: raise HTTPException(404, "Booking not found")
    signature = hmac.new(RAZORPAY_KEY_SECRET.encode(), f"{data.razorpay_order_id}|{data.razorpay_payment_id}".encode(), hashlib.sha256).hexdigest()
    if not RAZORPAY_KEY_SECRET or not hmac.compare_digest(signature, data.razorpay_signature): raise HTTPException(400, "Payment verification failed")
    db.bookings.update_one({"_id": booking["_id"]}, {"$set": {"payment_status": "PAID", "payment_id": data.razorpay_payment_id, "status": "Confirmed"}})
    return {"payment_status": "PAID", "status": "Confirmed"}

@router.post("/recommendations")
def recommendations(data: PreferenceRequest, user=Depends(current_user)):
    scored = []
    for package in db.packages.find({"status": "Approved"}):
        score = 0; reasons = []; price = package["price"]
        in_range = (not data.budget_min or price >= data.budget_min) and (not data.budget_max or price <= data.budget_max) and price <= data.budget
        if in_range: score += 30; reasons.append("fits your budget")
        elif price <= data.budget: score += 15
        if not data.destination or data.destination.lower() in package["destination"].lower(): score += 20; reasons.append("matches your destination")
        if abs(package["duration"] - data.duration) <= 2: score += 15; reasons.append("matches your trip length")
        if data.travel_type and data.travel_type.lower() in package.get("category", "").lower(): score += 10; reasons.append("matches your travel style")
        if set(i.lower() for i in data.interests) & set(a.lower() for a in package.get("activities", [])): score += 20; reasons.append("matches your interests")
        score += min(package.get("rating", 0), 5)
        package = serialize(package); package["match_score"] = score; package["reason"] = " and ".join(reasons[:2]).capitalize() or "highly rated by Voyara travelers"; scored.append(package)
    return sorted(scored, key=lambda p: p["match_score"], reverse=True)[:6]

@router.post("/sos")
def sos(payload: dict, user=Depends(current_user)):
    item = {"user_id": user["id"], "location": payload.get("location"), "created_at": datetime.utcnow(), "status": "Recorded for support"}; result = db.sos_events.insert_one(item); item["_id"] = result.inserted_id
    return {"event": serialize(item), "message": "Your SOS event was recorded. Contact local emergency services directly if you are in immediate danger."}
