from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MessageProcessor:
    """معالج الرسائل مع تحسينات"""
    
    def __init__(self, whatsapp_api):
        self.whatsapp_api = whatsapp_api
        self.keywords = {
            'سداد': self.handle_payment,
            'دفع': self.handle_payment, 
            'دفعة': self.handle_payment,
            'إيجار': self.handle_payment,
            'مبلغ': self.handle_payment,
            
            'صيانة': self.handle_maintenance,
            'إصلاح': self.handle_maintenance,
            'عطل': self.handle_maintenance,
            'مشكلة': self.handle_maintenance,
            'خراب': self.handle_maintenance,
            'يحتاج': self.handle_maintenance,
            
            'استفسار': self.handle_inquiry,
            'سؤال': self.handle_inquiry,
            'معلومات': self.handle_inquiry,
            'تفاصيل': self.handle_inquiry,
            
            'السلام': self.handle_greeting,
            'أهلا': self.handle_greeting,
            'مرحبا': self.handle_greeting,
            'صباح': self.handle_greeting,
            'مساء': self.handle_greeting
        }
    
    def process(self, message, sender, message_id=None):
        """معالجة الرسالة وإرسال الرد"""
        message_text = message.lower().strip()
        
        for keyword, handler in self.keywords.items():
            if keyword in message_text:
                result = handler(message_text, sender, message_id)
                if result.get('response'):
                    send_result = self.whatsapp_api.send_message(sender, result['response'])
                    result['whatsapp_status'] = send_result.get('status')
                return result
        
        result = self.handle_default(message_text, sender, message_id)
        if result.get('response'):
            send_result = self.whatsapp_api.send_message(sender, result['response'])
            result['whatsapp_status'] = send_result.get('status')
        return result
    
    def handle_payment(self, message, sender, message_id):
        logger.info(f"طلب دفع من {sender}: {message}")
        return {
            "status": "success",
            "response": "✅ تم تسجيل عملية الدفع بنجاح!\n📋 سيتم مراجعة الدفعة وإرسال إيصال خلال ساعات قليلة.\n📞 للاستفسار: اتصل بنا على الرقم المعتاد",
            "action": "payment_registered",
            "sender": sender,
            "timestamp": datetime.now().isoformat()
        }
    
    def handle_maintenance(self, message, sender, message_id):
        logger.info(f"طلب صيانة من {sender}: {message}")
        return {
            "status": "success",
            "response": "🛠️ تم استلام بلاغ الصيانة!\n⏰ سيتم التواصل معك خلال 24 ساعة لترتيب موعد الصيانة.\n📝 رقم البلاغ: #" + str(hash(message_id or sender))[-6:],
            "action": "maintenance_ticket_created",
            "sender": sender,
            "timestamp": datetime.now().isoformat()
        }
    
    def handle_inquiry(self, message, sender, message_id):
        logger.info(f"استفسار من {sender}: {message}")
        return {
            "status": "success", 
            "response": "📞 تم استلام استفسارك!\n⏰ سيتم الرد عليك من قبل فريق خدمة العملاء خلال ساعات العمل.\n🕐 ساعات العمل: السبت - الخميس من 8 صباحاً حتى 6 مساءً",
            "action": "inquiry_received",
            "sender": sender,
            "timestamp": datetime.now().isoformat()
        }
    
    def handle_greeting(self, message, sender, message_id):
        logger.info(f"تحية من {sender}: {message}")
        greetings = [
            "🌟 أهلاً وسهلاً بك!\nكيف يمكنني مساعدتك اليوم؟",
            "👋 مرحباً بك!\nنحن هنا لخدمتك، كيف يمكنني المساعدة؟",
            "🏠 أهلاً بك في خدمة إدارة العقارات!\nما الذي تحتاج إليه؟"
        ]
        greeting_index = hash(sender) % len(greetings)
        return {
            "status": "success",
            "response": greetings[greeting_index],
            "action": "greeting_sent", 
            "sender": sender,
            "timestamp": datetime.now().isoformat()
        }
    
    def handle_default(self, message, sender, message_id):
        logger.info(f"رسالة عامة من {sender}: {message}")
        return {
            "status": "success",
            "response": "📨 تم استلام رسالتك بنجاح!\n⏰ سيتم الرد عليك في أقرب وقت ممكن.\n\nللمساعدة السريعة، يمكنك استخدام:\n• كلمة 'صيانة' لبلاغات الصيانة\n• كلمة 'سداد' لعمليات الدفع\n• كلمة 'استفسار' للأسئلة العامة",
            "action": "message_received",
            "sender": sender,
            "timestamp": datetime.now().isoformat()
        }