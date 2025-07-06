import telebot
from flask import Flask, request
import os

# ✅ توكن البوت من @BotFather
API_TOKEN = '7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw'

# ✅ معلومات القناة والإدارة
CHANNEL_USERNAME = "@MARK01i"
ADMIN_USERNAME = "@M_A_R_K75"

# إنشاء كائن البوت والتطبيق
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# ✅ رسالة التفعيل الإجبارية
def subscription_required_msg():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ اشترك الآن", url="https://t.me/MARK01i"),
        telebot.types.InlineKeyboardButton("💬 راسل الأدمن", url="https://t.me/M_A_R_K75")
    )
    return (
        "🚫 عذرًا، لا يمكنك استخدام البوت حاليًا.\n\n"
        f"💸 لتفعيل البوت راسل الأدمن:\n{ADMIN_USERNAME}\n\n"
        "💰 سعر الاشتراك: 40 دولار فقط ✅\n"
        "📢 الرجاء الاشتراك في القناة قبل التفعيل."
    ), markup

# ✅ التعامل مع أي رسالة أو وسائط
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'contact', 'location'])
def handle_all(message):
    msg, markup = subscription_required_msg()
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

# ✅ نقطة استقبال Webhook من Telegram
@app.route(f'/{API_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok'

# ✅ صفحة فحص للتأكد أن السيرفر يعمل
@app.route('/')
def index():
    return '🤖 البوت يعمل بنجاح على Webhook!'

# ✅ تشغيل Webhook عند الإقلاع
if __name__ == '__main__':
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # يجب تعيينه في Railway
    if WEBHOOK_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{WEBHOOK_URL}/{API_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
