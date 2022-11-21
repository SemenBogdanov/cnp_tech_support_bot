# handlers
from tgbot.handlers.admin import admin_user
from tgbot.handlers.user import any_user
from tgbot.handlers.emails import send_support_mail_1

# telebot
from telebot import TeleBot

# config


# I recommend increasing num_threads
from tgbot.key import TOKEN

bot = TeleBot(TOKEN, num_threads=5)


def register_handlers():
    bot.register_message_handler(admin_user, commands=['start'], pass_bot=True)
    # bot.register_message_handler(any_user, commands=['start'],  pass_bot=True)
    bot.register_message_handler(send_support_mail_1, commands=['new'], pass_bot=True)
    bot.register_message_handler(send_support_mail_1, func=lambda msg: msg.text == 'Новое обращение!', pass_bot=True)


register_handlers()


def run():
    print('Запуск бота...')
    bot.infinity_polling()


run()
