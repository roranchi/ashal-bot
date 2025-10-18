from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os, logging, psycopg2
from dotenv import load_dotenv

# --- استيراد الداشبورد ---
from app.routes.dashboard import router as dashboard_router
# --- نهاية استيراد الداشبورد ---

# استيراد الروترات القديمة (لن نكررها)
from app.routes.contract_handler import router as contract_router
from app.routes.contract_handler_fixed import router as contract_fixed_router
from app.routes.maintenance_handler import router as maintenance_router
from app.routes.payment_handler import router as payment_router
from app.routes.webhook import router as webhook_router
from app.routes.api_routes import router as api_router
from app.routes.auth import router as auth_router
from app.routes.endpoints.send_message import router as send_message_router
from app.routes.endpoints.contracts import router as contracts_router
from app.routes.endpoints.payments import router as payments_router


load_dotenv()
app = FastAPI(title="Ashal Bot API", version="2.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mount static files (إذا كان لديك مجلد باسم 'static' بجانب 'app')
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- تهيئة لوحة تحكم FastAPI-Admin ---
@app.on_event("startup")
async def startup_event():
    logger.info("... بدء تهيئة FastAPI-Admin")
# --- نهاية تهيئة لوحة تحكم FastAPI-Admin ---

# Register all Routers
routers = [
    contract_router,
    contract_fixed_router,
    maintenance_router,
    payment_router,
    webhook_router,
    api_router,
    auth_router,
    dashboard_router,
    send_message_router,
    contracts_router,
    payments_router
]

for r in routers:
    app.include_router(r)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Ashal Bot FastAPI is running"}

@app.on_event("startup")
def connect_db_legacy():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        logger.info("✅ اتصال قاعدة البيانات ناجح!")
        conn.close()
    except Exception as e:
        logger.error(f"❌ فشل الاتصال بقاعدة البيانات: {e}")

# Properties routes
from app.routes.properties import router as properties_router
app.include_router(properties_router, prefix="/dashboard/properties", tags=["Properties"])

# Tenants routes
from app.routes.tenants import router as tenants_router
app.include_router(tenants_router, prefix="/dashboard/tenants", tags=["Tenants"])

# Tenants routes
from app.routes.tenants import router as tenants_router
app.include_router(tenants_router, prefix="/dashboard/tenants", tags=["Tenants"])

# Contracts routes - استبدل المسار القديم
from app.routes.contracts import router as contracts_router_new
app.include_router(contracts_router_new, prefix="/dashboard/contracts", tags=["Contracts Dashboard"])

# Payments Dashboard routes
from app.routes.payments_dashboard import router as payments_dash_router
app.include_router(payments_dash_router, prefix="/dashboard/payments", tags=["Payments Dashboard"])
