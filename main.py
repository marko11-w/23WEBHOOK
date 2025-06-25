import telebot
import json
import os
import threading
import time
import schedule
from flask import Flask, request

TOKEN = "7504294266:AAHgYMIxq5G1hxXRmGF2O7zYKKi-bPjReeM"
ADMIN_ID = 7758666677
WEBHOOK_URL = "https://23webhook-production.up.railway.app/"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

DATA_FILE = "subs.json"
COUNT_FILE = "count.json"

# تحميل أو إنشاء ملفات البيانات
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(COUNT_FILE):
    with open(COUNT_FILE, "w") as f:
        json.dump({"count": 0, "users": []}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_count():
    with open(COUNT_FILE, "r") as f:
        return json.load(f)

def save_count(data):
    with open(COUNT_FILE, "w") as f:
        json.dump(data, f, indent=2)

user_subscriptions = load_data()
count_data = load_count()
count_lock = threading.Lock()

# Flask webhook
@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is running.", 200

# أمر /start مع تسجيل عدد المستخدمين الجدد
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    with count_lock:
        if user_id not in count_data["users"]:
            count_data["users"].append(user_id)
            count_data["count"] += 1
            save_count(count_data)

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.row("💰 رصيدي", "💸 سحب الأرباح")
    keyboard.row("📦 الاشتراك", "🚫 إلغاء الاشتراك")

    text = (
        "السلام عليكم ورحمة الله وبركاته ✅\n\n"
        "عروض جديدة ✅\n\n"
        "العروض كالتالي:\n\n"
        "🌟 الفئات العادية 🌟\n"
        "50 ألف - ربح يومي 15 ألف 😍\n"
        "100 ألف - ربح يومي 30 ألف 🟢\n"
        "150 ألف - ربح يومي 50 ألف 🟢\n"
        "200 ألف - ربح يومي 65 ألف 🟢\n"
        "250 ألف - ربح يومي 85 ألف 🟢\n"
        "300 ألف - ربح يومي 100 ألف 🟢\n"
        "350 ألف - ربح يومي 115 ألف 🟢\n"
        "400 ألف - ربح يومي 125 ألف 🟢\n"
        "450 ألف - ربح يومي 135 ألف 🟢\n"
        "500 ألف - ربح يومي 150 ألف 🟢\n\n"
        "🌐 فئات رجال الأعمال 🌐\n"
        "600 ألف - ربح يومي 250 ألف ⭐️\n"
        "700 ألف - ربح يومي 300 ألف ⭐️\n"
        "800 ألف - ربح يومي 350 ألف ⭐️\n"
        "900 ألف - ربح يومي 400 ألف ⭐️\n"
        "1 مليون - ربح يومي 500 ألف ⭐️\n\n"
        "مدة الاشتراك شهرين ✅\n"
        "يمكنك تجديد الاشتراك بعد انتهاء المدة ➡️✅\n\n"
        "للتواصل والاشتراك: @M_A_R_K75"
    )
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

# استقبال صورة البطاقة مع المبلغ في التعليق
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if not message.caption:
        return bot.reply_to(message, "❗ أرسل صورة البطاقة الاسيا سيل  مع كتابة مبلغ الاشتراك في التعليق.")
    
    # ابحث عن مبلغ الاشتراك في التعليق (رقم فقط)
    amount = None
    for word in message.caption.split():
        if word.isdigit():
            amount = int(word)
            break
    if not amount:
        return bot.reply_to(message, "❗ اكتب مبلغ الاشتراك في تعليق الصورة بشكل واضح (مثلاً: 50000).")

    user_id = str(message.from_user.id)
    user_subscriptions[user_id] = {
        "confirmed": False,
        "balance": 0,
        "days_paid": 0,
        "amount": amount
    }
    save_data(user_subscriptions)

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ تم التفعيل", callback_data=f"accept_{user_id}"),
        telebot.types.InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user_id}")
    )

    bot.send_photo(ADMIN_ID, message.photo[-1].file_id,
        caption=f"طلب اشتراك من @{message.from_user.username} بمبلغ {amount} دينار",
        reply_markup=markup
    )
    bot.reply_to(message, "📩 تم إرسال صورة البطاقة للإدارة، انتظر المراجعة.")

# قبول الاشتراك
@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_"))
def accept_subscription(call):
    user_id = call.data.split("_")[1]
    user = user_subscriptions.get(user_id)
    if user:
        user["confirmed"] = True
        user["days_paid"] = 0
        save_data(user_subscriptions)
        bot.send_message(user_id, "✅ تم تفعيل اشتراكك، وستبدأ أرباحك اليومية من الآن.")
        bot.answer_callback_query(call.id, "تم التفعيل.")

# رفض الاشتراك
@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_subscription(call):
    user_id = call.data.split("_")[1]
    if user_id in user_subscriptions:
        del user_subscriptions[user_id]
        save_data(user_subscriptions)
        bot.send_message(user_id, "❌ تم رفض اشتراكك من الإدارة.")
        bot.answer_callback_query(call.id, "❌ تم الرفض")

# عرض الرصيد
@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = str(message.from_user.id)
    user = user_subscriptions.get(user_id)
    if user and user["confirmed"]:
        bot.reply_to(message, f"📊 رصيدك: {user['balance']} دينار\n🗓 أيام: {user['days_paid']}")
    else:
        bot.reply_to(message, "❌ لا تملك اشتراك مفعل.")

# سحب الأرباح
@bot.message_handler(commands=['withdraw'])
def withdraw(message):
    args = message.text.split()
    user_id = str(message.from_user.id)
    user = user_subscriptions.get(user_id)

    if not user or not user["confirmed"]:
        bot.reply_to(message, "❌ لا تملك اشتراك مفعل.")
        return

    if len(args) != 2 or not args[1].isdigit():
        bot.reply_to(message, "❌ استخدم الأمر هكذا: /withdraw 20000")
        return

    amount = int(args[1])
    if amount > user["balance"]:
        bot.reply_to(message, f"❌ رصيدك لا يكفي. لديك {user['balance']} دينار")
    else:
        user["balance"] -= amount
        save_data(user_subscriptions)
        bot.reply_to(message, f"✅ تم استلام طلب السحب بقيمة {amount} دينار.\n📩 سيتم التحويل قريباً.")

# أمر /count للأدمن لمعرفة عدد المستخدمين الذين ضغطوا /start
@bot.message_handler(commands=['count'])
def count_users(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(ADMIN_ID, f"👥 عدد المستخدمين الذين ضغطوا /start: {count_data['count']}")

# ربط أزرار لوحة المفاتيح بالنصوص
@bot.message_handler(func=lambda m: m.text == "💰 رصيدي")
def handle_balance_button(message):
    user_id = str(message.from_user.id)
    user = user_subscriptions.get(user_id)
    if user and user["confirmed"]:
        bot.reply_to(message, f"📊 رصيدك: {user['balance']} دينار\n🗓 أيام: {user['days_paid']}")
    else:
        bot.reply_to(message, "❌ لا تملك اشتراك مفعل.")

@bot.message_handler(func=lambda m: m.text == "💸 سحب الأرباح")
def handle_withdraw_button(message):
    bot.reply_to(message, "💬 أرسل المبلغ الذي تريد سحبه بهذه الصيغة:\n`/withdraw 15000`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📦 الاشتراك")
def handle_subscribe_button(message):
    bot.reply_to(message, "💳 أرسل صورة بطاقة الدفع اسيا سيل  الآن مع ذكر مبلغ الاشتراك بالتعليق.")

@bot.message_handler(func=lambda m: m.text == "🚫 إلغاء الاشتراك")
def handle_cancel_button(message):
    user_id = str(message.from_user.id)
    if user_id in user_subscriptions:
        del user_subscriptions[user_id]
        save_data(user_subscriptions)
        bot.reply_to(message, "🚫 تم إلغاء اشتراكك.")
    else:
        bot.reply_to(message, "❌ لا يوجد اشتراك مفعل.")

# إرسال الأرباح اليومية تلقائيًا
def send_daily_profits():
    for uid, user in user_subscriptions.items():
        if user["confirmed"]:
            daily = int((user["amount"] / 50000) * 15000)
            user["balance"] += daily
            user["days_paid"] += 1
            try:
                bot.send_message(int(uid), f"💸 أرباح اليوم: {daily} دينار\n📊 رصيدك: {user['balance']} دينار")
            except:
                pass
    save_data(user_subscriptions)

@bot.message_handler(commands=['sendprofits'])
def manual_send(message):
    if message.from_user.id != ADMIN_ID:
        return
    send_daily_profits()
    bot.send_message(ADMIN_ID, "✅ تم إرسال الأرباح يدوياً.")

schedule.every(24).hours.do(send_daily_profits)

def schedule_thread():
    while True:
        schedule.run_pending()
        time.sleep(10)

threading.Thread(target=schedule_thread).start()

# إعداد webhook
bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url=WEBHOOK_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
