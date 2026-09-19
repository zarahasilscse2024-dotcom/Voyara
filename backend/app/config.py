import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "voyara")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-change-this-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def _get_allowed_origins() -> list[str]:
    defaults = [
        "https://voyara-h7fj.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    raw = os.getenv("FRONTEND_ORIGIN", "")
    origins = list(defaults)
    if raw:
        for item in raw.split(","):
            cleaned = item.strip().rstrip("/")
            if cleaned and cleaned not in origins:
                origins.append(cleaned)
    return origins

ALLOWED_ORIGINS = _get_allowed_origins()
FRONTEND_ORIGIN = ALLOWED_ORIGINS[0]

AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
AI_TIMEOUT_SECONDS = float(os.getenv("AI_TIMEOUT_SECONDS", "20"))
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
