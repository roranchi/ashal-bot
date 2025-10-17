from fastapi import FastAPI, Depends, Request
import os, logging
from dotenv import load_dotenv
from app.db.models.base import engine, Base
from app.admin import startup_admin
from fastapi_admin.app import FastAPIAdmin

# (اختياري) تأكد من أن هذه الاستيرادات موجودة إذا كنت تحتاج للـ API Routers الأساسية
# from app.routes.api_routes import router as api_router
# from app.routes.webhook import router as webhook_router

load_dotenv()

app = FastAPI(title="Ashal Bot API - Core", version="2.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- دمج FastAPI Admin ---
@app.on_event("startup")
async def startup_event():
    # Base.metadata.create_all(bind=engine) # استخدم هذا السطر فقط إذا كنت متأكداً من أن الجداول غير موجودة
    await startup_admin()
    app.mount("/admin", FastAPIAdmin(engine=engine), name="admin")
    logger.info("✅ FastAPI Admin جاهز: /admin")

# --- Endpoints الأساسية ---
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Ashal Bot FastAPI is running, Admin panel is active."}

# *****************************************************************
# NOTE: إذا كان لديك Routers أساسية أخرى (مثل /webhook, /api/stats, /send-message)
# يجب استيرادها وإضافتها هنا (باستخدام app.include_router)
# مثال:
# app.include_router(api_router, prefix="/api")
# app.include_router(webhook_router, prefix="/webhook")
# *****************************************************************
