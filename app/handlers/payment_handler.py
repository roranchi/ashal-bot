import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../..')

from app.database import get_connection
# # from database.models.payment import Payment

class PaymentHandler:
    def __init__(self, whatsapp_client=None):
        self.client = whatsapp_client
    
    def handle_message(self, phone_number, message):
        message_lower = message.strip().lower()
        
        if "سداد" in message_lower:
            return self._handle_payment(phone_number, message)
        elif message_lower in ["تقرير السداد", "/payments"]:
            return self.get_payment_report()
        
        return None
    
    def _handle_payment(self, phone_number, message):
        try:
            payment = Payment(tenant_id=phone_number, amount=500, status="pending")
            payment.save()
            return "✅ تم استلام طلب السداد. سيتم المراجعة خلال ٢٤ ساعة"
        except Exception as e:
            return f"❌ حدث خطأ: {str(e)}"
    
    def get_payment_report(self):
        try:
            pending_payments = Payment.get_pending_payments()
            if not pending_payments:
                return "📋 لا توجد مدفوعات منتظرة"
            
            report = "📋 طلبات السداد المنتظرة:\n\n"
            for i, payment in enumerate(pending_payments, 1):
                report += f"{i}. {payment['tenant_id']} - {payment['amount']} ريال - {payment['payment_date']}\n"
            
            report += "\n💡 للرد: رد بـ الرقم + ✅ (مثال: 1 ✅)"
            return report
            
        except Exception as e:
            return f"❌ خطأ في التقرير: {str(e)}"

if __name__ == "__main__":
    handler = PaymentHandler()
    print("✅ معالج السداد جاهز")
