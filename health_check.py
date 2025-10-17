from dotenv import load_dotenv
import os
from supabase import create_client
from guardian.smart_project_guardian import SmartProjectGuardianUltra
import requests
import datetime

# تحميل المتغيرات البيئية فقط عند الاستيراد
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# دالة لإنشاء Supabase client بعد التأكد من المتغيرات البيئية
def init_supabase():
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise Exception("SUPABASE_URL و SUPABASE_KEY يجب أن تكونا موجودتين في ملف .env أو متغيرات البيئة")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# قائمة نقاط التحقق
ENDPOINTS = [
    'http://localhost:5000/ai-agent/health',
    'http://localhost:5000/ai-agent/report',
    'http://localhost:5000/analytics/sql/occupancy/1',
    'http://localhost:5000/analytics/sql/churn-risk/1'
]

# دالة تسجيل الأحداث في Supabase
def log_to_supabase(supabase_client, event_type, details, status="success"):
    try:
        supabase_client.table('ai_agent_logs').insert({
            'event_type': event_type,
            'details': details,
            'severity': 'high' if status == 'error' else 'info',
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
        }).execute()
    except Exception as e:
        print(f"❌ Error logging to Supabase: {e}")

# دالة تشغيل الفحص الصحي
def run_health_check(supabase_client, guardian_client):
    print("🚀 Running automated health check...")
    results = []
    for url in ENDPOINTS:
        try:
            r = requests.get(url, timeout=10)
            status = 'success' if r.status_code == 200 else 'error'
            results.append({
                'url': url,
                'status_code': r.status_code,
                'status': status,
                'response': r.text[:200]
            })
            log_to_supabase(supabase_client, 'endpoint_check', {'url': url, 'status': status, 'code': r.status_code})
        except Exception as e:
            log_to_supabase(supabase_client, 'endpoint_check', {'url': url, 'error': str(e)}, status='error')
            guardian_client.run_silent_monitoring()
    print("✅ Health check complete.")
    return results
