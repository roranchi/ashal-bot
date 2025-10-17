from datetime import datetime

def get_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    try:
        return conn
    except Exception as e:
        print(f'❌ خطأ في الاتصال بقاعدة البيانات: {e}')
        return None

def check_due_reminders():
    """التحقق من التذكيرات المستحقة"""
    print("🔔 جاري فحص التذكيرات المستحقة...")
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # استخدام اسم العمود الصحيح (ربما due_date أو تاريخ)
            query = "SELECT * FROM contract_reminders WHERE due_date <= date('now') AND status = 'pending'"
            cursor.execute(query)
            reminders = cursor.fetchall()
            
            for reminder in reminders:
                print(f"📋 تذكير مستحق: {reminder}")
            
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ خطأ في التحقق من التذكيرات: {e}")
            return False
    return False
