import telebot
import os
import flask
from flask import request

BOT_TOKEN = "7986534203:AAEhipvwQCuhxF_67M3pSx6naPCjnX86Zb0"
bot = telebot.TeleBot(BOT_TOKEN)
app = flask.Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "🎬 جاري إرسال الفيديو، يرجى الانتظار...")
    try:
        video_url = "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"
        bot.send_video(message.chat.id, video_url, caption="✅ هذا فيديو جاهز باستخدام الذكاء الاصطناعي!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ حدث خطأ أثناء إرسال الفيديو: {e}")

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@app.route('/', methods=['GET'])
def index():
    return 'بوت الفيديو يعمل ✅', 200
