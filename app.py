import os, requests, engine
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from duckduckgo_search import DDGS

app = Flask(__name__)

# إعداداتك الخاصة
TELEGRAM_TOKEN = "8256002438:AAFoyPHxDUyKX_twpy0YVk2Klyg49B6v_l8"
CHAT_ID = "8323244727"
OPEN_API_KEY = os.getenv("OPENROUTER_API_KEY")

def analyze_and_predict(text):
    # استخدام المحرك السريع بدلاً من Mojo مؤقتاً
    spike = engine.get_spike_score(text)
    
    if spike > 0.8: # إذا كان الاحتمال قوياً
        headers = {"Authorization": f"Bearer {OPEN_API_KEY}"}
        payload = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [{"role": "user", "content": f"تحليل عاجل للمباراة: {text}"}]
        }
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        return res.json()['choices'][0]['message']['content']
    return None

def job():
    with DDGS() as ddgs:
        results = list(ddgs.text("football live scores predictions", timelimit='d'))[:3]
        for r in results:
            analysis = analyze_and_predict(r['body'])
            if analysis:
                msg = f"🚨 *توقع ذكي (Spike Active):*\n{analysis}"
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                              json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

scheduler = BackgroundScheduler()
scheduler.add_job(job, 'interval', minutes=10)
scheduler.start()

@app.route('/')
def home(): return "🤖 Fast-Python Radar is Active!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
