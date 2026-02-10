import os
import requests
import engine
import logging
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from duckduckgo_search import DDGS
from datetime import datetime

# --- إعداد نظام المراقبة المتقدم ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [RADAR_CORE] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- الإعدادات السيادية ---
TELEGRAM_TOKEN = "8256002438:AAFoyPHxDUyKX_twpy0YVk2Klyg49B6v_l8"
CHAT_ID = "8323244727"
OPEN_API_KEY = os.getenv("OPENROUTER_API_KEY")

def send_telegram_alert(message):
    """إرسال تنبيه فوري إلى تلجرام مع حماية الاتصال"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": message, 
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
        logger.info("✅ تم إرسال التنبيه إلى تلجرام بنجاح")
    except Exception as e:
        logger.error(f"❌ فشل إرسال التنبيه: {str(e)}")

def deep_analysis_workflow(match_data):
    """سير عمل التحليل العميق: إنتروبي -> ذكاء اصطناعي -> توقع"""
    logger.info(f"🔍 بدء معالجة البيانات للمباراة: {match_data[:40]}...")
    
    # الخطوة 1: اختبار الانفجار الاحتمالي عبر المحرك السريع
    spike_score = engine.get_spike_score(match_data)
    logger.info(f"📊 درجة الانفجار الاحتمالي (Spike Score): {spike_score:.4f}")

    # الخطوة 2: اتخاذ القرار (فقط إذا كان التوقع قوياً > 0.75)
    if spike_score > 0.75:
        logger.info("🔥 تم رصد إشارة قوية! استدعاء الذكاء الاصطناعي للتحليل النهائي...")
        
        headers = {
            "Authorization": f"Bearer {OPEN_API_KEY}",
            "Content-Type": "application/json"
        }
        prompt = f"أنت محلل رياضي محترف. بناءً على هذه المعطيات الحية: {match_data}، أعطني توقعاً دقيقاً للنتيجة ونسبة حدوث هدف قادم. كن مختصراً وحاسماً."
        
        payload = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                                     headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content']
                return f"⚠️ *إشارة قوية مستشعرة ({spike_score*100:.1f}%)*\n\n{result}"
        except Exception as e:
            logger.error(f"❌ خطأ في محرك التحليل: {str(e)}")
    
    return None

def main_radar_job():
    """المهمة الدورية لجلب وتحليل البيانات"""
    logger.info("🌐 جاري سحب بيانات الملاعب الحية من الرادار...")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text("football live scores and predictions today", timelimit='d'))[:5]
            
            for i, r in enumerate(results):
                match_info = f"{r['title']} - {r['body']}"
                prediction = deep_analysis_workflow(match_info)
                
                if prediction:
                    send_telegram_alert(f"🚀 **توقع رادار جديد #{i+1}**\n{prediction}")
    except Exception as e:
        logger.error(f"❌ فشل الرادار في جلب البيانات: {str(e)}")

# --- جدولة المهام الذكية ---
scheduler = BackgroundScheduler()
scheduler.add_job(main_radar_job, 'interval', minutes=15) # فحص كل 15 دقيقة
scheduler.start()

@app.route('/')
def health_check():
    return jsonify({
        "status": "online",
        "engine": "Fast-Numba-Vector",
        "last_scan": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "protection": "active"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"📡 البوت يعمل الآن على المنفذ {port}")
    app.run(host="0.0.0.0", port=port)
