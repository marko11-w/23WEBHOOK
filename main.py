import telebot
import json
import os
import threading
import time
import schedule
from flask import Flask, request
from telebot import types

# إعدادات البوت
TOKEN = "7504294266:AAHgYMIxq5G1hxXRmGF2O7zYKKi-bPjReeM"
ADMIN_ID = 7758666677
WEBHOOK_URL = "https://23webhook-production.up.railway.app/"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

DATA_FILE = "subs.json"
COUNT_FILE = "count.json"

# إنشاء ملفات البيانات
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(COUNT_FILE):
    with open(COUNT_FILE, "w") as f:
        json.dump({"count": 0, "users": []}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data=None):
    if data is None:
        data = user_subscriptions
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

@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is running.", 200

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)

    with count_lock:
        if user_id not in count_data["users"]:
            count_data["users"].append(user_id)
            count_data["count"] += 1
            save_count(count_data)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    user = user_subscriptions.get(user_id)
    if user and user.get("confirmed"):
        keyboard.row("💰 رصيدي", "💸 سحب الأرباح")
    keyboard.row("📦 الاشتراك", "🚫 إلغاء الاشتراك")
    if int(user_id) == ADMIN_ID:
        keyboard.row("👥 عدد المستخدمين")

    text = (
        "السلام عليكم ورحمة الله وبركاته ✅\n\n"
        "عروض جديدة ✅\n\n"
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
        "✅ مدة الاشتراك: شهرين\n"
        "💳 الدفع عبر بطاقة آسياسيل فقط\n\n"
        "📩 للتواصل: @M_A_R_K75"
    )
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

# زر الاشتراك
@bot.message_handler(func=lambda m: m.text == "📦 الاشتراك")
def handle_subscribe_button(message):
    user_id = str(message.from_user.id)
    bot.send_message(message.chat.id, "💳 أرسل صورة بطاقة الدفع *آسيا سيل فقط* الآن مع ذكر مبلغ الاشتراك في التعليق.", parse_mode="Markdown")
    user_subscriptions[user_id] = {"confirmed": False, "amount": 0, "balance": 0, "days_paid": 0}
    save_data()

# استقبال صورة البطاقة
@bot.message_handler(content_types=['photo'])
def handle_payment_photo(message):
    user_id = str(message.from_user.id)
    if user_id not in user_subscriptions:
        return bot.reply_to(message, "❗️ اضغط على زر الاشتراك أولاً.")
    
    caption = message.caption or "لا يوجد تعليق"
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ تم التفعيل", callback_data=f"confirm_{user_id}"),
        types.InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user_id}")
    )
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id,
                   caption=f"📩 طلب اشتراك من المستخدم:\n\nID: `{user_id}`\nيوزر: @{message.from_user.username or 'لا يوجد'}\n\n💬 تعليق:\n{caption}",
                   parse_mode="Markdown", reply_markup=markup)
    bot.reply_to(message, "✅ تم إرسال الطلب للإدارة، يرجى الانتظار...")

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_subscription(call):
    user_id = call.data.split("_")[1]
    if user_id in user_subscriptions:
        try:
            caption = call.message.caption or ""
            comment = "0"
            for line in caption.split("\n"):
                if "تعليق" in line:
                    comment = line.replace("💬 تعليق:", "").strip()
            amount = int(''.join([c for c in comment if c.isdigit()]))
            user_subscriptions[user_id]["confirmed"] = True
            user_subscriptions[user_id]["amount"] = amount
            save_data()
            bot.send_message(int(user_id), "✅ تم تفعيل اشتراكك بنجاح.\nابدأ الربح اليومي تلقائيًا 🎉")
            bot.answer_callback_query(call.id, "✅ تم التفعيل")
        except:
            bot.answer_callback_query(call.id, "❌ خطأ في التفعيل")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_subscription(call):
    user_id = call.data.split("_")[1]
    if user_id in user_subscriptions:
        del user_subscriptions[user_id]
        save_data()
        bot.send_message(int(user_id), "❌ تم رفض اشتراكك من الإدارة.")
        bot.answer_callback_query(call.id, "❌ تم الرفض")

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

@bot.message_handler(commands=['withdraw'])
def withdraw(message):
    args = message.text.split()
    user_id = str(message.from_user.id)
    user = user_subscriptions.get(user_id)
    if not user or not user["confirmed"]:
        return bot.reply_to(message, "❌ لا تملك اشتراك مفعل.")
    if len(args) != 2 or not args[1].isdigit():
        return bot.reply_to(message, "❌ استخدم الأمر هكذا: /withdraw 20000")
    amount = int(args[1])
    if amount > user["balance"]:
        bot.reply_to(message, f"❌ رصيدك لا يكفي. لديك {user['balance']} دينار")
    else:
        user["balance"] -= amount
        save_data()
        bot.reply_to(message, f"✅ تم استلام طلب السحب بقيمة {amount} دينار.\n📩 سيتم التحويل قريباً.")

@bot.message_handler(func=lambda m: m.text == "🚫 إلغاء الاشتراك")
def handle_cancel_button(message):
    user_id = str(message.from_user.id)
    if user_id in user_subscriptions:
        del user_subscriptions[user_id]
        save_data()
        bot.reply_to(message, "🚫 تم إلغاء اشتراكك.")
    else:
        bot.reply_to(message, "❌ لا يوجد اشتراك مفعل.")

@bot.message_handler(func=lambda m: m.text == "👥 عدد المستخدمين")
def show_members(message):
    if message.from_user.id != ADMIN_ID:
        return
    count = sum(1 for u in user_subscriptions.values() if u["confirmed"])
    names = [f"{uid} - {data['amount']} دينار" for uid, data in user_subscriptions.items() if data["confirmed"]]
    msg = f"👥 عدد المشتركين المفعلين: {count}\n\n" + "\n".join(names)
    bot.send_message(ADMIN_ID, msg)

def send_daily_profits():
    for uid, user in user_subscriptions.items():
        if user.get("confirmed"):
            daily = int((user["amount"] / 50000) * 15000)
            user["balance"] += daily
            user["days_paid"] += 1
            try:
                bot.send_message(int(uid), f"💸 أرباح اليوم: {daily} دينار\n📊 رصيدك: {user['balance']} دينار")
            except:
                continue
    save_data()

@bot.message_handler(commands=['sendprofits'])
def manual_send(message):
    if message.from_user.id == ADMIN_ID:
        send_daily_profits()
        bot.send_message(ADMIN_ID, "✅ تم إرسال الأرباح يدوياً.")

# جدولة الأرباح يومياً
schedule.every(24).hours.do(send_daily_profits)

def schedule_thread():
    while True:
        schedule.run_pending()
        time.sleep(10)

# تشغيل الويب هوك والجدولة
threading.Thread(target=schedule_thread).start()
threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()
