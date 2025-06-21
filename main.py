import telebot
from telebot import types
from flask import Flask, request
import json
import os

API_TOKEN = "YOUR_TOKEN"  # استبدل بالتوكن الحقيقي
ADMIN_ID = 123456789       # استبدل بمعرفك الخاص (أو معرف المسؤول)

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")
app = Flask(__name__)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

USERS_FILE = os.path.join(DATA_DIR, "users.json")
CHANNELS_FILE = os.path.join(DATA_DIR, "channels.json")
BUTTONS_FILE = os.path.join(DATA_DIR, "buttons.json")
BANNED_FILE = os.path.join(DATA_DIR, "banned.json")

def load_json(path, default):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default, f)
    with open(path, encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

users = load_json(USERS_FILE, {})
channels = load_json(CHANNELS_FILE, {})
buttons = load_json(BUTTONS_FILE, {})
banned = load_json(BANNED_FILE, [])

default_buttons = {
    "collect": "🔄 جمع النقاط",
    "request": "➕ طلب متابعين",
    "balance": "📊 رصيدي",
    "status": "🎯 حالتي",
    "support": "📞 الدعم"
}

if not buttons:
    buttons.update(default_buttons)
    save_json(BUTTONS_FILE, buttons)

if not isinstance(banned, list):
    banned = []
    save_json(BANNED_FILE, banned)

def get_user(uid):
    uid = str(uid)
    if uid not in users:
        users[uid] = {"points": 0, "vip": False}
        save_json(USERS_FILE, users)
    return users[uid]

def is_banned(uid):
    return str(uid) in banned

def check_subscription(user_id, channel_username):
    if not channel_username.startswith("@"):
        channel_username = "@" + channel_username
    try:
        member = bot.get_chat_member(channel_username, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Error checking subscription for {channel_username} and user {user_id}: {e}")
        return False

@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id
    if is_banned(uid):
        return
    user = get_user(uid)
    if message.from_user.username:
        user["username"] = message.from_user.username
        save_json(USERS_FILE, users)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(buttons["collect"], buttons["request"])
    markup.row(buttons["balance"], buttons["status"])
    markup.row(buttons["support"])
    bot.send_message(uid, "👋 مرحباً بك في بوت رحلة المليار!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == buttons["collect"])
def handle_collect(message):
    uid = message.from_user.id
    user = get_user(uid)

    for ch in channels.keys():
        if not check_subscription(uid, ch):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("✅ اشتركت ✅", callback_data=f"check_{ch}"))
            bot.send_message(uid, f"📢 اشترك في القناة {ch} للحصول على 10 نقاط", reply_markup=markup)
            return

    bot.send_message(uid, "✅ لقد اشتركت في جميع القنوات. لا توجد قنوات جديدة حاليًا.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def callback_check(call):
    uid = call.from_user.id
    ch = call.data.split("check_")[1]
    if check_subscription(uid, ch):
        user = get_user(uid)
        user["points"] += 10
        save_json(USERS_FILE, users)
        bot.answer_callback_query(call.id, "✅ تم التحقق من الاشتراك. تم إضافة 10 نقاط!")
        bot.send_message(uid, f"🎉 حصلت على 10 نقاط. رصيدك الآن: {user['points']}")
    else:
        bot.answer_callback_query(call.id, "❌ لم يتم التأكد من اشتراكك. تأكد من الانضمام للقناة أولاً.")

@bot.message_handler(func=lambda m: m.text == buttons["support"])
def handle_support(message):
    bot.send_message(message.chat.id, "📞 تواصل مع الدعم: [@M_A_R_K75](https://t.me/M_A_R_K75)")

@bot.message_handler(func=lambda m: m.text == buttons["request"])
def handle_request(message):
    msg = bot.send_message(message.chat.id, "📨 أرسل رابط قناتك بالشكل التالي:\nhttps://t.me/YourChannel")
    bot.register_next_step_handler(msg, save_channel)

def save_channel(message):
    uid = message.from_user.id
    user = get_user(uid)

    if not message.text.startswith("https://t.me/"):
        bot.send_message(uid, "❌ الرابط غير صالح. تأكد من أنه يبدأ بـ https://t.me/")
        return

    username = message.text.split("https://t.me/")[1].replace("@", "")
    full_username = f"@{username}"

    try:
        member = bot.get_chat_member(full_username, bot.get_me().id)
        if member.status not in ["administrator", "creator"]:
            bot.send_message(uid, f"❌ يجب أولاً تعيين البوت كمشرف في قناتك {full_username}.")
            return
    except Exception as e:
        print(f"Error verifying channel admin: {e}")
        bot.send_message(uid, f"❌ فشل التحقق من قناة {full_username}. تأكد أن البوت مشرف وأن القناة عامة.")
        return

    if user["points"] < 2:
        bot.send_message(uid, "❌ تحتاج على الأقل نقطتين لطلب المتابعين.")
        return

    user["points"] -= 2
    channels[full_username] = True
    save_json(USERS_FILE, users)
    save_json(CHANNELS_FILE, channels)
    bot.send_message(uid, f"✅ تم تفعيل قناتك {full_username} بنجاح!")

@bot.message_handler(func=lambda m: m.text == buttons["balance"])
def handle_balance(message):
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"💰 رصيدك الحالي: {user['points']} نقطة")

@bot.message_handler(func=lambda m: m.text == buttons["status"])
def handle_status(message):
    user = get_user(message.from_user.id)
    vip_status = "✅ VIP" if user.get("vip") else "❌ عادي"
    bot.send_message(message.chat.id, f"🎯 حالتك: {vip_status}")

@bot.message_handler(commands=["addpoints"])
def admin_add_points(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "❌ الاستخدام الصحيح: /addpoints user_id amount")
        return
    try:
        target_id = str(args[1])
        amount = int(args[2])
        user = get_user(target_id)
        user["points"] += amount
        save_json(USERS_FILE, users)
        bot.reply_to(message, f"✅ تم إضافة {amount} نقطة للمستخدم {target_id}.")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

@bot.message_handler(commands=["ban"])
def admin_ban(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "❌ الاستخدام الصحيح: /ban user_id")
        return
    uid = str(args[1])
    if uid not in banned:
        banned.append(uid)
        save_json(BANNED_FILE, banned)
        bot.reply_to(message, f"🚫 تم حظر المستخدم {uid}.")
    else:
        bot.reply_to(message, f"🔒 المستخدم {uid} محظور بالفعل.")

@bot.message_handler(commands=["unban"])
def admin_unban(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "❌ الاستخدام الصحيح: /unban user_id")
        return
    uid = str(args[1])
    if uid in banned:
        banned.remove(uid)
        save_json(BANNED_FILE, banned)
        bot.reply_to(message, f"✅ تم رفع الحظر عن المستخدم {uid}.")
    else:
        bot.reply_to(message, f"ℹ️ المستخدم {uid} غير محظور.")

@bot.message_handler(commands=["vip"])
def admin_vip(message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "❌ الاستخدام الصحيح: /vip user_id on|off")
        return
    uid = str(args[1])
    mode = args[2].lower()
    user = get_user(uid)
    user["vip"] = True if mode == "on" else False
    save_json(USERS_FILE, users)
    bot.reply_to(message, f"✨ تم {'تفعيل' if mode == 'on' else 'إلغاء'} VIP للمستخدم {uid}.")

@bot.message_handler(commands=["adminhelp"])
def admin_help(message):
    if message.from_user.id != ADMIN_ID:
        return
    help_text = (
        "🛠️ أوامر الإدارة:\n"
        "/addpoints user_id amount — لإضافة نقاط\n"
        "/ban user_id — لحظر مستخدم\n"
        "/unban user_id — لفك الحظر\n"
        "/vip user_id on|off — لتفعيل أو إلغاء VIP\n"
        "/adminhelp — عرض هذه القائمة"
    )
    bot.reply_to(message, help_text)

@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data(as_text=True))
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "polling":
        print("Bot started with polling...")
        bot.infinity_polling()
    else:
        print("Bot started with webhook Flask server...")
        app.run(host="0.0.0.0", port=8080)
