FROM python:3.11-slim

WORKDIR /app

# تثبيت الاعتماديات النظامية
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# نسخ requirements.txt أولاً (لتحسين caching)
COPY requirements.txt .

# تثبيت مكتبات Python
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كامل المشروع (بما فيهم مجلد app)
COPY . .

# إنشاء مجلد اللوغز
RUN mkdir -p logs

# إضافة المسار الصحيح لـ Python
ENV PYTHONPATH=/app

# تشغيل التطبيق
CMD ["python", "app/main.py"]
