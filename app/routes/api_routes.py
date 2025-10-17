from flask import Blueprint, request, jsonify
from core.db import execute_query
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/tenants', methods=['GET'])
def get_tenants():
    """الحصول على قائمة المستأجرين"""
    try:
        tenants = execute_query("""
            SELECT id, name, phone, email, building_id, balance, last_payment
            FROM tenants ORDER BY name
        """, fetch=True)
        
        return jsonify([dict(tenant) for tenant in tenants])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/tenants/<phone_number>', methods=['GET'])
def get_tenant_by_phone(phone_number):
    """الحصول على معلومات مستأجر برقم الهاتف"""
    try:
        tenant = execute_query("""
            SELECT id, name, phone, email, building_id, balance, last_payment
            FROM tenants WHERE phone = %s
        """, (phone_number,), fetch=True)
        
        if tenant:
            return jsonify(dict(tenant[0]))
        else:
            return jsonify({"error": "المستأجر غير موجود"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/payments', methods=['GET'])
def get_payments():
    """الحصول على المدفوعات"""
    try:
        payments = execute_query("""
            SELECT p.id, p.amount, p.status, p.due_date, p.payment_date, t.name 
            FROM payments p 
            LEFT JOIN tenants t ON p.tenant_id = t.id 
            ORDER BY p.due_date DESC 
            LIMIT 100
        """, fetch=True)
        
        return jsonify([dict(payment) for payment in payments])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/payments', methods=['POST'])
def create_payment():
    """إنشاء دفعة جديدة"""
    try:
        data = request.get_json()
        
        required_fields = ['tenant_id', 'amount', 'due_date']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"حقل {field} مطلوب"}), 400
        
        query = """
            INSERT INTO payments (tenant_id, amount, due_date, status, payment_date, method)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        payment_id = execute_query(
            query, 
            (
                data['tenant_id'],
                data['amount'],
                data['due_date'],
                data.get('status', 'pending'),
                data.get('payment_date'),
                data.get('method', 'cash')
            ),
            fetch=True
        )
        
        return jsonify({"message": "تم إنشاء الدفعة بنجاح", "payment_id": payment_id[0]['id']}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/tenants/<int:tenant_id>/balance', methods=['GET'])
def get_tenant_balance(tenant_id):
    """الحصول على رصيد مستأجر معين"""
    try:
        tenant = execute_query("""
            SELECT name, balance, last_payment
            FROM tenants WHERE id = %s
        """, (tenant_id,), fetch=True)
        
        if not tenant:
            return jsonify({"error": "المستأجر غير موجود"}), 404
        
        return jsonify({
            "name": tenant[0]['name'],
            "balance": tenant[0]['balance'],
            "last_payment": tenant[0]['last_payment']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/buildings', methods=['GET'])
def get_buildings():
    """الحصول على قائمة المباني"""
    try:
        buildings = execute_query("""
            SELECT id, name, address, description
            FROM buildings ORDER BY name
        """, fetch=True)
        
        return jsonify([dict(building) for building in buildings])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/maintenance', methods=['GET'])
def get_maintenance_requests():
    """الحصول على طلبات الصيانة"""
    try:
        maintenance = execute_query("""
            SELECT m.id, m.description, m.status, m.priority, 
                   t.name as tenant_name, b.name as building_name
            FROM maintenance m
            LEFT JOIN tenants t ON m.tenant_id = t.id
            LEFT JOIN buildings b ON m.building_id = b.id
            ORDER BY m.created_at DESC
            LIMIT 50
        """, fetch=True)
        
        return jsonify([dict(req) for req in maintenance])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """الحصول على إحصائيات النظام"""
    try:
        stats = {}
        
        # عدد المستأجرين
        stats['tenants_count'] = execute_query("SELECT COUNT(*) FROM tenants", fetch=True)[0][0]
        
        # عدد العقود النشطة
        stats['active_contracts'] = execute_query("SELECT COUNT(*) FROM contracts WHERE active = true", fetch=True)[0][0]
        
        # إجمالي المدفوعات المكتملة
        stats['total_payments'] = execute_query("SELECT SUM(amount) FROM payments WHERE status = 'paid'", fetch=True)[0][0] or 0
        
        # المدفوعات المستحقة
        stats['pending_payments'] = execute_query("SELECT SUM(amount) FROM payments WHERE status = 'pending'", fetch=True)[0][0] or 0
        
        # طلبات الصيانة المعلقة
        stats['pending_maintenance'] = execute_query("SELECT COUNT(*) FROM maintenance WHERE status = 'pending'", fetch=True)[0][0]
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500