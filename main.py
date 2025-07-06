#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot - بوت اختراق مارك
يدعم webhook و polling على Railway
"""

import os
import logging
import requests
import json
import time
from threading import Thread
from flask import Flask, request

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ إعدادات البوت (تم التعديل حسب طلبك)
BOT_TOKEN = "7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw"
WEBHOOK_URL = "https://23webhook-production.up.railway.app"
USE_WEBHOOK = True
LAST_UPDATE_ID = 0

# Flask app
app = Flask(__name__)


def send_subscription_message(chat_id):
    """إرسال رسالة الاشتراك للمستخدم"""
    try:
        message = """🔐 مرحباً بك في بوت اختراق مارك!

للحصول على جميع الميزات المتقدمة، يرجى الاشتراك:

💰 السعر: 40 دولار فقط
⭐ الباقة تشمل:
• أدوات اختراق متقدمة
• تحديثات مستمرة
• دعم فني 24/7
• دروس تعليمية حصرية

📞 للتواصل مع الإدارة أو الاشتراك:
استخدم الأزرار أدناه ⬇️"""

        keyboard = {
            "inline_keyboard": [[{
                "text": "📢 القناة الرسمية",
                "url": "https://t.me/MARK01i"
            }],
                                [{
                                    "text": "💬 التواصل مع الإدارة",
                                    "url": "https://t.me/M_A_R_K75"
                                }]]
        }

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "reply_markup": json.dumps(keyboard)
        }

        response = requests.post(url, json=data, timeout=10)
        result = response.json()

        if result.get("ok"):
            logger.info(f"✅ تم إرسال الرسالة للمحادثة {chat_id}")
            return True
        else:
            logger.error(f"❌ فشل في إرسال الرسالة: {result}")
            return False

    except Exception as e:
        logger.error(f"❌ خطأ في إرسال الرسالة: {str(e)}")
        return False


def get_updates():
    """الحصول على التحديثات من تليجرام"""
    global LAST_UPDATE_ID
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        params = {
            "offset": LAST_UPDATE_ID + 1,
            "timeout": 30,
            "allowed_updates": ["message", "edited_message", "callback_query"]
        }

        response = requests.get(url, params=params, timeout=35)
        result = response.json()

        if result.get("ok"):
            updates = result.get("result", [])
            for update in updates:
                LAST_UPDATE_ID = update["update_id"]
                process_update(update)
        else:
            logger.error(f"❌ خطأ في الحصول على التحديثات: {result}")

    except requests.exceptions.Timeout:
        logger.debug("⏱️ انتهت مهلة الاتصال - سيتم المحاولة مرة أخرى")
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على التحديثات: {str(e)}")


def process_update(update):
    """معالجة التحديث الواحد"""
    try:
        chat_id = None
        message_type = ""

        if 'message' in update:
            chat_id = update['message']['chat']['id']
            message_type = "رسالة جديدة"
        elif 'edited_message' in update:
            chat_id = update['edited_message']['chat']['id']
            message_type = "رسالة معدلة"
        elif 'callback_query' in update:
            chat_id = update['callback_query']['message']['chat']['id']
            message_type = "ضغط على زر"

        if chat_id:
            logger.info(f"📨 معالجة {message_type} من المحادثة {chat_id}")
            send_subscription_message(chat_id)

    except Exception as e:
        logger.error(f"❌ خطأ في معالجة التحديث: {str(e)}")


def run_bot():
    """تشغيل البوت"""
    logger.info("🚀 بدء تشغيل البوت...")

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        result = response.json()

        if result.get("ok"):
            bot_info = result.get("result", {})
            logger.info(
                f"✅ البوت متصل: @{bot_info.get('username', 'unknown')}")
        else:
            logger.error(f"❌ خطأ في التحقق من البوت: {result}")
            return

    except Exception as e:
        logger.error(f"❌ خطأ في الاتصال بالبوت: {str(e)}")
        return

    while True:
        try:
            get_updates()
        except KeyboardInterrupt:
            logger.info("⏹️ تم إيقاف البوت")
            break
        except Exception as e:
            logger.error(f"❌ خطأ في حلقة البوت: {str(e)}")
            time.sleep(5)


def set_webhook():
    """تعيين webhook للبوت"""
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook", timeout=10)

        webhook_endpoint = f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}"
        set_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        data = {"url": webhook_endpoint}

        response = requests.post(set_url, json=data, timeout=10)
        result = response.json()

        if result.get("ok"):
            logger.info(f"✅ تم تعيين webhook: {webhook_endpoint}")
            return True
        else:
            logger.error(f"❌ فشل في تعيين webhook: {result}")
            return False

    except Exception as e:
        logger.error(f"❌ خطأ في تعيين webhook: {str(e)}")
        return False


# Flask routes
@app.route('/')
def home():
    mode = "Webhook" if USE_WEBHOOK else "Polling"
    return f"🤖 البوت يعمل بنجاح! - وضع: {mode}"


@app.route('/health')
def health():
    mode = "webhook" if USE_WEBHOOK else "polling"
    return {"status": "ok", "bot": "running", "mode": mode}


@app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if not update:
            return "ok"

        logger.info(f"📨 webhook update: {update.get('update_id', 'unknown')}")
        process_update(update)
        return "ok"

    except Exception as e:
        logger.error(f"❌ خطأ في webhook: {str(e)}")
        return "ok"


@app.route('/set_webhook', methods=['GET', 'POST'])
def setup_webhook():
    result = set_webhook()
    if result:
        return {"status": "success", "message": "تم تعيين webhook بنجاح"}
    else:
        return {"status": "error", "message": "فشل في تعيين webhook"}


def start_app():
    if USE_WEBHOOK and WEBHOOK_URL:
        logger.info("🌐 تشغيل البوت بوضع Webhook")
        if set_webhook():
            logger.info("✅ تم تعيين webhook بنجاح")
        else:
            logger.warning("⚠️ فشل في تعيين webhook - سيتم التبديل إلى polling")
            bot_thread = Thread(target=run_bot, daemon=True)
            bot_thread.start()
    else:
        logger.info("📡 تشغيل البوت بوضع Polling")
        bot_thread = Thread(target=run_bot, daemon=True)
        bot_thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    start_app()
