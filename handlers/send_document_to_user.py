import logging
import time

from config import OPERATOR_ID
from services.db_data import get_user_data_from_db, get_user_list_of_questions_informal_and_answers, \
    delete_user_answers_in_section, update_info_about_user_docs_in_db
from services.files import generate_technical_task_file

logger = logging.getLogger(__name__)


def callback_technical_exercise(call, bot):
    logger.info(f'callback_technical_exercise: пришел callback: {call.data}')
    user_id = call.from_user.id
    directory = call.data.split('_')[1].split('|')[0]
    section = call.data.split('_')[1].split('|')[-1]

    bot.send_dice(user_id, emoji='🏀', timeout=5)
    bot.send_message(user_id, 'Ваш файл формируется')
    bot.send_chat_action(user_id, action="upload_document", timeout=5)
    time.sleep(3)

    user_data = get_user_data_from_db(user_id)
    list_of_questions_informal = get_user_list_of_questions_informal_and_answers(user_id, directory, section)
    bot.delete_message(call.message.chat.id, call.message.id)
    delete_user_answers_in_section(call.from_user.id, directory, section)
    document_path = generate_technical_task_file(user_id=user_id,
                                                 section=section,
                                                 client_name=user_data['name'],
                                                 company=user_data['company'],
                                                 phone=user_data['phone'],
                                                 website=user_data['website'],
                                                 list_of_questions=[question[0] for question in
                                                                    list_of_questions_informal],
                                                 answers=[answer[1] for answer in list_of_questions_informal])
    update_info_about_user_docs_in_db(user_id, tech_doc=True)
    time.sleep(3)
    send_document_to_telegram(bot, user_id, user_data, document_path, operator=True)


def send_document_to_telegram(bot, user_id, user_data, document_path, operator: bool = None):
    with open(document_path, 'rb') as file:
        bot.send_document(chat_id=user_id, document=file,
                          caption=f"Ваше сформированное техническое задание",
                          disable_content_type_detection=True)
    if operator:
        with open(document_path, 'rb') as file:
            bot.send_document(chat_id=OPERATOR_ID, document=file,
                              caption=f"Техническое задание от пользователя:\n{user_data['name']}\n"
                                      f"Username: {user_data['tg_username']}\n"
                                      f"Компания: {user_data['company']}\n"
                                      f"Телефон: {user_data['phone']}\n"
                                      f"Website: {user_data['website']}\n",
                              disable_content_type_detection=True)
