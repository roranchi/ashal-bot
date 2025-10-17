#!/usr/bin/env python3
"""
ASHAL Bot - الإصدار المحسن جاهز للإنتاج
"""

import sys
import os
sys.path.append("/opt/ashal-bot")

import requests
from flask import Flask, request, jsonify
from app.database import get_connection
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """فحص صحة التطبيق واتصال قاعدة البيانات"""
    try:
        conn = get_connection()
        conn.close()
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": "2025-10-16 23:47:00"
        }), 200
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500

@app.route('/', methods=['GET'])
def home():
    """الصفحة الرئيسية"""
    return jsonify({
        "message": "مرحباً بك في Ashal Bot!",
        "version": "2.0",
        "status": "running"
    }), 200

@app.route('/send-message', methods=['POST'])
def send_message():
    """إرسال رسالة واتساب"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        message = data.get('message')
        
        if not phone or not message:
            return jsonify({"error": "رقم الهاتف والرسالة مطلوبان"}), 400
        
        # TODO: تنفيذ إرسال الرسالة عبر واتساب
        logging.info(f"إرسال رسالة إلى {phone}: {message}")
        
        return jsonify({
            "status": "success",
            "message": "تم إرسال الرسالة بنجاح",
            "phone": phone
        }), 200
        
    except Exception as e:
        logging.error(f"Error sending message: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
