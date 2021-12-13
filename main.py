import telebot
from telebot import types
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import date, timedelta
from tokenT import token
from helper_func import (num_of_current_week, get_day, start_time,
                         subject_type, weekday)

bot = telebot.TeleBot(token)
conn = psycopg2.connect(database="schedule_bot",
                        user="dbadmin",
                        password="pass",
                        host="localhost",
                        port="5434")
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()



keyboard = types.InlineKeyboardMarkup()
b_mon = types.InlineKeyboardButton(text='Понедельник', callback_data='0')
b_tue = types.InlineKeyboardButton(text='Вторник', callback_data='1')
b_wed = types.InlineKeyboardButton(text='Среда', callback_data='2')
b_thu = types.InlineKeyboardButton(text='Четверг', callback_data='3')
b_fri = types.InlineKeyboardButton(text='Пятница', callback_data='4')
b_sat = types.InlineKeyboardButton(text='Суббота', callback_data='5')
b_this = types.InlineKeyboardButton(text='Эта неделя', callback_data='t')
b_next = types.InlineKeyboardButton(text='Следующая неделя', callback_data='n')
keyboard.add(b_mon, b_tue, b_wed, b_thu, b_fri, b_sat, b_this, b_next)


def day_schedule(data, cur_date):
    query = f"SELECT timetable.subject, timetable.s_type, room_numb, start_time, full_name FROM public.timetable \
              INNER JOIN public.teacher ON (public.timetable.subject = public.teacher.subject AND \
              public.timetable.s_type = public.teacher.s_type) WHERE day='{get_day(int(data), cur_date)}' ORDER BY start_time ASC"
    cursor.execute(query)
    ans = cursor.fetchall()
    s = weekday(int(data)) + '\n'
    for i in ans:
        s += f"{start_time(i[3])} {i[0]} {subject_type(i[1])} {i[2]} {i[4]} \n"
    return s




@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Здравствуйте! Это бот с расписанием группы БВТ2104. Введите /help, чтобы узнать список команд', reply_markup=keyboard)

@bot.message_handler(commands=['mtuci'])
def mtuci(message):
    bot.send_message(message.chat.id, 'https://mtuci.ru/')

@bot.message_handler(commands=['week'])
def week(message):
    s = 'Сейчас ' + ('верхняя' if num_of_current_week(date.today()) % 2 == 0 else 'нижняя') + ' неделя'
    bot.send_message(message.chat.id, s, reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def help(message):
    s = 'Список команд: \n \
        /week - верхняя или нижняя неделя \n \
        /mtuci или "сайт" - ссылка на сайт МТУСИ \n \
        Нажимайте на кнопки, чтобы получить расписание на соответствующий день/неделю \n \
        Этого бота сделал Афанасьев Никита из БВТ2104. Поднял docker с postgres и adminer, присоединился к БД \
        при помощи psycopg2, для работы с телегой - pyTelegramBotAPI. В репозитории есть папка db с файлами для \
        инициализации БД'
    bot.send_message(message.chat.id, s, reply_markup=keyboard)

@bot.callback_query_handler(func = lambda call: True)
def schedule(call):
    data = call.data
    weekdays = '012345'
    cur_date = date.today()
    if data in weekdays:
        s = day_schedule(data, cur_date)
        bot.send_message(call.message.chat.id, s, reply_markup=keyboard)
    elif data == 't':
        s = 'Расписание на эту неделю: \n'
        for i in weekdays:
            s += day_schedule(i, cur_date)
        bot.send_message(call.message.chat.id, s, reply_markup=keyboard)
    elif data == 'n':
        s = 'Расписание на следующую неделю: \n'
        for i in weekdays:
            s += day_schedule(i, cur_date + timedelta(7))
        bot.send_message(call.message.chat.id, s, reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def answer(message):
    if message.text.lower() == "сайт":
        bot.send_message(message.chat.id, 'https://mtuci.ru/')
    else:
        bot.send_message(message.chat.id, 'Извините, я Вас не понял')


if __name__ == '__main__':
    bot.infinity_polling()