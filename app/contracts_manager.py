#!/usr/bin/env python3
"""
نظام إدارة العقود الشامل - Property WhatsApp Bot
===============================================
ملف contracts_manager.py محدث مع أفضل الممارسات لـ PostgreSQL
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
import json
from pathlib import Path
from contextlib import contextmanager
import logging
import psycopg2
from psycopg2.extras import DictCursor

from app.database import get_connection

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContractsManager:
    def __init__(self):
        """
        مدير العقود - يتكامل مع قاعدة البيانات الجديدة
        """
        self.init_database()
    
    @contextmanager
    def _get_connection(self):
        """مدير سياق للاتصال بقاعدة البيانات الجديدة"""
        conn = get_connection()
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """إنشاء/تحديث جداول العقود في قاعدة البيانات"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contracts (
                    id SERIAL PRIMARY KEY,
                    contract_number TEXT UNIQUE NOT NULL,
                    property_id INTEGER,
                    tenant_id INTEGER,
                    owner_id INTEGER,
                    tenant_name TEXT,
                    tenant_phone TEXT,
                    property_address TEXT,
                    contract_type TEXT DEFAULT 'rental',
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    monthly_rent DECIMAL(10,2) DEFAULT 0,
                    total_amount DECIMAL(10,2) DEFAULT 0,
                    deposit_amount DECIMAL(10,2) DEFAULT 0,
                    commission_rate DECIMAL(5,2) DEFAULT 5.0,
                    payment_frequency TEXT DEFAULT 'monthly',
                    currency TEXT DEFAULT 'OMR',
                    status TEXT DEFAULT 'active',
                    active BOOLEAN DEFAULT TRUE,
                    auto_renewal BOOLEAN DEFAULT FALSE,
                    renewal_notice_days INTEGER DEFAULT 60,
                    terms_conditions TEXT,
                    special_conditions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    notes TEXT,
                    days_remaining INTEGER,
                    is_expiring BOOLEAN DEFAULT FALSE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contract_renewals (
                    id SERIAL PRIMARY KEY,
                    contract_id INTEGER NOT NULL,
                    old_end_date DATE NOT NULL,
                    new_end_date DATE NOT NULL,
                    old_rent DECIMAL(10,2),
                    new_rent DECIMAL(10,2),
                    renewal_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    created_by TEXT,
                    FOREIGN KEY (contract_id) REFERENCES contracts (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contract_reminders (
                    id SERIAL PRIMARY KEY,
                    contract_id INTEGER NOT NULL,
                    reminder_type TEXT NOT NULL,
                    reminder_date DATE NOT NULL,
                    message TEXT,
                    is_sent BOOLEAN DEFAULT FALSE,
                    sent_at TIMESTAMP,
                    phone_number TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contract_id) REFERENCES contracts (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contract_payments (
                    id SERIAL PRIMARY KEY,
                    contract_id INTEGER NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    payment_date DATE,
                    due_date DATE NOT NULL,
                    payment_type TEXT DEFAULT 'rent',
                    status TEXT DEFAULT 'pending',
                    payment_method TEXT,
                    reference_number TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contract_id) REFERENCES contracts (id)
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_contracts_end_date ON contracts(end_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_contracts_phone ON contracts(tenant_phone)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_contract_payments_status ON contract_payments(status)')
            
            conn.commit()
        logger.info("✅ تم إنشاء/تحديث قاعدة البيانات")
    
    def create_contract(self, contract_data: Dict[str, Any]) -> Tuple[bool, str, Optional[int]]:
        """إنشاء عقد جديد مع التحقق من البيانات"""
        try:
            required_fields = ['contract_number', 'start_date', 'end_date']
            for field in required_fields:
                if not contract_data.get(field):
                    return False, f"الحقل {field} مطلوب", None
            
            with self._get_connection() as conn:
                cursor = conn.cursor(cursor_factory=DictCursor)
                
                cursor.execute("SELECT id FROM contracts WHERE contract_number = %s", 
                             (contract_data['contract_number'],))
                if cursor.fetchone():
                    return False, "رقم العقد موجود مسبقاً", None
                
                end_date = datetime.strptime(contract_data['end_date'], '%Y-%m-%d')
                days_remaining = (end_date - datetime.now()).days
                is_expiring = days_remaining <= 30
                
                insert_query = '''
                    INSERT INTO contracts (
                        contract_number, property_id, tenant_id, owner_id, tenant_name,
                        tenant_phone, property_address, contract_type, start_date, end_date, 
                        monthly_rent, total_amount, deposit_amount, commission_rate, payment_frequency,
                        currency, terms_conditions, special_conditions, created_by, notes,
                        days_remaining, is_expiring
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                '''
                
                cursor.execute(insert_query, (
                    contract_data['contract_number'],
                    contract_data.get('property_id'),
                    contract_data.get('tenant_id'),
                    contract_data.get('owner_id'),
                    contract_data.get('tenant_name', ''),
                    contract_data.get('tenant_phone', ''),
                    contract_data.get('property_address', ''),
                    contract_data.get('contract_type', 'rental'),
                    contract_data['start_date'],
                    contract_data['end_date'],
                    contract_data.get('monthly_rent', 0),
                    contract_data.get('total_amount', 0),
                    contract_data.get('deposit_amount', 0),
                    contract_data.get('commission_rate', 5.0),
                    contract_data.get('payment_frequency', 'monthly'),
                    contract_data.get('currency', 'OMR'),
                    contract_data.get('terms_conditions', ''),
                    contract_data.get('special_conditions', ''),
                    contract_data.get('created_by', 'System'),
                    contract_data.get('notes', ''),
                    days_remaining,
                    is_expiring
                ))
                
                contract_id = cursor.fetchone()[0]
                
                self._create_auto_reminders(cursor, contract_id, contract_data)
                
                if contract_data.get('contract_type') == 'rental' and contract_data.get('monthly_rent'):
                    self._create_payment_schedule(cursor, contract_id, contract_data)
                
                conn.commit()
                
            return True, f"تم إنشاء العقد رقم {contract_data['contract_number']} بنجاح", contract_id
            
        except psycopg2.Error as e:
            logger.error(f"خطأ في إنشاء العقد: {str(e)}")
            return False, f"خطأ في إنشاء العقد: {str(e)}", None
    
    def get_contracts_by_phone(self, phone: str) -> List[Dict[str, Any]]:
        """الحصول على جميع العقود المرتبطة برقم هاتف معين"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(cursor_factory=DictCursor)
                
                cursor.execute('''
                    SELECT * FROM contracts 
                    WHERE tenant_phone = %s 
                    ORDER BY created_at DESC
                ''', (phone,))
                
                contracts = [dict(row) for row in cursor.fetchall()]
                
                for contract in contracts:
                    if contract['end_date']:
                        end_date = datetime.strptime(str(contract['end_date']), '%Y-%m-%d')
                        contract['days_remaining'] = (end_date - datetime.now()).days
                        contract['is_expiring'] = contract['days_remaining'] <= 30
                
                return contracts
                
        except psycopg2.Error as e:
            logger.error(f"خطأ في الحصول على العقود بالهاتف: {e}")
            return []
    
    def get_tenant_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """البحث عن عقد مستأجر برقم الهاتف"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(cursor_factory=DictCursor)
                cursor.execute(
                    "SELECT id, tenant_name, tenant_phone FROM contracts WHERE tenant_phone = %s LIMIT 1",
                    (phone_number,)
                )
                tenant = cursor.fetchone()
                return dict(tenant) if tenant else None
        except psycopg2.Error as e:
            logger.error(f"خطأ في البحث عن المستأجر برقم الهاتف: {e}")
            return None

    def get_tenant_payments(self, tenant_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """الحصول على مدفوعات مستأجر محدد"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(cursor_factory=DictCursor)
                query = """
                    SELECT * FROM contract_payments
                    WHERE contract_id = %s
                    ORDER BY due_date DESC
                """
                params = [tenant_id]
                if limit:
                    query += " LIMIT %s"
                    params.append(limit)
                
                cursor.execute(query, tuple(params))
                return [dict(row) for row in cursor.fetchall()]
        except psycopg2.Error as e:
            logger.error(f"خطأ في الحصول على مدفوعات المستأجر: {e}")
            return []
    
    def search_contracts(self, search_term: str) -> List[Dict[str, Any]]:
        """بحث في العقود بمختلف الحقول"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(cursor_factory=DictCursor)
                
                query = '''
                    SELECT * FROM contracts 
                    WHERE contract_number LIKE %s 
                       OR tenant_name LIKE %s 
                       OR tenant_phone LIKE %s 
                       OR property_address LIKE %s
                    ORDER BY created_at DESC
                '''
                
                search_pattern = f"%{search_term}%"
                cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
                
                contracts = [dict(row) for row in cursor.fetchall()]
                
                for contract in contracts:
                    if contract['end_date']:
                        end_date = datetime.strptime(str(contract['end_date']), '%Y-%m-%d')
                        contract['days_remaining'] = (end_date - datetime.now()).days
                        contract['is_expiring'] = contract['days_remaining'] <= 30
                
                return contracts
                
        except psycopg2.Error as e:
            logger.error(f"خطأ في البحث: {e}")
            return []
    
    def _create_auto_reminders(self, cursor, contract_id: int, contract_data: Dict[str, Any]):
        """إنشاء تذكيرات تلقائية للعقد"""
        end_date = datetime.strptime(contract_data['end_date'], '%Y-%m-%d')
        
        reminder_60 = end_date - timedelta(days=60)
        if reminder_60 > datetime.now():
            cursor.execute('''
                INSERT INTO contract_reminders (contract_id, reminder_type, reminder_date, message)
                VALUES (%s, 'expiry_warning', %s, 'تنبيه: ينتهي العقد خلال شهرين')
            ''', (contract_id, reminder_60.strftime('%Y-%m-%d')))
        
        reminder_30 = end_date - timedelta(days=30)
        if reminder_30 > datetime.now():
            cursor.execute('''
                INSERT INTO contract_reminders (contract_id, reminder_type, reminder_date, message)
                VALUES (%s, 'expiry_warning', %s, 'تنبيه: ينتهي العقد خلال شهر')
            ''', (contract_id, reminder_30.strftime('%Y-%m-%d')))
        
        reminder_7 = end_date - timedelta(days=7)
        if reminder_7 > datetime.now():
            cursor.execute('''
                INSERT INTO contract_reminders (contract_id, reminder_type, reminder_date, message)
                VALUES (%s, 'expiry_urgent', %s, 'عاجل: ينتهي العقد خلال أسبوع!')
            ''', (contract_id, reminder_7.strftime('%Y-%m-%d')))
    
    def _create_payment_schedule(self, cursor, contract_id: int, contract_data: Dict[str, Any]):
        """إنشاء جدول المدفوعات الشهرية"""
        start_date = datetime.strptime(contract_data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(contract_data['end_date'], '%Y-%m-%d')
        monthly_rent = float(contract_data['monthly_rent'])
        
        current_date = start_date
        while current_date <= end_date:
            due_date = current_date.replace(day=1)
            
            cursor.execute('''
                INSERT INTO contract_payments (
                    contract_id, amount, due_date, payment_type, status
                ) VALUES (%s, %s, %s, 'rent', 'pending')
            ''', (contract_id, monthly_rent, due_date.strftime('%Y-%m-%d')))
            
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
    
    def get_all_contracts(self, search_term: str = None, filter_status: str = None) -> List[Dict[str, Any]]:
        """الحصول على جميع العقود مع البحث والفلترة"""
        with self._get_connection() as conn:
            cursor = conn.cursor(cursor_factory=DictCursor)
            
            query = "SELECT * FROM contracts WHERE 1=1"
            params = []
            
            if search_term:
                query += " AND (contract_number LIKE %s OR tenant_name LIKE %s OR property_address LIKE %s OR tenant_phone LIKE %s)"
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
            
            if filter_status:
                query += " AND status = %s"
                params.append(filter_status)
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            contracts = [dict(row) for row in cursor.fetchall()]
            
            for contract in contracts:
                if contract['end_date']:
                    end_date = datetime.strptime(str(contract['end_date']), '%Y-%m-%d')
                    contract['days_remaining'] = (end_date - datetime.now()).days
                    contract['is_expiring'] = contract['days_remaining'] <= 30
            
            return contracts
    
    def get_contract_by_id(self, contract_id: int) -> Optional[Dict[str, Any]]:
        """الحصول على تفاصيل عقد محدد"""
        with self._get_connection() as conn:
            cursor = conn.cursor(cursor_factory=DictCursor)
            
            cursor.execute("SELECT * FROM contracts WHERE id = %s", (contract_id,))
            contract = cursor.fetchone()
            
            if not contract:
                return None
            
            contract_dict = dict(contract)
            
            if contract_dict['end_date']:
                end_date = datetime.strptime(str(contract_dict['end_date']), '%Y-%m-%d')
                contract_dict['days_remaining'] = (end_date - datetime.now()).days
                contract_dict['is_expiring'] = contract_dict['days_remaining'] <= 30
            
            cursor.execute("""
                SELECT * FROM contract_payments 
                WHERE contract_id = %s 
                ORDER BY due_date DESC
            """, (contract_id,))
            contract_dict['payments'] = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("""
                SELECT * FROM contract_reminders 
                WHERE contract_id = %s 
                ORDER BY reminder_date DESC
            """, (contract_id,))
            contract_dict['reminders'] = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("""
                SELECT * FROM contract_renewals 
                WHERE contract_id = %s 
                ORDER BY renewal_date DESC
            """, (contract_id,))
            contract_dict['renewals'] = [dict(row) for row in cursor.fetchall()]
            
            return contract_dict
    
    def update_contract_status(self, contract_id: int, new_status: str, notes: str = "") -> Tuple[bool, str]:
        """تحديث حالة العقد"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE contracts 
                    SET status = %s, updated_at = %s, notes = notes || %s
                    WHERE id = %s
                """, (
                    new_status,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    f"\n{datetime.now().strftime('%Y-%m-%d')}: تم تغيير الحالة إلى {new_status}. {notes}",
                    contract_id
                ))
                
                if cursor.rowcount == 0:
                    return False, "العقد غير موجود"
                
                conn.commit()
            
            return True, f"تم تحديث حالة العقد إلى {new_status}"
            
        except psycopg2.Error as e:
            logger.error(f"خطأ في تحديث حالة العقد: {str(e)}")
            return False, f"خطأ في التحديث: {str(e)}"
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """إحصائيات شاملة للوحة التحكم"""
        stats = {}
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM contracts")
            stats['total_contracts'] = cursor.fetchone()[0]
            
            conn.commit()
            
            return stats