import os
import requests
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from duckduckgo_search import DDGS
from datetime import datetime

app = Flask(__name__)

# === الإعدادات (تأكد من صحتها في Koyeb) ===
TELEGRAM_TOKEN = "8256002438:AAFoyPHxDUyKX_twpy0YVk2Klyg49B6v_l8"
CHAT_ID = "8323244727"
OPEN_API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_football_data(query_type="live"):
    """جلب بيانات المباريات حسب النوع (حية أو قادمة)"""
    today = datetime.now().strftime("%Y-%m-%d")
    if query_type == "live":
        query = f"football live scores now {today}"
    else:
        query = f"football matches schedule today {today} predictions"
        
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(query, timelimit='d'))[:4]
    except:
        return []

def analyze_with_ai(prompt):
    """الاستعانة بـ DeepSeek للتحليل"""
    if not OPEN_API_KEY:
        return "⚠️ مفتاح API مفقود في إعدادات Koyeb"
        
    headers = {
        "Authorization": f"Bearer {OPEN_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://koyeb.com"
    }
    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                                 headers=headers, json=payload, timeout=40)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"⚠️ عذراً، المحرك مشغول (خطأ: {response.status_code})"
    except:
        return "❌ فشل الاتصال بالمحلل الذكي"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=15)
    except:
        pass

# --- 1. وظيفة تحليل مباريات اليوم (قبل البدء) ---
def pre_match_analysis():
    matches = get_football_data(query_type="upcoming")
    if not matches: return
    
    report = "🔮 **توقعات مباريات اليوم قبل الانطلاق:**\n"
    for m in matches:
        prompt = f"حلل المباراة القادمة: {m['title']}. البيانات: {m['body']}. توقع النتيجة النهائية ونسبة الفوز."
        analysis = analyze_with_ai(prompt)
        report += f"\n🏟️ *{m['title']}*\n{analysis}\n---"
    send_telegram(report)

# --- 2. وظيفة التحليل المباشر (أثناء المباراة) ---
def live_match_analysis():
    matches = get_football_data(query_type="live")
    if not matches: return
    
    for m in matches:
        prompt = f"حلل المباراة الحالية: {m['title']}. الأحداث: {m['body']}. هل هناك هدف وشيك؟ ومن المسيطر؟"
        analysis = analyze_with_ai(prompt)
        if "هدف" in analysis or "ضغط" in analysis:
            alert = f"🚨 **تنبيه لايف:** *{m['title']}*\n{analysis}"
            send_telegram(alert)

# === جدولة المهام ===
scheduler = BackgroundScheduler()
# فحص المباريات القادمة كل 4 ساعات
scheduler.add_job(pre_match_analysis, 'interval', hours=4)
# فحص المباريات الحية كل 10 دقائق
scheduler.add_job(live_match_analysis, 'interval', minutes=10)
scheduler.start()

@app.route('/')
def home():
    return "🤖 Dual Radar (Pre-match & Live) is Active!"

@app.route('/trigger-all')
def manual_trigger():
    pre_match_analysis()
    live_match_analysis()
    return "✅ تم تفعيل الفحص الشامل (قادم + لايف)!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
