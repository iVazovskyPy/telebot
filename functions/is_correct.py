from loguru import logger
import telebot


@logger.catch
def is_correct(msg: telebot.types.Message, lst: list, arg1: str, func, arg2=None):
    """
    Проверяет корректность введенных данных диапозона цен либо расстояний
    :param msg: telebot.types.Message
    :param lst: list()
    :param arg1: str() or list()
    :param func: function
    :param arg2: str()
    :return:
    """
    message = None

    if not lst[0].isdigit() or not lst[1].isdigit() or len(lst) != 2:
        if msg.from_user.language_code == 'ru':
            message = bot.send_message(msg.from_user.id, 'Было введено некорректное значение (необходимо ввести '
                                                         'верхнюю и нижнюю грнаицы диапозона поиска), введите любое '
                                                         'значение для продолжения')
        elif msg.from_user.language_code == 'en':
            message = bot.send_message(msg.from_user.id, 'Was received incorrect value (you should\'ve enter lower '
                                                         'and upper borders of search range), please enter something '
                                                         'to continue')
        if not arg2:
            return bot.register_next_step_handler(message, func, arg1)
        else:
            return bot.register_next_step_handler(message, func, arg2, arg1)
    elif int(lst[0]) > int(lst[1]):
        if msg.from_user.language_code == 'ru':
            message = bot.send_message(msg.from_user.id, 'Было введено некорректное значение (нижняя граница должна '
                                                         'быть меньше/равна верхней), введите любое значение для '
                                                         'продолжения')
        elif msg.from_user.language_code == 'en':
            message = bot.send_message(msg.from_user.id, 'Was received incorrect value (lower border should be '
                                                         'lower/equal the upper one), please enter something '
                                                         'to continue')
        if not arg2:
            return bot.register_next_step_handler(message, func, arg1)
        else:
            return bot.register_next_step_handler(message, func, arg2, arg1)
    else:
        return 'correct'
