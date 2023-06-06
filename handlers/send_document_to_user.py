import logging
import time

from config import OPERATOR_ID, DIR_FOR_TECHNICAL_TASKS
from handlers.keyboards import keyboard_for_clients_in_brief
from services.db_data import get_user_data_from_db, get_user_list_of_questions_informal_and_answers, \
    delete_user_answers_in_section, update_info_about_user_docs_in_db
from services.files import generate_technical_task_file, extract_filename
from services.redis_db import set_last_file_path, get_first_client_from_queue

logger = logging.getLogger(__name__)


def callback_for_registration_technical_exercise(call, bot):
    logger.info(f'callback_technical_exercise: пришел callback: {call.data}')
    user_id = call.from_user.id
    directory = call.data.split('_')[1].split('|')[0]
    section = call.data.split('_')[1].split('|')[-1]

    bot.send_dice(user_id, emoji='🏀', timeout=5)
    bot.send_chat_action(user_id, action="upload_document", timeout=3)
    bot.send_message(user_id, 'Ваш файл формируется, а пока, давайте сыграем 😊')
    time.sleep(3)

    bot.send_message(user_id, 'Хотите чтобы мы оценили ваш проект?',
                     reply_markup=keyboard_for_clients_in_brief())

    user_data = get_user_data_from_db(user_id)
    questions, answers = get_user_list_of_questions_informal_and_answers(user_id, directory, section)
    bot.delete_message(call.message.chat.id, call.message.id)
    delete_user_answers_in_section(call.from_user.id, directory, section)
    document_path = generate_technical_task_file(user_id=user_id,
                                                 section=section,
                                                 client_name=user_data['name'],
                                                 company=user_data['company'],
                                                 phone=user_data['phone'],
                                                 website=user_data['website'],
                                                 list_of_questions=questions,
                                                 answers=answers)
    set_last_file_path(user_id, document_path)
    update_info_about_user_docs_in_db(user_id, documents=True)
    time.sleep(1)
    send_document_to_client(bot, user_data, document_path)


def callback_for_send_file(call, bot):
    bot.delete_message(call.message.chat.id, call.message.id)
    user_id = call.from_user.id
    if user_id == OPERATOR_ID:
        user_id = get_first_client_from_queue()
        filename = extract_filename(call.data)
        path_to_file = f'{DIR_FOR_TECHNICAL_TASKS}/{user_id}/{filename}'
        user_data = get_user_data_from_db(user_id)
        send_document_to_operator(bot, user_data, path_to_file)
        return
    filename = extract_filename(call.data)
    path_to_file = f'{DIR_FOR_TECHNICAL_TASKS}/{user_id}/{filename}'
    user_data = get_user_data_from_db(user_id)
    send_document_to_client(bot, user_data, path_to_file)


def send_document_to_client(bot, user_data, document_path):
    try:
        with open(document_path, 'rb') as file:
            bot.send_document(chat_id=user_data['id'], document=file,
                              caption=f"Ваше сформированное техническое задание",
                              disable_content_type_detection=True,
                              visible_file_name=f'Тех.задание компании {user_data["company"]}.docx')
    except FileNotFoundError:
        logger.error('Файл не найден')
        bot.send_message(user_data['id'], 'К сожалению ваш файл не найден в нашей базе данных, свяжитесь с оператором')


def send_document_to_operator(bot, user_data, document_path):
    try:
        with open(document_path, 'rb') as file:
            bot.send_document(chat_id=OPERATOR_ID, document=file,
                              caption=f"Техническое задание от пользователя:\n{user_data['name']}\n"
                                      f"Username: {user_data['tg_username']}\n"
                                      f"Компания: {user_data['company']}\n"
                                      f"Телефон: {user_data['phone']}\n"
                                      f"Website: {user_data['website']}\n",
                              disable_content_type_detection=True,
                              visible_file_name=f'Тех.задание компании {user_data["company"]}.docx')
    except FileNotFoundError:
        logger.error('Файл не найден')
        bot.send_message(user_data['id'], 'К сожалению ваш файл не найден в нашей базе данных, свяжитесь с оператором')
