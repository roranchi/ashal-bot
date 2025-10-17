from fastapi import APIRouter, Request
from typing import Dict, Any

router = APIRouter()

@router.post("/webhook")
async def handle_webhook(request: Request):
    """معالجة Webhook من WhatsApp"""
    try:
        body = await request.json()
        # TODO: إضافة منطق معالجة الـ webhook
        return {
            "status": "success",
            "message": "Webhook received"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/webhook")
async def verify_webhook(request: Request):
    """التحقق من Webhook (WhatsApp verification)"""
    params = request.query_params
    
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    if mode == "subscribe" and token:
        # TODO: التحقق من الـ token
        return int(challenge) if challenge else {"status": "ok"}
    
    return {"status": "error", "message": "Verification failed"}
