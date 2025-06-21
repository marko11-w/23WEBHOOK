# ✅ كود بوت Telegram الكامل - الإصدار الجديد new55
# ميزات: إدارة القنوات، النقاط، VIP، الحظر، الأزرار، Webhook عبر Railway

import telebot
from telebot import types
from flask import Flask, request
import json
import os

# بيانات الدخول
API_TOKEN = "7877754239:AAFP3ljogZijfNia3sVdgnEaIPR9EbrgGK8"
ADMIN_ID = 7758666677
SUPPORT_USER = "@M_A_R_K75"

# تهيئة البوت وFlask
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# المسارات للملفات
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(DATA_DIR, "users.json")
CHANNELS_FILE = os.path.join(DATA_DIR, "channels.json")
BUTTONS_FILE = os.path.join(DATA_DIR, "buttons.json")
BANNED_FILE = os.path.join(DATA_DIR, "banned.json")

# تحميل/حفظ JSON

def load_json(path):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# تحميل البيانات
users = load_json(USERS_FILE)
channels = load_json(CHANNELS_FILE)
buttons = load_json(BUTTONS_FILE)
banned = load_json(BANNED_FILE)

# أزرار المستخدم الافتراضية
default_buttons = {
    "collect": "🔄 جمع النقاط",
    "request": "➕ طلب متابعين",
    "balance": "📊 رصيدي",
    "status": "🎯 حالتي",
    "support": "📞 الدعم الفني"
}

for k, v in default_buttons.items():
    buttons[k] = v
save_json(BUTTONS_FILE, buttons)

# أدوات أساسية
def get_user(uid):
    uid = str(uid)
    if uid not in users:
        users[uid] = {"points": 0, "vip": False, "username": ""}
        save_json(USERS_FILE, users)
    return users[uid]

def is_banned(uid):
    return str(uid) in banned

def check_subscription(user_id, username):
    try:
        member = bot.get_chat_member(username, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# الأوامر العامة
@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id
    uname = message.from_user.username or ""
    if is_banned(uid): return
    user = get_user(uid)
    user["username"] = uname
    save_json(USERS_FILE, users)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(buttons["collect"], buttons["request"])
    markup.row(buttons["balance"], buttons["status"])
    markup.row(buttons["support"])
    bot.send_message(uid, "👋 مرحباً بك في بوت رحلة المليار!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == buttons["collect"])
def collect(message):
    uid = message.from_user.id
    if is_banned(uid): return
    for ch in channels:
        if check_subscription(uid, ch):
            continue
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("اشترك ثم اضغط هنا ✅", callback_data="check_" + ch))
        bot.send_message(uid, f"📸 اشترك في القناة {ch} لتحصل على 10 نقاط", reply_markup=markup)
        return
    bot.send_message(uid, "✅ لقد اشتركت في كل القنوات")

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def check(call):
    uid = call.from_user.id
    ch = call.data.split("_", 1)[1]
    if check_subscription(uid, ch):
        users[str(uid)]["points"] += 10
        save_json(USERS_FILE, users)
        bot.answer_callback_query(call.id, "✅ تم التحقق")
        bot.send_message(uid, "🎉 تم إضافة 10 نقاط")
    else:
        bot.answer_callback_query(call.id, "❌ لم تشترك")

@bot.message_handler(func=lambda m: m.text == buttons["balance"])
def balance(message):
    uid = message.from_user.id
    if is_banned(uid): return
    user = get_user(uid)
    vip = "🌟 VIP" if user["vip"] else "🔑 عادي"
    bot.send_message(uid, f"💰 رصيدك: {user['points']} نقطة\n🔹 الحالة: {vip}")

@bot.message_handler(func=lambda m: m.text == buttons["support"])
def support(message):
    bot.send_message(message.chat.id, f"📞 الدعم: {SUPPORT_USER}")

@bot.message_handler(func=lambda m: m.text == buttons["status"])
def status(message):
    uid = message.from_user.id
    if is_banned(uid): return
    user = get_user(uid)
    bot.send_message(uid, f"📊 حالتك محفوظة. لديك {user['points']} نقطة")

@bot.message_handler(func=lambda m: m.text == buttons["request"])
def request_followers(message):
    uid = message.from_user.id
    if is_banned(uid): return
    msg = bot.send_message(uid, "📨 أرسل رابط قناتك:\nhttps://t.me/YourChannel")
    bot.register_next_step_handler(msg, lambda m: save_channel(m, uid))

def save_channel(message, uid):
    if not message.text.startswith("https://t.me/"):
        return bot.send_message(uid, "❌ رابط غير صالح")
    username = message.text.split("/")[-1]
    ch = f"@{username}"
    if ch not in channels:
        channels[ch] = True
        save_json(CHANNELS_FILE, channels)
        bot.send_message(uid, f"✅ تم إضافة قناتك {ch}")

# أوامر الأدمن
@bot.message_handler(commands=["admin"])
def admin_cmds(message):
    if message.from_user.id != ADMIN_ID: return
    bot.send_message(message.chat.id, """
⚖️ أوامر الأدمن:
/addchannel @ch
/removechannel @ch
/channels
/setpoints @user 100
/vip @user
/ban @user
/unban @user
/addbutton نص
/buttons
""")

@bot.message_handler(commands=["addchannel", "removechannel", "channels", "setpoints", "vip", "ban", "unban", "addbutton", "buttons"])
def admin_actions(message):
    if message.from_user.id != ADMIN_ID: return
    cmd, *args = message.text.split()
    if cmd == "/addchannel" and args:
        channels[args[0]] = True
        save_json(CHANNELS_FILE, channels)
        bot.send_message(message.chat.id, f"✅ أضفت {args[0]}")
    elif cmd == "/removechannel" and args:
        channels.pop(args[0], None)
        save_json(CHANNELS_FILE, channels)
        bot.send_message(message.chat.id, f"❌ حذفت {args[0]}")
    elif cmd == "/channels":
        bot.send_message(message.chat.id, "\n".join(channels.keys()) or "لا يوجد")
    elif cmd == "/setpoints" and len(args) == 2:
        uname = args[0].replace("@", "")
        pts = int(args[1])
        for uid, u in users.items():
            if u.get("username") == uname:
                users[uid]["points"] = pts
                save_json(USERS_FILE, users)
                bot.send_message(message.chat.id, f"✅ {uname} = {pts}")
                return
        bot.send_message(message.chat.id, "❌ لم يعثر على المستخدم")
    elif cmd == "/vip" and args:
        uname = args[0].replace("@", "")
        for uid, u in users.items():
            if u.get("username") == uname:
                users[uid]["vip"] = True
                save_json(USERS_FILE, users)
                bot.send_message(message.chat.id, f"🌟 تم ترقية {uname} لـ VIP")
                return
        bot.send_message(message.chat.id, "❌ لم يتم العثور")
    elif cmd == "/ban" and args:
        uname = args[0].replace("@", "")
        for uid, u in users.items():
            if u.get("username") == uname:
                banned[uid] = True
                save_json(BANNED_FILE, banned)
                bot.send_message(message.chat.id, f"⛔ تم حظر {uname}")
                return
    elif cmd == "/unban" and args:
        uname = args[0].replace("@", "")
        for uid, u in users.items():
            if u.get("username") == uname:
                banned.pop(uid, None)
                save_json(BANNED_FILE, banned)
                bot.send_message(message.chat.id, f"✅ تم رفع الحظر {uname}")
                return
    elif cmd == "/addbutton" and args:
        key = args[0]
        text = " ".join(args)
        buttons[key] = text
        save_json(BUTTONS_FILE, buttons)
        bot.send_message(message.chat.id, f"✉ تم إضافة زر: {text}")
    elif cmd == "/buttons":
        out = "\n".join(buttons.values()) or "لا يوجد أزرار"
        bot.send_message(message.chat.id, out)

# Webhook
@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
