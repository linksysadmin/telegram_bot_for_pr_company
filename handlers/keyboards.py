import logging

from telebot import types

from services.db_data import get_directories, \
    get_sections_from_db, get_questions_from_db, get_questions_id_from_user_answers, get_sub_directions, \
    get_users_data_from_db
from services.redis_db import redis_cache
from services.string_parser import CallDataParser

logger = logging.getLogger(__name__)


def keyboard_enter_menu_for_clients(doc=False):
    """Keyboard for main menu"""
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    key1 = types.InlineKeyboardButton(text='📋 Сформировать Тех. Задание', callback_data='scenario')
    key2 = types.InlineKeyboardButton(text='💬 Поставить задачу', callback_data='instant_messaging_service')
    key3 = types.InlineKeyboardButton(text='📝 Файлы',
                                      callback_data='technical_tasks_and_commercial_offer')
    key4 = types.InlineKeyboardButton(text='🎲 Игры', callback_data='games')
    key5 = types.InlineKeyboardButton(text='👨‍💻 Написать оператору', callback_data='chat_with_operator')
    # key = types.InlineKeyboardButton(text='🤳 Блог', callback_data='blog')
    keyboard.add(key1)
    if doc is True:
        keyboard.add(key3)
    keyboard.row(key2, key4)
    keyboard.add(key5)
    return keyboard


def keyboard_for_reference_and_commercial_offer():
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    key1 = types.InlineKeyboardButton(text='📃 Тех.задания', callback_data='technical_tasks')
    key2 = types.InlineKeyboardButton(text='📑 Коммерческие предложения', callback_data='commercial_offers')
    key3 = types.InlineKeyboardButton(text='📈 Отчеты', callback_data='reports')
    key4 = types.InlineKeyboardButton(text='📇 Документы', callback_data='documents')
    key5 = types.InlineKeyboardButton(text='Назад', callback_data='cancel_from_inline_menu')
    keyboard.add(key1, key2, key3, key4, key5)
    return keyboard


def keyboard_for_files(dict_path_to_files):
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    cancel = types.InlineKeyboardButton(text='Назад', callback_data='technical_tasks_and_commercial_offer')
    main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    if dict_path_to_files is None:
        keyboard.row(cancel, main_menu)
        return keyboard
    else:
        for key, value in dict_path_to_files.items():
            filename = CallDataParser.get_file_name(value)
            keyboard.add(types.InlineKeyboardButton(text=f'{filename}', callback_data=f'get|file|{key}'))
        keyboard.row(cancel, main_menu)
        return keyboard


def keyboard_for_briefings():
    keyboard = types.InlineKeyboardMarkup()
    list_of_directions = get_directories()
    for dir_ in list_of_directions:
        keyboard.add(types.InlineKeyboardButton(text=dir_, callback_data=dir_))
    cancel = types.InlineKeyboardButton(text='Назад', callback_data='cancel_from_inline_menu')
    keyboard.add(cancel)
    return keyboard


def keyboard_for_direction(direction):
    keyboard = types.InlineKeyboardMarkup()
    list_of_sub_directions = get_sub_directions(direction)
    if list_of_sub_directions:
        for sub_direction in list_of_sub_directions:
            keyboard.add(
                types.InlineKeyboardButton(text=sub_direction, callback_data=f'{direction}|{sub_direction}'))
    else:
        list_of_sections = get_sections_from_db(direction)
        for section in list_of_sections:
            keyboard.add(types.InlineKeyboardButton(text=section, callback_data=f'{direction}|{section}'))
    cancel = types.InlineKeyboardButton(text='Назад', callback_data='cancel_to_directions')
    main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    keyboard.add(cancel, main_menu)
    return keyboard


def keyboard_for_sub_direction(path):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    dir_, sub_dir = CallDataParser.get_dir_and_sub_dir(path)
    list_of_subcategories = get_sections_from_db(dir_, sub_dir)
    for sub_dir in list_of_subcategories:
        keyboard.add(types.InlineKeyboardButton(text=sub_dir, callback_data=f'{path}|{sub_dir}'))
    cancel = types.InlineKeyboardButton(text='Назад', callback_data='cancel_to_directions')
    main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    keyboard.add(cancel, main_menu)
    return keyboard


def keyboard_for_questions(user_id: int, path: str):
    redis_cache.add_keyboard_for_questions(user_id, path)
    dir_, sub_dir, section = CallDataParser.get_directory_sub_direction_section(path)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = []
    list_of_questions_id_from_user_answers = get_questions_id_from_user_answers(user_id)
    dict_of_questions = get_questions_from_db(dir_, section, sub_dir)

    for question_id, number_of_question in dict_of_questions.items():
        if question_id in list_of_questions_id_from_user_answers:
            buttons.append(types.InlineKeyboardButton(text=f'✅ {number_of_question}', callback_data=f'question|{question_id}'))
        else:
            buttons.append(types.InlineKeyboardButton(text=f'❓ Вопрос {number_of_question}', callback_data=f'question|{question_id}'))
    max_question_id = list(dict_of_questions.keys())[-1]
    redis_cache.set_max_question_id(user_id, max_question_id)
    button_rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
    for row in button_rows:
        keyboard.row(*row)
    technical_exercise = types.InlineKeyboardButton(text='Сформировать ТЗ', callback_data=f'tex|{path}')
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
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    change = types.InlineKeyboardButton(text='Изменить ответ', callback_data='change_answer')
    cancel = types.InlineKeyboardButton(text='К вопросам', callback_data='back_to_questions')
    menu = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    keyboard.add(change, cancel, menu)
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


def keyboard_for_games():
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    game1 = types.InlineKeyboardButton(text='Karate Kido 2', callback_data='karatekido2')
    game2 = types.InlineKeyboardButton(text='Qubo', callback_data='qubo')
    game3 = types.InlineKeyboardButton(text='Basket Boy Rush', callback_data='basketboyrush')
    game4 = types.InlineKeyboardButton(text='Spiky Fish 3', callback_data='spikyfish3')
    game5 = types.InlineKeyboardButton(text='Basket Boy', callback_data='basketboy')
    game6 = types.InlineKeyboardButton(text='Gravity Ninja: Emerald City', callback_data='gravityninjaemeraldcity')
    game7 = types.InlineKeyboardButton(text='Keep it UP', callback_data='keepitup')
    main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_from_inline_menu')
    keyboard.row(game1, game2, game3)
    keyboard.row(game4, game5, game6)
    keyboard.row(game7, main_menu)
    return keyboard


# Keyboards for operator

def keyboard_enter_menu_for_operator():
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    key1 = types.InlineKeyboardButton(text='Запросы', callback_data='requests')
    key2 = types.InlineKeyboardButton(text='Клиенты', callback_data='clients')
    key3 = types.InlineKeyboardButton(text='Задачи', callback_data='tasks')
    key4 = types.InlineKeyboardButton(text='Настройки', callback_data='settings')
    keyboard.add(key1, key2, key3, key4)
    return keyboard


def keyboard_with_clients(clients, callback_data_prefix):
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    cancel = types.InlineKeyboardButton(text='Назад', callback_data='cancel_to_enter_menu_for_operator')
    if not clients:
        keyboard.add(cancel)
        return keyboard
    users_data = get_users_data_from_db(clients)
    for client in users_data:
        keyboard.add(types.InlineKeyboardButton(text=f'❗️{client["name"]}|{client["company"]}',
                                                callback_data=f'{callback_data_prefix}|{client["id"]}'))
    keyboard.add(cancel)
    return keyboard


def keyboard_for_view_customer_information(client_id: int):
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    dialogue_history = types.InlineKeyboardButton(text='История переписки',
                                                  callback_data=f'dialogue_history|{client_id}')
    show_user_documents = types.InlineKeyboardButton(text='Документы пользователя',
                                                     callback_data=f'get_documents|{client_id}')
    insert_into_dialogue = types.InlineKeyboardButton(text='✅Вступить в диалог',
                                                      callback_data=f'enter_into_a_dialog|{client_id}')
    cancel = types.InlineKeyboardButton(text='Назад', callback_data='cancel_to_enter_menu_for_operator')

    keyboard.add(dialogue_history, show_user_documents, insert_into_dialogue, cancel)
    return keyboard


def keyboard_for_menu_in_dialogue():
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    tech_tasks = types.InlineKeyboardButton(text='Технические задания и брифы',
                                            callback_data='technical_tasks_for_operator_in_dialogue')
    commercial_offers = types.InlineKeyboardButton(text='Коммерческие предложения',
                                                   callback_data='commercial_offers_for_operator_in_dialogue')
    reports = types.InlineKeyboardButton(text='Отчеты', callback_data='reports_for_operator_in_dialogue')
    documents = types.InlineKeyboardButton(text='Документы', callback_data='other_documents_for_operator_in_dialogue')
    cancel = types.InlineKeyboardButton(text='❌Выйти из диалога', callback_data='cancel_from_dialog')
    keyboard.add(tech_tasks, commercial_offers, reports, documents, cancel)
    return keyboard


def keyboard_with_client_files(dict_of_path_files, in_dialogue=None):
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    callback_data_for_upload_file = 'upload_file'
    callback_data_for_cancel = 'cancel_to_enter_menu_for_operator'
    if in_dialogue:
        callback_data_for_upload_file = 'upload_file_in_dialogue'
        callback_data_for_cancel = 'cancel_to_enter_menu_in_dialogue'
    upload_file = types.InlineKeyboardButton(text='Загрузить файл', callback_data=callback_data_for_upload_file)
    cancel = types.InlineKeyboardButton(text='Главное меню', callback_data=callback_data_for_cancel)
    if dict_of_path_files is None:
        keyboard.row(cancel, upload_file)
        return keyboard
    else:
        for key, value in dict_of_path_files.items():
            filename = value.split('/')[-1]
            keyboard.add(types.InlineKeyboardButton(text=f'{filename}', callback_data=f'get|file|{key}'))
        keyboard.row(cancel, upload_file)
        return keyboard


def keyboard_menu_directions_of_documents(client_id: int):
    keyboard = types.InlineKeyboardMarkup(row_width=True)
    tech_tasks = types.InlineKeyboardButton(text='Технические задания и брифы',
                                            callback_data=f'TT_for_operator|{client_id}')
    commercial_offers = types.InlineKeyboardButton(text='Коммерческие предложения',
                                                   callback_data=f'CO_operator|{client_id}')
    reports = types.InlineKeyboardButton(text='Отчеты', callback_data=f'R_operator|{client_id}')
    documents = types.InlineKeyboardButton(text='Документы', callback_data=f'OD_operator|{client_id}')
    cancel = types.InlineKeyboardButton(text='Главное меню', callback_data='cancel_to_enter_menu_for_operator')
    keyboard.add(tech_tasks, commercial_offers, reports, documents, cancel)
    return keyboard


def remove_keyboard(message, bot, text: str) -> None:
    bot.send_message(message.chat.id, f'{text}',
                     reply_markup=types.ReplyKeyboardRemove())
