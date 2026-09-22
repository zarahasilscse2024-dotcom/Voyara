from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import ALLOWED_ORIGINS, GOOGLE_MAPS_API_KEY
from app.database.connection import check_connection
from app.auth.security import current_user
from app.schemas.models import ProfileUpdateRequest
from app.routes.auth import update_me
from app.routes import auth, packages, features, management, chat

app = FastAPI(title="Voyara API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(packages.router, prefix="/api")
app.include_router(features.router, prefix="/api")
app.include_router(management.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

@app.on_event("startup")
def startup_event():
    try:
        from seed import seed_if_empty
        seed_if_empty()
    except Exception:
        pass

@app.get("/api/me", tags=["auth"])
def api_me(user=Depends(current_user)):
    return user

@app.patch("/api/me", tags=["auth"])
def api_update_me(data: ProfileUpdateRequest, user=Depends(current_user)):
    return update_me(data, user)

@app.get("/")
def root():
    return {
        "service": "Voyara API",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health",
    }

@app.get("/health")
@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "database": "connected" if check_connection() else "unavailable",
        "service": "Voyara API",
    }

@app.get("/api/maps/config")
def maps_config():
    return {
        "configured": bool(GOOGLE_MAPS_API_KEY),
        "message": "Google Maps is configured." if GOOGLE_MAPS_API_KEY else "Google Maps API key is not configured for this environment.",
    }

