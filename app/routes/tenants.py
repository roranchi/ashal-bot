from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db.database import get_connection
from app.routes.auth import verify_credentials
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def list_tenants(request: Request, username: str = Depends(verify_credentials)):
    """قائمة المستأجرين"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id, t.name, t.phone, t.email, t.national_id,
                   COUNT(c.id) as contracts_count
            FROM tenants t
            LEFT JOIN contracts c ON t.id = c.tenant_id
            GROUP BY t.id, t.name, t.phone, t.email, t.national_id
            ORDER BY t.created_at DESC
        """)
        tenants = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return templates.TemplateResponse("dashboard/tenants/list.html", {
            "request": request,
            "tenants": tenants,
            "username": username
        })
    except Exception as e:
        return templates.TemplateResponse("dashboard/tenants/list.html", {
            "request": request,
            "tenants": [],
            "username": username,
            "error": str(e)
        })

@router.get("/add", response_class=HTMLResponse)
async def add_tenant_form(request: Request, username: str = Depends(verify_credentials)):
    """صفحة إضافة مستأجر"""
    return templates.TemplateResponse("dashboard/tenants/add.html", {
        "request": request,
        "username": username
    })

@router.post("/add")
async def add_tenant(
    name: str = Form(...),
    phone: str = Form(...),
    email: Optional[str] = Form(None),
    national_id: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    username: str = Depends(verify_credentials)
):
    """إضافة مستأجر جديد"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tenants (name, phone, email, national_id, address, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (name, phone, email, national_id, address, notes))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return RedirectResponse(url="/dashboard/tenants", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في إضافة المستأجر: {str(e)}")

@router.get("/{tenant_id}", response_class=HTMLResponse)
async def view_tenant(tenant_id: int, request: Request, username: str = Depends(verify_credentials)):
    """عرض تفاصيل مستأجر"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,))
        tenant = cursor.fetchone()
        
        if not tenant:
            raise HTTPException(status_code=404, detail="المستأجر غير موجود")
        
        # جلب العقود
        cursor.execute("""
            SELECT c.*, p.name as property_name
            FROM contracts c
            LEFT JOIN properties p ON c.property_id = p.id
            WHERE c.tenant_id = ?
            ORDER BY c.start_date DESC
        """, (tenant_id,))
        contracts = cursor.fetchall()
        
        # جلب المدفوعات
        cursor.execute("""
            SELECT * FROM payments 
            WHERE tenant_id = ?
            ORDER BY payment_date DESC
            LIMIT 10
        """, (tenant_id,))
        payments = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return templates.TemplateResponse("dashboard/tenants/view.html", {
            "request": request,
            "tenant": tenant,
            "contracts": contracts,
            "payments": payments,
            "username": username
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{tenant_id}/delete")
async def delete_tenant(tenant_id: int, username: str = Depends(verify_credentials)):
    """حذف مستأجر"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tenants WHERE id = ?", (tenant_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return RedirectResponse(url="/dashboard/tenants", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في حذف المستأجر: {str(e)}")
