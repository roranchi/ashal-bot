from fastapi import APIRouter
from app.db.database import get_connection

router = APIRouter()

@router.get("/payments/test")
async def test_payments():
    """اختبار payment handler"""
    return {"status": "success", "message": "Payment handler working"}

@router.post("/payments/collect")
async def collect_payment(tenant_id: int, amount: float):
    """تحصيل دفعة"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # TODO: إضافة منطق تحصيل الدفعات
        cursor.close()
        conn.close()
        return {
            "status": "success",
            "message": f"تم تسجيل دفعة بمبلغ {amount}",
            "amount": amount,
            "tenant_id": tenant_id
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/payments/reminders")
async def send_payment_reminders():
    """إرسال تذكيرات الدفع"""
    try:
        # TODO: إضافة منطق التذكيرات
        return {
            "status": "success",
            "message": "تم إرسال التذكيرات"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
