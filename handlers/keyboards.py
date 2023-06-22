import logging

from telebot import types

from services.db_data import get_directories, \
    get_sections_from_db, get_questions_from_db, get_questions_id_from_user_answers, \
    get_users_data
from services.redis_db import redis_cache
from services.string_parser import CallDataParser

logger = logging.getLogger(__name__)


class GeneralKeyboards:
    data_enter_menu = 'enter_menu'
    data_briefing = "briefing"
    data_directory = get_directories()
    data_files = 'files'
    data_chat = 'chat'
    data_blog = 'blog'
    data_get_file = 'get|file|'
    data_get_documents = 'get_documents|'
    data_question = 'question|'
    data_cancel_to_directions = 'cancel_to_directions'
    data_back_to_questions = 'back_to_questions'
    data_games = 'games'
    data_instant_message = 'instant_message'
    data_karatekido2 = 'karatekido2'
    data_qubo = 'qubo'
    data_basketboyrush = 'basketboyrush'
    data_spikyfish3 = 'spikyfish3'
    data_basketboy = 'basketboy'
    data_gravityninjaemeraldcity = 'gravityninjaemeraldcity'
    data_keepitup = 'keepitup'


    @staticmethod
    def type_of_user():
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        keyboard.add(types.KeyboardButton(text="Клиент"))
        keyboard.add(types.KeyboardButton(text="Партнер"))
        return keyboard

    @staticmethod
    def enter_menu(doc=False):
        """Keyboard for main menu"""
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        key1 = types.InlineKeyboardButton(text='📋 Сформировать Тех. Задание', callback_data=GeneralKeyboards.data_briefing)
        key2 = types.InlineKeyboardButton(text='💬 Поставить задачу', callback_data=GeneralKeyboards.data_instant_message)
        key3 = types.InlineKeyboardButton(text='📝 Файлы',
                                          callback_data=GeneralKeyboards.data_files)
        key4 = types.InlineKeyboardButton(text='🎲 Игры', callback_data=GeneralKeyboards.data_games)
        key5 = types.InlineKeyboardButton(text='👨‍💻 Написать оператору', callback_data=GeneralKeyboards.data_chat)
        # key = types.InlineKeyboardButton(text='🤳 Блог', callback_data=GeneralKeyboards.data_blog)
        keyboard.add(key1)
        if doc is True:
            keyboard.add(key3)
        keyboard.row(key2, key4)
        keyboard.add(key5)
        return keyboard

    @staticmethod
    def directions() -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup()
        list_of_directions = get_directories()
        for dir_ in list_of_directions:
            keyboard.add(types.InlineKeyboardButton(text=dir_, callback_data=dir_))
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=GeneralKeyboards.data_enter_menu)
        keyboard.add(cancel)
        return keyboard

    @staticmethod
    def sub_directions(direction, list_of_sub_directions) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup()
        for sub_direction in list_of_sub_directions:
            keyboard.add(
                types.InlineKeyboardButton(text=sub_direction, callback_data=f'{direction}|{sub_direction}'))
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=GeneralKeyboards.data_cancel_to_directions)
        main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data=GeneralKeyboards.data_enter_menu)
        keyboard.add(cancel, main_menu)
        return keyboard

    @staticmethod
    def sections(direction, list_of_sections) -> types.InlineKeyboardMarkup:
        logger.info(f'Клавиатура: sections')
        keyboard = types.InlineKeyboardMarkup()
        for section in list_of_sections:
            keyboard.add(types.InlineKeyboardButton(text=section, callback_data=f'{direction}|{section}'))
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=GeneralKeyboards.data_cancel_to_directions)
        main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data=GeneralKeyboards.data_enter_menu)
        keyboard.add(cancel, main_menu)
        return keyboard

    @staticmethod
    def sections_from_subcategory(path: str) -> types.InlineKeyboardMarkup:
        logger.info(f'Клавиатура: sections_from_subcategory')
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        dir_, sub_dir = CallDataParser.get_dir_and_sub_dir(path)
        list_of_subcategories = get_sections_from_db(dir_, sub_dir)
        for section in list_of_subcategories:
            keyboard.add(types.InlineKeyboardButton(text=section, callback_data=f'{dir_}|{sub_dir}|{section}'))
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=GeneralKeyboards.data_cancel_to_directions)
        main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data=GeneralKeyboards.data_enter_menu)
        keyboard.add(cancel, main_menu)
        return keyboard

    @staticmethod
    def games():
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        game1 = types.InlineKeyboardButton(text='Karate Kido 2', callback_data=GeneralKeyboards.data_karatekido2)
        game2 = types.InlineKeyboardButton(text='Qubo', callback_data=GeneralKeyboards.data_qubo)
        game3 = types.InlineKeyboardButton(text='Basket Boy Rush', callback_data=GeneralKeyboards.data_basketboyrush)
        game4 = types.InlineKeyboardButton(text='Spiky Fish 3', callback_data=GeneralKeyboards.data_spikyfish3)
        game5 = types.InlineKeyboardButton(text='Basket Boy', callback_data=GeneralKeyboards.data_basketboy)
        game6 = types.InlineKeyboardButton(text='Gravity Ninja: Emerald City',
                                           callback_data=GeneralKeyboards.data_gravityninjaemeraldcity)
        game7 = types.InlineKeyboardButton(text='Keep it UP', callback_data=GeneralKeyboards.data_keepitup)
        main_menu = types.InlineKeyboardButton(text='Назад', callback_data=GeneralKeyboards.data_enter_menu)
        keyboard.row(game1, game2, game3)
        keyboard.row(game4, game5, game6)
        keyboard.row(game7, main_menu)
        return keyboard


class ClientKeyboards:
    data_change_answer = 'change_answer'
    data_technical_tasks = 'technical_tasks'
    data_commercial_offers = 'commercial_offers'
    data_reports = 'reports'
    data_documents = 'documents'
    data_evaluate = 'client_grade_yes'
    data_do_not_evaluate = 'client_grade_no'
    data_gen_tech_exercise = 'tex|'


    @staticmethod
    def types_of_files():
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        key1 = types.InlineKeyboardButton(text='📃 Тех.задания', callback_data=ClientKeyboards.data_technical_tasks)
        key2 = types.InlineKeyboardButton(text='📑 Коммерческие предложения',
                                          callback_data=ClientKeyboards.data_commercial_offers)
        key3 = types.InlineKeyboardButton(text='📈 Отчеты', callback_data=ClientKeyboards.data_reports)
        key4 = types.InlineKeyboardButton(text='📇 Документы', callback_data=ClientKeyboards.data_documents)
        key5 = types.InlineKeyboardButton(text='Назад', callback_data=GeneralKeyboards.data_enter_menu)
        keyboard.add(key1, key2, key3, key4, key5)
        return keyboard

    @staticmethod
    def files(dict_path_to_files):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=GeneralKeyboards.data_files)
        main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data=GeneralKeyboards.data_enter_menu)
        if dict_path_to_files is None:
            keyboard.row(cancel, main_menu)
            return keyboard
        else:
            for key, value in dict_path_to_files.items():
                filename = CallDataParser.get_file_name(value)
                keyboard.add(
                    types.InlineKeyboardButton(text=f'{filename}', callback_data=f'{GeneralKeyboards.data_get_file}{key}'))
            keyboard.row(cancel, main_menu)
            return keyboard

    @staticmethod
    def questions(user_id: int, path: str):
        redis_cache.add_keyboard_for_questions(user_id, path)
        dir_, sub_dir, section = CallDataParser.get_directory_sub_direction_section(path)
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = []
        list_of_questions_id_from_user_answers = get_questions_id_from_user_answers(user_id)
        dict_of_questions = get_questions_from_db(dir_, section, sub_dir)

        for question_id, number_of_question in dict_of_questions.items():
            if question_id in list_of_questions_id_from_user_answers:
                buttons.append(
                    types.InlineKeyboardButton(text=f'✅ {number_of_question}',
                                               callback_data=f'{GeneralKeyboards.data_question}{question_id}'))
            else:
                buttons.append(types.InlineKeyboardButton(text=f'❓ Вопрос {number_of_question}',
                                                          callback_data=f'{GeneralKeyboards.data_question}{question_id}'))
        max_question_id = list(dict_of_questions.keys())[-1]
        redis_cache.set_max_question_id(user_id, max_question_id)
        button_rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
        for row in button_rows:
            keyboard.row(*row)
        technical_exercise = types.InlineKeyboardButton(text='Сформировать ТЗ',
                                                        callback_data=f'{ClientKeyboards.data_gen_tech_exercise}{path}')
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=GeneralKeyboards.data_cancel_to_directions)
        main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data=GeneralKeyboards.data_enter_menu)
        keyboard.add(technical_exercise, cancel, main_menu)
        return keyboard

    @staticmethod
    def answer(answers):
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for answer in answers:
            keyboard.add(types.KeyboardButton(text=answer))
        keyboard.add(types.KeyboardButton(text="✅ Отправить ответ"))
        keyboard.add(types.KeyboardButton(text="Следующий вопрос"))
        keyboard.add(types.KeyboardButton(text="К вопросам"))
        return keyboard

    @staticmethod
    def change_answer():
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        change = types.InlineKeyboardButton(text='Изменить ответ', callback_data=ClientKeyboards.data_change_answer)
        cancel = types.InlineKeyboardButton(text='К вопросам', callback_data=GeneralKeyboards.data_back_to_questions)
        menu = types.InlineKeyboardButton(text='Главное меню', callback_data=GeneralKeyboards.data_enter_menu)
        keyboard.add(change, cancel, menu)
        return keyboard

    @staticmethod
    def send_phone():
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
        send_phone_button = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
        cancel_button = types.KeyboardButton(text="Отменить")
        keyboard.add(send_phone_button, cancel_button)
        return keyboard

    @staticmethod
    def sex():
        """ Keyboard for choice the sex """
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        key1 = types.KeyboardButton(text='Мужской')
        key2 = types.KeyboardButton(text='Женский')
        send = types.KeyboardButton(text="✅ Отправить ответ")
        next_ = types.KeyboardButton(text="Следующий вопрос")
        cancel_button = types.KeyboardButton(text="Отменить")
        keyboard.add(key1, key2, send, next_, cancel_button)
        return keyboard

    @staticmethod
    def age():
        """ Keyboard for choice the sex """
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        key1 = types.KeyboardButton(text='От 18 до 25')
        key2 = types.KeyboardButton(text='От 25 до 35')
        key3 = types.KeyboardButton(text='От 35 до 50')
        send = types.KeyboardButton(text="✅ Отправить ответ")
        next_ = types.KeyboardButton(text="Следующий вопрос")
        cancel_button = types.KeyboardButton(text="Отменить")
        keyboard.add(key1, key2, key3)
        keyboard.add(send, next_, cancel_button)
        return keyboard

    @staticmethod
    def other_answers():
        """ Keyboard for choice the sex """
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        send = types.KeyboardButton(text="✅ Отправить ответ")
        next_ = types.KeyboardButton(text="Следующий вопрос")
        cancel_button = types.KeyboardButton(text="Отменить")
        keyboard.add(send, next_, cancel_button)
        return keyboard

    @staticmethod
    def evaluation():
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        key1 = types.InlineKeyboardButton(text='Да', callback_data=ClientKeyboards.data_evaluate)
        key2 = types.InlineKeyboardButton(text='Пока нет', callback_data=ClientKeyboards.data_do_not_evaluate)
        menu = types.InlineKeyboardButton(text='Главное меню', callback_data=GeneralKeyboards.data_enter_menu)
        keyboard.add(key1, key2, menu)
        return keyboard


class OperatorKeyboards:

    data_enter_dialog = "enter_into_a_dialog|"
    data_menu_in_dialogue = 'operator_menu_in_dialogue'
    data_queue = 'queue|'
    data_requests = 'requests'
    data_clients = 'clients'
    data_tasks = 'tasks'
    data_settings = 'settings'
    data_change_question = 'change_question'
    data_add_question = 'add_question'
    data_client_info = "client|info|"
    data_tech_tasks_in_dialogue = 'technical_tasks_for_operator_in_dialogue'
    data_com_offers_in_dialogue = 'commercial_offers_for_operator_in_dialogue'
    data_reports_in_dialogue = 'reports_for_operator_in_dialogue'
    data_other_documents_in_dialogue = 'other_documents_for_operator_in_dialogue'
    data_upload_file = 'upload_file'
    data_upload_file_in_dialogue = 'upload_file_in_dialogue'
    data_show_tech_tasks = 'TT_for_operator|'
    data_show_com_offers = 'CO_operator|'
    data_show_reports = 'R_operator|'
    data_show_other_documents = 'OD_operator|'
    data_dialog_history = 'dialogue_history|'
    data_end_dialogue = 'end_the_dialogue'

    @staticmethod
    def enter_menu():
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        key1 = types.InlineKeyboardButton(text='Запросы', callback_data=OperatorKeyboards.data_requests)
        key2 = types.InlineKeyboardButton(text='Клиенты', callback_data=OperatorKeyboards.data_clients)
        key3 = types.InlineKeyboardButton(text='Задачи', callback_data=OperatorKeyboards.data_tasks)
        key4 = types.InlineKeyboardButton(text='Настройки', callback_data=OperatorKeyboards.data_settings)
        keyboard.add(key1, key2, key3, key4)
        return keyboard

    @staticmethod
    def clients(clients, callback_data_prefix):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=GeneralKeyboards.data_enter_menu)
        if not clients:
            keyboard.add(cancel)
            return keyboard
        users_data = get_users_data(clients)

        for client in users_data:
            keyboard.add(types.InlineKeyboardButton(text=f'❗️{client["name"]}|{client["company"]}',
                                                    callback_data=f'{callback_data_prefix}|{client["id"]}'))
        keyboard.add(cancel)
        return keyboard

    @staticmethod
    def settings():
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        key1 = types.InlineKeyboardButton(text='Изменить вопрос', callback_data=OperatorKeyboards.data_change_question)
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=GeneralKeyboards.data_enter_menu)
        keyboard.add(key1, cancel)
        return keyboard

    @staticmethod
    def customer_information(client_id: int):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        dialogue_history = types.InlineKeyboardButton(text='История переписки',
                                                      callback_data=f'{OperatorKeyboards.data_dialog_history}{client_id}')
        show_user_documents = types.InlineKeyboardButton(text='Документы пользователя',
                                                         callback_data=f'{GeneralKeyboards.data_get_documents}{client_id}')
        insert_into_dialogue = types.InlineKeyboardButton(text='✅Вступить в диалог',
                                                          callback_data=f'{OperatorKeyboards.data_enter_dialog}{client_id}')
        cancel = types.InlineKeyboardButton(text='Главное меню', callback_data=GeneralKeyboards.data_enter_menu)

        keyboard.add(dialogue_history, show_user_documents, insert_into_dialogue, cancel)
        return keyboard

    @staticmethod
    def menu_in_dialogue():
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        tech_tasks = types.InlineKeyboardButton(text='Технические задания и брифы',
                                                callback_data=OperatorKeyboards.data_tech_tasks_in_dialogue)
        commercial_offers = types.InlineKeyboardButton(text='Коммерческие предложения',
                                                       callback_data=OperatorKeyboards.data_com_offers_in_dialogue)
        reports = types.InlineKeyboardButton(text='Отчеты', callback_data=OperatorKeyboards.data_reports_in_dialogue)
        documents = types.InlineKeyboardButton(text='Документы',
                                               callback_data=OperatorKeyboards.data_other_documents_in_dialogue)
        cancel = types.InlineKeyboardButton(text='❌Выйти из диалога', callback_data=OperatorKeyboards.data_end_dialogue)
        keyboard.add(tech_tasks, commercial_offers, reports, documents, cancel)
        return keyboard

    @staticmethod
    def client_files(dict_of_path_files, in_dialogue=None):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        callback_1 = OperatorKeyboards.data_upload_file
        callback_2 = GeneralKeyboards.data_enter_menu
        if in_dialogue:
            callback_1 = OperatorKeyboards.data_upload_file_in_dialogue
            callback_2 = OperatorKeyboards.data_menu_in_dialogue
        upload_file = types.InlineKeyboardButton(text='Загрузить файл', callback_data=callback_1)
        cancel = types.InlineKeyboardButton(text='Главное меню', callback_data=callback_2)
        if dict_of_path_files is None:
            keyboard.row(cancel, upload_file)
            return keyboard
        else:
            for key, value in dict_of_path_files.items():
                filename = value.split('/')[-1]
                keyboard.add(
                    types.InlineKeyboardButton(text=f'{filename}', callback_data=f'{GeneralKeyboards.data_get_file}{key}'))
            keyboard.row(cancel, upload_file)
            return keyboard

    @staticmethod
    def types_documents(client_id: int):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        tech_tasks = types.InlineKeyboardButton(text='Технические задания и брифы',
                                                callback_data=f'{OperatorKeyboards.data_show_tech_tasks}{client_id}')
        commercial_offers = types.InlineKeyboardButton(text='Коммерческие предложения',
                                                       callback_data=f'{OperatorKeyboards.data_show_com_offers}{client_id}')
        reports = types.InlineKeyboardButton(text='Отчеты',
                                             callback_data=f'{OperatorKeyboards.data_show_reports}{client_id}')
        documents = types.InlineKeyboardButton(text='Документы',
                                               callback_data=f'{OperatorKeyboards.data_show_other_documents}{client_id}')
        cancel = types.InlineKeyboardButton(text='Главное меню', callback_data=GeneralKeyboards.data_enter_menu)
        keyboard.add(tech_tasks, commercial_offers, reports, documents, cancel)
        return keyboard

    @staticmethod
    def questions(operator_id, path: str):
        redis_cache.add_keyboard_for_questions(operator_id, path)

        dir_, sub_dir, section = CallDataParser.get_directory_sub_direction_section(path)
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = []
        dict_of_questions = get_questions_from_db(dir_, section, sub_dir)
        for question_id, number_of_question in dict_of_questions.items():
            buttons.append(types.InlineKeyboardButton(text=f'❓ Вопрос {number_of_question}',
                                                      callback_data=f'{GeneralKeyboards.data_question}{question_id}'))

        button_rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
        for row in button_rows:
            keyboard.row(*row)
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=GeneralKeyboards.data_cancel_to_directions)
        add_question = types.InlineKeyboardButton(text='Добавить вопрос', callback_data=OperatorKeyboards.data_add_question)
        main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data=GeneralKeyboards.data_enter_menu)
        keyboard.add(cancel, add_question, main_menu)
        return keyboard

    @staticmethod
    def change_question():
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=GeneralKeyboards.data_back_to_questions)
        main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data=GeneralKeyboards.data_enter_menu)
        keyboard.add(cancel, main_menu)
        return keyboard


class PartnerKeyboards(GeneralKeyboards):
    @staticmethod
    def enter_menu(doc: bool = False):
        """Keyboard for main menu for partner"""
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        key1 = types.InlineKeyboardButton(text='📋 Сформировать Тех. Задание', callback_data=GeneralKeyboards.data_briefing)
        key2 = types.InlineKeyboardButton(text='💬 Поставить задачу', callback_data=GeneralKeyboards.data_instant_message)
        key3 = types.InlineKeyboardButton(text='📝 Файлы',
                                          callback_data=GeneralKeyboards.data_files)
        key4 = types.InlineKeyboardButton(text='🎲 Игры', callback_data=GeneralKeyboards.data_games)
        key5 = types.InlineKeyboardButton(text='👨‍💻 Написать оператору', callback_data=GeneralKeyboards.data_chat)
        # key = types.InlineKeyboardButton(text='🤳 Блог', callback_data=Callbacks.blog)
        keyboard.add(key1)
        if doc is True:
            keyboard.add(key3)
        keyboard.row(key2, key4)
        keyboard.add(key5)
        return keyboard


def remove_keyboard(message, bot, text: str) -> None:
    bot.send_message(message.chat.id, f'{text}',
                     reply_markup=types.ReplyKeyboardRemove())
