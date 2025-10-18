# 📚 توثيق مشروع أسهل - نظام إدارة العقارات

## 📋 نظرة عامة
- **اسم المشروع:** أسهل (Ashal)
- **النوع:** نظام إدارة عقارات ذكي
- **التقنيات:** FastAPI + PostgreSQL (Supabase) + Docker
- **الحالة:** ✅ Dashboard مكتمل 90%

---

## 🌐 معلومات السيرفر

| المعلومة | القيمة |
|----------|--------|
| **IP** | `64.226.85.15` |
| **Port** | `5001` |
| **Dashboard** | `http://64.226.85.15:5001/dashboard/` |
| **API Docs** | `http://64.226.85.15:5001/docs` |
| **Container** | `ashal-bot-ashal-bot-1` |
| **Login** | admin / admin123 |

---

## 🗂️ بنية المشروع
```
/opt/ashal-bot/
├── app/
│   ├── main.py                    # نقطة الدخول الرئيسية
│   ├── routes/                    # جميع الـ endpoints
│   │   ├── auth.py               # نظام المصادقة (HTTP Basic Auth)
│   │   ├── dashboard.py          # الصفحة الرئيسية
│   │   ├── clients.py            # إدارة العملاء ✅
│   │   ├── properties.py         # إدارة العقارات ✅
│   │   ├── tenants.py            # إدارة المستأجرين ✅
│   │   ├── contracts.py          # إدارة العقود ✅
│   │   └── payments_dashboard.py # إدارة المدفوعات ✅
│   ├── db/
│   │   └── database.py           # اتصال قاعدة البيانات
│   ├── services/                 # منطق العمل
│   └── templates/                # صفحات HTML
│       └── dashboard/
│           ├── base.html         # القالب الأساسي (Goth Dark Theme)
│           ├── clients/
│           ├── properties/
│           ├── tenants/
│           ├── contracts/
│           └── payments/
├── Dockerfile
├── requirements.txt
└── .env                          # متغيرات البيئة
```

---

## 🔑 معلومات قاعدة البيانات (Supabase)
```env
DATABASE_URL=postgresql://postgres.udvmhyxihqmraknmwvei:Pyfpuk-wozbyd-0taktu@aws-1-eu-north-1.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://udvmhyxihqmraknmwvei.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkdm1oeXhpaHFtcmFrbm13dmVpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1NDcxNTgsImV4cCI6MjA3MzEyMzE1OH0.wMF7CX98rNbqyrPnf8Yu6QRFIdCENgnA4DBChDJl9N4
```

**⚠️ مهم:** استخدم Transaction Pooler (Port 6543) وليس Direct Connection!

---

## 📊 الجداول في قاعدة البيانات

### 1. `clients` (العملاء/المالكين)
```sql
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT NOT NULL,
    address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2. `properties` (العقارات)
```sql
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    type TEXT,  -- apartment, villa, office, etc.
    rent_amount DECIMAL(10,2),
    client_id INTEGER REFERENCES clients(id),
    rooms INTEGER,
    bathrooms INTEGER,
    area DECIMAL(10,2),
    floor INTEGER,
    status TEXT DEFAULT 'available',  -- available, rented, maintenance
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3. `tenants` (المستأجرين)
```sql
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    national_id TEXT,
    address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4. `contracts` (العقود)
```sql
CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id),
    property_id INTEGER REFERENCES properties(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    rent_amount DECIMAL(10,2) NOT NULL,
    deposit_amount DECIMAL(10,2),
    payment_day INTEGER,
    status TEXT DEFAULT 'active',  -- active, expired
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 5. `payments` (المدفوعات)
```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id),
    property_id INTEGER REFERENCES properties(id),
    amount DECIMAL(10,2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method TEXT,  -- cash, bank_transfer, cheque, online
    status TEXT DEFAULT 'completed',  -- completed, pending, cancelled
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🎨 التصميم الحالي

**Theme:** Dark Goth Modern
- 🌑 خلفية سوداء متدرجة
- 💜 ألوان بنفسجية (Purple: #8b5cf6)
- 🟡 ألوان ذهبية (Gold: #fbbf24)
- ✨ Glassmorphism effects
- 🎭 Glow shadows

**المكتبات:**
- Tailwind CSS 3.x
- Alpine.js 3.x (للتفاعلية)
- Chart.js (الرسوم البيانية)
- Font Awesome 6.4 (الأيقونات)
- Google Fonts: Tajawal (عربي) + Orbitron (إنجليزي)

---

## 🔧 أوامر Docker الأساسية

### إعادة بناء وتشغيل:
```bash
docker rm -f ashal-bot-ashal-bot-1 && \
docker build -t ashal-bot-ashal-bot /opt/ashal-bot && \
docker run -d \
  --name ashal-bot-ashal-bot-1 \
  -p 5001:5001 \
  -e DATABASE_URL="postgresql://postgres.udvmhyxihqmraknmwvei:Pyfpuk-wozbyd-0taktu@aws-1-eu-north-1.pooler.supabase.com:6543/postgres" \
  ashal-bot-ashal-bot
```

### عرض اللوقات:
```bash
docker logs -f ashal-bot-ashal-bot-1
```

### إيقاف:
```bash
docker stop ashal-bot-ashal-bot-1
```

### الدخول للـ Container:
```bash
docker exec -it ashal-bot-ashal-bot-1 bash
```

---

## ✅ الصفحات المكتملة

| الصفحة | المسار | الحالة | الوصف |
|--------|--------|--------|-------|
| Dashboard | `/dashboard/` | ✅ | الصفحة الرئيسية + إحصائيات |
| العملاء | `/dashboard/clients` | ✅ | قائمة، إضافة، عرض، حذف |
| العقارات | `/dashboard/properties` | ✅ | قائمة، إضافة، عرض، حذف |
| المستأجرين | `/dashboard/tenants` | ✅ | قائمة، إضافة، عرض، حذف |
| العقود | `/dashboard/contracts` | ✅ | قائمة، إضافة، عرض، حذف |
| المدفوعات | `/dashboard/payments` | ✅ | قائمة، إضافة، حذف |

---

## 🔄 الصفحات المطلوبة (لم تُبنَ بعد)

- 🔄 `/dashboard/messages` - رسائل WhatsApp
- 🔄 `/dashboard/reports` - التقارير
- 🔄 `/dashboard/settings` - الإعدادات
- 🔄 صفحة عرض تفاصيل العميل
- 🔄 صفحة عرض تفاصيل العقار
- 🔄 صفحة تعديل (Edit) لكل entity

---

## 🐛 المشاكل المعروفة والحلول

### 1. Port مشغول:
```bash
kill -9 $(lsof -ti:5001)
docker rm -f ashal-bot-ashal-bot-1
```

### 2. خطأ في الـ imports:
- ✅ تم حلها: جميع الـ imports تبدأ بـ `app.`
- مثال: `from app.routes.auth import verify_credentials`

### 3. FastAPI-Admin error:
- ✅ تم حلها: حذف السطر من `main.py`

---

## 📝 ملاحظات مهمة للمطور القادم

1. **الاستيرادات:** كل import يجب أن يبدأ بـ `app.`
2. **قاعدة البيانات:** استخدم `get_connection()` من `app.db.database`
3. **Templates:** كلها في `/opt/ashal-bot/templates/dashboard/`
4. **Authentication:** HTTP Basic Auth في `app/routes/auth.py`
5. **التصميم:** base.html يحتوي على Sidebar + Top Bar + Styles

---

## 🎯 الخطوات التالية (Priority)

### قصيرة المدى (أسبوع):
1. ✅ إضافة صفحة View كاملة لكل entity
2. ✅ إضافة صفحة Edit لكل entity
3. ✅ صفحة الإعدادات (Settings)
4. ✅ صفحة رسائل WhatsApp

### متوسطة المدى (شهر):
1. 🔄 تفعيل WhatsApp Business API
2. 🔄 نظام الإشعارات التلقائية
3. 🔄 التقارير (Excel/PDF Export)
4. 🔄 تحسين UX/UI

### طويلة المدى (3 أشهر):
1. 🔄 نظام Multi-tenancy (صلاحيات للمالكين)
2. 🔄 تطبيق موبايل
3. 🔄 AI Chatbot

---

## 🆘 في حالة الطوارئ

### المشروع لا يعمل؟
```bash
# 1. تحقق من الـ Container
docker ps -a | grep ashal

# 2. شاهد اللوقات
docker logs ashal-bot-ashal-bot-1

# 3. أعد البناء من الصفر
docker system prune -af
cd /opt/ashal-bot
docker build -t ashal-bot-ashal-bot .
docker run -d --name ashal-bot-ashal-bot-1 -p 5001:5001 \
  -e DATABASE_URL="postgresql://postgres.udvmhyxihqmraknmwvei:Pyfpuk-wozbyd-0taktu@aws-1-eu-north-1.pooler.supabase.com:6543/postgres" \
  ashal-bot-ashal-bot
```

### قاعدة البيانات لا تستجيب؟
- تحقق من Supabase Dashboard
- جرب Direct Connection (Port 5432)
- تحقق من الـ Connection String

---

## 📞 معلومات الاتصال

- **المالك:** أنت
- **السيرفر:** DigitalOcean - `64.226.85.15`
- **قاعدة البيانات:** Supabase
- **المشروع:** `/opt/ashal-bot/`

---

**آخر تحديث:** 18 أكتوبر 2025  
**الحالة:** 🟢 يعمل بنجاح
