from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class MessageRequest(BaseModel):
    phone: str
    message: str

@router.post("/send-message")
async def send_message(data: MessageRequest):
    """إرسال رسالة واتساب"""
    try:
        # TODO: إضافة منطق إرسال الرسالة عبر WhatsApp API
        return {
            "status": "success",
            "message": "تم إرسال الرسالة",
            "phone": data.phone
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/send-message/test")
async def test_send_message():
    """اختبار إرسال الرسائل"""
    return {"status": "success", "message": "Send message endpoint working"}
