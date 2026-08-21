from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from app.database.connection import db, serialize
from app.auth.security import current_user, require_roles
from app.schemas.models import PackageRequest

router = APIRouter(tags=["management"])

@router.post("/operator/packages")
def create_package(data: PackageRequest, user=Depends(require_roles("operator"))):
    item = {**data.model_dump(), "operator_id": user.get("operator_id", user["id"]), "operator_name": user["full_name"], "operator_verified": True, "status": "Pending", "rating": 0, "review_count": 0, "created_at": datetime.utcnow()}
    result = db.packages.insert_one(item); item["_id"] = result.inserted_id
    return serialize(item)

@router.get("/operator/packages")
def operator_packages(user=Depends(require_roles("operator"))):
    return [serialize(p) for p in db.packages.find({"operator_id": user.get("operator_id", user["id"])})]

@router.get("/operator/bookings")
def operator_bookings(user=Depends(require_roles("operator"))):
    package_ids = [p["id"] for p in [serialize(item) for item in db.packages.find({"operator_id": user.get("operator_id", user["id"])})]]
    return [serialize(item) for item in db.bookings.find({"package_id": {"$in": package_ids}}).sort("created_at", -1)]

@router.put("/operator/packages/{package_id}")
def update_operator_package(package_id: str, data: PackageRequest, user=Depends(require_roles("operator"))):
    result = db.packages.update_one({"_id": ObjectId(package_id), "operator_id": user.get("operator_id", user["id"])}, {"$set": {**data.model_dump(), "status": "Pending"}})
    if not result.matched_count: raise HTTPException(404, "Package not found")
    return {"message": "Package updated and submitted for approval"}

@router.delete("/operator/packages/{package_id}")
def delete_operator_package(package_id: str, user=Depends(require_roles("operator"))):
    result = db.packages.delete_one({"_id": ObjectId(package_id), "operator_id": user.get("operator_id", user["id"])})
    if not result.deleted_count: raise HTTPException(404, "Package not found")
    return {"deleted": True}

@router.get("/admin/users")
def admin_users(user=Depends(require_roles("admin"))): return [serialize(x) for x in db.users.find({}, {"password_hash": 0})]

@router.patch("/admin/users/{user_id}")
def update_user_status(user_id: str, active: bool, user=Depends(require_roles("admin"))):
    result = db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"active": active}})
    if not result.matched_count: raise HTTPException(404, "User not found")
    return {"active": active}

@router.get("/admin/operators")
def admin_operators(user=Depends(require_roles("admin"))): return [serialize(x) for x in db.operators.find()]

@router.patch("/admin/operators/{operator_id}")
def verify_operator(operator_id: str, verified: bool, user=Depends(require_roles("admin"))):
    result = db.operators.update_one({"_id": ObjectId(operator_id)}, {"$set": {"verified": verified}})
    if not result.matched_count: raise HTTPException(404, "Operator not found")
    db.packages.update_many({"operator_id": operator_id}, {"$set": {"operator_verified": verified}})
    return {"verified": verified}

@router.get("/admin/packages")
def admin_packages(user=Depends(require_roles("admin"))): return [serialize(x) for x in db.packages.find()]

@router.patch("/admin/packages/{package_id}")
def review_package(package_id: str, status: str, user=Depends(require_roles("admin"))):
    if status not in ["Approved", "Rejected", "Pending"]: raise HTTPException(422, "Invalid package status")
    result = db.packages.update_one({"_id": ObjectId(package_id)}, {"$set": {"status": status}})
    if not result.matched_count: raise HTTPException(404, "Package not found")
    return {"status": status}

@router.get("/admin/sos")
def admin_sos(user=Depends(require_roles("admin"))): return [serialize(x) for x in db.sos_events.find().sort("created_at", -1)]

@router.get("/admin/stats")
def admin_stats(user=Depends(require_roles("admin"))):
    return {"tourists": db.users.count_documents({"role": "traveler"}), "operators": db.users.count_documents({"role": "operator"}), "verified_operators": db.operators.count_documents({"verified": True}), "packages": db.packages.count_documents({}), "approved_packages": db.packages.count_documents({"status": "Approved"}), "pending_packages": db.packages.count_documents({"status": "Pending"}), "bookings": db.bookings.count_documents({}), "sos_alerts": db.sos_events.count_documents({})}

@router.get("/admin/bookings")
def admin_bookings(user=Depends(require_roles("admin"))): return [serialize(x) for x in db.bookings.find().sort("created_at", -1)]

@router.get("/admin/reviews")
def admin_reviews(user=Depends(require_roles("admin"))): return [serialize(x) for x in db.reviews.find().sort("created_at", -1)]

@router.delete("/admin/reviews/{review_id}")
def delete_review(review_id: str, user=Depends(require_roles("admin"))):
    result = db.reviews.delete_one({"_id": ObjectId(review_id)})
    if not result.deleted_count: raise HTTPException(404, "Review not found")
    return {"deleted": True}
