from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt, JWTError
from bson import ObjectId
from app.config import JWT_SECRET, JWT_ALGORITHM
from app.schemas.models import RegisterRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, ProfileUpdateRequest
from app.database.connection import db, serialize
from app.auth.security import hash_password, verify_password, create_token, current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(data: RegisterRequest):
    if data.password != data.confirm_password: raise HTTPException(422, "Passwords do not match")
    if data.role != "traveler": raise HTTPException(403, "Public registration is limited to travelers")
    if db.users.find_one({"email": data.email.lower()}): raise HTTPException(409, "An account with this email already exists")
    user = {"full_name": data.full_name, "email": data.email.lower(), "phone": data.phone, "password_hash": hash_password(data.password), "role": "traveler", "created_at": datetime.utcnow()}
    result = db.users.insert_one(user); user["_id"] = result.inserted_id
    return {"token": create_token(user), "user": serialize(user)}

@router.post("/login")
def login(data: LoginRequest):
    user = db.users.find_one({"email": data.email.lower()})
    if not user or not verify_password(data.password, user["password_hash"]): raise HTTPException(401, "Invalid email or password")
    if user.get("active", True) is False: raise HTTPException(403, "This account is inactive")
    requested_role = {"tourist": "traveler", "tour_operator": "operator"}.get(data.role, data.role)
    if requested_role != user["role"]: raise HTTPException(403, "This account does not have the selected role")
    return {"token": create_token(user), "user": serialize(user)}

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    user = db.users.find_one({"email": data.email.lower()})
    response = {"message": "If that email is registered, a reset request is ready."}
    if user:
        token = jwt.encode({"sub": str(user["_id"]), "purpose": "password_reset", "exp": datetime.now(timezone.utc) + timedelta(minutes=15)}, JWT_SECRET, algorithm=JWT_ALGORITHM)
        response["development_reset_token"] = token
        response["development_note"] = "Email delivery is not configured. Use this development token to continue."
    return response

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest):
    if data.password != data.confirm_password:
        raise HTTPException(422, "Passwords do not match")
    try:
        payload = jwt.decode(data.token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("purpose") != "password_reset": raise JWTError()
        user_id = ObjectId(payload["sub"])
    except (JWTError, ValueError, TypeError):
        raise HTTPException(400, "Reset link is invalid or expired")
    result = db.users.update_one({"_id": user_id}, {"$set": {"password_hash": hash_password(data.password)}})
    if not result.matched_count: raise HTTPException(400, "Reset link is invalid or expired")
    return {"message": "Password updated. You can now log in."}

@router.get("/me")
def me(user=Depends(current_user)): return user

@router.patch("/me")
def update_me(data: ProfileUpdateRequest, user=Depends(current_user)):
    db.users.update_one({"_id": ObjectId(user["id"])}, {"$set": {"full_name": data.full_name, "phone": data.phone}})
    updated = db.users.find_one({"_id": ObjectId(user["id"])})
    return serialize(updated)
