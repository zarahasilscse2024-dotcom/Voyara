# Voyara

Voyara is a full-stack travel discovery and comparison platform. Travelers can explore operator packages, save favorites, receive rule-based recommendations, ask the travel assistant questions, record SOS events, and submit booking enquiries.

## Stack
React + Vite + React Router + Axios, FastAPI + Uvicorn + Pydantic + JWT, and MongoDB through PyMongo.

## Prerequisites
Install Node.js 20+, Python 3.11+, and MongoDB Community Server (or use a MongoDB Atlas URI). MongoDB must be running for registration, packages, and all persistence flows.

## Windows setup

```powershell
cd C:\Users\lenovo\Desktop\project
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
python backend\seed.py
cd frontend
npm install
Copy-Item .env.example .env
```

Set a real `MONGO_URI` and a long random `JWT_SECRET` in `backend/.env`. The frontend uses `VITE_API_URL=http://localhost:8000/api`.

Run two PowerShell windows:

```powershell
cd C:\Users\lenovo\Desktop\project; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --app-dir backend --reload --port 8000
cd C:\Users\lenovo\Desktop\project\frontend; npm run dev
```

Open http://localhost:5173. API health is http://localhost:8000/api/health.

## Demo accounts

`operator@example.com` / `VoyaraDemo123` and `admin@example.com` / `VoyaraAdmin123`. Public registration creates traveler accounts only. Demo passwords are seed data, not application source credentials.

## Password reset in development

`POST /api/auth/forgot-password` checks the registered email and returns a short-lived `development_reset_token` in the response because email delivery is not configured locally. The React Forgot Password screen consumes that token and calls `POST /api/auth/reset-password`. Production should replace this response with a backend email provider; no plaintext password or permanent reset token is stored.

## API overview

Health, auth, packages/search/filtering, favorites, reviews, recommendations, SOS, bookings, operator packages, and admin package/user/operator/SOS routes are available below `/api`. Operator and admin routes enforce roles on the backend as well as navigation. Compare is a frontend shortlist backed by actual package response data.

The seed creates three verified operator documents and 24 approved packages, including three each for Kerala, Ooty, Goa, Munnar, Manali, Kashmir, Rajasthan, and Coorg. Re-run `python backend\seed.py` whenever you want to restore that demo dataset.

Authenticated users can edit their name and phone at `/profile` and view their own booking enquiries at `/bookings`. Booking totals are calculated from the approved MongoDB package price on the backend.

## Voyara AI chatbot

The floating Voyara AI assistant calls `POST /api/chat`. It searches approved MongoDB packages first, then sends only matching package context to the configured OpenAI-compatible provider. The key stays in `backend/.env` and is never sent to React.

Add these backend variables for external AI replies:

```env
AI_API_KEY=your-provider-key
AI_MODEL=gpt-4o-mini
AI_BASE_URL=https://api.openai.com/v1
AI_TIMEOUT_SECONDS=20
```

Without `AI_API_KEY`, the chatbot uses a transparent, package-grounded fallback so local development still works. It does not pretend that an external AI provider responded. Start FastAPI normally, open the frontend, click **Ask Voyara AI**, and try `Show me Ooty packages under 15000`.

Payment is disabled until `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` are provided. The backend creates orders and verifies signatures before marking bookings paid; it returns `503` when unconfigured. `GET /api/maps/config` reports whether `GOOGLE_MAPS_API_KEY` is configured, without exposing the key.

## Notes

The assistant is a transparent application-data fallback; no external AI key is required. SOS records an event and optional browser location but does not contact emergency services. Live operator notifications and production email delivery are not configured.
