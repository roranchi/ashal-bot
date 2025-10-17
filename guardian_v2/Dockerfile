FROM python:3.9-slim

WORKDIR /app

# نسخ المتطلبات أولاً (لتحسين caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY . .

# إنشاء مستخدم غير root
RUN useradd -m -u 1000 guardian
USER guardian

EXPOSE 8000

CMD ["python", "app/main.py"]
