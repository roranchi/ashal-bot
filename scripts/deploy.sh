#!/bin/bash

echo "🚀 بدء نشر ASHAL Bot على DigitalOcean..."

# التحقق من وجود Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker غير مثبت"
    exit 1
fi

# بناء الصورة
echo "📦 جاري بناء Docker image..."
docker-compose -f docker-compose.prod.yml build

# تشغيل الخدمات
echo "🐳 جاري تشغيل الخدمات..."
docker-compose -f docker-compose.prod.yml up -d

echo "✅ تم النشر بنجاح!"
echo "📍 التطبيق يعمل على: http://your-server-ip"
echo "🔧 للتحقق من السجلات: docker logs ashal-bot"
