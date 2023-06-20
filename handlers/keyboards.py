import logging

from telebot import types

from services.callbacks import ClientCallbacks, GamesCallbacks, OperatorCallbacks, BaseCallbacks
from services.db_data import get_directories, \
    get_sections_from_db, get_questions_from_db, get_questions_id_from_user_answers, \
    get_users_data_from_db
from services.redis_db import redis_cache
from services.string_parser import CallDataParser

logger = logging.getLogger(__name__)


class GeneralKeyboards:
    @staticmethod
    def directions() -> types.InlineKeyboardMarkup:
        logger.info(f'Клавиатура: directions')
        keyboard = types.InlineKeyboardMarkup()
        list_of_directions = get_directories()
        for dir_ in list_of_directions:
            keyboard.add(types.InlineKeyboardButton(text=dir_, callback_data=dir_))
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=BaseCallbacks.enter_menu)
        keyboard.add(cancel)
        return keyboard

    @staticmethod
    def sub_directions(direction, list_of_sub_directions) -> types.InlineKeyboardMarkup:
        logger.info(f'Клавиатура: sub_directions')
        keyboard = types.InlineKeyboardMarkup()
        for sub_direction in list_of_sub_directions:
            keyboard.add(
                types.InlineKeyboardButton(text=sub_direction, callback_data=f'{direction}|{sub_direction}'))
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=BaseCallbacks.cancel_to_directions)
        main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data=BaseCallbacks.enter_menu)
        keyboard.add(cancel, main_menu)
        return keyboard

    @staticmethod
    def sections(direction, list_of_sections) -> types.InlineKeyboardMarkup:
        logger.info(f'Клавиатура: sections')
        keyboard = types.InlineKeyboardMarkup()
        for section in list_of_sections:
            keyboard.add(types.InlineKeyboardButton(text=section, callback_data=f'{direction}|{section}'))
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=BaseCallbacks.cancel_to_directions)
        main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data=BaseCallbacks.enter_menu)
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
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=BaseCallbacks.cancel_to_directions)
        main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data=BaseCallbacks.enter_menu)
        keyboard.add(cancel, main_menu)
        return keyboard


class ClientKeyboards(GeneralKeyboards):
    @staticmethod
    def enter_menu(doc=False):
        """Keyboard for main menu"""
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        key1 = types.InlineKeyboardButton(text='📋 Сформировать Тех. Задание', callback_data=BaseCallbacks.briefing)
        key2 = types.InlineKeyboardButton(text='💬 Поставить задачу', callback_data=ClientCallbacks.instant_message)
        key3 = types.InlineKeyboardButton(text='📝 Файлы',
                                          callback_data=ClientCallbacks.files)
        key4 = types.InlineKeyboardButton(text='🎲 Игры', callback_data=ClientCallbacks.games)
        key5 = types.InlineKeyboardButton(text='👨‍💻 Написать оператору', callback_data=ClientCallbacks.chat)
        # key = types.InlineKeyboardButton(text='🤳 Блог', callback_data=Callbacks.blog)
        keyboard.add(key1)
        if doc is True:
            keyboard.add(key3)
        keyboard.row(key2, key4)
        keyboard.add(key5)
        return keyboard

    @staticmethod
    def types_of_files():
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        key1 = types.InlineKeyboardButton(text='📃 Тех.задания', callback_data=ClientCallbacks.technical_tasks)
        key2 = types.InlineKeyboardButton(text='📑 Коммерческие предложения',
                                          callback_data=ClientCallbacks.commercial_offers)
        key3 = types.InlineKeyboardButton(text='📈 Отчеты', callback_data=ClientCallbacks.reports)
        key4 = types.InlineKeyboardButton(text='📇 Документы', callback_data=ClientCallbacks.documents)
        key5 = types.InlineKeyboardButton(text='Назад', callback_data=BaseCallbacks.enter_menu)
        keyboard.add(key1, key2, key3, key4, key5)
        return keyboard

    @staticmethod
    def files(dict_path_to_files):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=ClientCallbacks.files)
        main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data=BaseCallbacks.enter_menu)
        if dict_path_to_files is None:
            keyboard.row(cancel, main_menu)
            return keyboard
        else:
            for key, value in dict_path_to_files.items():
                filename = CallDataParser.get_file_name(value)
                keyboard.add(
                    types.InlineKeyboardButton(text=f'{filename}', callback_data=f'{BaseCallbacks.get_file}{key}'))
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
                                               callback_data=f'{BaseCallbacks.question}{question_id}'))
            else:
                buttons.append(types.InlineKeyboardButton(text=f'❓ Вопрос {number_of_question}',
                                                          callback_data=f'{BaseCallbacks.question}{question_id}'))
        max_question_id = list(dict_of_questions.keys())[-1]
        redis_cache.set_max_question_id(user_id, max_question_id)
        button_rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
        for row in button_rows:
            keyboard.row(*row)
        technical_exercise = types.InlineKeyboardButton(text='Сформировать ТЗ',  callback_data=f'{ClientCallbacks.gen_tech_exercise}{path}')
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=BaseCallbacks.cancel_to_directions)
        main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data=BaseCallbacks.enter_menu)
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
        change = types.InlineKeyboardButton(text='Изменить ответ', callback_data=ClientCallbacks.change_answer)
        cancel = types.InlineKeyboardButton(text='К вопросам', callback_data=BaseCallbacks.back_to_questions)
        menu = types.InlineKeyboardButton(text='Главное меню', callback_data=BaseCallbacks.enter_menu)
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
        key1 = types.InlineKeyboardButton(text='Да', callback_data=ClientCallbacks.evaluate)
        key2 = types.InlineKeyboardButton(text='Пока нет', callback_data=ClientCallbacks.do_not_evaluate)
        menu = types.InlineKeyboardButton(text='Главное меню', callback_data=BaseCallbacks.enter_menu)
        keyboard.add(key1, key2, menu)
        return keyboard

    @staticmethod
    def games():
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        game1 = types.InlineKeyboardButton(text='Karate Kido 2', callback_data=GamesCallbacks.karatekido2)
        game2 = types.InlineKeyboardButton(text='Qubo', callback_data=GamesCallbacks.qubo)
        game3 = types.InlineKeyboardButton(text='Basket Boy Rush', callback_data=GamesCallbacks.basketboyrush)
        game4 = types.InlineKeyboardButton(text='Spiky Fish 3', callback_data=GamesCallbacks.spikyfish3)
        game5 = types.InlineKeyboardButton(text='Basket Boy', callback_data=GamesCallbacks.basketboy)
        game6 = types.InlineKeyboardButton(text='Gravity Ninja: Emerald City',
                                           callback_data=GamesCallbacks.gravityninjaemeraldcity)
        game7 = types.InlineKeyboardButton(text='Keep it UP', callback_data=GamesCallbacks.keepitup)
        main_menu = types.InlineKeyboardButton(text='Назад', callback_data=BaseCallbacks.enter_menu)
        keyboard.row(game1, game2, game3)
        keyboard.row(game4, game5, game6)
        keyboard.row(game7, main_menu)
        return keyboard


class OperatorKeyboards(GeneralKeyboards):
    @staticmethod
    def enter_menu():
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        key1 = types.InlineKeyboardButton(text='Запросы', callback_data=OperatorCallbacks.requests)
        key2 = types.InlineKeyboardButton(text='Клиенты', callback_data=OperatorCallbacks.clients)
        key3 = types.InlineKeyboardButton(text='Задачи', callback_data=OperatorCallbacks.tasks)
        key4 = types.InlineKeyboardButton(text='Настройки', callback_data=OperatorCallbacks.settings)
        keyboard.add(key1, key2, key3, key4)
        return keyboard

    @staticmethod
    def clients(clients, callback_data_prefix):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=OperatorCallbacks.enter_menu)
        if not clients:
            keyboard.add(cancel)
            return keyboard
        users_data = get_users_data_from_db(clients)
        for client in users_data:
            keyboard.add(types.InlineKeyboardButton(text=f'❗️{client["name"]}|{client["company"]}',
                                                    callback_data=f'{callback_data_prefix}|{client["id"]}'))
        keyboard.add(cancel)
        return keyboard

    @staticmethod
    def settings():
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        key1 = types.InlineKeyboardButton(text='Изменить вопрос', callback_data=OperatorCallbacks.change_question)
        key2 = types.InlineKeyboardButton(text='Добавить вопрос', callback_data=OperatorCallbacks.add_question)
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=OperatorCallbacks.enter_menu)
        keyboard.add(key1, key2, cancel)
        return keyboard

    @staticmethod
    def customer_information(client_id: int):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        dialogue_history = types.InlineKeyboardButton(text='История переписки',
                                                      callback_data=f'{OperatorCallbacks.dialog_history}{client_id}')
        show_user_documents = types.InlineKeyboardButton(text='Документы пользователя',
                                                         callback_data=f'{OperatorCallbacks.get_documents}{client_id}')
        insert_into_dialogue = types.InlineKeyboardButton(text='✅Вступить в диалог',
                                                          callback_data=f'{OperatorCallbacks.enter_dialog}{client_id}')
        cancel = types.InlineKeyboardButton(text='Главное меню', callback_data=OperatorCallbacks.enter_menu)

        keyboard.add(dialogue_history, show_user_documents, insert_into_dialogue, cancel)
        return keyboard

    @staticmethod
    def menu_in_dialogue():
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        tech_tasks = types.InlineKeyboardButton(text='Технические задания и брифы',
                                                callback_data=OperatorCallbacks.tech_tasks_in_dialogue)
        commercial_offers = types.InlineKeyboardButton(text='Коммерческие предложения',
                                                       callback_data=OperatorCallbacks.com_offers_in_dialogue)
        reports = types.InlineKeyboardButton(text='Отчеты', callback_data=OperatorCallbacks.reports_in_dialogue)
        documents = types.InlineKeyboardButton(text='Документы',
                                               callback_data=OperatorCallbacks.other_documents_in_dialogue)
        cancel = types.InlineKeyboardButton(text='❌Выйти из диалога', callback_data=OperatorCallbacks.end_dialogue)
        keyboard.add(tech_tasks, commercial_offers, reports, documents, cancel)
        return keyboard

    @staticmethod
    def client_files(dict_of_path_files, in_dialogue=None):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        callback_1 = OperatorCallbacks.upload_file
        callback_2 = OperatorCallbacks.enter_menu
        if in_dialogue:
            callback_1 = OperatorCallbacks.upload_file_in_dialogue
            callback_2 = OperatorCallbacks.menu_in_dialogue
        upload_file = types.InlineKeyboardButton(text='Загрузить файл', callback_data=callback_1)
        cancel = types.InlineKeyboardButton(text='Главное меню', callback_data=callback_2)
        if dict_of_path_files is None:
            keyboard.row(cancel, upload_file)
            return keyboard
        else:
            for key, value in dict_of_path_files.items():
                filename = value.split('/')[-1]
                keyboard.add(
                    types.InlineKeyboardButton(text=f'{filename}', callback_data=f'{OperatorCallbacks.get_file}{key}'))
            keyboard.row(cancel, upload_file)
            return keyboard

    @staticmethod
    def types_documents(client_id: int):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        tech_tasks = types.InlineKeyboardButton(text='Технические задания и брифы',
                                                callback_data=f'{OperatorCallbacks.show_tech_tasks}{client_id}')
        commercial_offers = types.InlineKeyboardButton(text='Коммерческие предложения',
                                                       callback_data=f'{OperatorCallbacks.show_com_offers}{client_id}')
        reports = types.InlineKeyboardButton(text='Отчеты',
                                             callback_data=f'{OperatorCallbacks.show_reports}{client_id}')
        documents = types.InlineKeyboardButton(text='Документы',
                                               callback_data=f'{OperatorCallbacks.show_other_documents}{client_id}')
        cancel = types.InlineKeyboardButton(text='Главное меню', callback_data=OperatorCallbacks.enter_menu)
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
                                                      callback_data=f'{BaseCallbacks.question}{question_id}'))

        button_rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
        for row in button_rows:
            keyboard.row(*row)
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=OperatorCallbacks.cancel_to_directions)
        main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data=OperatorCallbacks.enter_menu)
        keyboard.add(cancel, main_menu)
        return keyboard

    @staticmethod
    def change_question():
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        cancel = types.InlineKeyboardButton(text='Назад', callback_data=OperatorCallbacks.back_to_questions)
        main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data=OperatorCallbacks.enter_menu)
        keyboard.add(cancel, main_menu)
        return keyboard


class PartnerKeyboards(GeneralKeyboards):
    @staticmethod
    def start():
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        btn1 = types.InlineKeyboardButton(text='', callback_data='')
        btn2 = types.InlineKeyboardButton(text='', callback_data='')
        btn3 = types.InlineKeyboardButton(text='Документы', callback_data='')
        btn4 = types.InlineKeyboardButton(text='Связаться с оператором компании Mr.Эйч', callback_data='')
        keyboard.add(btn1, btn2, btn3, btn4)
        return keyboard


def remove_keyboard(message, bot, text: str) -> None:
    bot.send_message(message.chat.id, f'{text}',
                     reply_markup=types.ReplyKeyboardRemove())
