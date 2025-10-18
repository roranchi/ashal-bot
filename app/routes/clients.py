from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.db.database import get_connection
from app.routes.auth import verify_credentials
from models.client import ClientCreate, ClientUpdate
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def list_clients(request: Request, username: str = Depends(verify_credentials)):
    """قائمة العملاء"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, email, phone, address, notes, created_at, updated_at 
            FROM clients 
            ORDER BY created_at DESC
        """)
        clients = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return templates.TemplateResponse("dashboard/clients/list.html", {
            "request": request,
            "clients": clients,
            "username": username
        })
    except Exception as e:
        return templates.TemplateResponse("dashboard/clients/list.html", {
            "request": request,
            "clients": [],
            "username": username,
            "error": str(e)
        })

@router.get("/add", response_class=HTMLResponse)
async def add_client_form(request: Request, username: str = Depends(verify_credentials)):
    """صفحة إضافة عميل"""
    return templates.TemplateResponse("dashboard/clients/add.html", {
        "request": request,
        "username": username
    })

@router.post("/add")
async def add_client(
    client: ClientCreate = Depends(),
    username: str = Depends(verify_credentials)
):
    """إضافة عميل جديد"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO clients (name, email, phone, address, notes, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id
        """, (client.name, client.email, client.phone, client.address, client.notes))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return RedirectResponse(url="/dashboard/clients", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في إضافة العميل: {str(e)}")

@router.get("/{client_id}", response_class=HTMLResponse)
async def view_client(client_id: int, request: Request, username: str = Depends(verify_credentials)):
    """عرض تفاصيل عميل"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, email, phone, address, notes, created_at, updated_at FROM clients WHERE id = %s", (client_id,))
        client = cursor.fetchone()
        
        if not client:
            raise HTTPException(status_code=404, detail="العميل غير موجود")
        
        cursor.execute("SELECT id, name, address, type, status FROM properties WHERE client_id = %s", (client_id,))
        properties = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return templates.TemplateResponse("dashboard/clients/view.html", {
            "request": request,
            "client": client,
            "properties": properties,
            "username": username
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{client_id}/edit", response_class=HTMLResponse)
async def edit_client_form(client_id: int, request: Request, username: str = Depends(verify_credentials)):
    """صفحة تعديل عميل"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, email, phone, address, notes FROM clients WHERE id = %s", (client_id,))
        client = cursor.fetchone()
        
        if not client:
            raise HTTPException(status_code=404, detail="العميل غير موجود")
        
        cursor.close()
        conn.close()
        
        return templates.TemplateResponse("dashboard/clients/edit.html", {
            "request": request,
            "client": client,
            "username": username
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{client_id}/edit")
async def edit_client(
    client_id: int,
    client: ClientUpdate = Depends(),
    username: str = Depends(verify_credentials)
):
    """تعديل عميل"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        update_fields = []
        update_values = []
        
        if client.name:
            update_fields.append("name = %s")
            update_values.append(client.name)
        if client.email is not None:
            update_fields.append("email = %s")
            update_values.append(client.email)
        if client.phone:
            update_fields.append("phone = %s")
            update_values.append(client.phone)
        if client.address is not None:
            update_fields.append("address = %s")
            update_values.append(client.address)
        if client.notes is not None:
            update_fields.append("notes = %s")
            update_values.append(client.notes)
        
        if update_fields:
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            update_values.append(client_id)
            
            query = f"UPDATE clients SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(query, update_values)
            conn.commit()
        
        cursor.close()
        conn.close()
        
        return RedirectResponse(url=f"/dashboard/clients/{client_id}", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في تعديل العميل: {str(e)}")

@router.post("/{client_id}/delete")
async def delete_client(client_id: int, username: str = Depends(verify_credentials)):
    """حذف عميل"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM clients WHERE id = %s", (client_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return RedirectResponse(url="/dashboard/clients", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في حذف العميل: {str(e)}")
