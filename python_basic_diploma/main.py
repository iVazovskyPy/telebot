import telebot
import sqlite3
from decouple import config
from loguru import logger
from datetime import datetime
from functions.get_city_info import get_city_info
from functions.get_hotels import get_hotels
from functions.recognize_language import recognize_language
from functions.is_correct import is_correct


con = sqlite3.connect('./hotels_base.db', check_same_thread=False)
cur = con.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS hotels_table(user_id TEXT,'
            '                                        city TEXT,'
            '                                        command TEXT,'
            '                                        request_time TEXT,'
            '                                        hotel TEXT)')

bot = telebot.TeleBot(config('KEY'))
logger.add('logs/logs.log', rotation="5 MB", level='DEBUG')


@bot.message_handler(content_types=['text'])
@logger.catch
def get_text_messages(message: telebot.types.Message):
    """
    Указываем действие для бота (получить помощь по командам либо список отелей)
    :param message: telebot.types.Message
    :return:
    """

    if message.text == "/help":
        if message.from_user.language_code == 'ru':
            bot.send_message(message.from_user.id, "/lowprice — вывод самых дешёвых отелей в городе\n"
                                                   "/highprice — вывод самых дорогих отелей в городе\n"
                                                   "/bestdeal — вывод отелей, наиболее подходящих по цене и "
                                                   "расположению от центра\n"
                                                   "/history - показать последние запросы")
        elif message.from_user.language_code == 'en':
            bot.send_message(message.from_user.id, "/lowprice — to get the lowest hotel's prices in the city\n"
                                                   "/highprice — to get the highest hotel's prices in the city\n"
                                                   "/bestdeal — to get the most acceptable hotels in the city by price "
                                                   "and distance from downtown\n"
                                                   "/history - to get the last request's results")

    elif message.text == '/lowprice':
        city = str()
        if message.from_user.language_code == 'ru':
            city = bot.send_message(message.from_user.id, 'Укажите город')
        elif message.from_user.language_code == 'en':
            city = bot.send_message(message.from_user.id, 'Specify your city')
        bot.register_next_step_handler(city, get_city_l)

    elif message.text == '/highprice':
        city = str()
        if message.from_user.language_code == 'ru':
            city = bot.send_message(message.from_user.id, 'Укажите город')
        elif message.from_user.language_code == 'en':
            city = bot.send_message(message.from_user.id, 'Specify your city')
        bot.register_next_step_handler(city, get_city_h)

    elif message.text == '/bestdeal':
        city = str()
        if message.from_user.language_code == 'ru':
            city = bot.send_message(message.from_user.id, 'Укажите город')
        elif message.from_user.language_code == 'en':
            city = bot.send_message(message.from_user.id, 'Specify your city')
        bot.register_next_step_handler(city, set_price_range)
    elif message.text == '/history':
        # query = 'SELECT * FROM requests_calls ORDER BY r_time DESC'
        query = 'SELECT * FROM requests_calls'
        cur.execute(query)
        requests = cur.fetchall()[-3:]
        output_line = str()

        if message.from_user.language_code == 'ru':
            command = 'Команда: '
            city_lang_line = 'Город: '
            time_lang_line = 'Время запроса: '
            hotels_lang_line = 'Отели: '
            distance_range = 'Диапозон расстояний: '
            price_range = 'Диапозон цен: '
        else:
            command = 'Command: '
            city_lang_line = 'City: '
            time_lang_line = 'Request\'s time: '
            hotels_lang_line = 'Hotels: '
            distance_range = 'Distance range: '
            price_range = 'Price range: '

        for i_req in requests[::-1]:
            is_topic_set = False
            if i_req[0] != 'bestdeal':
                query = 'SELECT * FROM hotels_table WHERE user_id=' + str(message.chat.id) + '  AND request_time=' + '\'' \
                        + str(i_req[1]) + '\''
                cur.execute(query)
                res = cur.fetchall()
                if len(res) < 3:
                    stop = len(res)
                else:
                    stop = 3
                for i_tuple in res[:stop]:
                    if not is_topic_set:
                        output_line += command + i_tuple[2] + '\n' + city_lang_line + i_tuple[1] + '\n' \
                                       + time_lang_line + i_tuple[3] + '\n' + hotels_lang_line + '\n-  ' + i_tuple[4] + '\n'
                        is_topic_set = True
                    else:
                        output_line += '-  ' + i_tuple[4] + '\n'

                output_line += '\n'
                is_topic_set = False

            else:
                query = 'SELECT * FROM best_deal_table WHERE user_id=' + str(
                    message.chat.id) + '  AND request_time=' + '\'' \
                        + str(i_req[1]) + '\''
                cur.execute(query)
                res = cur.fetchall()
                if len(res) < 3:
                    stop = len(res)
                else:
                    stop = 3

                is_deal_topic_set = False
                for i_tuple in res[:stop]:
                    if not is_deal_topic_set:
                        output_line += command + i_tuple[2] + '\n' + city_lang_line + i_tuple[1] + '\n' + price_range \
                                       + str(i_tuple[3]) + ' - ' + str(i_tuple[4]) + '\n' + distance_range + \
                                       str(i_tuple[5]) + ' - ' + str(i_tuple[6]) + '\n' + time_lang_line + i_tuple[7] \
                                       + '\n' + hotels_lang_line + '\n-  ' + i_tuple[8] + '\n'
                        is_deal_topic_set = True
                    else:
                        output_line += '-  ' + i_tuple[8] + '\n'
                output_line += '\n'
                is_deal_topic_set = False

        bot.send_message(message.from_user.id, output_line[:-2])

    else:
        if message.from_user.language_code == 'ru':
            bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")
        elif message.from_user.language_code == 'en':
            bot.send_message(message.from_user.id, "Sorry but i can't understand you, please use the command /help.")


@bot.message_handler(content_types=['text'])
@logger.catch
def get_city_l(message: telebot.types.Message):
    """
    Выводит результирующую строку состоящую из списка отелей по возрастанию цены
    :param message: telebot.types.Message
    :return:
    """
    locale = recognize_language(message)

    city_info = get_city_info(message.text, locale)
    result = get_hotels(city_info, locale)
    user_id = message.chat.id
    city = message.text
    command = 'lowprice'
    requests_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    hotels_list = list()

    cur.execute('CREATE TABLE IF NOT EXISTS requests_calls(request TEXT,'
                '                                          r_time TEXT)')

    cur.execute('INSERT INTO requests_calls VALUES(?, ?)', [r'lowprice',
                                                            datetime.now().strftime("%d/%m/%Y %H:%M:%S")])

    for i_line in result.split('\n'):
        if i_line != "":
            hotels_list.append(i_line)

    for i_line in hotels_list:
        cur.execute('INSERT INTO hotels_table VALUES(?,?,?,?,?)', [user_id, city, command, requests_time, i_line])

    con.commit()
    bot.send_message(message.from_user.id, result)


@bot.message_handler(content_types=['text'])
@logger.catch
def get_city_h(message: telebot.types.Message):
    """
    Выводит результирующую строку состоящую из списка отелей по убыванию цены
    :param message: telebot.types.Message
    :return:
    """
    locale = recognize_language(message)

    city_info = get_city_info(message.text, locale)
    result = get_hotels(city_info, locale, rev=True)
    user_id = message.chat.id
    city = message.text
    command = 'highprice'
    requests_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    hotels_list = list()

    cur.execute('CREATE TABLE IF NOT EXISTS requests_calls(request TEXT,'
                '                                          r_time TEXT)')

    cur.execute('INSERT INTO requests_calls VALUES(?, ?)', [r'highprice',
                                                            datetime.now().strftime("%d/%m/%Y %H:%M:%S")])

    for i_line in result.split('\n'):
        if i_line != "":
            hotels_list.append(i_line)

    for i_line in hotels_list:
        cur.execute('INSERT INTO hotels_table VALUES(?,?,?,?,?)', [user_id, city, command, requests_time, i_line])

    con.commit()
    bot.send_message(message.from_user.id, result)


@bot.message_handler(content_types=['text'])
@logger.catch
def set_price_range(message: telebot.types.Message, is_arg_exists=None):
    """
    Запрашивает диапозон цен
    :param message: telebot.types.Message
    :param is_arg_exists: str()
    :return:
    """
    price_range = str()
    if message.from_user.language_code == 'ru':
        price_range = bot.send_message(message.from_user.id, 'Укажите диапозон цен (через пробел)')
    elif message.from_user.language_code == 'en':
        price_range = bot.send_message(message.from_user.id, 'Specify your price range (with space)')

    if is_arg_exists:
        bot.register_next_step_handler(price_range, set_distance_range, is_arg_exists)
    else:
        bot.register_next_step_handler(price_range, set_distance_range, message.text)


@bot.message_handler(content_types=['text'])
@logger.catch
def set_distance_range(message: telebot.types.Message, city: str, price_is_received=None):
    """
    Запрашивает диапозон удалённости от центра
    :param message: telebot.types.Message
    :param city: str()
    :param price_is_received: str()
    :return:
    """
    price_list = message.text.split()
    distance_range = str()

    if not price_is_received:
        correct = is_correct(message, price_list, city, set_price_range)
        if correct == 'correct':
            if message.from_user.language_code == 'ru':
                distance_range = bot.send_message(message.from_user.id, 'Укажите диапозон растояний (через пробел)')
            elif message.from_user.language_code == 'en':
                distance_range = bot.send_message(message.from_user.id, 'Specify distance range(with space)')
            bot.register_next_step_handler(distance_range, get_distances, message.text, city)
    else:
        if message.from_user.language_code == 'ru':
            distance_range = bot.send_message(message.from_user.id, 'Укажите диапозон растояний (через пробел)')
        elif message.from_user.language_code == 'en':
            distance_range = bot.send_message(message.from_user.id, 'Specify distance range(with space)')
        bot.register_next_step_handler(distance_range, get_distances, price_is_received, city)


@bot.message_handler(content_types=['text'])
@logger.catch
def get_distances(message: telebot.types.Message, price: str, city: str):
    """
    Выводит строку состоящую из списка отелей подходящих по цене и удалённости от центра
    :param message: telebot.types.Message
    :param price: str()
    :param city: str()
    :return:
    """
    distance_list = message.text.split()
    locale = recognize_language(message)

    correct = is_correct(message, distance_list, price, set_distance_range, city)
    if correct == 'correct':
        distance = message.text.split()
        price = price.split()
        city_info = get_city_info(city, locale)
        result = get_hotels(city_info, locale)
        result_line = str()
        hotel_price = float()
        hotel_distance = float()

        data = result.split('\n')
        for i_line in data:
            if i_line:
                line_chars = i_line.split()
                for i_index, i_char in enumerate(line_chars):
                    if message.from_user.language_code == 'en':
                        if "$" in i_char:
                            hotel_price = float(i_char[:-2])
                    elif message.from_user.language_code == 'ru':
                        if 'руб.' in i_char:
                            hotel_price = float(line_chars[i_index - 1])
                    if i_index == len(line_chars) - 2:
                        hotel_distance = float(i_char)
                if (float(price[0]) <= hotel_price <= float(price[1])) and (
                        float(distance[0]) <= hotel_distance <= float(distance[1])):
                    result_line += i_line + '\n\n'

        if result_line:
            cur.execute('CREATE TABLE IF NOT EXISTS best_deal_table(user_id TEXT,'
                        '                                           city TEXT,'
                        '                                           command TEXT,'
                        '                                           price_range_l INTEGER,'
                        '                                           price_range_r INTEGER,'
                        '                                           dis_range_l INTEGER,'
                        '                                           dis_range_r INTEGER,'
                        '                                           request_time TEXT,'
                        '                                           hotel TEXT)')

            cur.execute('CREATE TABLE IF NOT EXISTS requests_calls(request TEXT,'
                        '                                          r_time TEXT)')

            cur.execute('INSERT INTO requests_calls VALUES(?, ?)', [r'bestdeal',
                                                                    datetime.now().strftime("%d/%m/%Y %H:%M:%S")])

            user_id = message.chat.id
            command = r'bestdeal'
            requests_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            hotels_list = list()

            for i_line in result_line.split('\n'):
                if i_line != "":
                    hotels_list.append(i_line)

            for i_line in hotels_list:
                cur.execute('INSERT INTO best_deal_table VALUES(?,?,?,?,?,?,?,?,?)', [user_id, city, command, price[0],
                                                                                   price[1], distance[0], distance[1],
                                                                                   requests_time, i_line])

            con.commit()
            bot.send_message(message.from_user.id, result_line)
        else:
            if message.from_user.language_code == 'en':
                bot.send_message(message.from_user.id, 'There\'s nothing found by specified criteria')
            elif message.from_user.language_code == 'ru':
                bot.send_message(message.from_user.id, 'По указанным критериям ни чего не найдено')


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
