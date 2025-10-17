from datetime import datetime
from app.database import get_connection
from services.reminder_service import SmartReminder
from whatsapp.templates.contract_reminders import ContractTemplates

class ContractHandler:
    def __init__(self, whatsapp_client):
        self.client = whatsapp_client
    
    def send_contract_reminders(self):
        """إرسال تنبيهات تجديد العقود تلقائياً"""
        reminders = SmartReminder.check_contract_reminders()
        sent_count = 0
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # الحصول على أرقام هواتف المستأجرين
        for period, contracts in reminders.items():
            for contract in contracts:
                try:
                    # الحصول على رقم هاتف المستأجر
                    cursor.execute('''
                        SELECT t.phone 
                        FROM tenants t 
                        JOIN contracts c ON t.id = c.tenant_id 
                        WHERE c.id = ?
                    ''', (contract['contract_id'],))
                    
                    tenant_phone = cursor.fetchone()
                    
                    if tenant_phone and tenant_phone[0]:
                        # إرسال الرسالة المناسبة
                        message = self._get_reminder_message(period, contract)
                        self.client.send_message(tenant_phone[0], message)
                        
                        # تسجيل التنبيه في قاعدة البيانات
                        SmartReminder.log_reminder(
                            contract['contract_id'], 
                            f'{period}_reminder'
                        )
                        
                        sent_count += 1
                        print(f"✅ تم إرسال تنبيه {period} إلى {contract['name']}")
                    
                except Exception as e:
                    print(f"❌ خطأ في إرسال تنبيه: {e}")
        
        conn.close()
        return sent_count
    
    def _get_reminder_message(self, period, contract):
        """الحصول على الرسالة المناسبة حسب الفترة"""
        templates = {
            '90_days': ContractTemplates.contract_90_days_reminder,
            '60_days': ContractTemplates.contract_60_days_reminder,
            '30_days': ContractTemplates.contract_30_days_reminder,
            '7_days': ContractTemplates.contract_7_days_reminder
        }
        
        if period in templates:
            return templates[period](
                contract['name'],
                contract['end_date'],
                contract['days_left']
            )
        
        return ""
    
    def handle_contract_renewal(self, phone_number, message):
        """معالجة ردود المستأجرين على تجديد العقود"""
        responses = {
            'نعم': self._confirm_renewal,
            'موافق': self._confirm_renewal,
            'أوافق': self._confirm_renewal,
            'لا': self._reject_renewal,
            'رفض': self._reject_renewal
        }
        
        response = message.strip().lower()
        if response in responses:
            return responses[response](phone_number)
        
        return "لم أفهم الرد، الرجاء الرد بنعم أو لا"
    
    def _confirm_renewal(self, phone_number):
        """معالجة قبول التجديد"""
        # سيتم تطويرها بالكامل لاحقاً
        return "شكراً لقبولكم التجديد. سيتواصل معكم المسؤول قريباً"
    
    def _reject_renewal(self, phone_number):
        """معالجة رفض التجديد"""
        # سيتم تطويرها بالكامل لاحقاً
        return "نحترم قراركم. نأمل التواصل لترتيب إخلاء الوحدة"
