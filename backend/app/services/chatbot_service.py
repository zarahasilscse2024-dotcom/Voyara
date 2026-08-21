import re
from typing import Any
import httpx
from app.config import AI_API_KEY, AI_BASE_URL, AI_MODEL, AI_TIMEOUT_SECONDS
from app.database.connection import db, serialize

SYSTEM_PROMPT = """You are Voyara AI, an intelligent travel planning assistant for the Voyara comparison platform.
Be concise, warm, practical, and honest. Use only the supplied Voyara package context for package availability, prices, ratings, and operators.
Do not claim real-time knowledge, invent packages, or promise bookings. Explain differences between options and help the traveler choose based on their preferences.
If the context has no matching packages, say so clearly and suggest changing the budget or destination."""

def _budget(message: str):
    normalized = message.lower().replace("\u20b9", " rs ")
    values = [float(value.replace(',', '')) for value in re.findall(r'(?:under|below|less than|rs\.?|inr)\s*([\d,]+)', normalized)]
    return values[0] if values else None

def _packages(message: str):
    lowered = message.lower()
    destinations = db.packages.distinct("destination", {"status": "Approved"})
    destination = next((item for item in destinations if item.lower() in lowered), "")
    query: dict[str, Any] = {"status": "Approved"}
    if destination: query["destination"] = {"$regex": destination, "$options": "i"}
    budget = _budget(message)
    if budget is not None: query["price"] = {"$lte": budget}
    packages = [serialize(item) for item in db.packages.find(query).sort([("rating", -1), ("price", 1)]).limit(6)]
    return packages, destination, budget

def _package_context(packages):
    return [{key: item.get(key) for key in ["id", "name", "destination", "price", "duration", "rating", "operator_name", "operator_verified", "included", "activities", "accommodation", "transport", "meals"]} for item in packages]

def _fallback(message, packages, destination, budget):
    if packages:
        title = f"I found {len(packages)} Voyara package{'s' if len(packages) != 1 else ''}"
        if destination: title += f" for {destination}"
        if budget is not None: title += f" under ₹{budget:,.0f}"
        lines = [title + ".", ""]
        lines.extend(f"{index}. {item['name']} — ₹{item['price']:,.0f} — {item.get('rating', 'New')}★ — {item.get('operator_name', 'Verified operator')}" for index, item in enumerate(packages[:4], 1))
        lines.append("\nUse the package actions below to inspect or compare the real options.")
        return "\n".join(lines)
    return "I couldn't find a matching Voyara package for those preferences. Try increasing your budget or changing your destination."

async def answer(message: str, conversation: list[dict[str, str]]):
    packages, destination, budget = _packages(message)
    fallback = _fallback(message, packages, destination, budget)
    if not AI_API_KEY:
        return fallback, packages
    payload = {"model": AI_MODEL, "temperature": 0.3, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, *conversation[-10:], {"role": "user", "content": f"Voyara package context (authoritative): {_package_context(packages)}\n\nTraveler request: {message}"}]}
    try:
        async with httpx.AsyncClient(timeout=AI_TIMEOUT_SECONDS) as client:
            response = await client.post(f"{AI_BASE_URL.rstrip('/')}/chat/completions", headers={"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"}, json=payload)
            response.raise_for_status()
            reply = response.json()["choices"][0]["message"]["content"]
            return reply, packages
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
        return "Sorry, I'm having trouble connecting right now. Please try again.", packages