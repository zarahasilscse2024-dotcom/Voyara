from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId
from app.config import JWT_SECRET, JWT_ALGORITHM
from app.database.connection import db, serialize

import bcrypt
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    try:
        pwd_bytes = plain.encode('utf-8')[:72]
        hashed_bytes = hashed.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False

def create_token(user):
    payload = {"sub": str(user["_id"]), "role": user["role"], "exp": datetime.now(timezone.utc) + timedelta(days=7)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def current_user(token: str = Depends(oauth2_scheme)):
    if not token: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = db.users.find_one({"_id": ObjectId(payload["sub"])})
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Session expired")
    if not user: raise HTTPException(status_code=401, detail="User not found")
    if user.get("active", True) is False: raise HTTPException(status_code=403, detail="This account is inactive")
    return serialize(user)

def require_roles(*roles):
    def dependency(user=Depends(current_user)):
        if user["role"] not in roles: raise HTTPException(status_code=403, detail="You are not authorized")
        return user
    return dependency
