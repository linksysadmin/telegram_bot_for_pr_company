import logging

from config import OPERATOR_ID, DIR_FOR_COMMERCIAL_OFFERS, DIR_FOR_TECHNICAL_TASKS, DIR_FOR_OTHER_FILES, DIR_FOR_REPORTS
from handlers.keyboards import keyboard_for_briefings, \
    keyboard_for_questions, keyboard_for_direction, keyboard_for_sub_direction, keyboard_enter_menu_for_clients, \
    keyboard_for_answer, keyboard_for_change_answer, keyboard_for_reference_and_commercial_offer, \
    keyboard_for_files, keyboard_for_view_customer_information
from handlers.documents import send_document_to_telegram
from services.db_data import get_data_questions, get_question_and_answers_from_db, \
    get_user_answer, get_user_data_from_db, get_directories
from services.files import find_user_documents
from services.redis_db import set_question_id_in_redis, get_question_id_from_redis, \
    set_next_question_callback_in_redis, get_max_question_id_in_redis, get_keyboard_for_questions_from_redis, \
    get_last_file_path, add_client_to_queue, set_selected_directory_in_redis, \
    save_dict_of_path_for_download_file_in_redis
from services.states import MyStates
from handlers.text_messages import TEXT_MESSAGES


logger = logging.getLogger(__name__)


def callback_scenario(call, bot):
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(call.message.chat.id, TEXT_MESSAGES['menu'], reply_markup=keyboard_for_briefings())


def callback_technical_tasks_and_commercial_offer(call, bot):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Выберите тип файла',
                          reply_markup=keyboard_for_reference_and_commercial_offer())


def show_files_for_client(call, bot, directory):
    user_id = call.from_user.id
    logger.info(f'Клиент {user_id} запросил файлы')
    dict_path_to_files = find_user_documents(user_id, directory)
    set_selected_directory_in_redis(call.from_user.id, directory)
    if not dict_path_to_files:
        text = 'К сожалению у вас нет оформленных файлов'
    else:
        save_dict_of_path_for_download_file_in_redis(user_id, dict_path_to_files)
        text = 'Выберите какой файл вы хотите получить:'
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=text, reply_markup=keyboard_for_files(dict_path_to_files))


def callback_technical_tasks(call, bot):
    show_files_for_client(call, bot, DIR_FOR_TECHNICAL_TASKS)


def callback_commercial_offer(call, bot):
    show_files_for_client(call, bot, DIR_FOR_COMMERCIAL_OFFERS)


def callback_reports(call, bot):
    show_files_for_client(call, bot, DIR_FOR_REPORTS)


def callback_documents(call, bot):
    show_files_for_client(call, bot, DIR_FOR_OTHER_FILES)


def callback_chat_with_operator(call, bot):
    bot.send_contact(call.message.chat.id, phone_number='+74950188868', first_name='Оператор Mr.Эйч')
    bot.send_message(call.message.chat.id, TEXT_MESSAGES['chat_with_operator'])


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
    user_data = get_user_data_from_db(client_id)
    reply_markup = keyboard_enter_menu_for_clients(doc=False)
    if user_data['documents']:
        reply_markup = keyboard_enter_menu_for_clients(doc=True)
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
            caption = f"Техническое задание от пользователя:\n{user_data['name']}\n" \
                      f"Username: {user_data['tg_username']}\n" \
                      f"Компания: {user_data['company']}\n" \
                      f"Телефон: {user_data['phone']}\n" \
                      f"Website: {user_data['website']}\n"
            visible_file_name = f'Тех.задание компании {user_data["company"]}.docx'
            send_document_to_telegram(bot, OPERATOR_ID, path_to_file, caption=caption, visible_file_name=visible_file_name)
            add_client_to_queue(call.from_user.id)
            bot.send_message(OPERATOR_ID, 'Начать чат с клиентом ?', reply_markup=keyboard_for_view_customer_information(call.from_user.id))
        case 'client_grade_no':
            bot.send_message(call.message.chat.id, f'Хорошо, отличного дня!')
