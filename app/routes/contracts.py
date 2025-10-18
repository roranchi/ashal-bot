from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db.database import get_connection
from app.routes.auth import verify_credentials
from typing import Optional
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def list_contracts(request: Request, username: str = Depends(verify_credentials)):
    """قائمة العقود"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.id, c.start_date, c.end_date, c.rent_amount, c.status,
                   t.name as tenant_name, p.name as property_name,
                   CAST((julianday(c.end_date) - julianday('now')) AS INTEGER) as days_left
            FROM contracts c
            LEFT JOIN tenants t ON c.tenant_id = t.id
            LEFT JOIN properties p ON c.property_id = p.id
            ORDER BY c.start_date DESC
        """)
        contracts = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return templates.TemplateResponse("dashboard/contracts/list.html", {
            "request": request,
            "contracts": contracts,
            "username": username
        })
    except Exception as e:
        return templates.TemplateResponse("dashboard/contracts/list.html", {
            "request": request,
            "contracts": [],
            "username": username,
            "error": str(e)
        })

@router.get("/add", response_class=HTMLResponse)
async def add_contract_form(request: Request, username: str = Depends(verify_credentials)):
    """صفحة إضافة عقد"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name FROM tenants ORDER BY name")
        tenants = cursor.fetchall()
        
        cursor.execute("SELECT id, name FROM properties WHERE status = 'available' ORDER BY name")
        properties = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return templates.TemplateResponse("dashboard/contracts/add.html", {
            "request": request,
            "tenants": tenants,
            "properties": properties,
            "username": username
        })
    except Exception as e:
        return templates.TemplateResponse("dashboard/contracts/add.html", {
            "request": request,
            "tenants": [],
            "properties": [],
            "username": username,
            "error": str(e)
        })

@router.post("/add")
async def add_contract(
    tenant_id: int = Form(...),
    property_id: int = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    rent_amount: float = Form(...),
    deposit_amount: Optional[float] = Form(None),
    payment_day: Optional[int] = Form(None),
    notes: Optional[str] = Form(None),
    username: str = Depends(verify_credentials)
):
    """إضافة عقد جديد"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO contracts 
            (tenant_id, property_id, start_date, end_date, rent_amount, 
             deposit_amount, payment_day, status, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?, datetime('now'))
        """, (tenant_id, property_id, start_date, end_date, rent_amount, 
              deposit_amount, payment_day, notes))
        
        # تحديث حالة العقار إلى مؤجر
        cursor.execute("UPDATE properties SET status = 'rented' WHERE id = ?", (property_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return RedirectResponse(url="/dashboard/contracts", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في إضافة العقد: {str(e)}")

@router.get("/{contract_id}", response_class=HTMLResponse)
async def view_contract(contract_id: int, request: Request, username: str = Depends(verify_credentials)):
    """عرض تفاصيل عقد"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.*, t.name as tenant_name, t.phone as tenant_phone,
                   p.name as property_name, p.address as property_address
            FROM contracts c
            LEFT JOIN tenants t ON c.tenant_id = t.id
            LEFT JOIN properties p ON c.property_id = p.id
            WHERE c.id = ?
        """, (contract_id,))
        contract = cursor.fetchone()
        
        if not contract:
            raise HTTPException(status_code=404, detail="العقد غير موجود")
        
        cursor.close()
        conn.close()
        
        return templates.TemplateResponse("dashboard/contracts/view.html", {
            "request": request,
            "contract": contract,
            "username": username
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{contract_id}/delete")
async def delete_contract(contract_id: int, username: str = Depends(verify_credentials)):
    """حذف عقد"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # جلب property_id قبل الحذف
        cursor.execute("SELECT property_id FROM contracts WHERE id = ?", (contract_id,))
        result = cursor.fetchone()
        
        if result:
            property_id = result[0]
            cursor.execute("DELETE FROM contracts WHERE id = ?", (contract_id,))
            cursor.execute("UPDATE properties SET status = 'available' WHERE id = ?", (property_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return RedirectResponse(url="/dashboard/contracts", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في حذف العقد: {str(e)}")
