import telebot
from telebot import types
from flask import Flask, request
import json
import os

API_TOKEN = "7877754239:AAFP3ljogZijfNia3sVdgnEaIPR9EbrgGK8"
ADMIN_ID = 7758666677

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

USERS_FILE = os.path.join(DATA_DIR, "users.json")
CHANNELS_FILE = os.path.join(DATA_DIR, "channels.json")
BUTTONS_FILE = os.path.join(DATA_DIR, "buttons.json")
BANNED_FILE = os.path.join(DATA_DIR, "banned.json")


def load_json(path):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

users = load_json(USERS_FILE)
channels = load_json(CHANNELS_FILE)
buttons = load_json(BUTTONS_FILE)
banned = load_json(BANNED_FILE)

default_buttons = {
    "collect": "🔄 جمع النقاط",
    "request": "➕ طلب متابعين",
    "balance": "📊 رصيدي",
    "status": "🎯 حالتي",
    "support": "📞 الدعم"
}
buttons.update(default_buttons)

def get_user(uid):
    uid = str(uid)
    if uid not in users:
        users[uid] = {"points": 0, "vip": False}
    return users[uid]

def is_banned(uid):
    return str(uid) in banned

def check_subscription(user_id, username):
    try:
        member = bot.get_chat_member(username, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
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

@bot.message_handler(commands=["admin"])
def admin_help(message):
    if message.from_user.id != ADMIN_ID:
        return
    help_text = '''
🛠 أوامر الأدمن:
/addchannel @channel
/removechannel @channel
/channels
/setpoints @username عدد
/vip @username
/ban @username
/unban @username
/addbutton نص_الزر
/buttons
'''
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=["setpoints", "vip", "ban", "unban", "addchannel", "removechannel", "channels", "addbutton", "buttons"])
def admin_commands(message):
    if message.from_user.id != ADMIN_ID:
        return
    cmd, *args = message.text.split()

    if cmd == "/setpoints" and len(args) == 2:
        identifier = args[0].replace("@", "")
        try:
            points = int(args[1])
        except:
            bot.send_message(message.chat.id, "❌ عدد النقاط غير صالح")
            return
        found = False
        for uid, data in users.items():
            if data.get("username") == identifier or uid == identifier:
                users[uid]["points"] = points
                save_json(USERS_FILE, users)
                bot.send_message(message.chat.id, f"✅ تم تعيين {points} نقطة للمستخدم {identifier}")
                found = True
                break
        if not found:
            bot.send_message(message.chat.id, "❌ لم يتم العثور على المستخدم")

    elif cmd == "/vip" and args:
        uname = args[0].replace("@", "")
        for uid, data in users.items():
            if data.get("username") == uname or uid == uname:
                users[uid]["vip"] = True
                save_json(USERS_FILE, users)
                bot.send_message(message.chat.id, f"🎖️ تم ترقية المستخدم {uname} إلى VIP")
                return
        bot.send_message(message.chat.id, "❌ لم يتم العثور على المستخدم")

    elif cmd == "/ban" and args:
        uname = args[0].replace("@", "")
        for uid, data in users.items():
            if data.get("username") == uname or uid == uname:
                banned[uid] = True
                save_json(BANNED_FILE, banned)
                bot.send_message(message.chat.id, f"🚫 تم حظر المستخدم {uname}")
                return
        bot.send_message(message.chat.id, "❌ لم يتم العثور على المستخدم")

    elif cmd == "/unban" and args:
        uname = args[0].replace("@", "")
        for uid, data in users.items():
            if data.get("username") == uname or uid == uname:
                banned.pop(uid, None)
                save_json(BANNED_FILE, banned)
                bot.send_message(message.chat.id, f"✅ تم إلغاء الحظر عن المستخدم {uname}")
                return
        bot.send_message(message.chat.id, "❌ لم يتم العثور على المستخدم")

    elif cmd == "/addchannel" and args:
        ch = args[0]
        channels[ch] = True
        save_json(CHANNELS_FILE, channels)
        bot.send_message(message.chat.id, f"✅ تم إضافة القناة {ch}")

    elif cmd == "/removechannel" and args:
        ch = args[0]
        if ch in channels:
            del channels[ch]
            save_json(CHANNELS_FILE, channels)
            bot.send_message(message.chat.id, f"🗑️ تم حذف القناة {ch}")
        else:
            bot.send_message(message.chat.id, "❌ القناة غير موجودة")

    elif cmd == "/channels":
        if channels:
            text = "\n".join(channels.keys())
        else:
            text = "لا توجد قنوات"
        bot.send_message(message.chat.id, text)

    elif cmd == "/addbutton" and args:
        key = "_".join(args)
        buttons[key] = " ".join(args)
        save_json(BUTTONS_FILE, buttons)
        bot.send_message(message.chat.id, f"تمت إضافة زر: {buttons[key]}")

    elif cmd == "/buttons":
        btns = "\n".join(buttons.values())
        bot.send_message(message.chat.id, f"🧮 الأزرار الحالية:\n{btns}")

@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
