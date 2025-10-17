#!/bin/bash

echo "🛠️  إعداد سيرفر DigitalOcean لـ ASHAL Bot..."

# تحديث النظام
echo "🔄 تحديث النظام..."
apt-get update && apt-get upgrade -y

# تثبيت Docker
echo "🐳 تثبيت Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# تثبيت Docker Compose
echo "📦 تثبيت Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# إعداد مجموعة Docker
echo "👥 إعداد مجموعة Docker..."
usermod -aG docker $USER

# إنشاء مجلدات التطبيق
echo "📁 إنشاء مجلدات التطبيق..."
mkdir -p /opt/ashal-bot/{logs,data,ssl}
chmod -R 755 /opt/ashal-bot

echo "✅ تم إعداد السيرفر بنجاح!"
echo "📍 الخطوات التالية:"
echo "   1. انسخي ملفات التطبيق إلى /opt/ashal-bot"
echo "   2. عدلي ملف .env.production بالإعدادات الحقيقية"
echo "   3. شغلي ./deploy.sh"
