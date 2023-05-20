import logging

from telebot import types

from services.db_data import get_directions_from_db, get_sub_directions_from_db, \
    get_sections_from_db, get_questions_from_db
from services.redis_db import add_keyboard_for_questions_in_redis

logger = logging.getLogger(__name__)


def keyboard_enter_menu_for_clients():
    """Keyboard for main menu"""
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    key1 = types.InlineKeyboardButton(text='🎲 Брифинг', callback_data='scenario')
    key2 = types.InlineKeyboardButton(text='📝 Формирование КП', callback_data='formation_of_the_cp')
    key3 = types.InlineKeyboardButton(text='👨‍💻 Чат с оператором', callback_data='chat_with_operator')
    key4 = types.InlineKeyboardButton(text='💬 Сервис мгновенных сообщений', callback_data='instant_messaging_service')
    key5 = types.InlineKeyboardButton(text='📈 Выгрузка отчёта', callback_data='upload_report')
    key6 = types.InlineKeyboardButton(text='🤳 Блог', callback_data='blog')
    keyboard.add(key1, key2, key3, key4, key5, key6)
    return keyboard


def keyboard_for_briefings():
    keyboard = types.InlineKeyboardMarkup()
    list_of_directions = get_directions_from_db()
    logger.info(f'Клавиатура выбора директорий - {list_of_directions}')
    for i in list_of_directions:
        keyboard.add(types.InlineKeyboardButton(text=i[0], callback_data=i[0]))
        logger.info(f'В keyboard_for_scenario Созданы callbackи: {i[0]}')
    cancel = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    keyboard.add(cancel)
    return keyboard


def keyboard_for_direction(direction):
    keyboard = types.InlineKeyboardMarkup()
    list_of_sub_directions = get_sub_directions_from_db(direction)
    if list_of_sub_directions:
        logger.info(f'Клавиатура выбора поддиректорий - {list_of_sub_directions}')
        for sub_direction in list_of_sub_directions:
            keyboard.add(
                types.InlineKeyboardButton(text=sub_direction[0], callback_data=f'{direction}|{sub_direction[0]}'))
            logger.info(f'В keyboard_for_direction Созданы callbackи: {direction}|{sub_direction[0]}')
    else:
        list_of_sections = get_sections_from_db(direction)
        logger.info(f'Клавиатура выбора секций вопросов - {list_of_sections}')
        for section in list_of_sections:
            keyboard.add(types.InlineKeyboardButton(text=section[0], callback_data=f'{direction}|{section[0]}'))
            logger.info(f'В keyboard_for_direction Созданы callbackи: {direction}|{section[0]}')
    cancel = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    keyboard.add(cancel)
    return keyboard


def keyboard_for_sub_direction(path):
    logger.info(f'Клавиатура выбора подкатегорий')
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    list_of_subcategories = get_sections_from_db(path.split('|')[0], path.split('|')[1])
    for i in list_of_subcategories:
        keyboard.add(types.InlineKeyboardButton(text=i[0], callback_data=f'{path}|{i[0]}'))
        logger.info(f'В keyboard_for_sub_direction: Созданы callbackи: {path}|{i[0]}')
    cancel = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    keyboard.add(cancel)
    return keyboard


def keyboard_for_questions(user_id: int, path: str):
    logger.info(f'Клавиатура вопросов: {path}')
    add_keyboard_for_questions_in_redis(user_id, path)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    if len(path.split('|')) == 2:  # если мы перешли с dir|sec
        list_of_questions = get_questions_from_db(path.split('|')[0], path.split('|')[1])

        for i in list_of_questions:
            keyboard.add(types.InlineKeyboardButton(text=f'Вопрос {i[1]}', callback_data=f'question_{i[0]}'))
            logger.info(f'В keyboard_for_questions Созданы callbackи: question_{i[0]}')
    if len(path.split('|')) == 3:  # если мы перешли с dir|sub|sec
        list_of_questions = get_questions_from_db(path.split('|')[0], path.split('|')[2], path.split('|')[1])
        for i in list_of_questions:
            keyboard.add(types.InlineKeyboardButton(text=f'Вопрос {i[1]}', callback_data=f'question_{i[0]}'))
            logger.info(f'В keyboard_for_questions Созданы callbackи: question_{i[0]}')
    cancel = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    keyboard.add(cancel)
    return keyboard


def keyboard_for_answer(answers):
    logger.info(f'Клавиатура ответов')
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for answer in answers:
        keyboard.add(types.KeyboardButton(text=answer))
    keyboard.add(types.KeyboardButton(text="Отправить ответ"))
    keyboard.add(types.KeyboardButton(text="К вопросам"))
    return keyboard


def keyboard_for_change_answer():
    logger.info(f'Клавиатура для изменения')
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    key1 = types.InlineKeyboardButton(text='Изменить ответ', callback_data='change_answer')
    cancel = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    keyboard.add(key1, cancel)
    return keyboard


def keyboard_for_operator():
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    key1 = types.InlineKeyboardButton(text='✅Вступить в диалог', callback_data='enter_into_a_dialog')
    keyboard.add(key1)
    return keyboard


def keyboard_for_delete_dialogue():
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    key1 = types.InlineKeyboardButton(text='❌Выйти из диалога', callback_data='cancel_from_dialog')
    keyboard.add(key1)
    return keyboard


def keyboard_send_phone():
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    send_phone_button = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    cancel_button = types.KeyboardButton(text="Отменить")
    keyboard.add(send_phone_button, cancel_button)
    return keyboard


# REMOVE KEYBOARD
def remove_keyboard(message, bot, text: str) -> None:
    bot.send_message(message.chat.id, f'{text}',
                     reply_markup=types.ReplyKeyboardRemove())
