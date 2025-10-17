from fastapi import APIRouter, HTTPException
from app.db.database import get_connection

router = APIRouter()

@router.get("/api/properties")
async def get_properties():
    """الحصول على قائمة العقارات"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM properties LIMIT 100")
        properties = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"status": "success", "data": properties}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/tenants")
async def get_tenants():
    """الحصول على قائمة المستأجرين"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tenants LIMIT 100")
        tenants = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"status": "success", "data": tenants}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/contracts")
async def get_contracts():
    """الحصول على قائمة العقود"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contracts LIMIT 100")
        contracts = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"status": "success", "data": contracts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/stats")
async def get_stats():
    """إحصائيات عامة"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM properties")
        stats['properties_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tenants")
        stats['tenants_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contracts")
        stats['contracts_count'] = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
