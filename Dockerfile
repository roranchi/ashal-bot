FROM python:3.11-slim
WORKDIR /app
# تثبيت الاعتماديات النظامية وتثبيت curl
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*
# نسخ requirements.txt أولاً (لتحسين caching)
COPY requirements.txt .
# تثبيت مكتبات Python في خطوة واحدة
RUN pip install --no-cache-dir -r requirements.txt
# نسخ كامل المشروع
COPY . .
# إنشاء مجلد اللوغز
RUN mkdir -p logs
# ضبط PYTHONPATH بشكل صحيح
ENV PYTHONPATH=/app
# تشغيل التطبيق
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5001", "--reload"]
