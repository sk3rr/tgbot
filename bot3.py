# -*- coding: utf-8 -*-
# ============================================================
#  БОТ "СООБЩЕНИЯ ИЗ ЛИЧКИ -> ГРУППА, ОТВЕТЫ ИЗ ГРУППЫ -> ЛИЧКА"
#  Готовый скрипт. Осталось вставить 2 строчки ниже и запустить.
# ============================================================

# ---------- ЧТО НУЖНО ЗАМЕНИТЬ ----------
TOKEN = "bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))"  # токен из BotFather
GROUP_ID = -1001234567890                   # ID твоей группы (с минусом!)
# ----------------------------------------
import os
import re
import telebot

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# запоминаем: id сообщения в группе -> id пользователя в личке
links = {}   # {message_id_в_группе: user_id}
counter = 0


# ---------- Человек пишет боту в личку ----------
@bot.message_handler(func=lambda m: m.chat.type == "private")
def from_user(message):
    global counter
    counter += 1
    user = message.from_user
    name = user.first_name or "Пользователь"
    username = f"@{user.username}" if user.username else "без юзернейма"

    card = bot.send_message(
        GROUP_ID,
        f"📩 <b>Заявка №{counter}</b>\n"
        f"От: {name} ({username})\n"
        f"ID: <code>{user.id}</code>\n\n"
        f"Чтобы ответить — нажми <b>«Ответить»</b> на сообщение ниже.",
    )
    # копируем сообщение целиком (текст, фото, голос, файл — всё передастся)
    copied = bot.copy_message(GROUP_ID, message.chat.id, message.message_id,
                              reply_to_message_id=card.message_id)
    links[copied.message_id] = user.id

    bot.send_message(message.chat.id,
                     "✅ Сообщение отправлено! Скоро ответим 🙂")


# ---------- Ты отвечаешь реплаем в группе ----------
@bot.message_handler(func=lambda m: m.chat.id == GROUP_ID and m.reply_to_message)
def from_admin(message):
    replied = message.reply_to_message
    user_id = links.get(replied.message_id)

    if user_id is None:
        # пробуем достать ID из текста карточки (если бот перезапускался)
        match = re.search(r"ID: (\d+)", replied.text or "")
        user_id = int(match.group(1)) if match else None

    if user_id is None:
        bot.send_message(GROUP_ID,
                         "⚠️ Не понял, кому отвечать. Отвечай реплаем прямо на сообщение-заявку.")
        return

    try:
        bot.copy_message(user_id, GROUP_ID, message.message_id)
    except Exception:
        bot.send_message(GROUP_ID,
                         "⚠️ Не удалось отправить ответ: пользователь заблокировал бота.")


# ---------- Любые другие сообщения в группе — игнорируем ----------
@bot.message_handler(func=lambda m: True)
def other(message):
    pass



bot.delete_webhook(drop_pending_updates=True)
print("Бот запущен! Не закрывай это окно.")
bot.infinity_polling(timeout=20, long_polling_timeout=10, none_stop=True)