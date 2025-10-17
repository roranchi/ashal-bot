import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

def get_connection():
    """اتصال Transaction Pooler بـ Supabase"""
    try:
        supabase_password = os.getenv('SUPABASE_PASSWORD', 'Pyfpuk-wozbyd-0taktu')
        database_url = f"postgresql://postgres.udvmhyxihqmraknmwvei:{supabase_password}@aws-1-eu-north-1.pooler.supabase.com:6543/postgres?sslmode=require"
        conn = psycopg2.connect(database_url, connect_timeout=20)
        logging.info("✅ اتصال Transaction Pooler ناجح!")
        return conn
    except Exception as e:
        logging.error(f"❌ فشل الاتصال: {e}")
        raise e

class Payment:
    def __init__(self, tenant_id, amount, status="pending"):
        self.tenant_id = tenant_id
        self.amount = amount
        self.status = status
        self.payment_date = datetime.now().strftime('%Y-%m-%d')
    
    def save(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (tenant_id, amount, status, payment_date)
            VALUES (%s, %s, %s, %s)
        ''', (self.tenant_id, self.amount, self.status, self.payment_date))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_pending_payments():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT tenant_id, amount, payment_date FROM payments WHERE status = %s', ('pending',))
        payments = [{'tenant_id': row[0], 'amount': row[1], 'payment_date': row[2]} for row in cursor.fetchall()]
        conn.close()
        return payments
