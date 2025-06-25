import telebot
from generate_video import generate_ai_video
import flask
from flask import request

BOT_TOKEN = "7986534203:AAEhipvwQCuhxF_67M3pSx6naPCjnX86Zb0"
bot = telebot.TeleBot(BOT_TOKEN)
app = flask.Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "🎬 جاري إنشاء الفيديو بالذكاء الاصطناعي، يرجى الانتظار...")

    try:
        video_path = generate_ai_video()
        with open(video_path, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="✅ تم إنشاء الفيديو بنجاح!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ حدث خطأ أثناء توليد الفيديو: {e}")

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@app.route('/', methods=['GET'])
def index():
    return 'بوت الفيديو يعمل ✅', 200