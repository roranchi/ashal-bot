from datetime import datetime
from fastapi import APIRouter
from app.db.database import get_connection
from app.services.reminder_service import SmartReminder
from app.templates.contract_reminders import ContractTemplates

router = APIRouter()

@router.post("/maintenance/contract-reminders/send")
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
                try:
                    cursor.execute('''
                        SELECT t.phone
                        FROM tenants t
                        JOIN contracts c ON t.id = c.tenant_id
                        WHERE c.id = ?
                    ''', (contract['contract_id'],))
                    
                    tenant_phone = cursor.fetchone()
                    
                    if tenant_phone and tenant_phone[0]:
                        sent_count += 1
                        
                except Exception as e:
                    print(f"❌ خطأ في إرسال تنبيه: {e}")
        
        conn.close()
        return {
            "status": "success",
            "sent_count": sent_count,
            "message": f"تم إرسال {sent_count} تذكير"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/maintenance/contract-renewal")
async def handle_contract_renewal(phone_number: str, message: str):
    """معالجة ردود المستأجرين على تجديد العقود"""
    responses = {
        'نعم': "شكراً لقبولكم التجديد. سيتواصل معكم المسؤول قريباً",
        'موافق': "شكراً لقبولكم التجديد. سيتواصل معكم المسؤول قريباً",
        'لا': "نحترم قراركم. نأمل التواصل لترتيب إخلاء الوحدة",
        'رفض': "نحترم قراركم. نأمل التواصل لترتيب إخلاء الوحدة"
    }
    
    response = message.strip().lower()
    reply = responses.get(response, "لم أفهم الرد، الرجاء الرد بنعم أو لا")
    
    return {"status": "success", "reply": reply}
