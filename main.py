import telebot
from flask import Flask, request
import os

# ✅ توكن البوت
API_TOKEN = '7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw'

# ✅ القناة المطلوبة للاشتراك الإجباري
CHANNEL_USERNAME = "@MARK01i"

# ✅ يوزر الأدمن
ADMIN_USERNAME = "@M_A_R_K75"

# إنشاء كائن البوت و Flask app
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# ⚠️ رسالة الاشتراك الإجباري
def subscription_required_msg():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ اشترك الآن", url="https://t.me/MARK01i"),
        telebot.types.InlineKeyboardButton("💬 راسل الأدمن", url="https://t.me/M_A_R_K75")
    )
    return (
        "🚫 *عذرًا، لا يمكنك استخدام البوت حاليًا.*\n\n"
        "💸 لتفعيل البوت راسل الأدمن:\n"
        f"{ADMIN_USERNAME}\n\n"
        "💰 *سعر الاشتراك: 40 دولار فقط ✅*\n"
        "📢 الرجاء الاشتراك في القناة قبل التفعيل."
    ), markup

# ✅ التحقق من الاشتراك في القناة
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# 📩 التعامل مع أي رسالة أو وسائط
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def handle_all(message):
    if not check_subscription(message.from_user.id):
        msg, markup = subscription_required_msg()
        bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "✅ تم التفعيل مسبقًا. مرحبًا بك!")

# ✅ Webhook endpoint
@app.route(f'/{API_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok'

# 🌐 صفحة الفحص الرئيسية
@app.route('/')
def index():
    return '🤖 البوت يعمل بنجاح عبر Webhook!'

# 🚀 تشغيل التطبيق
if __name__ == '__main__':
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # تأكد أنه مضاف كمتغير في Railway
    if WEBHOOK_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{WEBHOOK_URL}/{API_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
