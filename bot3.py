import os
import telebot

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Бот успешно запущен на Render! 🎉")

if __name__ == '__main__':
    bot.polling(none_stop=True)
