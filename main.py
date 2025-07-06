import telebot
from flask import Flask, request
import os

API_TOKEN = '7684563087:AAEO4rd2t7X3v8CsZMdfzOc9s9otm9OGxfw'
CHANNEL_USERNAME = "@MARK01i"
ADMIN_USERNAME = "@M_A_R_K75"

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# رسالة الرد على كل شيء
def subscription_required_msg():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ اشترك الآن", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}"),
        telebot.types.InlineKeyboardButton("💬 راسل الأدمن", url=f"https://t.me/{ADMIN_USERNAME.strip('@')}")
    )
    return (
        "🚫 *عذرًا، لا يمكنك استخدام البوت حاليًا.*\n\n"
        "💸 لتفعيل البوت راسل الأدمن:\n"
        f"{ADMIN_USERNAME}\n\n"
        "💰 *سعر الاشتراك: 40 دولار فقط ✅*\n"
        "📢 الرجاء الاشتراك في القناة قبل التفعيل."
    ), markup

# التحقق من الاشتراك الإجباري
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# الرد على أي رسالة أو أمر
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def handle_all(message):
    if not check_subscription(message.from_user.id):
        msg, markup = subscription_required_msg()
        bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")
        return
    # يمكن لاحقًا إضافة وظائف حقيقية هنا بعد الاشتراك
    bot.send_message(message.chat.id, "✅ تم التفعيل مسبقًا.")

# إعداد Webhook
@app.route(f'/{API_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok'

@app.route('/')
def index():
    return 'بوت الاختراق جاهز 🔐'

if __name__ == '__main__':
    # تعيين رابط الويب هوك تلقائيًا (إذا لم يكن مُعد بعد)
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # تعيينه في إعدادات ريوالي مثل: https://xxxx.up.railway.app
    if WEBHOOK_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{WEBHOOK_URL}/{API_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
