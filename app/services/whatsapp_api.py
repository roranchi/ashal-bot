import requests
import logging
import os

logger = logging.getLogger(__name__)

class WhatsAppAPI:
    """فئة للتعامل مع API واتساب"""
    
    def __init__(self, access_token, phone_number_id):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.base_url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def send_message(self, recipient, message):
        """إرسال رسالة نصية"""
        try:
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient,
                "type": "text",
                "text": {"body": message}
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"تم إرسال رسالة إلى {recipient}: {message}")
                return {"status": "success", "data": response.json()}
            else:
                logger.error(f"فشل إرسال الرسالة: {response.status_code} - {response.text}")
                return {"status": "error", "message": response.text}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"خطأ في الاتصال بـ WhatsApp API: {str(e)}")
            return {"status": "error", "message": str(e)}