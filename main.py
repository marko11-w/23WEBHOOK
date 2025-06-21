import telebot
from telebot import types
from flask import Flask, request
import json
import os

API_TOKEN = "7877754239:AAFP3ljogZijfNia3sVdgnEaIPR9EbrgGK8"
ADMIN_ID = 7758666677

bot = telebot.TeleBot(API_TOKEN, parse_mode="Markdown")
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

@bot.message_handler(func=lambda m: m.text == buttons["support"])
def handle_support(message):
    bot.send_message(message.chat.id, "📞 تواصل مع الدعم: [@M_A_R_K75](https://t.me/M_A_R_K75)")

# باقي الكود بدون تغيير...
@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
