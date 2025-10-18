from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db.database import get_connection
from app.routes.auth import verify_credentials
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def list_properties(request: Request, username: str = Depends(verify_credentials)):
    """قائمة العقارات"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.id, p.name, p.address, p.type, p.status, 
                   p.rent_amount, c.name as client_name
            FROM properties p
            LEFT JOIN clients c ON p.client_id = c.id
            ORDER BY p.created_at DESC
        """)
        properties = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return templates.TemplateResponse("dashboard/properties/list.html", {
            "request": request,
            "properties": properties,
            "username": username
        })
    except Exception as e:
        return templates.TemplateResponse("dashboard/properties/list.html", {
            "request": request,
            "properties": [],
            "username": username,
            "error": str(e)
        })

@router.get("/add", response_class=HTMLResponse)
async def add_property_form(request: Request, username: str = Depends(verify_credentials)):
    """صفحة إضافة عقار"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # جلب قائمة العملاء
        cursor.execute("SELECT id, name FROM clients ORDER BY name")
        clients = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return templates.TemplateResponse("dashboard/properties/add.html", {
            "request": request,
            "clients": clients,
            "username": username
        })
    except Exception as e:
        return templates.TemplateResponse("dashboard/properties/add.html", {
            "request": request,
            "clients": [],
            "username": username,
            "error": str(e)
        })

@router.post("/add")
async def add_property(
    name: str = Form(...),
    address: str = Form(...),
    property_type: str = Form(...),
    rent_amount: float = Form(...),
    client_id: Optional[int] = Form(None),
    rooms: Optional[int] = Form(None),
    bathrooms: Optional[int] = Form(None),
    area: Optional[float] = Form(None),
    floor: Optional[int] = Form(None),
    notes: Optional[str] = Form(None),
    username: str = Depends(verify_credentials)
):
    """إضافة عقار جديد"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO properties 
            (name, address, type, rent_amount, client_id, rooms, bathrooms, 
             area, floor, status, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'available', ?, datetime('now'))
        """, (name, address, property_type, rent_amount, client_id, 
              rooms, bathrooms, area, floor, notes))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return RedirectResponse(url="/dashboard/properties", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في إضافة العقار: {str(e)}")

@router.get("/{property_id}", response_class=HTMLResponse)
async def view_property(property_id: int, request: Request, username: str = Depends(verify_credentials)):
    """عرض تفاصيل عقار"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, c.name as client_name, c.phone as client_phone
            FROM properties p
            LEFT JOIN clients c ON p.client_id = c.id
            WHERE p.id = ?
        """, (property_id,))
        property_data = cursor.fetchone()
        
        if not property_data:
            raise HTTPException(status_code=404, detail="العقار غير موجود")
        
        # جلب العقود المرتبطة
        cursor.execute("""
            SELECT c.*, t.name as tenant_name
            FROM contracts c
            LEFT JOIN tenants t ON c.tenant_id = t.id
            WHERE c.property_id = ?
            ORDER BY c.start_date DESC
        """, (property_id,))
        contracts = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return templates.TemplateResponse("dashboard/properties/view.html", {
            "request": request,
            "property": property_data,
            "contracts": contracts,
            "username": username
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{property_id}/delete")
async def delete_property(property_id: int, username: str = Depends(verify_credentials)):
    """حذف عقار"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM properties WHERE id = ?", (property_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return RedirectResponse(url="/dashboard/properties", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في حذف العقار: {str(e)}")
