import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
import time
import threading
import schedule
from datetime import datetime

TOKEN = "7504294266:AAHgYMIxq5G1hxXRmGF2O7zYKKi-bPjReeM"
ADMIN_ID = 7758666677
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "subs.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

user_subscriptions = load_data()

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("📦 الاشتراك", "💰 رصيدي")
    keyboard.add("💸 سحب الأرباح", "🚫 إلغاء الاشتراك")
    bot.send_message(message.chat.id,
        "👋 مرحبًا بك في بوت الاستثمار!\n"
        "💼 أرسل صورة بطاقة الدفع الآن مع ذكر المبلغ (50000، 100000...)\n"
        "وسيتم مراجعتها من قبل الإدارة.",
        reply_markup=keyboard
    )

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if not message.caption or not any(x in message.caption for x in ["50000", "100000", "150000"]):
        return bot.reply_to(message, "❗ أرسل صورة البطاقة مع كتابة مبلغ الاشتراك في التعليق.")
    
    user_id = str(message.from_user.id)
    user_subscriptions[user_id] = {
        "confirmed": False,
        "balance": 0,
        "days_paid": 0,
        "amount": 0
    }
    save_data(user_subscriptions)

    amount = int([x for x in message.caption.split() if x.isdigit()][0])
    user_subscriptions[user_id]["amount"] = amount

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ تم التفعيل", callback_data=f"accept_{user_id}"),
        InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user_id}")
    )

    bot.send_photo(ADMIN_ID, message.photo[-1].file_id,
        caption=f"طلب اشتراك من @{message.from_user.username} بمبلغ {amount} دينار",
        reply_markup=markup
    )
    bot.reply_to(message, "📩 تم إرسال صورة البطاقة للإدارة، انتظر المراجعة.")

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

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_subscription(call):
    user_id = call.data.split("_")[1]
    if user_id in user_subscriptions:
        del user_subscriptions[user_id]
        save_data(user_subscriptions)
        bot.send_message(user_id, "❌ تم رفض اشتراكك من الإدارة.")
        bot.answer_callback_query(call.id, "❌ تم الرفض")

@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = str(message.from_user.id)
    user = user_subscriptions.get(user_id)
    if user and user["confirmed"]:
        bot.reply_to(message, f"📊 رصيدك: {user['balance']} دينار\n🗓 أيام: {user['days_paid']}")
    else:
        bot.reply_to(message, "❌ لا تملك اشتراك مفعل.")

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

@bot.message_handler(commands=['members'])
def show_members(message):
    if message.from_user.id != ADMIN_ID:
        return
    count = sum(1 for u in user_subscriptions.values() if u["confirmed"])
    names = [f"{uid} - {data['amount']}" for uid, data in user_subscriptions.items() if data["confirmed"]]
    msg = f"👥 عدد المشتركين: {count}\n\n" + "\n".join(names)
    bot.send_message(ADMIN_ID, msg)

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
    bot.reply_to(message, "💳 أرسل صورة بطاقة الدفع الآن مع ذكر مبلغ الاشتراك بالتعليق.")

@bot.message_handler(func=lambda m: m.text == "🚫 إلغاء الاشتراك")
def handle_cancel_button(message):
    user_id = str(message.from_user.id)
    if user_id in user_subscriptions:
        del user_subscriptions[user_id]
        save_data(user_subscriptions)
        bot.reply_to(message, "🚫 تم إلغاء اشتراكك.")
    else:
        bot.reply_to(message, "❌ لا يوجد اشتراك مفعل.")

def send_daily_profits():
    for uid, user in user_subscriptions.items():
        if user["confirmed"]:
            daily = int((user["amount"] / 50000) * 15000)
            user["balance"] += daily
            user["days_paid"] += 1
            try:
                bot.send_message(int(uid), f"💸 أرباح اليوم: {daily} دينار\n📊 رصيدك: {user['balance']} دينار")
            except:
                continue
    save_data(user_subscriptions)

@bot.message_handler(commands=['sendprofits'])
def manual_send(message):
    if message.from_user.id != ADMIN_ID:
        return
    send_daily_profits()
    bot.send_message(ADMIN_ID, "✅ تم إرسال الأرباح يدوياً.")

# جدولة الأرباح كل 24 ساعة
schedule.every(24).hours.do(send_daily_profits)

def schedule_thread():
    while True:
        schedule.run_pending()
        time.sleep(10)

threading.Thread(target=schedule_thread).start()

print("🤖 Bot is running...")
bot.infinity_polling()
