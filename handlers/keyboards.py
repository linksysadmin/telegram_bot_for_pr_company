import logging
from typing import Tuple, Dict

from telebot import types

from services.db_data import db
from services.states import OperatorStates
from services.string_parser import Parser
from services.tg_games import games

logger = logging.getLogger(__name__)


class CallbackValue:
    def __set_name__(self, owner, name):
        self.name = '__' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        setattr(instance, self.name, value)


class CallbackButton:
    name = CallbackValue()
    text = CallbackValue()
    usertype = CallbackValue()
    parse = CallbackValue()

    def __init__(self, data, text, **kwargs):
        """
        :param data: строка с помощью которой вызывается функция.
        :param text: Текст кнопки
        :param keyboard: Клавиатура

        :param kwargs: parse=True, usertype = client or operator or partner and other attributes
        """
        self.data = data
        self.text = text
        self.flags = kwargs


class CallbackButtonsList:

    def __init__(self):
        self.__callbacks = []

    def add(self, *args: 'CallbackButton') -> None:
        for callback in args:
            self.__callbacks.append(callback)

    def get_buttons(self):
        return self.__callbacks

    def __len__(self):
        return len(self.__callbacks)


callbacks_button_list = CallbackButtonsList()


class Keyboard:
    @classmethod
    def reply_keyboard(cls, buttons_text: Tuple):
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        buttons = []
        for text in buttons_text:
            buttons.append(types.KeyboardButton(text=text))
        keyboard.add(*buttons)
        return keyboard

    @classmethod
    def inline_keyboard(cls, dict_text_callback: Dict, row=False):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        buttons = []
        for text, callback in dict_text_callback.items():
            buttons.append(types.InlineKeyboardButton(text=text, callback_data=callback))
        if row:
            button_rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
            for row in button_rows:
                keyboard.row(*row)
        else:
            keyboard.add(*buttons)
        return keyboard


class GeneralKeyboard(Keyboard):
    question_button = CallbackButton('question|', '❓ Вопрос', parse=True)
    cancel_to_directions_button = CallbackButton('cancel_to_directions', 'Назад')
    directory_button = CallbackButton(db.get_directories, 'Директория')
    section_button = CallbackButton(db.get_sections_from_db, 'Секция', section=True)
    sub_directory_button = CallbackButton(db.get_sub_directions, 'Секция', sub_directory=True)
    instant_message_button = CallbackButton('instant_message', '💬 Поставить задачу')
    game_button = CallbackButton('choose_game', '🎲 Игры')
    send_game_button = CallbackButton(games.get_list_short_names(), 'Играть')
    tex_button = CallbackButton('tex|', 'Сформировать ТЗ', parse=True)
    files_button = CallbackButton('files', '📝 Файлы')
    chat_button = CallbackButton('chat', '👨‍💻 Написать оператору')
    blog_button = CallbackButton('blog', 'GPT')
    briefing_button = CallbackButton('briefing', '📋 Сформировать Тех. Задание', operator=False)
    enter_menu_for_client_button = CallbackButton('enter_menu', 'Главное меню', client=True)

    def enter_menu(self, doc=False):
        """Keyboard for main menu"""
        # print(self.blog)
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        key1 = types.InlineKeyboardButton(text=self.briefing_button.text, callback_data=self.briefing_button.data)
        key2 = types.InlineKeyboardButton(text=self.instant_message_button.text,
                                          callback_data=self.instant_message_button.data)
        key3 = types.InlineKeyboardButton(text=self.files_button.text, callback_data=self.files_button.data)
        key4 = types.InlineKeyboardButton(text=self.game_button.text, callback_data=self.game_button.data)
        key5 = types.InlineKeyboardButton(text=self.chat_button.text, callback_data=self.chat_button.data)
        key6 = types.InlineKeyboardButton(text=self.blog_button.text, callback_data=self.blog_button.data)
        keyboard.add(key1)
        if doc is True:
            keyboard.add(key3)
        keyboard.row(key2, key4)
        keyboard.add(key5)
        keyboard.add(key6)
        return keyboard

    def directions(self) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup()
        list_of_directions = db.get_directories()
        for dir_ in list_of_directions:
            keyboard.add(types.InlineKeyboardButton(text=dir_, callback_data=dir_))
        cancel = types.InlineKeyboardButton(text=self.enter_menu_for_client_button.text,
                                            callback_data=self.enter_menu_for_client_button.data)
        keyboard.add(cancel)
        return keyboard

    def sub_directions(self, direction, list_of_sub_directions) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup()
        for sub_direction in list_of_sub_directions:
            keyboard.add(
                types.InlineKeyboardButton(text=sub_direction, callback_data=f'{direction}|{sub_direction}'))
        cancel = types.InlineKeyboardButton(text=self.cancel_to_directions_button.text,
                                            callback_data=self.cancel_to_directions_button.data)
        main_menu = types.InlineKeyboardButton(text=self.enter_menu_for_client_button.text,
                                               callback_data=self.enter_menu_for_client_button.data)
        keyboard.add(cancel, main_menu)
        return keyboard

    def sections(self, direction, list_of_sections) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup()
        for section in list_of_sections:
            keyboard.add(types.InlineKeyboardButton(text=section, callback_data=f'{direction}|{section}'))
        cancel = types.InlineKeyboardButton(text=self.cancel_to_directions_button.text,
                                            callback_data=self.cancel_to_directions_button.data)
        main_menu = types.InlineKeyboardButton(text=self.enter_menu_for_client_button.text,
                                               callback_data=self.enter_menu_for_client_button.data)
        keyboard.add(cancel, main_menu)
        return keyboard

    def sections_from_subcategory(self, path: str) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        dir_, sub_dir = Parser.get_dir_and_sub_dir(path)
        list_of_subcategories = db.get_sections_from_db(dir_, sub_dir)
        for section in list_of_subcategories:
            keyboard.add(types.InlineKeyboardButton(text=section, callback_data=f'{dir_}|{sub_dir}|{section}'))
        cancel = types.InlineKeyboardButton(text=self.cancel_to_directions_button.text,
                                            callback_data=self.cancel_to_directions_button.data)
        main_menu = types.InlineKeyboardButton(text=self.enter_menu_for_client_button.text,
                                               callback_data=self.enter_menu_for_client_button.data)
        keyboard.add(cancel, main_menu)
        return keyboard

    def questions(self, user_id: int, directory: str, sub_direction: str, section: str):
        dict_of_question_id_and_number = db.get_question_id_and_number(directory, section, sub_direction)
        list_of_id_questions_to_which_the_user_answered = db.get_questions_id_from_user_answers(user_id)
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = []
        for question_id, number_of_question in dict_of_question_id_and_number.items():
            if question_id in list_of_id_questions_to_which_the_user_answered:
                buttons.append(
                    types.InlineKeyboardButton(text=f'✅ {number_of_question}',
                                               callback_data=f'{self.question_button.data}{question_id}|{number_of_question}'))
            else:
                buttons.append(types.InlineKeyboardButton(text=f'❓ Вопрос {number_of_question}',
                                                          callback_data=f'{self.question_button.data}{question_id}|{number_of_question}'))
        button_rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
        for row in button_rows:
            keyboard.row(*row)
        technical_exercise = types.InlineKeyboardButton(text=self.tex_button.text,
                                                        callback_data=f'{self.tex_button.data}{directory}|{sub_direction}|{section}')
        cancel = types.InlineKeyboardButton(text=self.cancel_to_directions_button.text,
                                            callback_data=self.cancel_to_directions_button.data)
        main_menu = types.InlineKeyboardButton(text=self.enter_menu_for_client_button.text,
                                               callback_data=self.enter_menu_for_client_button.data)
        keyboard.add(technical_exercise, cancel, main_menu)
        return keyboard

    def games(self):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        tmp_games_buttons = []
        for game in games.list:
            game_button = types.InlineKeyboardButton(text=game.visual_name, callback_data=game.official_name)
            tmp_games_buttons.append(game_button)
        keyboard.row(*tmp_games_buttons[:3])
        keyboard.row(*tmp_games_buttons[4:])
        main_menu = types.InlineKeyboardButton(text=self.enter_menu_for_client_button.text,
                                               callback_data=self.enter_menu_for_client_button.data)
        keyboard.row(main_menu)
        return keyboard

    def blog(self) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup()
        cancel = types.InlineKeyboardButton(text=self.enter_menu_for_client_button.text,
                                            callback_data=self.enter_menu_for_client_button.data)
        keyboard.add(cancel)
        return keyboard


class ClientKeyboard(Keyboard):
    change_answer_button = CallbackButton('change_answer', 'Изменить ответ')
    technical_tasks_button = CallbackButton('technical_task', '📃 Тех.задания')
    commercial_offers_button = CallbackButton('commercial_offer', '📑 Коммерческие предложения')
    reports_button = CallbackButton('reports', 'Отчеты')
    documents_button = CallbackButton('documents', '📇 Документы')
    client_grade_yes_button = CallbackButton('client_grade_yes', 'Да', client=True)
    client_grade_no_button = CallbackButton('client_grade_no', 'Пока нет', client=True)
    tex_button = CallbackButton('tex|', 'Сформировать ТЗ', parse=True)
    files_button = CallbackButton('files', '📝 Файлы')
    chat_button = CallbackButton('chat', '👨‍💻 Написать оператору')
    blog_button = CallbackButton('blog', 'GPT')
    instant_message_button = CallbackButton('instant_message', '💬 Поставить задачу')
    enter_menu_for_client_button = CallbackButton('enter_menu', 'Главное меню', client=True)

    get_file_button = CallbackButton('get|file|', 'Имя файла!', operator=False, client=True, parse=True)
    back_to_questions_client_button = CallbackButton('back_to_questions', 'К вопросам', client=True)

    def types_of_files(self):
        dict_text_callback = {
            self.technical_tasks_button.text: self.technical_tasks_button.data,
            self.commercial_offers_button.text: self.commercial_offers_button.data,
            self.reports_button.text: self.reports_button.data,
            self.documents_button.text: self.documents_button.data,
            self.enter_menu_for_client_button.text: self.enter_menu_for_client_button.data,
        }

        return self.inline_keyboard(dict_text_callback)

    def files(self, dict_path_to_files):
        dict_text_callback = {
            self.enter_menu_for_client_button.text: self.enter_menu_for_client_button.data
        }
        if dict_path_to_files:
            for key, value in dict_path_to_files.items():
                filename = Parser.get_file_name_from_path(value)
                file = {filename: f'{self.get_file_button.data}{key}'}
                dict_text_callback.update(file)
        return self.inline_keyboard(dict_text_callback, row=True)

    def answer(self, answers: list):
        buttons_text = ("✅ Отправить ответ", "Следующий вопрос", "Отменить") + tuple(answers)
        return self.reply_keyboard(buttons_text)

    def change_answer(self):
        dict_text_callback = {
            self.change_answer_button.text: self.change_answer_button.data,
            self.back_to_questions_client_button.text: self.back_to_questions_client_button.data,
            self.enter_menu_for_client_button.text: self.enter_menu_for_client_button.data,
        }

        return self.inline_keyboard(dict_text_callback)

    def send_phone(self):
        buttons_text = ("Отправить номер телефона", "Отменить")
        return self.reply_keyboard(buttons_text)

    def sex(self):
        buttons_text = ('Мужской', 'Женский', "✅ Отправить ответ", "Следующий вопрос", "Отменить")
        return self.reply_keyboard(buttons_text)

    def age(self):
        buttons_text = (
            'От 18 до 25', 'От 25 до 35', 'От 35 до 50', "✅ Отправить ответ", "Следующий вопрос", "Отменить")
        return self.reply_keyboard(buttons_text)

    def other_answers(self):
        buttons_text = ("✅ Отправить ответ", "Следующий вопрос", "Отменить")
        return self.reply_keyboard(buttons_text)

    def evaluation(self):
        text_and_callbacks = {
            self.client_grade_yes_button.text: self.client_grade_yes_button.data,
            self.client_grade_no_button.text: self.client_grade_yes_button.data,
            self.enter_menu_for_client_button.text: self.enter_menu_for_client_button.data}
        return self.inline_keyboard(text_and_callbacks)


class OperatorKeyboard(Keyboard):
    enter_into_a_dialog_button = CallbackButton("enter_into_a_dialog|", '✅Вступить в диалог', operator=True, parse=True)
    operator_menu_in_dialogue_button = CallbackButton('operator_menu_in_dialogue', 'Главное меню', operator=True)
    queue_button = CallbackButton('queue|', 'Запросы', operator=True, parse=True)
    requests_button = CallbackButton('requests', 'Запросы', operator=True)
    clients_button = CallbackButton('clients', 'Клиенты', operator=True)
    tasks_button = CallbackButton('tasks', "Задачи", operator=True)
    settings_button = CallbackButton('settings', 'Настройки', operator=True)
    change_question_button = CallbackButton('change_question', 'Изменить вопрос', operator=True)
    add_question_button = CallbackButton('add_question', 'Добавить вопрос', operator=True)
    client_info_button = CallbackButton("client|info|", 'Инфрмация о клиенте', operator=True, parse=True)
    technical_tasks_for_operator_in_dialogue_button = CallbackButton('technical_tasks_for_operator_in_dialogue',
                                                                     'Технические задания и брифы', operator=True)
    commercial_offers_for_operator_in_dialogue_button = CallbackButton('commercial_offers_for_operator_in_dialogue',
                                                                       'Коммерческие предложения', operator=True)
    reports_for_operator_in_dialogue_button = CallbackButton('reports_for_operator_in_dialogue', 'Отчеты',
                                                             operator=True)
    other_documents_for_operator_in_dialogue_button = CallbackButton('other_documents_for_operator_in_dialogue',
                                                                     'Документы',
                                                                     operator=True)
    back_to_questions_button = CallbackButton('back_to_questions', 'Назад к вопросам', operator=True)
    upload_file_button = CallbackButton('upload_file', 'Загрузить файл', operator=True)
    upload_file_in_dialogue_button = CallbackButton('upload_file_in_dialogue', 'Загрузить файл', operator=True)
    tt_operator_button = CallbackButton('TT_for_operator|', 'Тех. задания',
                                        operator=True, parse=True)
    co_operator_button = CallbackButton('CO_operator|', 'Коммерческие предложения',
                                        operator=True, parse=True)
    r_operator_button = CallbackButton('R_operator|', 'Отчеты', operator=True, parse=True)
    od_operator_button = CallbackButton('OD_operator|', 'Документы', operator=True, parse=True)
    dialogue_history_button = CallbackButton('dialogue_history|', 'История переписки', operator=True, parse=True)
    end_the_dialogue_button = CallbackButton('end_the_dialogue', '❌Выйти из диалога', operator=True)
    get_documents_button = CallbackButton('get_documents|', 'Документы пользователя', operator=True, parse=True)
    enter_menu_for_operator_button = CallbackButton('enter_menu', 'Главное меню', operator=True)
    briefing_button = CallbackButton('briefing', '📋 Сформировать Тех. Задание', operator=False)
    question_for_operator_button = CallbackButton('question|', '❓ Вопрос', parse=True, operator=True)
    get_file_for_operator_button = CallbackButton('get|file|', 'Имя файла!', operator=True, parse=True)
    get_file_in_dialogue_operator_button = CallbackButton('get|file|', 'Имя файла!',
                                                          state=OperatorStates.dialogue_with_client,
                                                          operator=True, parse=True)
    cancel_to_directions_button = CallbackButton('cancel_to_directions', 'Назад')

    def enter_menu(self):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        key1 = types.InlineKeyboardButton(text=self.requests_button.text, callback_data=self.requests_button.data)
        key2 = types.InlineKeyboardButton(text=self.clients_button.text, callback_data=self.clients_button.data)
        key3 = types.InlineKeyboardButton(text=self.tasks_button.text, callback_data=self.tasks_button.data)
        key4 = types.InlineKeyboardButton(text=self.settings_button.text, callback_data=self.settings_button.data)
        keyboard.add(key1, key2, key3, key4)
        return keyboard

    def clients(self, clients, callback_data_prefix):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        cancel = types.InlineKeyboardButton(text=self.enter_menu_for_operator_button.text,
                                            callback_data=self.enter_menu_for_operator_button.data)
        if not clients:
            keyboard.add(cancel)
            return keyboard
        users_data = db.get_users_data(clients)

        for client in users_data:
            keyboard.add(types.InlineKeyboardButton(text=f'❗️{client["name"]}|{client["company"]}',
                                                    callback_data=f'{callback_data_prefix}|{client["id"]}'))
        keyboard.add(cancel)
        return keyboard

    def settings(self):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        key1 = types.InlineKeyboardButton(text=self.change_question_button.text,
                                          callback_data=self.change_question_button.data)
        cancel = types.InlineKeyboardButton(text=self.enter_menu_for_operator_button.text,
                                            callback_data=self.enter_menu_for_operator_button.data)
        keyboard.add(key1, cancel)
        return keyboard

    def customer_information(self, client_id: int):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        dialogue_history = types.InlineKeyboardButton(text=self.dialogue_history_button.text,
                                                      callback_data=f'{self.dialogue_history_button.data}{client_id}')
        show_user_documents = types.InlineKeyboardButton(text=self.get_documents_button.text,
                                                         callback_data=f'{self.get_documents_button.data}{client_id}')
        insert_into_dialogue = types.InlineKeyboardButton(text=self.enter_into_a_dialog_button.text,
                                                          callback_data=f'{self.enter_into_a_dialog_button.data}{client_id}')
        cancel = types.InlineKeyboardButton(text=self.enter_menu_for_operator_button.text,
                                            callback_data=self.enter_menu_for_operator_button.data)

        keyboard.add(dialogue_history, show_user_documents, insert_into_dialogue, cancel)
        return keyboard

    def menu_in_dialogue(self):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        tech_tasks = types.InlineKeyboardButton(text=self.technical_tasks_for_operator_in_dialogue_button.text,
                                                callback_data=self.technical_tasks_for_operator_in_dialogue_button.data)
        commercial_offers = types.InlineKeyboardButton(text=self.commercial_offers_for_operator_in_dialogue_button.text,
                                                       callback_data=self.commercial_offers_for_operator_in_dialogue_button.data)
        reports = types.InlineKeyboardButton(text=self.reports_for_operator_in_dialogue_button.text,
                                             callback_data=self.reports_for_operator_in_dialogue_button.data)
        documents = types.InlineKeyboardButton(text=self.other_documents_for_operator_in_dialogue_button.text,
                                               callback_data=self.other_documents_for_operator_in_dialogue_button.data)
        cancel = types.InlineKeyboardButton(text=self.end_the_dialogue_button.text,
                                            callback_data=self.end_the_dialogue_button.data)
        keyboard.add(tech_tasks, commercial_offers, reports, documents, cancel)
        return keyboard

    def client_files(self, dict_of_path_files, in_dialogue=None):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        callback_1 = self.upload_file_button.data
        callback_2 = self.enter_menu_for_operator_button.data
        if in_dialogue:
            callback_1 = self.upload_file_in_dialogue_button.data
            callback_2 = self.operator_menu_in_dialogue_button.data
        upload_file = types.InlineKeyboardButton(text='Загрузить файл', callback_data=callback_1)
        cancel = types.InlineKeyboardButton(text='Главное меню', callback_data=callback_2)
        if dict_of_path_files is None:
            keyboard.row(cancel, upload_file)
            return keyboard
        else:
            for key, value in dict_of_path_files.items():
                filename = value.split('/')[-1]
                keyboard.add(
                    types.InlineKeyboardButton(text=f'{filename}',
                                               callback_data=f'{self.get_file_for_operator_button.data}{key}'))
            keyboard.row(cancel, upload_file)
            return keyboard

    def types_documents(self, client_id: int):
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        tech_tasks = types.InlineKeyboardButton(text=self.tt_operator_button.text,
                                                callback_data=f'{self.tt_operator_button.data}{client_id}')
        commercial_offers = types.InlineKeyboardButton(text=self.co_operator_button.text,
                                                       callback_data=f'{self.co_operator_button.data}{client_id}')
        reports = types.InlineKeyboardButton(text=self.r_operator_button.text,
                                             callback_data=f'{self.r_operator_button.data}{client_id}')
        documents = types.InlineKeyboardButton(text=self.od_operator_button.text,
                                               callback_data=f'{self.od_operator_button.data}{client_id}')
        cancel = types.InlineKeyboardButton(text=self.enter_menu_for_operator_button.text,
                                            callback_data=self.enter_menu_for_operator_button.data)
        keyboard.add(tech_tasks, commercial_offers, reports, documents, cancel)
        return keyboard

    def questions(self, directory, sub_direction, section):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = []
        dict_of_question_id_and_number = db.get_question_id_and_number(directory, section, sub_direction)
        for question_id, number_of_question in dict_of_question_id_and_number.items():
            buttons.append(types.InlineKeyboardButton(text=f'❓ Вопрос {number_of_question}',
                                                      callback_data=f'{self.question_for_operator_button.data}{question_id}|{number_of_question}'))

        button_rows = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]
        for row in button_rows:
            keyboard.row(*row)
        cancel = types.InlineKeyboardButton(text=self.cancel_to_directions_button.text,
                                            callback_data=self.cancel_to_directions_button.data)
        add_question = types.InlineKeyboardButton(text=self.add_question_button.text,
                                                  callback_data=self.add_question_button.data)
        main_menu = types.InlineKeyboardButton(text=self.enter_menu_for_operator_button.text,
                                               callback_data=self.enter_menu_for_operator_button.data)
        keyboard.add(cancel, add_question, main_menu)
        return keyboard

    def change_question(self):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        cancel = types.InlineKeyboardButton(text=self.back_to_questions_button.text,
                                            callback_data=self.back_to_questions_button.data)
        main_menu = types.InlineKeyboardButton(text=self.enter_menu_for_operator_button.text,
                                               callback_data=self.enter_menu_for_operator_button.data)
        keyboard.add(cancel, main_menu)
        return keyboard


class PartnerKeyboard(Keyboard):
    enter_menu_for_partner = CallbackButton('enter_menu', 'Главное меню', partner=True)
    files = CallbackButton('files', '📝 Файлы')
    chat = CallbackButton('chat', '👨‍💻 Написать оператору')
    blog = CallbackButton('blog', 'GPT')
    instant_message = CallbackButton('instant_message', '💬 Поставить задачу')
    enter_menu_for_client = CallbackButton('enter_menu', 'Главное меню', client=True)
    briefing = CallbackButton('briefing', '📋 Сформировать Тех. Задание', operator=False)
    choose_game = CallbackButton('choose_game', '🎲 Игры')
    send_game = CallbackButton(games.get_list_short_names(), 'Играть')

    def enter_menu(self, doc: bool = False):
        """Keyboard for main menu for partner"""
        keyboard = types.InlineKeyboardMarkup(row_width=True)
        key1 = types.InlineKeyboardButton(text=self.briefing.text, callback_data=self.briefing.data)
        key2 = types.InlineKeyboardButton(text=self.instant_message.text, callback_data=self.instant_message.data)
        key3 = types.InlineKeyboardButton(text=self.files.text, callback_data=self.files.data)
        key4 = types.InlineKeyboardButton(text=self.choose_game.text, callback_data=self.choose_game.data)
        key5 = types.InlineKeyboardButton(text=self.chat.text, callback_data=self.chat.data)
        key6 = types.InlineKeyboardButton(text=self.blog.text, callback_data=self.blog.data)
        keyboard.add(key1)
        if doc is True:
            keyboard.add(key3)
        keyboard.row(key2, key4)
        keyboard.add(key5, key6)
        return keyboard


general_keyboard = GeneralKeyboard()
client_keyboard = ClientKeyboard()
operator_keyboard = OperatorKeyboard()
partner_keyboard = PartnerKeyboard()


def remove_keyboard(message, bot, text: str) -> None:
    bot.send_message(message.chat.id, f'{text}',
                     reply_markup=types.ReplyKeyboardRemove())
