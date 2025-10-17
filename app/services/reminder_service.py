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
        
        # استعلام للعقود المنتهية خلال 90 يوم
        cursor.execute('''
            SELECT t.name, c.end_date, c.id
            FROM contracts c
            JOIN tenants t ON c.tenant_id = t.id
            WHERE c.active = 1 AND c.end_date BETWEEN %s AND %s
        ''', (today.strftime('%Y-%m-%d'), target_date_90))
        
        contracts = cursor.fetchall()
        
        for name, end_date, contract_id in contracts:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            days_remaining = (end_date_obj - today).days
            
            if 85 <= days_remaining <= 90:
                reminders['90_days'].append({
                    'name': name, 
                    'end_date': end_date, 
                    'days_left': days_remaining,
                    'contract_id': contract_id
                })
            elif 55 <= days_remaining <= 60:
                reminders['60_days'].append({
                    'name': name, 
                    'end_date': end_date, 
                    'days_left': days_remaining,
                    'contract_id': contract_id
                })
            elif 25 <= days_remaining <= 30:
                reminders['30_days'].append({
                    'name': name, 
                    'end_date': end_date, 
                    'days_left': days_remaining,
                    'contract_id': contract_id
                })
            elif 5 <= days_remaining <= 7:
                reminders['7_days'].append({
                    'name': name, 
                    'end_date': end_date, 
                    'days_left': days_remaining,
                    'contract_id': contract_id
                })
        
        conn.close()
        return reminders

    @staticmethod
    def log_reminder(contract_id, reminder_type):
        """تسجيل التنبيه المرسل في قاعدة البيانات"""
        conn = get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT INTO contract_reminders (contract_id, reminder_type, sent_date)
            VALUES (%s, %s, %s)
        ''', (contract_id, reminder_type, today))
        
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_overdue_payments():
        """تتبع المدفوعات المتأخرة مصنفة"""
        conn = get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # استخدام due_date بدلاً من payment_date
        cursor.execute('''
            SELECT t.name, p.amount, p.due_date,
                   julianday(%s) - julianday(p.due_date) as days_late
            FROM payments p
            JOIN tenants t ON p.tenant_id = t.id
            WHERE p.status = 'pending' AND p.due_date < %s
        ''', (today, today))
        
        overdue_payments = cursor.fetchall()
        
        categorized = {
            '1_7_days': [],
            '8_30_days': [],
            'over_30_days': []
        }
        
        for name, amount, due_date, days_late in overdue_payments:
            payment_info = {
                'name': name,
                'amount': amount,
                'due_date': due_date,
                'days_late': int(days_late)
            }
            
            if 1 <= days_late <= 7:
                categorized['1_7_days'].append(payment_info)
            elif 8 <= days_late <= 30:
                categorized['8_30_days'].append(payment_info)
            else:
                categorized['over_30_days'].append(payment_info)
        
        conn.close()
        return categorized
