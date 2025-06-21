import telebot
from telebot import types
from flask import Flask, request
import threading

API_TOKEN = "7877754239:AAFP3ljogZijfNia3sVdgnEaIPR9EbrgGK8"
ADMIN_ID = 7758666677
SUPPORT_USER = "@M_A_R_K75"

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

users = {}
channels = [{"username": "@MA_R_KO1", "owner": "admin"}]
buttons = {
    "collect": "🔄 جمع النقاط",
    "request": "➕ طلب متابعين",
    "balance": "📊 رصيدي",
    "status": "🎯 حالتي",
    "support": "📞 الدعم الفني"
}
welcome_text = "👋 مرحبًا بك في بوت رحلة المليار!"

def get_user(uid):
    if uid not in users:
        users[uid] = {"points": 0, "channel": None}
    return users[uid]

def check_subscription(user_id, username):
    try:
        member = bot.get_chat_member(username, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id
    get_user(uid)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(buttons["collect"], buttons["request"])
    markup.row(buttons["balance"], buttons["status"])
    markup.row(buttons["support"])
    bot.send_message(uid, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == buttons["collect"])
def collect_points(message):
    uid = message.from_user.id
    user = get_user(uid)
    for ch in channels:
        if check_subscription(uid, ch["username"]):
            continue
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("اشترك ثم اضغط هنا ✅", callback_data="check_" + ch["username"]))
        bot.send_message(uid, f"📢 اشترك في القناة {ch['username']} لتحصل على 10 نقاط", reply_markup=markup)
        return
    bot.send_message(uid, "✅ لقد اشتركت في كل القنوات المتاحة حالياً.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def check_channel(call):
    uid = call.from_user.id
    username = call.data.split("_", 1)[1]
    if check_subscription(uid, username):
        users[uid]["points"] += 10
        bot.answer_callback_query(call.id, "✅ تم التحقق، وتمت إضافة 10 نقاط!")
        bot.send_message(uid, "🎉 تم إضافة 10 نقاط إلى رصيدك.")
    else:
        bot.answer_callback_query(call.id, "❌ لم يتم العثور على اشتراكك بالقناة.")

@bot.message_handler(func=lambda m: m.text == buttons["balance"])
def balance(message):
    uid = message.from_user.id
    user = get_user(uid)
    bot.send_message(uid, f"💰 رصيدك الحالي: {user['points']} نقطة")

@bot.message_handler(func=lambda m: m.text == buttons["support"])
def support(message):
    bot.send_message(message.chat.id, f"📞 للتواصل مع الدعم: {SUPPORT_USER}")

@bot.message_handler(func=lambda m: m.text == buttons["status"])
def status(message):
    uid = message.from_user.id
    user = get_user(uid)
    if user["channel"]:
        bot.send_message(uid, f"📡 قناتك النشطة: {user['channel']}")
    else:
        bot.send_message(uid, "❌ لا توجد قناة نشطة لك حالياً.")

@bot.message_handler(func=lambda m: m.text == buttons["request"])
def request_followers(message):
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
            bot.send_message(uid, f"❌ يجب أولاً تعيين البوت كـ مشرف في قناتك {full_username}.")
            return
    except:
        bot.send_message(uid, f"❌ فشل التحقق من قناة {full_username}.\nتأكد أن البوت مشرف وأن القناة عامة.")
        return

    if user["points"] < 2:
        bot.send_message(uid, "❌ تحتاج على الأقل نقطتين لطلب المتابعين.")
        return

    user["points"] -= 2
    user["channel"] = full_username
    channels.append({"username": full_username, "owner": uid})
    bot.send_message(uid, f"✅ تم تفعيل قناتك {user['channel']} في نظام تبادل المتابعين.")

@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)