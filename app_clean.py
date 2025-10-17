from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

# تحميل الإعدادات
load_dotenv()

app = Flask(__name__)

@app.route("/")
def home():
    return {"message": "Ashal Bot - Working Clean", "status": "running"}

@app.route("/health")
def health():
    return {"status": "healthy", "service": "ashal_bot"}

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    return {"status": "received", "message": "Webhook ready"}

if __name__ == "__main__":
    print("🚀 Starting Clean Ashal Bot...")
    app.run(host="0.0.0.0", port=5000, debug=True)
