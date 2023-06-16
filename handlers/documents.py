import logging
import random
import time

from config import OPERATOR_ID
from handlers.keyboards import keyboard_for_clients_in_brief
from services.db_data import get_user_data_from_db, get_user_list_of_questions_informal_and_answers, \
    delete_user_answers_in_section, update_info_about_user_docs_in_db
from services.file_handler import generate_technical_task_file
from services.redis_db import redis_cache
from services.string_parser import CallDataParser

logger = logging.getLogger(__name__)


def callback_for_registration_technical_exercise(call, bot):
    logger.info(f'callback_technical_exercise: пришел callback: {call.data}')
    client_id = call.from_user.id
    directory, sub_dir, section = CallDataParser.get_directory_sub_direction_section(call.data)
    all_emoji = ['🎲', '🎯', '🏀', '⚽', '🎳', '🎰']
    bot.send_dice(client_id, emoji=random.choice(all_emoji), timeout=5)
    bot.send_chat_action(client_id, action="upload_document", timeout=3)
    bot.send_message(client_id, 'Ваш файл формируется, а пока, давайте сыграем 😊')
    time.sleep(3)

    bot.send_message(client_id, 'Хотите чтобы мы оценили ваш проект?',
                     reply_markup=keyboard_for_clients_in_brief())

    user_data = get_user_data_from_db(client_id)
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
    time.sleep(1)
    send_document_to_telegram(bot, client_id, document_path, caption="Ваш файл",
                              visible_file_name=f'{user_data["company"]}.docx')


def callback_get_file_for_client(call, bot):
    bot.delete_message(call.message.chat.id, call.message.id)
    client_id = call.from_user.id
    key_for_path = CallDataParser.get_key_for_path(call.data)
    path_to_file = redis_cache.get_path_for_download_file_by_key(client_id, key_for_path)
    logger.info(f'Клиент {client_id} запросил файл: {path_to_file}')
    user_data = get_user_data_from_db(client_id)
    file_type = CallDataParser.get_file_type(path_to_file)
    send_document_to_telegram(bot, client_id, path_to_file, caption="Ваш файл",
                              visible_file_name=f'{user_data["company"]}.{file_type}')


def get_file_path_and_user_data(call, client_id):
    key_for_path = CallDataParser.get_key_for_path(call.data)
    path_to_file = redis_cache.get_path_for_download_file_by_key(client_id, key_for_path)
    logger.info(f'Оператор {call.from_user.id} запросил файл клиента: {path_to_file}')
    user_data = get_user_data_from_db(client_id)
    file_type = CallDataParser.get_file_type(path_to_file)
    caption = f"Файл пользователя:\n{user_data['name']}\n" \
              f"Username: {user_data['tg_username']}n" \
              f"Компания: {user_data['company']}\n" \
              f"Телефон: {user_data['phone']}\n" \
              f"Website: {user_data['website']}\n"
    visible_file_name = f'{user_data["company"]}.{file_type}'
    return path_to_file, caption, visible_file_name


def callback_get_file_for_operator_in_dialogue(call, bot):
    client_id = redis_cache.get_first_client_from_queue()
    path_to_file, caption, visible_file_name = get_file_path_and_user_data(call, client_id)
    send_document_to_telegram(bot, OPERATOR_ID, path_to_file, caption=caption, visible_file_name=visible_file_name)


def callback_get_file_for_operator(call, bot):
    client_id = redis_cache.get_user_to_display_information()
    path_to_file, caption, visible_file_name = get_file_path_and_user_data(call, client_id)
    send_document_to_telegram(bot, OPERATOR_ID, path_to_file, caption=caption, visible_file_name=visible_file_name)


def send_document_to_telegram(bot, addressee_id: int, document_path, caption, visible_file_name):
    with open(document_path, 'rb') as file:
        bot.send_document(chat_id=addressee_id, document=file,
                          caption=caption,
                          disable_content_type_detection=True,
                          visible_file_name=visible_file_name)
