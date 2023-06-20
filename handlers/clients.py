import logging

from config import OPERATOR_ID, DIR_FOR_COMMERCIAL_OFFERS, DIR_FOR_TECHNICAL_TASKS, DIR_FOR_OTHER_FILES, DIR_FOR_REPORTS
from handlers.keyboards import ClientKeyboards, OperatorKeyboards, GeneralKeyboards
from handlers.documents import send_document_to_telegram
from services.db_data import get_question_and_answers_from_db, \
    get_user_answer, get_user_data_from_db, get_sections_from_db, get_sub_directions
from services.file_handler import find_user_documents
from services.redis_db import redis_cache
from services.states import MyStates
from handlers.text_messages import TEXT_MESSAGES
from services.string_parser import CallDataParser

logger = logging.getLogger(__name__)


def callback_scenario(call, bot):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'], reply_markup=GeneralKeyboards.directions())


def callback_technical_tasks_and_commercial_offer(call, bot):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Выберите тип файла',
                          reply_markup=ClientKeyboards.types_of_files())


def show_files_for_client(call, bot, directory):
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


def callback_directory(call, bot):
    direction = call.data
    list_of_sub_directions = get_sub_directions(direction)
    if list_of_sub_directions:
        keyboard = ClientKeyboards.sub_directions(direction, list_of_sub_directions)
    else:
        list_of_sections = get_sections_from_db(direction)
        keyboard = ClientKeyboards.sections(direction, list_of_sections)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=keyboard)


def callback_sub_directory(call, bot):
    path = call.data
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=ClientKeyboards.sections_from_subcategory(path))


def callback_section(call, bot):
    path = call.data
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=ClientKeyboards.questions(call.from_user.id, path))


def callback_cancel_from_inline_menu(call, bot):
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


def callback_cancel_to_directions(call, bot):
    logger.warning(f'callback_cancel_to_directions| call.data:{call.data}')
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=ClientKeyboards.directions())


def callback_back_to_questions(call, bot):
    path = redis_cache.get_keyboard_for_questions(call.from_user.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=ClientKeyboards.questions(call.from_user.id, path))


def callback_for_change_answer(call, bot):
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.set_state(call.from_user.id, MyStates.answer_to_question, call.from_user.id)
    question_id = redis_cache.get_question_id(call.from_user.id)
    question, answers = get_question_and_answers_from_db(question_id)
    bot.send_message(call.message.chat.id, f'❓{question}?\n\nНапишите ответ и нажмите "✅ Отправить ответ"',
                     reply_markup=ClientKeyboards.answer(answers))


def callback_for_questions(call, bot):
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


def callback_for_registration(call, bot):
    question_id = CallDataParser.get_question_id(call.data)
    redis_cache.set_question_id(user=call.from_user.id, question_id=question_id)
    bot.set_state(call.from_user.id, MyStates.name, call.from_user.id)
    bot.add_data(call.from_user.id, call.message.chat.id, id_question=question_id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Укажите пожалуйста ваше имя:\n\n/cancel - отменить')


def callback_for_grade(call, bot):
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
