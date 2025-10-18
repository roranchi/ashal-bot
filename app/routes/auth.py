from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
import hashlib

router = APIRouter()
security = HTTPBasic()

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """التحقق من بيانات المستخدم"""
    username_correct = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    password_hash = hashlib.sha256(credentials.password.encode()).hexdigest()
    password_correct = secrets.compare_digest(password_hash, ADMIN_PASSWORD_HASH)
    
    if not (username_correct and password_correct):
        raise HTTPException(
            status_code=401,
            detail="خطأ في اسم المستخدم أو كلمة المرور",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
