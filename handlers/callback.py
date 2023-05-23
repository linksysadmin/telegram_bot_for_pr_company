import logging
import time

from config import BASE_DIR, OPERATOR_ID
from handlers.keyboards import keyboard_for_briefings, \
    keyboard_for_questions, keyboard_for_direction, keyboard_for_sub_direction, keyboard_enter_menu_for_clients, \
    keyboard_for_answer, keyboard_for_change_answer, keyboard_for_reference_and_commercial_offer, \
    keyboard_for_commercial_offer, keyboard_for_terms_of_reference
from services.db_data import get_data_questions, get_question_and_answers_from_db, \
    get_user_answer, get_user_data_from_db, get_user_list_of_questions_informal_and_answers, get_directories, \
    delete_user_answers_in_section
from services.document_generation import generate_doc_of_technical_task
from services.redis_db import set_question_id_in_redis, get_question_id_from_redis, set_next_question_callback_in_redis, \
    set_max_question_id_in_redis, get_max_question_id_in_redis, get_keyboard_for_questions_from_redis
from services.states import MyStates
from handlers.text_messages import TEXT_MESSAGES

logger = logging.getLogger(__name__)


def callback_scenario(call, bot):
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(call.message.chat.id, TEXT_MESSAGES['menu'], reply_markup=keyboard_for_briefings())
    logger.info(f'Состояние пользователя - {bot.get_state(call.message.chat.id, call.from_user.id)}')


def callback_terms_of_reference_and_commercial_offer(call, bot):
    logger.info(f'callback_terms_of_reference_and_commercial_offer: пришел callback: {call.data}')
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Выберите какой файл вы хотите получить:',
                          reply_markup=keyboard_for_reference_and_commercial_offer())


def callback_terms_of_reference(call, bot):
    logger.info(f'callback_terms_of_reference: пришел callback: {call.data}')
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Выберите какой файл вы хотите получить:',
                          reply_markup=keyboard_for_terms_of_reference(call.from_user_id))


def callback_commercial_offer(call, bot):
    logger.info(f'callback_terms_of_reference: пришел callback: {call.data}')
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Выберите какой файл вы хотите получить:',
                          reply_markup=keyboard_for_commercial_offer(call.from_user_id))


def callback_technical_exercise(call, bot):
    logger.info(f'callback_technical_exercise: пришел callback: {call.data}')
    bot.send_chat_action(call.from_user.id, action="upload_document")
    bot.send_dice(call.from_user.id, emoji='🎲', timeout=4)
    directory = call.data.split('_')[1].split('|')[0]
    section = call.data.split('_')[1].split('|')[-1]
    bot.send_message(call.message.chat.id, 'Ваш файл формируется')
    user_data = get_user_data_from_db(call.from_user.id)
    list_of_questions_informal = get_user_list_of_questions_informal_and_answers(call.from_user.id, directory, section)
    delete_user_answers_in_section(call.from_user.id, directory, section)
    generate_doc_of_technical_task(direction=directory,
                                   client_name=user_data['name'],
                                   company=user_data['company'],
                                   phone=user_data['phone'],
                                   website=user_data['website'],
                                   list_of_questions=[question[0] for question in list_of_questions_informal],
                                   answers=[answer[1] for answer in list_of_questions_informal])

    time.sleep(3)
    with open(f'{BASE_DIR}/static/documents/technical_tasks/{user_data["company"]}.docx', 'rb') as file:
        bot.send_document(chat_id=OPERATOR_ID, document=file,
                          caption=f"Техническое задание от пользователя:\n{user_data['name']}\n"
                                  f"Компания: {user_data['company']}\n"
                                  f"Телефон: {user_data['phone']}\n"
                                  f"Website: {user_data['website']}\n",
                          disable_content_type_detection=True)
    with open(f'{BASE_DIR}/static/documents/technical_tasks/{user_data["company"]}.docx', 'rb') as file:
        bot.send_document(chat_id=call.from_user.id, document=file,
                          caption=f"Ваше сформированное техническое задание",
                          disable_content_type_detection=True)
    bot.delete_message(call.message.chat.id, call.message.id)


def callback_chat_with_operator(call, bot):
    bot.send_message(call.message.chat.id, TEXT_MESSAGES['chat_with_operator'])
    logger.info(f'Состояние пользователя - {bot.get_state(call.message.chat.id, call.from_user.id)}')


def callback_upload_report(call, bot):
    pass
    # bot.delete_message(call.message.chat.id, call.message.id)
    # bot.send_message(call.message.chat.id, TEXT_MESSAGES['menu'], reply_markup=keyboard_for_scenario())
    # logger.info(f'Состояние пользователя - {bot.get_state(call.message.chat.id, call.from_user.id)}')


def callback_blog(call, bot):
    pass
    # bot.delete_message(call.message.chat.id, call.message.id)
    # bot.send_message(call.message.chat.id, TEXT_MESSAGES['blog'], reply_markup=keyboard_for_scenario())
    # logger.info(f'Состояние пользователя - {bot.get_state(call.message.chat.id, call.from_user.id)}')


def callback_query_for_scenario(call, bot):
    logger.info(f'callback_query_for_scenario: пришел callback: {call.data}')
    if call.data in get_directories():
        direction = call.data
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=keyboard_for_direction(direction=direction))
    elif call.data in [question[1] for question in get_data_questions()]:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['scenario'])


def callback_for_sub_direction(call, bot):
    logger.info(f'callback_for_sub_direction: пришел callback: {call.data}')
    path = call.data
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=keyboard_for_sub_direction(path))


def callback_for_section(call, bot):
    logger.info(f'callback_for_section: пришел callback: {call.data}')
    path = call.data
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=keyboard_for_questions(call.from_user.id, path))


def callback_section_from_subcategory(call, bot):
    logger.info(f'callback_section_from_subcategory: пришел callback: {call.data}')
    path = call.data
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=keyboard_for_questions(call.from_user.id, path))


def callback_cancel_from_inline_menu(call, bot):
    logger.info(f'callback_cancel_from_inline_menu: пришел callback: {call.data}')
    user_data = get_user_data_from_db(call.from_user.id)
    if user_data['tech_doc'] or user_data['cp_doc']:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['start'].format(username=user_data['name'],
                                                                 company=user_data['company']),
                              reply_markup=keyboard_enter_menu_for_clients(True))
        return
    else:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=TEXT_MESSAGES['start'].format(username=user_data['name'],
                                                                 company=user_data['company']),
                              reply_markup=keyboard_enter_menu_for_clients())


def callback_cancel_to_directions(call, bot):
    logger.info(f'callback_cancel_to_directions: пришел callback: {call.data}')
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=keyboard_for_briefings())


# def callback_cancel_to_sub_directions(call, bot):
#     logger.info(f'callback_cancel_to_sub_directions: пришел callback: {call.data}')
#     bot.edit_message_text(chat_id=call.message.chat.id,
#                           message_id=call.message.message_id,
#                           text=TEXT_MESSAGES['menu'],
#                           reply_markup=keyboard_for_sub_direction())


def callback_back_to_questions(call, bot):
    logger.info(f'callback_back_to_questions: пришел callback: {call.data}')
    path = get_keyboard_for_questions_from_redis(call.from_user.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=keyboard_for_questions(call.from_user.id, path))


def callback_for_change_answer(call, bot):
    logger.info(f'callback_for_change_answer: пришел callback: {call.data}')
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.set_state(call.from_user.id, MyStates.answer_to_question, call.from_user.id)
    question_id = get_question_id_from_redis(call.from_user.id)
    question, answers = get_question_and_answers_from_db(question_id)
    bot.send_message(call.message.chat.id, f'❓{question}?\n\nНапишите ответ и нажмите "✅ Отправить ответ"',
                     reply_markup=keyboard_for_answer(answers))


def callback_for_questions(call, bot):
    logger.info(f'callback_for_questions: пришел callback: {call.data}')
    question_id = call.data.split('_')[1]
    if int(question_id) <= get_max_question_id_in_redis(call.from_user.id):
        next_callback = f"{call.data.split('_')[0]}_{int(call.data.split('_')[1]) + 1}"
        set_question_id_in_redis(user=call.from_user.id, question_id=question_id)
        set_next_question_callback_in_redis(user=call.from_user.id, callback=next_callback)
    question, answers = get_question_and_answers_from_db(question_id)
    user_answer = get_user_answer(call.from_user.id, question_id)
    if bool(user_answer):
        user_answer = user_answer[0][0]
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'❓{question}?\n\nВаше ответ:{user_answer}',
                              reply_markup=keyboard_for_change_answer())
        return
    bot.set_state(call.from_user.id, MyStates.answer_to_question, call.from_user.id)
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(call.message.chat.id, f'❓{question}?\n\nНапишите ответ и нажмите "✅ Отправить ответ"',
                     reply_markup=keyboard_for_answer(answers))


def callback_for_registration(call, bot):
    logger.info(f'callback_for_registration: пришел callback: {call.data}')
    question_id = call.data.split('_')[1]
    set_question_id_in_redis(user=call.from_user.id, question_id=question_id)
    bot.set_state(call.from_user.id, MyStates.name, call.from_user.id)
    bot.add_data(call.from_user.id, call.message.chat.id, id_question=question_id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Укажите пожалуйста ваше имя:\n\n/cancel - отменить')
    logger.info(f'Состояние пользователя - {bot.get_state(call.message.chat.id, call.from_user.id)}')
