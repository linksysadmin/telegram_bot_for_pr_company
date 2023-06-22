import logging
import random
import time

from telebot import apihelper

from config import OPERATOR_ID, DIR_FOR_OTHER_FILES, DIR_FOR_REPORTS, DIR_FOR_COMMERCIAL_OFFERS, \
    DIR_FOR_TECHNICAL_TASKS, DIR_FOR_SAVE_DIALOGS
from handlers.keyboards import OperatorKeyboards, ClientKeyboards, GeneralKeyboards
from handlers.text_messages import TEXT_MESSAGES
from services.db_data import get_sections_from_db, get_sub_directions, get_users_data, \
    get_question_and_answers_from_db, get_user_answer, update_user_status, update_info_about_user_docs_in_db, \
    delete_user_answers_in_section, get_user_list_of_questions_informal_and_answers
from services.file_handler import find_user_documents, get_list_of_clients_dialogue_files, file_check, \
    generate_technical_task_file
from services.redis_db import redis_cache
from services.states import MyStates, OperatorStates
from services.status import ClientStatus
from services.string_parser import CallDataParser

logger = logging.getLogger(__name__)


class GeneralCallbacks:

    @staticmethod
    def send_document_to_telegram(bot, addressee_id: int, document_path, caption, visible_file_name):
        with open(document_path, 'rb') as file:
            bot.send_document(chat_id=addressee_id, document=file,
                              caption=caption,
                              disable_content_type_detection=True,
                              visible_file_name=visible_file_name)

    @staticmethod
    def call_enter_menu(call, bot):
        client_id = call.from_user.id
        user_data = get_users_data(client_id)
        reply_markup = GeneralKeyboards.enter_menu(doc=False)
        if user_data['documents']:
            reply_markup = GeneralKeyboards.enter_menu(doc=True)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['start'].format(username=user_data['name'],
                                                                 company=user_data['company']),
                                                                 reply_markup=reply_markup)

    @staticmethod
    def call_briefing(call, bot):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'], reply_markup=GeneralKeyboards.directions())

    @staticmethod
    def call_directory(call, bot):
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
    def call_sub_directory(call, bot):
        path = call.data
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=GeneralKeyboards.sections_from_subcategory(path))

    @staticmethod
    def call_section(call, bot):
        path = call.data
        keyboard = OperatorKeyboards.questions(call.from_user.id, path)
        if call.from_user.id != OPERATOR_ID:
            keyboard = ClientKeyboards.questions(call.from_user.id, path)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=keyboard)

    @staticmethod
    def call_cancel_to_directions(call, bot):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=GeneralKeyboards.directions())

    @staticmethod
    def call_question(call, bot):
        question_id = CallDataParser.get_question_id(call.data)
        if question_id <= redis_cache.get_max_question_id(call.from_user.id):
            next_callback = CallDataParser.get_next_callback_for_question(question_id)
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

class ClientCallbacks:

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
    def call_file_types(call, bot):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Выберите тип файла',
                              reply_markup=ClientKeyboards.types_of_files())

    @staticmethod
    def call_technical_tasks(call, bot):
        ClientCallbacks.__show_files_for_client(call, bot, DIR_FOR_TECHNICAL_TASKS)

    @staticmethod
    def call_commercial_offer(call, bot):
        ClientCallbacks.__show_files_for_client(call, bot, DIR_FOR_COMMERCIAL_OFFERS)

    @staticmethod
    def call_reports(call, bot):
        ClientCallbacks.__show_files_for_client(call, bot, DIR_FOR_REPORTS)

    @staticmethod
    def call_documents(call, bot):
        ClientCallbacks.__show_files_for_client(call, bot, DIR_FOR_OTHER_FILES)

    @staticmethod
    def call_chat_with_operator(call, bot):
        bot.send_contact(call.message.chat.id, phone_number='+74950188868', first_name='Оператор Mr.Эйч')
        bot.send_message(call.message.chat.id, TEXT_MESSAGES['chat_with_operator'])

    @staticmethod
    def call_blog(call, bot):
        pass


    @staticmethod
    def call_change_answer(call, bot):
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.set_state(call.from_user.id, MyStates.answer_to_question, call.from_user.id)
        question_id = redis_cache.get_question_id(call.from_user.id)
        question, answers = get_question_and_answers_from_db(question_id)
        bot.send_message(call.message.chat.id, f'❓{question}?\n\nНапишите ответ и нажмите "✅ Отправить ответ"',
                         reply_markup=ClientKeyboards.answer(answers))

    @staticmethod
    def call_grade(call, bot):
        bot.delete_message(call.message.chat.id, call.message.id)
        match call.data:
            case 'client_grade_yes':
                user_data = get_users_data(call.from_user.id)
                path_to_file = redis_cache.get_last_file_path(call.from_user.id)
                caption = f"Техническое задание от пользователя:\n{user_data['name']}\n" \
                          f"Username: {user_data['tg_username']}\n" \
                          f"Компания: {user_data['company']}\n" \
                          f"Телефон: {user_data['phone']}\n" \
                          f"Website: {user_data['website']}\n"
                visible_file_name = f'Тех.задание компании {user_data["company"]}.docx'
                GeneralCallbacks.send_document_to_telegram(bot, OPERATOR_ID, path_to_file, caption=caption,
                                                           visible_file_name=visible_file_name)
                redis_cache.add_client_to_queue(call.from_user.id)
                bot.send_message(OPERATOR_ID, 'Начать чат с клиентом ?',
                                 reply_markup=OperatorKeyboards.customer_information(call.from_user.id))
            case 'client_grade_no':
                bot.send_message(call.message.chat.id, f'Хорошо, отличного дня!')

    # Диалог с оператором
    @staticmethod
    def call_instant_messaging_service(call, bot):
        client_id = call.from_user.id
        user_data = get_users_data(client_id)
        operator_state = redis_cache.get_operator_state()
        logger.info(f'Запрос от клиента {client_id} на диалог')
        match operator_state:
            case b'free' | None:
                redis_cache.set_operator_state(b'busy')
                logger.info(f'Перевод статуса оператора в "занят" (busy)')
                bot.send_message(OPERATOR_ID, f'💬Запрос на диалог!🧨\n\nКлиент: {user_data["name"]}\n'
                                              f'Компания: {user_data["company"]}\n'
                                              f'Телефон: {user_data["phone"]}',
                                 reply_markup=OperatorKeyboards.customer_information(client_id))
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

    @staticmethod
    def call_back_to_questions(call, bot):
        path = redis_cache.get_keyboard_for_questions(call.from_user.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=ClientKeyboards.questions(call.from_user.id, path))

    @staticmethod
    def call_generation_technical_exercise(call, bot):
        logger.info(f'Формирование и отправка файла')
        client_id = call.from_user.id
        directory, section = CallDataParser.get_directory_sub_direction_section(call.data)
        all_emoji = ['🎲', '🎯', '🏀', '⚽', '🎳', '🎰']
        bot.send_dice(client_id, emoji=random.choice(all_emoji), timeout=5)
        bot.send_chat_action(client_id, action="upload_document", timeout=3)
        bot.send_message(client_id, 'Ваш файл формируется, а пока, давайте сыграем 😊')
        time.sleep(3)

        bot.send_message(client_id, 'Хотите чтобы мы оценили ваш проект?',
                         reply_markup=ClientKeyboards.evaluation())

        user_data = get_users_data(client_id)
        questions, answers = get_user_list_of_questions_informal_and_answers(client_id, directory, section)
        bot.delete_message(call.message.chat.id, call.message.id)
        delete_user_answers_in_section(call.from_user.id, directory, section)
        document_path = generate_technical_task_file(user_id=client_id,
                                                     section=section,
                                                     client_name=user_data['name'],
                                                     company=user_data['company'],
                                                     phone=user_data['phone'],
                                                     website=user_data['website'],
                                                     list_of_questions=questions,
                                                     answers=answers)
        redis_cache.set_last_file_path(client_id, document_path)
        update_info_about_user_docs_in_db(client_id, documents=True)
        update_user_status(client_id, ClientStatus.tech_task)
        time.sleep(1)
        GeneralCallbacks.send_document_to_telegram(bot, client_id, document_path, caption="Ваш файл",
                                                   visible_file_name=f'{user_data["company"]}.docx')

    @staticmethod
    def call_get_file(call, bot):
        bot.delete_message(call.message.chat.id, call.message.id)
        client_id = call.from_user.id
        key_for_path = CallDataParser.get_key_for_path(call.data)
        path_to_file = redis_cache.get_path_for_download_file_by_key(client_id, key_for_path)
        logger.info(f'Клиент {client_id} запросил файл: {path_to_file}')
        user_data = get_users_data(client_id)
        file_type = CallDataParser.get_file_type(path_to_file)
        GeneralCallbacks.send_document_to_telegram(bot, client_id, path_to_file, caption="Ваш файл",
                                                   visible_file_name=f'{user_data["company"]}.{file_type}')


class GamesCallbacks:
    __karatekido2 = 'karatekido2'
    __qubo = 'qubo'
    __basketboyrush = 'basketboyrush'
    __spikyfish3 = 'spikyfish3'
    __basketboy = 'basketboy'
    __gravityninjaemeraldcity = 'gravityninjaemeraldcity'
    __keepitup = 'keepitup'

    @staticmethod
    def call_choose_game(call, bot):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Выберите игру:',
                              reply_markup=GeneralKeyboards.games())

    @staticmethod
    def call_send_game_1(call, bot):
        try:
            bot.send_game(call.from_user.id, game_short_name=GamesCallbacks.__karatekido2)
        except apihelper.ApiTelegramException:
            logger.error('Игра не зарегистрирована в данном боте, либо указано неверное название игры')

    @staticmethod
    def call_send_game_2(call, bot):
        try:
            bot.send_game(call.from_user.id, game_short_name=GamesCallbacks.__qubo)
        except apihelper.ApiTelegramException:
            logger.error('Игра не зарегистрирована в данном боте, либо указано неверное название игры')

    @staticmethod
    def call_send_game_3(call, bot):
        try:
            bot.send_game(call.from_user.id, game_short_name=GamesCallbacks.__basketboyrush)
        except apihelper.ApiTelegramException:
            logger.error('Игра не зарегистрирована в данном боте, либо указано неверное название игры')

    @staticmethod
    def call_send_game_4(call, bot):
        try:
            bot.send_game(call.from_user.id, game_short_name=GamesCallbacks.__spikyfish3)
        except apihelper.ApiTelegramException:
            logger.error('Игра не зарегистрирована в данном боте, либо указано неверное название игры')

    @staticmethod
    def call_send_game_5(call, bot):
        try:
            bot.send_game(call.from_user.id, game_short_name=GamesCallbacks.__basketboy)
        except apihelper.ApiTelegramException:
            logger.error('Игра не зарегистрирована в данном боте, либо указано неверное название игры')

    @staticmethod
    def call_send_game_6(call, bot):
        try:
            bot.send_game(call.from_user.id, game_short_name=GamesCallbacks.__gravityninjaemeraldcity)
        except apihelper.ApiTelegramException:
            logger.error('Игра не зарегистрирована в данном боте, либо указано неверное название игры')

    @staticmethod
    def call_send_game_7(call, bot):
        try:
            bot.send_game(call.from_user.id, game_short_name=GamesCallbacks.__keepitup)
        except apihelper.ApiTelegramException:
            logger.error('Игра не зарегистрирована в данном боте, либо указано неверное название игры')

    @staticmethod
    def call_game_1(call, bot):
        bot.answer_callback_query(call.id,
                                  url='https://prizes.gamee.com/game-bot/karatekid2-48c08d62bc7684c7c0020cac16b8c81d12073454')

    @staticmethod
    def call_game_2(call, bot):
        bot.answer_callback_query(call.id,
                                  url='https://prizes.gamee.com/game-bot/u0yXP5o-f4def4e95fbc17585cdcc1465e38469528a195bd')

    @staticmethod
    def call_game_3(call, bot):
        bot.answer_callback_query(call.id,
                                  url='https://prizes.gamee.com/game-bot/qxpwxJTh7-cd8fea3257629021cc34acaa33799c7386288a00')

    @staticmethod
    def call_game_4(call, bot):
        bot.answer_callback_query(call.id,
                                  url='https://prizes.gamee.com/game-bot/zcvFFeQ0t-5cce2e3225abc237098cd630f4e1a73d65a1afce')

    @staticmethod
    def call_game_5(call, bot):
        bot.answer_callback_query(call.id,
                                  url='https://prizes.gamee.com/game-bot/DwVcZZnbP-abd015ce95140f9779ee25dfcb67839c1a5163ec')

    @staticmethod
    def call_game_6(call, bot):
        bot.answer_callback_query(call.id,
                                  url='https://prizes.gamee.com/game-bot/gravityninjaemeraldcity-d52b84dc3d0cc986aee23b1ea66c49be28da32e5')

    @staticmethod
    def call_game_7(call, bot):
        bot.answer_callback_query(call.id,
                                  url='https://prizes.gamee.com/game-bot/a3pyHGoadz-c70a910a834b64c83d52e3ef7383882a690c43c8')


class OperatorCallbacks:

    @staticmethod
    def __get_file_path_caption_and_filename(call, client_id):
        key_for_path = CallDataParser.get_key_for_path(call.data)
        path_to_file = redis_cache.get_path_for_download_file_by_key(client_id, key_for_path)
        logger.info(f'Оператор {call.from_user.id} запросил файл клиента: {path_to_file}')
        user_data = get_users_data(client_id)
        file_type = CallDataParser.get_file_type(path_to_file)
        caption = f"Файл пользователя:\n{user_data['name']}\n" \
                  f"Username: {user_data['tg_username']}\n" \
                  f"Компания: {user_data['company']}\n" \
                  f"Телефон: {user_data['phone']}\n" \
                  f"Website: {user_data['website']}\n"
        visible_file_name = f'{user_data["company"]}.{file_type}'
        return path_to_file, caption, visible_file_name

    @staticmethod
    def call_requests(call, bot):
        queue_of_clients = redis_cache.get_queue_of_clients()
        text = 'Запросы от пользователей'
        if not queue_of_clients:
            text = 'Запросов от пользователей нет'
        callback_data_prefix = 'queue'
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text, reply_markup=OperatorKeyboards.clients(queue_of_clients, callback_data_prefix))

    @staticmethod
    def call_clients(call, bot):
        list_of_clients = get_list_of_clients_dialogue_files()
        text = 'Выберите клиента:'
        callback_data_prefix = 'client|info'
        if not list_of_clients:
            text = 'Нет доступных диалогов с клиентам'
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text, reply_markup=OperatorKeyboards.clients(list_of_clients, callback_data_prefix))

    @staticmethod
    def call_tasks(call, bot):
        pass

    @staticmethod
    def call_settings(call, bot):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Здесь вы можете изменить или добавить вопросы, секции и разделы',
                              reply_markup=OperatorKeyboards.settings())

    @staticmethod
    def call_enter_menu(call, bot):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['start_for_operator'], reply_markup=OperatorKeyboards.enter_menu())

    @staticmethod
    def call_back_to_questions(call, bot):
        path = redis_cache.get_keyboard_for_questions(call.from_user.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=OperatorKeyboards.questions(call.from_user.id, path))

    @staticmethod
    def call_get_dialogue_history(call, bot):
        client_id = CallDataParser.get_client_id(call.data)
        path_to_dialogue_file = f'{DIR_FOR_SAVE_DIALOGS}/{client_id}/dialogue.log'
        if file_check(path_to_dialogue_file):
            GeneralCallbacks.send_document_to_telegram(bot, call.from_user.id, path_to_dialogue_file,
                                                       caption='История диалога',
                                                       visible_file_name='Диалог.log')
        else:
            bot.send_message(call.from_user.id, 'История диалога пуста')

    @staticmethod
    def call_file_types(call, bot):
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
    def call_technical_tasks_in_dialogue(call, bot):
        user_id = redis_cache.get_first_client_from_queue()
        OperatorCallbacks.__show_client_files_in_dialogue(call, bot, DIR_FOR_TECHNICAL_TASKS, user_id)

    @staticmethod
    def call_commercial_offers_in_dialogue(call, bot):
        user_id = redis_cache.get_first_client_from_queue()
        OperatorCallbacks.__show_client_files_in_dialogue(call, bot, DIR_FOR_COMMERCIAL_OFFERS, user_id)

    @staticmethod
    def call_reports_in_dialogue(call, bot):
        user_id = redis_cache.get_first_client_from_queue()
        OperatorCallbacks.__show_client_files_in_dialogue(call, bot, DIR_FOR_REPORTS, user_id)

    @staticmethod
    def call_other_documents_in_dialogue(call, bot):
        user_id = redis_cache.get_first_client_from_queue()
        OperatorCallbacks.__show_client_files_in_dialogue(call, bot, DIR_FOR_OTHER_FILES, user_id)

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
    def call_client_technical_tasks(call, bot):
        client_id = CallDataParser.get_client_id(call.data)
        OperatorCallbacks.__show_client_files(call, bot, DIR_FOR_TECHNICAL_TASKS, client_id)

    @staticmethod
    def call_client_commercial_offers(call, bot):
        client_id = CallDataParser.get_client_id(call.data)
        OperatorCallbacks.__show_client_files(call, bot, DIR_FOR_COMMERCIAL_OFFERS, client_id)

    @staticmethod
    def call_client_reports(call, bot):
        client_id = CallDataParser.get_client_id(call.data)
        OperatorCallbacks.__show_client_files(call, bot, DIR_FOR_REPORTS, client_id)

    @staticmethod
    def call_client_other_documents(call, bot):
        client_id = CallDataParser.get_client_id(call.data)
        OperatorCallbacks.__show_client_files(call, bot, DIR_FOR_OTHER_FILES, client_id)

    @staticmethod
    def call_enter_menu_in_dialogue(call, bot):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Меню взаимодействия с клиентом', reply_markup=OperatorKeyboards.menu_in_dialogue())

    @staticmethod
    def call_upload_file_in_dialogue(call, bot):
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
    def call_upload_file(call, bot):
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
    def call_queue(call, bot):
        client_id = CallDataParser.get_client_id(call.data)
        redis_cache.move_client_to_first_place_in_queue(client_id)
        bot.send_message(call.message.chat.id, 'Вступить в диалог с клиентом ?',
                         reply_markup=OperatorKeyboards.customer_information(client_id))

    @staticmethod
    def call_change_question(call, bot):
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
    def call_add_question(call, bot):
        bot.send_message(call.message.chat.id, 'Введите новое название раздела')

    # Диалог с клиентом
    @staticmethod
    def call_enter_into_a_dialog(call, bot):
        operator = call.from_user.id
        client_id = CallDataParser.get_client_id(call.data)
        redis_cache.move_client_to_first_place_in_queue(client_id)
        redis_cache.set_operator_state(b'busy')
        logger.info(f'Оператор вступил в диалог с клиентом {client_id}')
        bot.set_state(client_id, MyStates.dialogue_with_operator)
        bot.set_state(operator, MyStates.dialogue_with_client)
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(client_id, 'Вы вступили в диалог с оператором\n')
        bot.send_message(operator, 'Вы вступили в диалог с клиентом\nНапишите ему:',
                         reply_markup=OperatorKeyboards.menu_in_dialogue())
        logger.info(
            f'Состояние клиента - {bot.get_state(client_id)}, оператора - {bot.get_state(operator)}')

    @staticmethod
    def call_client_info(call, bot):
        operator = call.from_user.id
        client_id = CallDataParser.get_client_id(call.data)
        bot.send_message(operator, 'Выберите действие',
                         reply_markup=OperatorKeyboards.customer_information(client_id))

    @staticmethod
    def call_left_dialog(call, bot):
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
        bot.send_message(OPERATOR_ID, f'💬Запрос на диалог!🧨\n\nОт пользователя:\nID: {next_client}\n'
                         , reply_markup=OperatorKeyboards.customer_information(next_client))

    @staticmethod
    def call_get_file_in_dialogue(call, bot):
        client_id = redis_cache.get_first_client_from_queue()
        path_to_file, caption, visible_file_name = OperatorCallbacks.__get_file_path_caption_and_filename(call,
                                                                                                          client_id)
        GeneralCallbacks.send_document_to_telegram(bot, OPERATOR_ID, path_to_file, caption=caption,
                                                   visible_file_name=visible_file_name)

    @staticmethod
    def call_get_file(call, bot):
        client_id = redis_cache.get_user_to_display_information()
        path_to_file, caption, visible_file_name = OperatorCallbacks.__get_file_path_caption_and_filename(call,
                                                                                                          client_id)
        GeneralCallbacks.send_document_to_telegram(bot, OPERATOR_ID, path_to_file, caption=caption,
                                                   visible_file_name=visible_file_name)
