import logging
import random
import time

from telebot import apihelper

from config import OPERATOR_ID, DIR_FOR_OTHER_FILES, DIR_FOR_REPORTS, DIR_FOR_COMMERCIAL_OFFERS, \
    DIR_FOR_TECHNICAL_TASKS, DIR_FOR_SAVE_DIALOGS, bot
from handlers.keyboards import general_keyboard, client_keyboard, operator_keyboard
from handlers.text_messages import TEXT_MESSAGES

from services.db_data import db
from services.file_handler import find_user_documents, get_list_of_clients_dialogue_files, file_check, \
    generate_technical_task_file
from services.redis_db import redis_cache
from services.states import GeneralStates, OperatorStates
from services.status import ClientStatus
from services.string_parser import Parser
from services.tg_games import games

logger = logging.getLogger(__name__)





class GeneralCallback:

    def send_document_to_telegram(self, addressee_id: int, document_path, caption, visible_file_name):
        try:
            with open(document_path, 'rb') as file:
                bot.send_document(chat_id=addressee_id, document=file,
                                  caption=caption,
                                  disable_content_type_detection=True,
                                  visible_file_name=visible_file_name)
            logger.info(f'Файл удачно отправлен пользователю: {addressee_id}')
        except Exception as e:
            logger.error(f'Неудачная отправка файла пользователю: {addressee_id}. Ошибка: {e}')


    def enter_menu(self, call):

        client_id = call.from_user.id
        user_data = db.get_users_data(client_id)
        reply_markup = general_keyboard.enter_menu(doc=False)
        if user_data['documents']:
            reply_markup = general_keyboard.enter_menu(doc=True)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['start'].format(username=user_data['name'],
                                                                 company=user_data['company']),
                              reply_markup=reply_markup)

    def briefing(self, call):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'], reply_markup=general_keyboard.directions())

    def directory(self, call):
        direction = call.data
        list_of_sub_directions = db.get_sub_directions(direction)
        if list_of_sub_directions:
            keyboard = general_keyboard.sub_directions(direction, list_of_sub_directions)
        else:
            list_of_sections = db.get_sections_from_db(direction)
            keyboard = general_keyboard.sections(direction, list_of_sections)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=keyboard)

    def sub_directory(self, call):
        path = call.data
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=general_keyboard.sections_from_subcategory(path))



    def section(self, call):
        path = call.data
        directory, sub_direction, section = Parser.get_directory_sub_direction_section(path)
        redis_cache.set_directory_subdir_section(call.from_user.id, path)
        keyboard = general_keyboard.questions(call.from_user.id, directory, sub_direction, section)
        if call.from_user.id == OPERATOR_ID:
            keyboard = operator_keyboard.questions(directory, sub_direction, section)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=keyboard)

    def cancel_to_directions(self, call):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=general_keyboard.directions())

    def question(self, call):
        user_id = call.from_user.id
        question_id, number_of_question = Parser.get_question_id_and_number(call.data)
        redis_cache.set_id_and_number_of_question(user_id, question_id, number_of_question)
        question, answers = db.get_question_and_answers_from_db(question_id)
        user_answer = db.get_user_answer(user_id, question_id)
        if user_answer:
            bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                  text=f'❓{question}?\n\nВаш ответ:{user_answer}',
                                  reply_markup=client_keyboard.change_answer())
            return
        bot.set_state(user_id, GeneralStates.answer_to_question, call.from_user.id)
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, f'❓{question}?\n\nНапишите ответ и нажмите "✅ Отправить ответ"',
                         reply_markup=client_keyboard.answer(answers))


class ClientCallback(GeneralCallback):

    def __show_files_for_client(self, call, directory):
        user_id = call.from_user.id
        logger.info(f'Клиент {user_id} запросил файлы')
        dict_path_to_files = find_user_documents(user_id, directory)
        redis_cache.set_selected_directory(call.from_user.id, directory)
        if not dict_path_to_files:
            text = 'К сожалению у вас нет оформленных файлов'
        else:
            redis_cache.save_dict_of_path_for_download_file(user_id, dict_path_to_files)
            text = 'Выберите какой файл вы хотите получить:'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=text, reply_markup=client_keyboard.files(dict_path_to_files))

    def file_types(self, call):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Выберите тип файла',
                              reply_markup=client_keyboard.types_of_files())

    def technical_task(self, call):
        self.__show_files_for_client(call, DIR_FOR_TECHNICAL_TASKS)

    def commercial_offer(self, call):
        self.__show_files_for_client(call, DIR_FOR_COMMERCIAL_OFFERS)

    def reports(self, call):
        self.__show_files_for_client(call, DIR_FOR_REPORTS)

    def documents(self, call):
        self.__show_files_for_client(call, DIR_FOR_OTHER_FILES)

    def chat_with_operator(self, call):
        bot.send_contact(call.message.chat.id, phone_number='+74950188868', first_name='Оператор Mr.Эйч')
        bot.send_message(call.message.chat.id, TEXT_MESSAGES['chat_with_operator'])

    def blog(self, call):
        user_id = call.from_user.id
        bot.send_message(call.message.chat.id,
                         'Напишите ваш вопрос и мы постараемся сразу ответить на него 😉\n\n'
                         '/cancel - Выход из блога')
        bot.set_state(user_id, GeneralStates.chat_gpt)

    def change_answer(self, call):
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.set_state(call.from_user.id, GeneralStates.answer_to_question, call.from_user.id)
        question_id = redis_cache.get_question_id(call.from_user.id)
        question, answers = db.get_question_and_answers_from_db(question_id)
        bot.send_message(call.message.chat.id, f'❓{question}?\n\nНапишите ответ и нажмите "✅ Отправить ответ"',
                         reply_markup=client_keyboard.answer(answers))

    def grade(self, call):
        bot.delete_message(call.message.chat.id, call.message.id)
        match call.data:
            case 'client_grade_yes':
                user_data = db.get_users_data(call.from_user.id)
                path_to_file = redis_cache.get_last_file_path(call.from_user.id)
                caption = f"Техническое задание от пользователя:\n{user_data['name']}\n" \
                          f"Username: {user_data['tg_username']}\n" \
                          f"Компания: {user_data['company']}\n" \
                          f"Телефон: {user_data['phone']}\n" \
                          f"Website: {user_data['website']}\n"
                visible_file_name = f'Тех.задание компании {user_data["company"]}.docx'
                self.send_document_to_telegram(OPERATOR_ID, path_to_file, caption=caption,
                                               visible_file_name=visible_file_name)
                redis_cache.add_client_to_queue(call.from_user.id)
                bot.send_message(OPERATOR_ID, 'Начать чат с клиентом ?',
                                 reply_markup=operator_keyboard.customer_information(call.from_user.id))
            case 'client_grade_no':
                bot.send_message(call.message.chat.id, f'Хорошо, отличного дня!')

    # Диалог с оператором

    def instant_messaging_service(self, call):
        client_id = call.from_user.id
        user_data = db.get_users_data(client_id)
        operator_state = redis_cache.get_operator_state()
        logger.info(f'Запрос от клиента {client_id} на диалог')
        match operator_state:
            case b'free' | None:
                redis_cache.set_operator_state(b'busy')
                logger.info(f'Перевод статуса оператора в "занят" (busy)')
                bot.send_message(OPERATOR_ID, f'💬Запрос на диалог!🧨\n\nКлиент: {user_data["name"]}\n'
                                              f'Компания: {user_data["company"]}\n'
                                              f'Телефон: {user_data["phone"]}',
                                 reply_markup=operator_keyboard.customer_information(client_id))
            case _:
                logger.info(f'Оператор занят')
        match redis_cache.add_client_to_queue(client_id):
            case True:
                logger.info(f'Клиент {client_id} зарегистрирован в очереди и ждет ответа оператора')
                bot.send_message(call.message.chat.id, 'Подождите пока оператор к вам присоединится...')
            case _:
                logger.info(f'Клиент {client_id} уже присутствует в очереди')
                bot.send_message(call.message.chat.id,
                                 'Вы уже в очереди подождите пожалуйста, пока оператор👨 ответит вам ‍💻😊')
                bot.send_message(OPERATOR_ID,
                                 f'❗️Не забывайте о клиенте\n'
                                 f'Он повторно запрашивает диалог\n\n'
                                 f'Клиент: {user_data["name"]}\n'
                                 f'Компания: {user_data["company"]}\n'
                                 f'Телефон: {user_data["phone"]}\n\n'
                                 f'Меню(/start) -> Запросы'
                                 )

    def back_to_questions(self, call):
        directory, sub_direction, section = redis_cache.get_directory_subdir_section(call.from_user.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=general_keyboard.questions(call.from_user.id, directory,
                                                                      sub_direction,
                                                                      section))

    def generation_technical_exercise(self, call):
        logger.info(f'Формирование и отправка файла')
        client_id = call.from_user.id
        directory, section = Parser.get_directory_sub_direction_section(call.data)
        all_emoji = ['🎲', '🎯', '🏀', '⚽', '🎳', '🎰']
        bot.send_dice(client_id, emoji=random.choice(all_emoji), timeout=5)
        bot.send_chat_action(client_id, action="upload_document", timeout=3)
        bot.send_message(client_id, 'Ваш файл формируется, а пока, давайте сыграем 😊')
        time.sleep(3)

        bot.send_message(client_id, 'Хотите чтобы мы оценили ваш проект?',
                         reply_markup=client_keyboard.evaluation())

        user_data = db.get_users_data(client_id)
        questions, answers = db.get_user_list_of_questions_informal_and_answers(client_id, directory, section)
        bot.delete_message(call.message.chat.id, call.message.id)
        db.delete_user_answers_in_section(call.from_user.id, directory, section)
        document_path = generate_technical_task_file(user_id=client_id,
                                                     section=section,
                                                     client_name=user_data['name'],
                                                     company=user_data['company'],
                                                     phone=user_data['phone'],
                                                     website=user_data['website'],
                                                     list_of_questions=questions,
                                                     answers=answers)
        redis_cache.set_last_file_path(client_id, document_path)
        db.update_info_about_user_docs_in_db(client_id, documents=True)
        db.update_user_status(client_id, ClientStatus.tech_task)
        time.sleep(1)
        self.send_document_to_telegram(client_id, document_path, caption="Ваш файл",
                                       visible_file_name=f'{user_data["company"]}.docx')

    def get_file(self, call):
        bot.delete_message(call.message.chat.id, call.message.id)
        client_id = call.from_user.id
        key_for_path = Parser.get_key_for_path(call.data)
        path_to_file = redis_cache.get_path_for_download_file_by_key(client_id, key_for_path)
        logger.info(f'Клиент {client_id} запросил файл: {path_to_file}')
        user_data = db.get_users_data(client_id)
        file_type = Parser.get_file_type(path_to_file)
        self.send_document_to_telegram(client_id, path_to_file, caption="Ваш файл",
                                       visible_file_name=f'{user_data["company"]}.{file_type}')


class GameCallback:

    def choose_game(self, call):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Выберите игру:',
                              reply_markup=general_keyboard.games())

    def send_game(self, call):
        game = call.data
        try:
            bot.send_game(call.from_user.id, game_short_name=game)
        except apihelper.ApiTelegramException:
            logger.error('Игра не зарегистрирована в данном боте, либо указано неверное название игры')

    def game(self, call):
        short_name = call.game_short_name
        for game in games.list:
            if short_name == game.official_name:
                bot.answer_callback_query(call.id, url=game.url)


class OperatorCallback(GeneralCallback):

    def __get_file_path_caption_and_filename(self, call, client_id):
        key_for_path = Parser.get_key_for_path(call.data)
        path_to_file = redis_cache.get_path_for_download_file_by_key(client_id, key_for_path)
        logger.info(f'Оператор {call.from_user.id} запросил файл клиента: {path_to_file}')
        user_data = db.get_users_data(client_id)
        file_type = Parser.get_file_type(path_to_file)
        caption = f"Файл пользователя:\n{user_data['name']}\n" \
                  f"Username: {user_data['tg_username']}\n" \
                  f"Компания: {user_data['company']}\n" \
                  f"Телефон: {user_data['phone']}\n" \
                  f"Website: {user_data['website']}\n"
        visible_file_name = f'{user_data["company"]}.{file_type}'
        return path_to_file, caption, visible_file_name

    def requests(self, call):
        queue_of_clients = redis_cache.get_queue_of_clients()
        text = 'Запросы от пользователей'
        if not queue_of_clients:
            text = 'Запросов от пользователей нет'
        callback_data_prefix = 'queue'
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text,
                              reply_markup=operator_keyboard.clients(queue_of_clients, callback_data_prefix))

    def clients(self, call):
        list_of_clients = get_list_of_clients_dialogue_files()
        text = 'Выберите клиента:'
        callback_data_prefix = 'client|info'
        if not list_of_clients:
            text = 'Нет доступных диалогов с клиентам'
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text,
                              reply_markup=operator_keyboard.clients(list_of_clients, callback_data_prefix))

    def tasks(self, call):
        pass

    def settings(self, call):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Здесь вы можете изменить или добавить вопросы, секции и разделы',
                              reply_markup=operator_keyboard.settings())

    def enter_menu(self, call):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['start_for_operator'],
                              reply_markup=operator_keyboard.enter_menu())

    def back_to_questions(self, call):
        directory, sub_direction, section = redis_cache.get_directory_subdir_section(call.from_user.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=operator_keyboard.questions(directory, sub_direction, section))

    def get_dialogue_history(self, call):
        client_id = Parser.get_client_id(call.data)
        path_to_dialogue_file = f'{DIR_FOR_SAVE_DIALOGS}/{client_id}/dialogue.log'
        if file_check(path_to_dialogue_file):
            self.send_document_to_telegram(call.from_user.id, path_to_dialogue_file,
                                           caption='История диалога',
                                           visible_file_name='Диалог.log')
        else:
            bot.send_message(call.from_user.id, 'История диалога пуста')

    def file_types(self, call):
        client_id = Parser.get_client_id(call.data)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text='Выберите раздел',
                              reply_markup=operator_keyboard.types_documents(client_id))

    def __show_client_files_in_dialogue(self, call, dir_path, client_id):
        if client_id is None:
            bot.delete_message(call.message.chat.id, call.message.id)
            return
        dict_path_to_files = find_user_documents(client_id, dir_path)
        redis_cache.set_selected_directory(call.from_user.id, dir_path)
        if not dict_path_to_files:
            text = f'Нет документов у клиента'
        else:
            redis_cache.save_dict_of_path_for_download_file(client_id, dict_path_to_files)
            text = 'Выберите какой файл вы хотите получить:'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                              reply_markup=operator_keyboard.client_files(dict_path_to_files, in_dialogue=True))

    def technical_tasks_in_dialogue(self, call):
        user_id = redis_cache.get_first_client_from_queue()
        self.__show_client_files_in_dialogue(call, DIR_FOR_TECHNICAL_TASKS, user_id)

    def commercial_offers_in_dialogue(self, call):
        user_id = redis_cache.get_first_client_from_queue()
        self.__show_client_files_in_dialogue(call, DIR_FOR_COMMERCIAL_OFFERS, user_id)

    def reports_in_dialogue(self, call):
        user_id = redis_cache.get_first_client_from_queue()
        self.__show_client_files_in_dialogue(call, DIR_FOR_REPORTS, user_id)

    def other_documents_in_dialogue(self, call):
        user_id = redis_cache.get_first_client_from_queue()
        self.__show_client_files_in_dialogue(call, DIR_FOR_OTHER_FILES, user_id)

    def __show_client_files(self, call, dir_path, client_id):
        logger.info(f'Запрос файлов клиента: {client_id}')
        dict_path_to_files = find_user_documents(client_id, dir_path)
        redis_cache.set_selected_directory(call.from_user.id, dir_path)
        redis_cache.set_user_to_display_information(client_id)
        if not dict_path_to_files:
            text = f'Нет документов у клиента'
        else:
            redis_cache.save_dict_of_path_for_download_file(client_id, dict_path_to_files)
            text = 'Выберите какой файл вы хотите получить:'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                              reply_markup=operator_keyboard.client_files(dict_path_to_files))

    def client_technical_tasks(self, call):
        client_id = Parser.get_client_id(call.data)
        self.__show_client_files(call, DIR_FOR_TECHNICAL_TASKS, client_id)

    def client_commercial_offers(self, call):
        client_id = Parser.get_client_id(call.data)
        self.__show_client_files(call, DIR_FOR_COMMERCIAL_OFFERS, client_id)

    def client_reports(self, call):
        client_id = Parser.get_client_id(call.data)
        self.__show_client_files(call, DIR_FOR_REPORTS, client_id)

    def client_other_documents(self, call):
        client_id = Parser.get_client_id(call.data)
        self.__show_client_files(call, DIR_FOR_OTHER_FILES, client_id)

    def enter_menu_in_dialogue(self, call):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Меню взаимодействия с клиентом',
                              reply_markup=operator_keyboard.menu_in_dialogue())

    def upload_file_in_dialogue(self, call):
        directory = redis_cache.get_selected_directory(call.from_user.id)
        logger.info(f'Выбрана директория для загрузки файла: {directory}')
        dir_to_state = {
            DIR_FOR_TECHNICAL_TASKS: OperatorStates.get_technical_task_file_in_dialogue,
            DIR_FOR_COMMERCIAL_OFFERS: OperatorStates.get_commercial_offer_file_in_dialogue,
            DIR_FOR_REPORTS: OperatorStates.get_report_file_in_dialogue,
            DIR_FOR_OTHER_FILES: OperatorStates.get_other_file_in_dialogue
        }
        message = 'Отправьте файл'
        state = dir_to_state.get(directory)
        bot.send_message(call.from_user.id, message)
        bot.set_state(call.from_user.id, state, call.from_user.id)

    def upload_file(self, call):
        directory = redis_cache.get_selected_directory(call.from_user.id)
        logger.info(f'Выбрана директория для загрузки файла: {directory}')
        dir_to_state = {
            DIR_FOR_TECHNICAL_TASKS: GeneralStates.get_technical_task_file,
            DIR_FOR_COMMERCIAL_OFFERS: GeneralStates.get_commercial_offer_file,
            DIR_FOR_REPORTS: GeneralStates.get_report_file,
            DIR_FOR_OTHER_FILES: GeneralStates.get_other_file
        }
        message = 'Отправьте файл'
        state = dir_to_state.get(directory)
        bot.send_message(call.from_user.id, message)
        bot.set_state(call.from_user.id, state, call.from_user.id)

    def queue(self, call):
        client_id = Parser.get_client_id(call.data)
        redis_cache.move_client_to_first_place_in_queue(client_id)
        bot.send_message(call.message.chat.id, 'Вступить в диалог с клиентом ?',
                         reply_markup=operator_keyboard.customer_information(client_id))

    def change_question(self, call):
        question_id, number_of_question = Parser.get_question_id_and_number(call.data)
        question, default_answers = db.get_question_and_answers_from_db(question_id)
        if not default_answers:
            default_answers = 'Нет вариантов ответов'
        bot.set_state(call.from_user.id, OperatorStates.change_question)
        bot.add_data(call.from_user.id, question_id_for_change=question_id)
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, f'Вопрос: {question}?\n\nОтветы:\n{default_answers}\n'
                                               f'Впишите вопрос и варианты ответов в формате:\n'
                                               f'ВОПРОС || ОТВЕТ1| ОТВЕТ2| ОТВЕТ3\n\n'
                                               f'Пример:\n'
                                               f'Каков рейтинг компании в России || 11| 34| Не знаю',
                         reply_markup=operator_keyboard.change_question())

    def add_question(self, call):
        bot.set_state(call.from_user.id, OperatorStates.add_question)
        bot.send_message(call.message.chat.id, f'Впишите вопрос и варианты ответов в формате:\n'
                                               f'ВОПРОС || ОТВЕТ1| ОТВЕТ2| ОТВЕТ3\n\n'
                                               f'\tПример:\t\n'
                                               f'Каков рейтинг компании в России || 11| 34| Не знаю')

    # Диалог с клиентом

    def enter_into_a_dialog(self, call):
        operator = call.from_user.id
        client_id = Parser.get_client_id(call.data)
        redis_cache.move_client_to_first_place_in_queue(client_id)
        redis_cache.set_operator_state(b'busy')
        logger.info(f'Оператор вступил в диалог с клиентом {client_id}')
        bot.set_state(client_id, GeneralStates.dialogue_with_operator)
        bot.set_state(operator, OperatorStates.dialogue_with_client)
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(client_id, 'Вы вступили в диалог с оператором\n')
        bot.send_message(operator, 'Вы вступили в диалог с клиентом\nНапишите ему:',
                         reply_markup=operator_keyboard.menu_in_dialogue())
        logger.info(
            f'Состояние клиента - {bot.get_state(client_id)}, оператора - {bot.get_state(operator)}')

    def client_info(self, call):
        operator = call.from_user.id
        client_id = Parser.get_client_id(call.data)
        bot.send_message(operator, 'Выберите действие',
                         reply_markup=operator_keyboard.customer_information(client_id))

    def left_dialog(self, call):
        bot.delete_message(call.message.chat.id, call.message.id)
        client_id = redis_cache.get_first_client_and_delete_from_queue()
        if client_id is None:
            bot.send_message(OPERATOR_ID, f'Вы уже выходили из этого диалога')
            return
        bot.delete_state(OPERATOR_ID, OPERATOR_ID)
        bot.delete_state(client_id, client_id)
        logger.info(f'Оператор завершил диалог с клиентом: {client_id}')
        logger.info(
            f'Состояние клиента - {bot.get_state(client_id, client_id)}, оператора - {bot.get_state(OPERATOR_ID, OPERATOR_ID)}')
        bot.send_message(OPERATOR_ID, f'Вы вышли из диалога!')
        next_client = redis_cache.get_first_client_from_queue()
        if next_client is None:
            redis_cache.set_operator_state(b'free')
            logger.info(f'Запросов в очереди нет, статус оператора перевод в "свободен" (free)')
            return
        logger.info(f'Запрос к оператору на диалог от клиента: {next_client}')
        logger.info(f'Есть запросы в очереди, статус оператора переведен в "занят" (busy)')
        redis_cache.set_operator_state(b'busy')
        bot.send_message(OPERATOR_ID, f'💬Запрос на диалог!🧨\n\nОт пользователя:\nID: {next_client}\n',
                         reply_markup=operator_keyboard.customer_information(next_client))

    def get_file_in_dialogue(self, call):
        client_id = redis_cache.get_first_client_from_queue()
        path_to_file, caption, visible_file_name = self.__get_file_path_caption_and_filename(call, client_id)
        self.send_document_to_telegram(OPERATOR_ID, path_to_file, caption=caption,
                                       visible_file_name=visible_file_name)

    def get_file(self, call):
        client_id = redis_cache.get_user_to_display_information()
        path_to_file, caption, visible_file_name = self.__get_file_path_caption_and_filename(call, client_id)
        self.send_document_to_telegram(OPERATOR_ID, path_to_file, caption=caption,
                                       visible_file_name=visible_file_name)


game_callback = GameCallback()
general_callback = GeneralCallback()
client_callback = ClientCallback()
operator_callback = OperatorCallback()





