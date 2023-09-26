from loguru import logger
import telebot


@logger.catch
def recognize_language(msg: telebot.types.Message):
    """
    Определяет язык системы пользователя
    :param msg: telegram.types.Message
    :return:
    """
    lcl = msg.from_user.language_code
    if lcl == 'en':
        lcl = 'en_US'
    elif lcl == 'ru':
        lcl = 'ru_RU'

    return lcl
