from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.routes.auth import verify_credentials
from app.db.database import get_connection

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request, username: str = Depends(verify_credentials)):
    """الصفحة الرئيسية للوحة التحكم"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # إحصائيات بسيطة
        cursor.execute("SELECT COUNT(*) FROM clients")
        total_clients = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM properties")
        total_properties = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return templates.TemplateResponse("dashboard/index.html", {
            "request": request,
            "username": username,
            "total_clients": total_clients,
            "total_properties": total_properties
        })
    except Exception as e:
        return templates.TemplateResponse("dashboard/index.html", {
            "request": request,
            "username": username,
            "total_clients": 0,
            "total_properties": 0,
            "error": str(e)
        })
