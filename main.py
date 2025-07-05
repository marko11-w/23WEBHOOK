import telebot
from flask import Flask, request

# ✅ توكن البوت
TOKEN = "7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ✅ الرسالة التي يرد بها البوت دائمًا
response_message = """
🚫 تم إيقاف البوت نهائيًا!
✅ تم استبداله بتطبيق الاختراق الجديد.

📲 للشراء راسل @M_A_R_K75
"""

# ✅ الرد على جميع الرسائل والأوامر
@bot.message_handler(func=lambda message: True)
def reply_all(message):
    bot.send_message(message.chat.id, response_message)

# ✅ نقطة استقبال Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# ✅ صفحة فحص عادية
@app.route("/", methods=["GET"])
def index():
    return "Bot is running ✅", 200

# ✅ إعداد Webhook عند تشغيل التطبيق
if __name__ == "__main__":
    import os
    bot.remove_webhook()
    bot.set_webhook(url=f"https://23webhook-bothack.up.railway.app/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
