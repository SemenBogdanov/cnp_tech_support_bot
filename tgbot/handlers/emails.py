from telebot import TeleBot
from telebot.types import Message
from email.message import EmailMessage
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import psycopg2
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.key import from_email, host_mail, port_mail, passsword_mail, username_mail, host_ip, port, username, password

ticket_data = {'mail_to': '', 'category': '', 'text': ''}


def send_support_mail_1(message: Message, bot: TeleBot):
    """
    1. Запрос к БД для проверки заполненности данных обратившегося пользователя
    2. Если пользователя нет, но запустить "знакомство"
    3. Если пользователь есть, то получить почту, опросить и отправить заявку в тех. поддержку.
    """
    is_user_exist = get_email_by_id(message)

    if len(is_user_exist):
        ticket_data['mail_to'] = is_user_exist[0]
        markup = ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
        markup.add(KeyboardButton('Проблемы с почтой'),
                   KeyboardButton('Новый ВКС или проблема с ВКС'),
                   KeyboardButton('Проблемы с интернетом'),
                   KeyboardButton('Проблемы с Wi-Fi'),
                   KeyboardButton('Проблемы с печатью'),
                   KeyboardButton('Проблемы с оборудованием в переговорной'),
                   KeyboardButton('🛠Узнать пароль от Wi-Fi (в разработке)'),
                   KeyboardButton('🛠Забронировать переговорную (в разработке)'),
                   KeyboardButton('🛠Заполнить Timesheet в Bitrix24 (в разработке)', ),
                   KeyboardButton('Отмена'),
                   )
        # msg = bot.send_message(message.chat.id, 'Пожалуйста выберите раздел для обращения', reply_markup=markup)
        msg = bot.reply_to(message, 'Пожалуйста выберите раздел для обращения', reply_markup=markup)
        bot.register_next_step_handler(msg, send_support_mail_2, bot)


def cancel_chain(message: Message, bot: TeleBot):
    start_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True).add(
        KeyboardButton('Новое обращение!'))
    bot.send_message(message.chat.id, 'Выполняется отмена. При необходимости начните заново!',
                     reply_markup=start_markup)
    bot.clear_step_handler_by_chat_id(message.chat.id)


def send_support_mail_2(message: Message, bot: TeleBot):
    if message.text in ['Отмена',
                        '🛠Узнать пароль от Wi-Fi (в разработке)',
                        '🛠Забронировать переговорную (в разработке)',
                        '🛠Заполнить Timesheet в Bitrix24 (в разработке)']:
        cancel_chain(message, bot)

    else:
        cancel_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True).add(
            KeyboardButton('Отмена'))

        ticket_data['category'] = message.text
        msg = bot.reply_to(message, 'Опишите ситуацию (что и где произошло), в свободной форме',
                           reply_markup=cancel_markup)
        bot.register_next_step_handler(msg, send_support_mail_3, bot)


def send_support_mail_3(message: Message, bot: TeleBot):
    if message.text == 'Отмена':
        bot.clear_step_handler_by_chat_id(message.chat.id)

    start_markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True).add(
        KeyboardButton('Новое обращение!'))

    m = bot.send_message(message.chat.id, 'Отправка письма в тех. поддержку...')
    ticket_data['text'] = message.text
    subject = 'Новое обращение через бота по теме: ' + ticket_data['category']
    html = f"""\
    <html>
      <head><h1>Новое обращение через бота по теме: \n{ticket_data['category']}</h1></head>
      <body>
        <hr>
        Текст обращения:<br>
        <i>{ticket_data['text']}</i>
      </body>
    </html>
    """

    part1 = MIMEText(html, 'html')
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ', '.join(ticket_data['mail_to'])
    msg.attach(part1)

    # Try to log in to server and send email

    host = smtplib.SMTP(host_mail, port_mail)
    try:
        host.connect(host_mail, port_mail)
        host.ehlo()
        host.starttls()  # Secure the connection
        host.ehlo()
        host.login(username_mail, passsword_mail)

        host.sendmail(from_email, msg['To'], msg.as_string())
        bot.delete_message(message.chat.id, m.id)
        bot.send_message(message.chat.id, 'Ваша заявка отправлена в службу технической поддержки! '
                                          'Обязательно дождитесь подтверждения запроса в электронной почте!',
                         reply_markup=start_markup)
        host.close()
    except Exception as e:
        print(e)
    finally:
        host.close()


def get_email_by_id(message: Message):
    with psycopg2.connect(host=host_ip, port=port, database='firstbase1', user=username, password=password) as conn:
        cur = conn.cursor()
        query = "select work_mail from kc_employees t1 where t1.tg_id in (%s);"
        cur.execute(query, ((message.chat.id),))
        res = cur.fetchall()
        # print(res)
        return res
