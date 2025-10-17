import os
from pathlib import Path

class Settings:
    PROJECT_PATH = Path("/opt/ashal-bot")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # إعدادات المراقبة
    SCAN_INTERVAL = 300  # 5 دقائق
    MAX_ISSUES_PER_SCAN = 50
    
    # إعدادات الإشعارات
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # API
    API_HOST = "0.0.0.0"
    API_PORT = 8000

settings = Settings()
