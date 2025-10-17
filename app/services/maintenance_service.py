#!/usr/bin/env python3
# خدمة إدارة الصيانة - حسب الخطة الأصلية

import sys
import os
from datetime import datetime

# إضافة المسار الحالي إلى Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')

from app.db.database import get_connection

class MaintenanceService:
    @staticmethod
    def create_maintenance_ticket(tenant_id, description, issue_type):
        """إنشاء تذكرة صيانة جديدة - مطابق للخطة"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # تحديد الأولوية بناءً على نوع العطل
        priority = MaintenanceService._determine_priority(issue_type)
        
        cursor.execute('''
            INSERT INTO maintenance (tenant_id, description, issue_type, status, priority_level)
            VALUES (?, ?, ?, 'open', ?)
        ''', (tenant_id, description, issue_type, priority))
        
        ticket_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return ticket_id
    
    @staticmethod
    def _determine_priority(issue_type):
        """تحديد أولوية التذكرة - حسب الخطة"""
        priority_map = {
            'كهرباء': 'high',
            'سباكة': 'high',
            'نقاشة': 'medium',
            'عامة': 'low'
        }
        return priority_map.get(issue_type, 'medium')
    
    @staticmethod
    def get_active_tickets():
        """الحصول على تذاكر الصيانة النشطة - حسب الخطة"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.*, t.name as tenant_name, t.phone as tenant_phone
            FROM maintenance m
            JOIN tenants t ON m.tenant_id = t.id
            WHERE m.status != 'completed' AND m.status != 'cancelled'
            ORDER BY m.priority_level DESC, m.created_at DESC
        ''')
        
        tickets = cursor.fetchall()
        conn.close()
        return tickets

if __name__ == "__main__":
    print("✅ خدمة الصيانة جاهزة - مطابقة للخطة الأصلية")
