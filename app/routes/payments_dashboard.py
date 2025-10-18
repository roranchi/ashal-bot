from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db.database import get_connection
from app.routes.auth import verify_credentials
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def list_payments(request: Request, username: str = Depends(verify_credentials)):
    """قائمة المدفوعات"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.id, p.amount, p.payment_date, p.payment_method, p.status,
                   t.name as tenant_name, pr.name as property_name
            FROM payments p
            LEFT JOIN tenants t ON p.tenant_id = t.id
            LEFT JOIN properties pr ON p.property_id = pr.id
            ORDER BY p.payment_date DESC
        """)
        payments = cursor.fetchall()
        
        # حساب الإحصائيات
        cursor.execute("SELECT SUM(amount) FROM payments WHERE status = 'completed'")
        total_received = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(amount) FROM payments WHERE status = 'pending'")
        total_pending = cursor.fetchone()[0] or 0
        
        cursor.close()
        conn.close()
        
        return templates.TemplateResponse("dashboard/payments/list.html", {
            "request": request,
            "payments": payments,
            "total_received": total_received,
            "total_pending": total_pending,
            "username": username
        })
    except Exception as e:
        return templates.TemplateResponse("dashboard/payments/list.html", {
            "request": request,
            "payments": [],
            "total_received": 0,
            "total_pending": 0,
            "username": username,
            "error": str(e)
        })

@router.get("/add", response_class=HTMLResponse)
async def add_payment_form(request: Request, username: str = Depends(verify_credentials)):
    """صفحة إضافة دفعة"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name FROM tenants ORDER BY name")
        tenants = cursor.fetchall()
        
        cursor.execute("SELECT id, name FROM properties ORDER BY name")
        properties = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return templates.TemplateResponse("dashboard/payments/add.html", {
            "request": request,
            "tenants": tenants,
            "properties": properties,
            "username": username
        })
    except Exception as e:
        return templates.TemplateResponse("dashboard/payments/add.html", {
            "request": request,
            "tenants": [],
            "properties": [],
            "username": username,
            "error": str(e)
        })

@router.post("/add")
async def add_payment(
    tenant_id: int = Form(...),
    property_id: Optional[int] = Form(None),
    amount: float = Form(...),
    payment_date: str = Form(...),
    payment_method: str = Form(...),
    notes: Optional[str] = Form(None),
    username: str = Depends(verify_credentials)
):
    """إضافة دفعة جديدة"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO payments 
            (tenant_id, property_id, amount, payment_date, payment_method, status, notes, created_at)
            VALUES (?, ?, ?, ?, ?, 'completed', ?, datetime('now'))
        """, (tenant_id, property_id, amount, payment_date, payment_method, notes))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return RedirectResponse(url="/dashboard/payments", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في إضافة الدفعة: {str(e)}")

@router.post("/{payment_id}/delete")
async def delete_payment(payment_id: int, username: str = Depends(verify_credentials)):
    """حذف دفعة"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return RedirectResponse(url="/dashboard/payments", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في حذف الدفعة: {str(e)}")
