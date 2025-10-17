from fastapi import APIRouter, HTTPException
from app.db.database import get_connection
from typing import Optional
from pydantic import BaseModel

router = APIRouter()

class PaymentCreate(BaseModel):
    tenant_id: int
    amount: float
    payment_date: Optional[str] = None
    notes: Optional[str] = None

@router.get("/payments")
async def get_payments(limit: Optional[int] = 100):
    """الحصول على قائمة الدفعات"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM payments ORDER BY payment_date DESC LIMIT {limit}")
        payments = cursor.fetchall()
        cursor.close()
        conn.close()
        return {
            "status": "success",
            "data": payments,
            "count": len(payments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payments/{payment_id}")
async def get_payment(payment_id: int):
    """الحصول على تفاصيل دفعة محددة"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
        payment = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not payment:
            raise HTTPException(status_code=404, detail="الدفعة غير موجودة")
        
        return {"status": "success", "data": payment}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/payments")
async def create_payment(payment: PaymentCreate):
    """تسجيل دفعة جديدة"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO payments (tenant_id, amount, payment_date, notes)
            VALUES (?, ?, COALESCE(?, date('now')), ?)
        """, (payment.tenant_id, payment.amount, payment.payment_date, payment.notes))
        conn.commit()
        payment_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "تم تسجيل الدفعة بنجاح",
            "payment_id": payment_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payments/tenant/{tenant_id}")
async def get_tenant_payments(tenant_id: int):
    """الحصول على دفعات مستأجر معين"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM payments WHERE tenant_id = ? ORDER BY payment_date DESC", (tenant_id,))
        payments = cursor.fetchall()
        cursor.close()
        conn.close()
        return {
            "status": "success",
            "data": payments,
            "count": len(payments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
