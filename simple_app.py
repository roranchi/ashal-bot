from flask import Flask, render_template
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def dashboard():
    try:
        stats = {
            "total_tenants": supabase.table("tenants").select("*").execute().count,
            "total_properties": supabase.table("properties").select("*").execute().count,
            "active_contracts": supabase.table("contracts").select("*").eq("status", "active").execute().count,
            "pending_maintenance": supabase.table("maintenance").select("*").eq("status", "pending").execute().count,
            "overdue_payments": supabase.table("payments").select("*").lt("due_date", "now()").execute().count,
        }

        recent_activity = supabase.table("activity_logs").select("*").order("timestamp", desc=True).limit(10).execute().data

    except Exception as e:
        stats = {}
        recent_activity = []
        print("Error fetching data:", e)

    return render_template("dashboard.html", stats=stats, recent_activity=recent_activity)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
