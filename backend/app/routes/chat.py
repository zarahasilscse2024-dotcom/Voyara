from fastapi import APIRouter, HTTPException
from app.schemas.models import ChatRequest
from app.services.chatbot_service import answer

router = APIRouter(tags=["chat"])

@router.post("/chat")
async def chat(data: ChatRequest):
    try:
        reply, packages = await answer(data.message, [item.model_dump() for item in data.conversation])
        return {"reply": reply, "suggestions": [{"id": item["id"], "name": item["name"], "destination": item["destination"], "price": item["price"], "rating": item.get("rating"), "operator_name": item.get("operator_name"), "image": (item.get("images") or [None])[0]} for item in packages]}
    except Exception:
        raise HTTPException(503, "Sorry, I'm having trouble connecting right now. Please try again.")