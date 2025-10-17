from datetime import datetime, timedelta
from database import get_connection

class SmartReminder:
    @staticmethod
    def check_contract_reminders():
        """فحص العقود التي تحتاج تنبيهات - 90, 60, 30, 7 أيام"""
        conn = get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().date()
        
        # العقود المنتهية خلال 90 يوم
        target_date_90 = (today + timedelta(days=90)).strftime('%Y-%m-%d')
        target_date_60 = (today + timedelta(days=60)).strftime('%Y-%m-%d')
        target_date_30 = (today + timedelta(days=30)).strftime('%Y-%m-%d')
        target_date_7 = (today + timedelta(days=7)).strftime('%Y-%m-%d')
        
        reminders = {
            '90_days': [],
            '60_days': [],
            '30_days': [],
            '7_days': []
        }
        
        try:
            # استعلام للعقود المنتهية خلال 90 يوم - تم التعديل لـ PostgreSQL
            cursor.execute('''
                SELECT t.name, c.end_date, c.id
                FROM contracts c
                JOIN tenants t ON c.tenant_id = t.id
                WHERE c.active = true AND c.end_date BETWEEN %s AND %s
            ''', (target_date_90, target_date_90))
            
            reminders['90_days'] = [
                {'name': row[0], 'end_date': row[1], 'id': row[2]}
                for row in cursor.fetchall()
            ]
            
            # استعلام للعقود المنتهية خلال 60 يوم
            cursor.execute('''
                SELECT t.name, c.end_date, c.id
                FROM contracts c
                JOIN tenants t ON c.tenant_id = t.id
                WHERE c.active = true AND c.end_date BETWEEN %s AND %s
            ''', (target_date_60, target_date_60))
            
            reminders['60_days'] = [
                {'name': row[0], 'end_date': row[1], 'id': row[2]}
                for row in cursor.fetchall()
            ]
            
            # استعلام للعقود المنتهية خلال 30 يوم
            cursor.execute('''
                SELECT t.name, c.end_date, c.id
                FROM contracts c
                JOIN tenants t ON c.tenant_id = t.id
                WHERE c.active = true AND c.end_date BETWEEN %s AND %s
            ''', (target_date_30, target_date_30))
            
            reminders['30_days'] = [
                {'name': row[0], 'end_date': row[1], 'id': row[2]}
                for row in cursor.fetchall()
            ]
            
            # استعلام للعقود المنتهية خلال 7 أيام
            cursor.execute('''
                SELECT t.name, c.end_date, c.id
                FROM contracts c
                JOIN tenants t ON c.tenant_id = t.id
                WHERE c.active = true AND c.end_date BETWEEN %s AND %s
            ''', (target_date_7, target_date_7))
            
            reminders['7_days'] = [
                {'name': row[0], 'end_date': row[1], 'id': row[2]}
                for row in cursor.fetchall()
            ]
            
        except Exception as e:
            print(f"❌ خطأ في فحص التذكيرات: {e}")
        finally:
            cursor.close()
            conn.close()
        
        return reminders

    @staticmethod
    def check_payment_reminders():
        """فحص المدفوعات المتأخرة - إصدار مبسط"""
        conn = get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().date()
        
        try:
            # المدفوعات المتأخرة
            cursor.execute('''
                SELECT t.name, p.amount, p.due_date
                FROM payments p
                JOIN tenants t ON p.tenant_id = t.id
                WHERE p.status = %s AND p.due_date < %s
            ''', ('pending', today))
            
            overdue_payments = [
                {'name': row[0], 'amount': row[1], 'due_date': row[2]}
                for row in cursor.fetchall()
            ]
            
            return overdue_payments
            
        except Exception as e:
            print(f"❌ خطأ في فحص المدفوعات: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
