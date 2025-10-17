from fastapi import APIRouter, HTTPException
from app.db.database import get_connection
from typing import Optional

router = APIRouter()

@router.get("/contracts")
async def get_contracts(limit: Optional[int] = 100):
    """الحصول على قائمة العقود"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM contracts LIMIT {limit}")
        contracts = cursor.fetchall()
        cursor.close()
        conn.close()
        return {
            "status": "success",
            "data": contracts,
            "count": len(contracts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contracts/{contract_id}")
async def get_contract(contract_id: int):
    """الحصول على تفاصيل عقد محدد"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contracts WHERE id = ?", (contract_id,))
        contract = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not contract:
            raise HTTPException(status_code=404, detail="العقد غير موجود")
        
        return {"status": "success", "data": contract}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contracts/expiring/soon")
async def get_expiring_contracts(days: Optional[int] = 30):
    """الحصول على العقود القريبة من الانتهاء"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM contracts 
            WHERE end_date <= date('now', '+' || ? || ' days')
            AND end_date >= date('now')
        """, (days,))
        contracts = cursor.fetchall()
        cursor.close()
        conn.close()
        return {
            "status": "success",
            "data": contracts,
            "count": len(contracts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
