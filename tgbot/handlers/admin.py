from telebot import TeleBot
from telebot.types import Message
from tgbot.handlers.emails import get_email_by_id
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def admin_user(message: Message, bot: TeleBot):
    """
    You can create a function and use parameter pass_bot.
    """
    greetings = "📣📣📣️<b> Привет!</b> \n\n" \
                "<b>Заявить о технических проблемах стало проще! 🧨\n\n</b>" \
                "<i>Теперь на IT-Support@ac.gov.ru можно оставить обращение через Telegram c помощью нового бота от 'Ангара.17'! \n\n</i>" \
                "---------------------------------------------\n" \
                "<b>На сегодня реализовали следующее:</b> \n" \
                " 📩 Проблемы при работе с почтой\n" \
                " 🌐 Проблемы с интернетом, Wi-Fi\n" \
                " 🖨 Проблемы в печатью, принтером\n" \
                " 📺 Проблемы с оборудованием в переговорной\n" \
                " 🎥 Сделать заявку на ВКС\n" \
                "---------------------------------------------\n" \
                "Уже можно начать! Нажми кнопку внизу чата в зависимости от проблемы и оставь тестовое обращение! Не " \
                "забываем, что меню можно скроллить ⏫⏬ "
    to_meet = "Добро пожаловать в чат технической поддержки сотрудников КЦ! К сожалению, мы с Вами еще не знакомы. Я " \
              "направить информацию администратору для организации Вам возможности оставлять обращения! Нужно " \
              "немного подождать, а пока можете оставить запрос стандартным способом! Спасибо! "
    markup = ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    markup.add(KeyboardButton('Новое обращение!'))
    try:
        is_user_exist = get_email_by_id(message)
        if is_user_exist:
            bot.send_message(message.chat.id, greetings, parse_mode='html', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, to_meet)
            bot.send_message('287994530', str(message))
    except Exception as e:
        print(e)
