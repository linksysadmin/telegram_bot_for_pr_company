import logging

from telebot import types

from config import OPERATOR_ID
from services.db_data import get_directories, \
    get_sections_from_db, get_questions_from_db, get_questions_id_from_user_answers, get_sub_directions
from services.redis_db import add_keyboard_for_questions_in_redis, set_max_question_id_in_redis

logger = logging.getLogger(__name__)


def keyboard_enter_menu_for_clients(doc=False):
    """Keyboard for main menu"""
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    key1 = types.InlineKeyboardButton(text='📋 Составить ТЗ', callback_data='scenario')
    key2 = types.InlineKeyboardButton(text='📝 Мои тех.задания и КП',
                                      callback_data='technical_tasks_and_commercial_offer')
    key3 = types.InlineKeyboardButton(text='👨‍💻 Чат с оператором', callback_data='chat_with_operator')
    key4 = types.InlineKeyboardButton(text='💬 Поставить задачу', callback_data='instant_messaging_service')
    key5 = types.InlineKeyboardButton(text='🎲 Игры', callback_data='games')
    # key5 = types.InlineKeyboardButton(text='🤳 Блог', callback_data='blog')
    if doc is True:
        keyboard.add(key2)
    keyboard.add(key1, key3, key4, key5)
    return keyboard


def keyboard_enter_menu_for_operator():
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    key1 = types.InlineKeyboardButton(text='Запросы', callback_data='requests')
    key2 = types.InlineKeyboardButton(text='Клиенты', callback_data='clients')
    key3 = types.InlineKeyboardButton(text='Задачи', callback_data='tasks')
    key4 = types.InlineKeyboardButton(text='Настройки', callback_data='settings')
    keyboard.add(key1, key2, key3, key4)
    return keyboard


def keyboard_for_reference_and_commercial_offer():
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    key1 = types.InlineKeyboardButton(text='📃 Тех.задания', callback_data='technical_tasks')
    key2 = types.InlineKeyboardButton(text='📑 Коммерческие предложения', callback_data='commercial_offers')
    key3 = types.InlineKeyboardButton(text='📈 Отчеты', callback_data='upload_report')
    key4 = types.InlineKeyboardButton(text='Назад', callback_data='cancel_from_inline_menu')
    keyboard.add(key1, key2, key3, key4)
    return keyboard


def keyboard_for_technical_tasks(list_of_files: list, operator: bool = None):
    """ Ищем документы "Технического задания" в папке documents и отображаем даты """
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    for file in list_of_files:
        keyboard.add(types.InlineKeyboardButton(text=f'{file}', callback_data=f'send_file_{file}'))
    if operator:
        return keyboard
    cancel = types.InlineKeyboardButton(text='Назад', callback_data='technical_tasks_and_commercial_offer')
    main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    keyboard.row(cancel, main_menu)
    return keyboard


def keyboard_for_commercial_offer(list_of_files: list):
    """ Ищем документы "Коммерческие предложения" в папке documents и отображаем даты """
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    for file in list_of_files:
        keyboard.add(types.InlineKeyboardButton(text=f'{file}', callback_data=f'send_file_{file}'))
    cancel = types.InlineKeyboardButton(text='Назад', callback_data='technical_tasks_and_commercial_offer')
    main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    keyboard.row(cancel, main_menu)
    return keyboard


def keyboard_for_briefings():
    keyboard = types.InlineKeyboardMarkup()
    list_of_directions = get_directories()
    logger.info(f'Клавиатура выбора директорий - {list_of_directions}')
    for dir in list_of_directions:
        keyboard.add(types.InlineKeyboardButton(text=dir, callback_data=dir))
    cancel = types.InlineKeyboardButton(text='Назад', callback_data='cancel_from_inline_menu')
    keyboard.add(cancel)
    return keyboard


def keyboard_for_direction(direction):
    keyboard = types.InlineKeyboardMarkup()
    list_of_sub_directions = get_sub_directions(direction)
    if list_of_sub_directions:
        logger.info(f'Клавиатура выбора поддиректорий - {list_of_sub_directions}')
        for sub_direction in list_of_sub_directions:
            keyboard.add(
                types.InlineKeyboardButton(text=sub_direction, callback_data=f'{direction}|{sub_direction}'))
            logger.info(f'В keyboard_for_direction Созданы callbackи: {direction}|{sub_direction}')
    else:
        list_of_sections = get_sections_from_db(direction)
        logger.info(f'Клавиатура выбора секций вопросов - {list_of_sections}')
        for section in list_of_sections:
            keyboard.add(types.InlineKeyboardButton(text=section, callback_data=f'{direction}|{section}'))
            logger.info(f'В keyboard_for_direction Созданы callbackи: {direction}|{section}')
    cancel = types.InlineKeyboardButton(text='Назад', callback_data='cancel_to_directions')
    main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    keyboard.add(cancel, main_menu)
    return keyboard


def keyboard_for_sub_direction(path):
    logger.info(f'Клавиатура выбора подкатегорий')
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    list_of_subcategories = get_sections_from_db(path.split('|')[0], path.split('|')[1])
    for sub_dir in list_of_subcategories:
        keyboard.add(types.InlineKeyboardButton(text=sub_dir, callback_data=f'{path}|{sub_dir}'))
        logger.info(f'В keyboard_for_sub_direction: Созданы callbackи: {path}|{sub_dir}')
    cancel = types.InlineKeyboardButton(text='Назад', callback_data='cancel_to_directions')
    main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    keyboard.add(cancel, main_menu)
    return keyboard


def keyboard_for_questions(user_id: int, path: str):
    logger.info(f'Клавиатура вопросов: {path}')
    add_keyboard_for_questions_in_redis(user_id, path)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    list_of_questions = None
    buttons = []
    list_of_questions_id_from_user_answers = get_questions_id_from_user_answers(user_id)
    if len(path.split('|')) == 2:  # если мы перешли с dir|sec
        list_of_questions = get_questions_from_db(path.split('|')[0], path.split('|')[1])
    if len(path.split('|')) == 3:  # если мы перешли с dir|sub|sec
        list_of_questions = get_questions_from_db(path.split('|')[0], path.split('|')[2], path.split('|')[1])
    for i in list_of_questions:
        if i[0] in list_of_questions_id_from_user_answers:
            buttons.append(types.InlineKeyboardButton(text=f'✅ {i[1]}', callback_data=f'question_{i[0]}'))
        else:
            buttons.append(types.InlineKeyboardButton(text=f'❓ Вопрос {i[1]}', callback_data=f'question_{i[0]}'))
    set_max_question_id_in_redis(user_id, list_of_questions[-1][0])
    button_rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in button_rows:
        keyboard.row(*row)
    technical_exercise = types.InlineKeyboardButton(text='Сформировать ТЗ', callback_data=f'tex_{path}')
    cancel = types.InlineKeyboardButton(text='Назад', callback_data='cancel_to_directions')
    main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    keyboard.add(technical_exercise, cancel, main_menu)
    return keyboard


def keyboard_for_answer(answers):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for answer in answers:
        keyboard.add(types.KeyboardButton(text=answer))
    keyboard.add(types.KeyboardButton(text="✅ Отправить ответ"))
    keyboard.add(types.KeyboardButton(text="Следующий вопрос"))
    keyboard.add(types.KeyboardButton(text="К вопросам"))
    return keyboard


def keyboard_for_change_answer():
    logger.info(f'Клавиатура для изменения')
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    change = types.InlineKeyboardButton(text='Изменить ответ', callback_data='change_answer')
    cancel = types.InlineKeyboardButton(text='К вопросам', callback_data='back_to_questions')
    menu = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    keyboard.add(change, cancel, menu)
    return keyboard


def keyboard_for_enter_dialogue():
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


def keyboard_for_sex():
    """ Keyboard for choice the sex """
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    key1 = types.KeyboardButton(text='Мужской')
    key2 = types.KeyboardButton(text='Женский')
    send = types.KeyboardButton(text="✅ Отправить ответ")
    next = types.KeyboardButton(text="Следующий вопрос")
    cancel_button = types.KeyboardButton(text="Отменить")
    keyboard.add(key1, key2, send, next, cancel_button)
    return keyboard


def keyboard_for_age():
    """ Keyboard for choice the sex """
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    key1 = types.KeyboardButton(text='От 18 до 25')
    key2 = types.KeyboardButton(text='От 25 до 35')
    key3 = types.KeyboardButton(text='От 35 до 50')
    send = types.KeyboardButton(text="✅ Отправить ответ")
    next = types.KeyboardButton(text="Следующий вопрос")
    cancel_button = types.KeyboardButton(text="Отменить")
    keyboard.add(key1, key2, key3)
    keyboard.add(send, next, cancel_button)
    return keyboard


def keyboard_for_other_answers():
    """ Keyboard for choice the sex """
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    send = types.KeyboardButton(text="✅ Отправить ответ")
    next = types.KeyboardButton(text="Следующий вопрос")
    cancel_button = types.KeyboardButton(text="Отменить")
    keyboard.add(send, next, cancel_button)
    return keyboard


def keyboard_for_clients_in_brief():
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    key1 = types.InlineKeyboardButton(text='Да', callback_data='client_grade_yes')
    key2 = types.InlineKeyboardButton(text='Пока нет', callback_data='client_grade_no')
    menu = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    keyboard.add(key1, key2, menu)
    return keyboard


def keyboard_for_menu_in_dialogue():
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    tech_tasks = types.InlineKeyboardButton(text='Технические задания и брифы', callback_data='technical_tasks_for_operator')
    commercial_offers = types.InlineKeyboardButton(text='Коммерческие предложения', callback_data='commercial_offers_for_operator')
    reports = types.InlineKeyboardButton(text='Отчеты', callback_data='reports')
    documents = types.InlineKeyboardButton(text='Документы', callback_data='documents')
    cancel = types.InlineKeyboardButton(text='❌Выйти из диалога', callback_data='cancel_from_dialog')
    keyboard.add(tech_tasks, commercial_offers, reports, documents, cancel)
    return keyboard


# REMOVE KEYBOARD
def remove_keyboard(message, bot, text: str) -> None:
    bot.send_message(message.chat.id, f'{text}',
                     reply_markup=types.ReplyKeyboardRemove())
