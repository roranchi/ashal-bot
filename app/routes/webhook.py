from flask import Blueprint, request, jsonify, render_template
from app.services.message_processor import MessageProcessor
from app.services.whatsapp_api import WhatsAppAPI
from app.utils.security import verify_webhook_signature
import os
import logging

logger = logging.getLogger(__name__)

# إنشاء Blueprint للويب هوك
webhook_bp = Blueprint('webhook', __name__)

# تهيئة APIs
whatsapp_api = WhatsAppAPI(
    os.environ.get('WHATSAPP_ACCESS_TOKEN'),
    os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
)
message_processor = MessageProcessor(whatsapp_api)

# صفحة الرئيسية
@webhook_bp.route('/')
def home():
    return render_template('home.html')

@webhook_bp.route('/webhook', methods=['GET', 'POST'])
def webhook():
    try:
        if request.method == 'GET':
            # التحقق من التوكن
            token = request.args.get('hub.verify_token')
            if token == os.environ.get('WHATSAPP_VERIFY_TOKEN'):
                return request.args.get('hub.challenge')
            return jsonify({"error": "Invalid token"}), 403

        # التحقق من التوقيع
        signature = request.headers.get('X-Hub-Signature-256')
        if not verify_webhook_signature(signature, request.data):
            return jsonify({"error": "Invalid signature"}), 403

        data = request.get_json()
        # معالجة البيانات هنا...
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"Error in webhook: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500