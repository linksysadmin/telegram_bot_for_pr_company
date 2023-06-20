import logging

from config import OPERATOR_ID, DIR_FOR_COMMERCIAL_OFFERS, DIR_FOR_TECHNICAL_TASKS, DIR_FOR_OTHER_FILES, \
    DIR_FOR_REPORTS, DIR_FOR_SAVE_DIALOGS
from handlers.keyboards import ClientKeyboards, OperatorKeyboards, GeneralKeyboards
from handlers.documents import send_document_to_telegram
from services.db_data import get_question_and_answers_from_db, \
    get_user_answer, get_user_data_from_db, get_sections_from_db, get_sub_directions
from services.file_handler import find_user_documents, file_check, get_list_of_clients_dialogue_files
from services.redis_db import redis_cache
from services.states import MyStates, OperatorStates
from handlers.text_messages import TEXT_MESSAGES
from services.string_parser import CallDataParser

logger = logging.getLogger(__name__)


class BaseCallbackHandlers:
    @staticmethod
    def briefing(call, bot):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'], reply_markup=GeneralKeyboards.directions())

    @staticmethod
    def directory(call, bot):
        direction = call.data
        list_of_sub_directions = get_sub_directions(direction)
        if list_of_sub_directions:
            keyboard = GeneralKeyboards.sub_directions(direction, list_of_sub_directions)
        else:
            list_of_sections = get_sections_from_db(direction)
            keyboard = GeneralKeyboards.sections(direction, list_of_sections)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=keyboard)

    @staticmethod
    def sub_directory(call, bot):
        path = call.data
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=GeneralKeyboards.sections_from_subcategory(path))

    @staticmethod
    def section(call, bot):
        path = call.data
        keyboard = OperatorKeyboards.questions(call.from_user.id, path)
        if call.from_user.id != OPERATOR_ID:
            keyboard = ClientKeyboards.questions(call.from_user.id, path)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=keyboard)

    @staticmethod
    def cancel_to_directions(call, bot):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=GeneralKeyboards.directions())

    @staticmethod
    def back_to_questions(call, bot):
        path = redis_cache.get_keyboard_for_questions(call.from_user.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=ClientKeyboards.questions(call.from_user.id, path))


class ClientCallbackHandlers:

    @staticmethod
    def file_types(call, bot):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Выберите тип файла',
                              reply_markup=ClientKeyboards.types_of_files())

    @staticmethod
    def __show_files_for_client(call, bot, directory):
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
                              text=text, reply_markup=ClientKeyboards.files(dict_path_to_files))

    @staticmethod
    def technical_tasks(call, bot):
        ClientCallbackHandlers.__show_files_for_client(call, bot, DIR_FOR_TECHNICAL_TASKS)

    @staticmethod
    def commercial_offer(call, bot):
        ClientCallbackHandlers.__show_files_for_client(call, bot, DIR_FOR_COMMERCIAL_OFFERS)

    @staticmethod
    def reports(call, bot):
        ClientCallbackHandlers.__show_files_for_client(call, bot, DIR_FOR_REPORTS)

    @staticmethod
    def documents(call, bot):
        ClientCallbackHandlers.__show_files_for_client(call, bot, DIR_FOR_OTHER_FILES)

    @staticmethod
    def chat_with_operator(call, bot):
        bot.send_contact(call.message.chat.id, phone_number='+74950188868', first_name='Оператор Mr.Эйч')
        bot.send_message(call.message.chat.id, TEXT_MESSAGES['chat_with_operator'])

    @staticmethod
    def blog(call, bot):
        pass

    @staticmethod
    def enter_menu(call, bot):
        client_id = call.from_user.id
        user_data = get_user_data_from_db(client_id)
        reply_markup = ClientKeyboards.enter_menu(doc=False)
        if user_data['documents']:
            reply_markup = ClientKeyboards.enter_menu(doc=True)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['start'].format(username=user_data['name'],
                                                                 company=user_data['company']),
                              reply_markup=reply_markup)

    @staticmethod
    def change_answer(call, bot):
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.set_state(call.from_user.id, MyStates.answer_to_question, call.from_user.id)
        question_id = redis_cache.get_question_id(call.from_user.id)
        question, answers = get_question_and_answers_from_db(question_id)
        bot.send_message(call.message.chat.id, f'❓{question}?\n\nНапишите ответ и нажмите "✅ Отправить ответ"',
                         reply_markup=ClientKeyboards.answer(answers))

    @staticmethod
    def questions(call, bot):
        question_id = CallDataParser.get_question_id(call.data)
        if question_id <= redis_cache.get_max_question_id(call.from_user.id):
            next_callback = f"question|{question_id + 1}"
            redis_cache.set_question_id(user=call.from_user.id, question_id=question_id)
            redis_cache.set_next_question_callback(user=call.from_user.id, callback=next_callback)
        question, answers = get_question_and_answers_from_db(question_id)
        user_answer = get_user_answer(call.from_user.id, question_id)
        if user_answer:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'❓{question}?\n\nВаш ответ:{user_answer}',
                                  reply_markup=ClientKeyboards.change_answer())
            return
        bot.set_state(call.from_user.id, MyStates.answer_to_question, call.from_user.id)
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, f'❓{question}?\n\nНапишите ответ и нажмите "✅ Отправить ответ"',
                         reply_markup=ClientKeyboards.answer(answers))

    @staticmethod
    def grade(call, bot):
        bot.delete_message(call.message.chat.id, call.message.id)
        match call.data:
            case 'client_grade_yes':
                user_data = get_user_data_from_db(call.from_user.id)
                path_to_file = redis_cache.get_last_file_path(call.from_user.id)
                caption = f"Техническое задание от пользователя:\n{user_data['name']}\n" \
                          f"Username: {user_data['tg_username']}\n" \
                          f"Компания: {user_data['company']}\n" \
                          f"Телефон: {user_data['phone']}\n" \
                          f"Website: {user_data['website']}\n"
                visible_file_name = f'Тех.задание компании {user_data["company"]}.docx'
                send_document_to_telegram(bot, OPERATOR_ID, path_to_file, caption=caption,
                                          visible_file_name=visible_file_name)
                redis_cache.add_client_to_queue(call.from_user.id)
                bot.send_message(OPERATOR_ID, 'Начать чат с клиентом ?',
                                 reply_markup=OperatorKeyboards.customer_information(call.from_user.id))
            case 'client_grade_no':
                bot.send_message(call.message.chat.id, f'Хорошо, отличного дня!')


class OperatorCallbackHandlers(BaseCallbackHandlers):
    @staticmethod
    def requests(call, bot):
        queue_of_clients = redis_cache.get_queue_of_clients()
        text = 'Запросы от пользователей'
        if not queue_of_clients:
            text = 'Запросов от пользователей нет'
        callback_data_prefix = 'queue'
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text, reply_markup=OperatorKeyboards.clients(queue_of_clients, callback_data_prefix))

    @staticmethod
    def clients(call, bot):
        list_of_clients = get_list_of_clients_dialogue_files()
        text = 'Выберите клиента:'
        callback_data_prefix = 'client|info'
        if not list_of_clients:
            text = 'Нет доступных диалогов с клиентам'
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text, reply_markup=OperatorKeyboards.clients(list_of_clients, callback_data_prefix))

    @staticmethod
    def tasks(call, bot):
        pass

    @staticmethod
    def settings(call, bot):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Здесь вы можете изменить или добавить вопросы, секции и разделы',
                              reply_markup=OperatorKeyboards.settings())

    @staticmethod
    def enter_menu(call, bot):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['start_for_operator'], reply_markup=OperatorKeyboards.enter_menu())

    @staticmethod
    def get_dialogue_history(call, bot):
        client_id = CallDataParser.get_client_id(call.data)
        path_to_dialogue_file = f'{DIR_FOR_SAVE_DIALOGS}/{client_id}/dialogue.log'
        if file_check(path_to_dialogue_file):
            send_document_to_telegram(bot, call.from_user.id, path_to_dialogue_file, caption='История диалога',
                                      visible_file_name='Диалог.log')
        else:
            bot.send_message(call.from_user.id, 'История диалога пуста')

    @staticmethod
    def file_types(call, bot):
        client_id = CallDataParser.get_client_id(call.data)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id, text='Выберите раздел',
                              reply_markup=OperatorKeyboards.types_documents(client_id))

    @staticmethod
    def __show_client_files_in_dialogue(call, bot, dir_path, client_id):
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
                              reply_markup=OperatorKeyboards.client_files(dict_path_to_files, in_dialogue=True))

    @staticmethod
    def technical_tasks_in_dialogue(call, bot):
        user_id = redis_cache.get_first_client_from_queue()
        OperatorCallbackHandlers.__show_client_files_in_dialogue(call, bot, DIR_FOR_TECHNICAL_TASKS, user_id)

    @staticmethod
    def commercial_offers_in_dialogue(call, bot):
        user_id = redis_cache.get_first_client_from_queue()
        OperatorCallbackHandlers.__show_client_files_in_dialogue(call, bot, DIR_FOR_COMMERCIAL_OFFERS, user_id)

    @staticmethod
    def reports_in_dialogue(call, bot):
        user_id = redis_cache.get_first_client_from_queue()
        OperatorCallbackHandlers.__show_client_files_in_dialogue(call, bot, DIR_FOR_REPORTS, user_id)

    @staticmethod
    def other_documents_in_dialogue(call, bot):
        user_id = redis_cache.get_first_client_from_queue()
        OperatorCallbackHandlers.__show_client_files_in_dialogue(call, bot, DIR_FOR_OTHER_FILES, user_id)

    @staticmethod
    def __show_client_files(call, bot, dir_path, client_id):
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
                              reply_markup=OperatorKeyboards.client_files(dict_path_to_files))

    @staticmethod
    def client_technical_tasks(call, bot):
        client_id = CallDataParser.get_client_id(call.data)
        OperatorCallbackHandlers.__show_client_files(call, bot, DIR_FOR_TECHNICAL_TASKS, client_id)

    @staticmethod
    def client_commercial_offers(call, bot):
        client_id = CallDataParser.get_client_id(call.data)
        OperatorCallbackHandlers.__show_client_files(call, bot, DIR_FOR_COMMERCIAL_OFFERS, client_id)

    @staticmethod
    def client_reports(call, bot):
        client_id = CallDataParser.get_client_id(call.data)
        OperatorCallbackHandlers.__show_client_files(call, bot, DIR_FOR_REPORTS, client_id)

    @staticmethod
    def client_other_documents(call, bot):
        client_id = CallDataParser.get_client_id(call.data)
        OperatorCallbackHandlers.__show_client_files(call, bot, DIR_FOR_OTHER_FILES, client_id)

    @staticmethod
    def enter_menu_in_dialogue(call, bot):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Меню взаимодействия с клиентом', reply_markup=OperatorKeyboards.menu_in_dialogue())

    @staticmethod
    def upload_file_in_dialogue(call, bot):
        directory = redis_cache.get_selected_directory(call.from_user.id)
        logger.info(f'Выбрана директория для загрузки файла: {directory}')
        dir_to_state = {
            DIR_FOR_TECHNICAL_TASKS: MyStates.get_technical_task_file_in_dialogue,
            DIR_FOR_COMMERCIAL_OFFERS: MyStates.get_commercial_offer_file_in_dialogue,
            DIR_FOR_REPORTS: MyStates.get_report_file_in_dialogue,
            DIR_FOR_OTHER_FILES: MyStates.get_other_file_in_dialogue
        }
        message = 'Отправьте файл'
        state = dir_to_state.get(directory)
        bot.send_message(call.from_user.id, message)
        bot.set_state(call.from_user.id, state, call.from_user.id)

    @staticmethod
    def upload_file(call, bot):
        directory = redis_cache.get_selected_directory(call.from_user.id)
        logger.info(f'Выбрана директория для загрузки файла: {directory}')
        dir_to_state = {
            DIR_FOR_TECHNICAL_TASKS: MyStates.get_technical_task_file,
            DIR_FOR_COMMERCIAL_OFFERS: MyStates.get_commercial_offer_file,
            DIR_FOR_REPORTS: MyStates.get_report_file,
            DIR_FOR_OTHER_FILES: MyStates.get_other_file
        }
        message = 'Отправьте файл'
        state = dir_to_state.get(directory)
        bot.send_message(call.from_user.id, message)
        bot.set_state(call.from_user.id, state, call.from_user.id)

    @staticmethod
    def queue(call, bot):
        client_id = CallDataParser.get_client_id(call.data)
        redis_cache.move_client_to_first_place_in_queue(client_id)
        bot.send_message(call.message.chat.id, 'Вступить в диалог с клиентом ?',
                         reply_markup=OperatorKeyboards.customer_information(client_id))

    @staticmethod
    def change_question(call, bot):
        question_id = CallDataParser.get_question_id(call.data)
        question, default_answers = get_question_and_answers_from_db(question_id)
        if not default_answers:
            default_answers = 'Нет вариантов ответов'
        bot.set_state(call.from_user.id, OperatorStates.change_question)
        bot.add_data(call.from_user.id, question_id_for_change=question_id)
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, f'Вопрос: {question}?\n\nОтветы:\n{default_answers}\n'
                                               f'Впишите вопрос и варианты ответов через |\n'
                                               f'ВОПРОС || ОТВЕТ1| ОТВЕТ2| ОТВЕТ3\n\n'
                                               f'Пример:\n'
                                               f'Каков рейтинг компании в России || 11| 34| Не знаю',
                         reply_markup=OperatorKeyboards.change_question())

    @staticmethod
    def add_question(call, bot):
        bot.send_message(call.message.chat.id, 'Введите новое название раздела')
