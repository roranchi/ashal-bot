from flask import Flask, jsonify
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# الواجهات الأساسية فقط
@app.route("/ai-agent/health", methods=["GET"])
def ai_agent_health():
    return jsonify({"status": "active", "monitoring": "silent"})

@app.route("/ai-agent/report", methods=["GET"])  
def ai_agent_report():
    return jsonify({"message": "AI Agent is monitoring"})

@app.route("/guardian/analyze", methods=["GET"])
def guardian_analyze():
    return jsonify({"message": "Guardian analysis ready"})

if __name__ == "__main__":
    app.run(debug=True)
