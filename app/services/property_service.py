from datetime import datetime, timedelta

DB_FILE = "property.db"

def create_tables():
    cursor = conn.cursor()

    # جدول المباني
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS buildings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT,
        system_type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # جدول المستأجرين
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tenants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        building_id INTEGER,
        payment_method TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(building_id) REFERENCES buildings(id)
    )
    """)

    # جدول العقود
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_id INTEGER,
        start_date DATE,
        end_date DATE,
        reminder_30days BOOLEAN DEFAULT 1,
        reminder_7days BOOLEAN DEFAULT 1,
        reminder_90days BOOLEAN DEFAULT 1,
        active BOOLEAN DEFAULT 1,
        FOREIGN KEY(tenant_id) REFERENCES tenants(id)
    )
    """)

    # جدول المدفوعات
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_id INTEGER,
        amount REAL,
        payment_date DATE,
        method TEXT,
        status TEXT,
        FOREIGN KEY(tenant_id) REFERENCES tenants(id)
    )
    """)

    # جدول الصيانة
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_id INTEGER,
        description TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(tenant_id) REFERENCES tenants(id)
    )
    """)

    conn.commit()
    conn.close()
    print("✅ جميع الجداول جاهزة!")

# ---- وظائف النظام ----

def add_building(name, address, system_type):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO buildings (name, address, system_type) VALUES (?, ?, ?)",
                   (name, address, system_type))
    conn.commit()
    conn.close()

def add_tenant(name, phone, building_id, payment_method):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tenants (name, phone, building_id, payment_method) VALUES (?, ?, ?, ?)",
                   (name, phone, building_id, payment_method))
    conn.commit()
    conn.close()

def add_contract(tenant_id, start_date, end_date):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO contracts (tenant_id, start_date, end_date) VALUES (?, ?, ?)",
                   (tenant_id, start_date, end_date))
    conn.commit()
    conn.close()

def add_payment(tenant_id, amount, payment_date, method, status="pending"):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO payments (tenant_id, amount, payment_date, method, status) VALUES (?, ?, ?, ?, ?)",
                   (tenant_id, amount, payment_date, method, status))
    conn.commit()
    conn.close()

def add_maintenance(tenant_id, description, status="open"):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO maintenance (tenant_id, description, status) VALUES (?, ?, ?)",
                   (tenant_id, description, status))
    conn.commit()
    conn.close()

# ---- تصنيفات المستأجرين ----

def classify_tenants():
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, payment_method FROM tenants")
    tenants = cursor.fetchall()
    result = {"cash": [], "check": [], "transfer": [], "needs_followup": []}
    for t in tenants:
        if t[2].lower() == "cash":
            result["cash"].append(t[1])
        elif t[2].lower() == "check":
            result["check"].append(t[1])
        elif t[2].lower() == "transfer":
            result["transfer"].append(t[1])
        else:
            result["needs_followup"].append(t[1])
    conn.close()
    return result

# ---- تذكيرات العقود ----

def contract_reminders():
    today = datetime.today().date()
    reminder_30 = today + timedelta(days=30)
    reminder_7 = today + timedelta(days=7)
    cursor = conn.cursor()
    cursor.execute("SELECT tenants.name, contracts.end_date FROM contracts JOIN tenants ON tenants.id = contracts.tenant_id WHERE contracts.active = 1")
    contracts = cursor.fetchall()
    reminders = {"30_days": [], "7_days": []}
    for name, end_date in contracts:
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        if end_date_dt == reminder_30:
            reminders["30_days"].append(name)
        if end_date_dt == reminder_7:
            reminders["7_days"].append(name)
    conn.close()
    return reminders

# ---- تقارير ----

def report_daily():
    today = datetime.today().date()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments WHERE payment_date = ?", (today,))
    daily_payments = cursor.fetchall()
    conn.close()
    return daily_payments

def report_weekly():
    today = datetime.today().date()
    start_week = today - timedelta(days=today.weekday())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments WHERE payment_date BETWEEN ? AND ?", (start_week, today))
    weekly_payments = cursor.fetchall()
    conn.close()
    return weekly_payments

def report_monthly():
    today = datetime.today().date()
    start_month = today.replace(day=1)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments WHERE payment_date BETWEEN ? AND ?", (start_month, today))
    monthly_payments = cursor.fetchall()
    conn.close()
    return monthly_payments

# ---- تشغيل النظام ----
if __name__ == "__main__":
    print("🔹 بدء تشغيل النظام...")
    create_tables()
    print("🚀 النظام يعمل! يمكنك الآن إضافة بيانات وتجربة الوظائف.")