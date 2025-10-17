from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok", "message": "🛡️ Guardian API is running!"}

@app.post("/whatsapp")
async def whatsapp(request: Request):
    data = await request.json()
    phone = data.get("phone")
    message = data.get("message")
    print(f"📩 Message to {phone}: {message}")
    return JSONResponse(content={"sent": True, "to": phone, "message": message})
