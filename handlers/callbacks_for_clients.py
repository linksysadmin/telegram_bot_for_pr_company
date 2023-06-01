from config import OPERATOR_ID
from handlers.keyboards import keyboard_for_briefings, \
    keyboard_for_questions, keyboard_for_direction, keyboard_for_sub_direction, keyboard_enter_menu_for_clients, \
    keyboard_for_answer, keyboard_for_change_answer, keyboard_for_reference_and_commercial_offer, \
    keyboard_for_commercial_offer, keyboard_for_technical_tasks, keyboard_for_enter_dialogue
from handlers.send_document_to_user import send_document_to_telegram
from services.db_data import get_data_questions, get_question_and_answers_from_db, \
    get_user_answer, get_user_data_from_db, get_directories
from services.files import find_user_files
from services.redis_db import set_question_id_in_redis, get_question_id_from_redis, \
    set_next_question_callback_in_redis, get_max_question_id_in_redis, get_keyboard_for_questions_from_redis, \
    get_last_file_path, add_client_to_queue, get_client_id
from services.states import MyStates
from handlers.text_messages import TEXT_MESSAGES


def callback_scenario(call, bot):
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(call.message.chat.id, TEXT_MESSAGES['menu'], reply_markup=keyboard_for_briefings())


def callback_technical_tasks_and_commercial_offer(call, bot):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Выберите какой файл вы хотите получить:',
                          reply_markup=keyboard_for_reference_and_commercial_offer())


def callback_technical_tasks(call, bot):
    user_id = call.from_user.id
    list_of_files = find_user_files(user_id, doc_type='technical_tasks')
    if bool(list_of_files) is False:
        text = 'К сожалению у вас нет оформленных технических заданий'
    else:
        text = 'Выберите какой файл вы хотите получить:'
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                          reply_markup=keyboard_for_technical_tasks(list_of_files, user_id))


def callback_commercial_offer(call, bot):
    user_id = call.from_user.id
    list_of_files = find_user_files(user_id, doc_type='commercial_offers')
    if bool(list_of_files) is False:
        text = 'К сожалению у вас нет оформленных коммерческих предложений'
    else:
        text = 'Выберите какой файл вы хотите получить:'
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                          reply_markup=keyboard_for_commercial_offer(list_of_files))


def callback_chat_with_operator(call, bot):
    bot.send_contact(call.message.chat.id, phone_number='+74950188868', first_name='Оператор Mr.Эйч')
    bot.send_message(call.message.chat.id, TEXT_MESSAGES['chat_with_operator'])


def callback_upload_report(call, bot):
    pass


def callback_blog(call, bot):
    pass


def callback_query_for_scenario(call, bot):
    directories = get_directories()
    match call.data:
        case data if data in directories:
            direction = call.data
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=TEXT_MESSAGES['menu'],
                                  reply_markup=keyboard_for_direction(direction=direction))
        case data if data in [question[1] for question in get_data_questions()]:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=TEXT_MESSAGES['scenario'])


def callback_for_sub_direction(call, bot):
    path = call.data
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=keyboard_for_sub_direction(path))


def callback_for_section(call, bot):
    path = call.data
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=keyboard_for_questions(call.from_user.id, path))


def callback_section_from_subcategory(call, bot):
    path = call.data
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=keyboard_for_questions(call.from_user.id, path))


def callback_cancel_from_inline_menu(call, bot):
    client_id = call.from_user.id
    if client_id == OPERATOR_ID:
        client_id = get_client_id()
    user_data = get_user_data_from_db(client_id)
    reply_markup = keyboard_enter_menu_for_clients(False)
    if user_data['documents']:
        reply_markup = keyboard_enter_menu_for_clients(True)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['start'].format(username=user_data['name'],
                                                             company=user_data['company']),
                                                             reply_markup=reply_markup)


def callback_cancel_to_directions(call, bot):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=keyboard_for_briefings())


def callback_back_to_questions(call, bot):
    path = get_keyboard_for_questions_from_redis(call.from_user.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=keyboard_for_questions(call.from_user.id, path))


def callback_for_change_answer(call, bot):
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.set_state(call.from_user.id, MyStates.answer_to_question, call.from_user.id)
    question_id = get_question_id_from_redis(call.from_user.id)
    question, answers = get_question_and_answers_from_db(question_id)
    bot.send_message(call.message.chat.id, f'❓{question}?\n\nНапишите ответ и нажмите "✅ Отправить ответ"',
                     reply_markup=keyboard_for_answer(answers))


def callback_for_questions(call, bot):
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
                              text=f'❓{question}?\n\nВаш ответ:{user_answer}',
                              reply_markup=keyboard_for_change_answer())
        return
    bot.set_state(call.from_user.id, MyStates.answer_to_question, call.from_user.id)
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(call.message.chat.id, f'❓{question}?\n\nНапишите ответ и нажмите "✅ Отправить ответ"',
                     reply_markup=keyboard_for_answer(answers))


def callback_for_registration(call, bot):
    question_id = call.data.split('_')[1]
    set_question_id_in_redis(user=call.from_user.id, question_id=question_id)
    bot.set_state(call.from_user.id, MyStates.name, call.from_user.id)
    bot.add_data(call.from_user.id, call.message.chat.id, id_question=question_id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Укажите пожалуйста ваше имя:\n\n/cancel - отменить')


def callback_for_grade(call, bot):
    bot.delete_message(call.message.chat.id, call.message.id)
    match call.data:
        case 'client_grade_yes':
            user_data = get_user_data_from_db(call.from_user.id)
            path_to_file = get_last_file_path(call.from_user.id)
            send_document_to_telegram(bot, user_data, path_to_file, operator=True)
            add_client_to_queue(call.from_user.id)
            bot.send_message(OPERATOR_ID, 'Начать чат с клиентом ?', reply_markup=keyboard_for_enter_dialogue())
        case 'client_grade_no':
            bot.send_message(call.message.chat.id, f'Хорошо, отличного дня!')