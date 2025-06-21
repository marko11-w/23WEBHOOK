...

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
