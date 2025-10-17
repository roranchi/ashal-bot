#!/usr/bin/env python3
# مجمع المدفوعات التلقائي

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from app.db.database import get_connection

class MockWhatsAppClient:
    def send_message(self, to, message):
        print(f"📤 إرسال إلى {to}:\n{message}\n{'─'*40}")

def run_daily_collection():
    """تشغيل تجميع المدفوعات اليومي"""
    try:
        print("🕘 بدء تجميع المدفوعات اليومي...")
        
        # هنا سيأتي كود التجميع الفعلي
        # سنستخدم Mock للاختبار أولاً
        
        client = MockWhatsAppClient()
        client.send_message("+96891234567", "📊 تقرير السداد التجريبي")
        
        print("✅ تم محاكاة إرسال التقارير")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إرسال التقارير: {e}")
        return False

def check_overdue_payments():
    """التحقق من المدفوعات المتأخرة"""
    print("💰 جاري فحص المدفوعات المتأخرة...")
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            SELECT p.*, t.phone, t.name 
            FROM payments p
            JOIN contracts c ON p.contract_id = c.id
            JOIN tenants t ON c.tenant_id = t.id
            WHERE p.paid = FALSE AND p.due_date < CURRENT_DATE
            """
            cursor.execute(query)
            overdue_payments = cursor.fetchall()
            
            for payment in overdue_payments:
                print(f"⚠️  دفعة متأخرة: {payment}")
            
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ خطأ في التحقق من المدفوعات: {e}")
            return False
    return False

if __name__ == "__main__":
    run_daily_collection()
