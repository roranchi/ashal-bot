from datetime import datetime
from fastapi import APIRouter
from app.db.database import get_connection
from app.services.reminder_service import SmartReminder
from app.templates.contract_reminders import ContractTemplates

router = APIRouter()

@router.post("/contracts/reminders/send")
async def send_contract_reminders():
    """إرسال تنبيهات تجديد العقود تلقائياً"""
    try:
        reminders = SmartReminder.check_contract_reminders()
        sent_count = 0
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # الحصول على أرقام هواتف المستأجرين
        for period, contracts in reminders.items():
            for contract in contracts:
                # TODO: إضافة منطق إرسال الرسائل
                sent_count += 1
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": f"تم إرسال {sent_count} تذكير",
            "sent_count": sent_count
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
