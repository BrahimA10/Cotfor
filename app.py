import os
import requests
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from duckduckgo_search import DDGS
from datetime import datetime

app = Flask(__name__)

# === إعدادات البوت الأساسية === #
TELEGRAM_TOKEN = "8256002438:AAFoyPHxDUyKX_twpy0YVk2Klyg49B6v_l8"
CHAT_ID = "8323244727"
OPEN_API_KEY = os.getenv("OPENROUTER_API_KEY")

# === نظام حماية مبسط === #
SENT_REQUESTS = []

def get_live_matches():
    """جلب أحدث المباريات الحية باستخدام بحث اليوم فقط"""
    today = datetime.now().strftime("%Y-%m-%d")
    query = f"football live scores matches {today}"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, timelimit='d'))
            return results[:3] 
    except:
        return []

def analyze_match_data(prompt):
    """تحليل البيانات باستخدام الذكاء الاصطناعي"""
    headers = {
        "Authorization": f"Bearer {OPEN_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=25)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Error API: {response.status_code}"
    except:
        return "فشل الاتصال بالذكاء الاصطناعي"

def send_telegram(msg):
    """إرسال مباشر بدون بروكسي"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=15)
        return "OK"
    except:
        return "فشل إرسال تلجرام"

def execute_football_scan():
    if not OPEN_API_KEY: return "مفتاح API مفقود"
    matches = get_live_matches()
    if not matches:
        return send_telegram("⚠️ لا توجد مباريات حية حالياً للتحليل.")
    
    full_report = f"🕔 **تحديث الرادار:** {datetime.now().strftime('%H:%M')}\n"
    for match in matches:
        prompt = f"حلل وضع هذه المباراة وتوقع هدفاً وشيكاً: {match.get('body', '')[:500]}"
        analysis = analyze_match_data(prompt)
        full_report += f"\n⚽ *{match.get('title', 'Match')}*\n{analysis}\n"
    
    return send_telegram(full_report)

# === جدولة المهام === #
scheduler = BackgroundScheduler()
scheduler.add_job(execute_football_scan, 'interval', minutes=10)
scheduler.start()

@app.route('/')
def home():
    return "🤖 Radar is Running on Render!"

@app.route('/trigger-scan')
def manual_trigger():
    execute_football_scan()
    return "✅ Scan Triggered and Sent to Telegram!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
