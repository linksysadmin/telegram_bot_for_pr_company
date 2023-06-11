import logging

from config import DIR_FOR_TECHNICAL_TASKS, DIR_FOR_COMMERCIAL_OFFERS, DIR_FOR_REPORTS, DIR_FOR_OTHER_FILES, \
    DIR_FOR_SAVE_DIALOGS, OPERATOR_ID
from handlers.keyboards import keyboard_queue_of_clients, \
    keyboard_enter_menu_for_operator, keyboard_for_view_customer_information, keyboard_with_client_files, \
    keyboard_for_menu_in_dialogue, keyboard_with_clients
from handlers.send_documents import send_document_to_telegram
from handlers.text_messages import TEXT_MESSAGES
from services.files import find_user_documents, get_list_of_clients_dialogue
from services.redis_db import get_first_client_from_queue, get_queue_of_clients, move_client_to_first_place_in_queue, \
    set_directory_in_redis, get_directory_from_redis
from services.states import MyStates

logger = logging.getLogger(__name__)


def callback_requests_for_operator(call, bot):
    queue_of_clients = get_queue_of_clients()
    text = 'Запросы от пользователей'
    if not queue_of_clients:
        text = 'Запросов от пользователей нет'
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=text, reply_markup=keyboard_queue_of_clients(queue_of_clients))


def callback_clients_for_operator(call, bot):
    list_of_clients = get_list_of_clients_dialogue()
    text = 'Диалоги с клиентами:'
    if not list_of_clients:
        text = 'Нет доступных диалогов с клиентам'
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=text, reply_markup=keyboard_with_clients(list_of_clients))


def callback_tasks_for_operator(call, bot):
    pass


def callback_settings_for_operator(call, bot):
    pass


def callback_cancel_to_enter_menu_for_operator(call, bot):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['start_for_operator'], reply_markup=keyboard_enter_menu_for_operator())


def callback_dialogue_history(call, bot):
    client_id = int(call.data.split('|')[1])
    path_to_dialogue_file = f'{DIR_FOR_SAVE_DIALOGS}/{client_id}/dialogue.log'
    print(path_to_dialogue_file)
    send_document_to_telegram(bot, OPERATOR_ID, path_to_dialogue_file, caption='История диалога', visible_file_name='Диалог.log')


def get_documents(call, bot, dir_path):
    user_id = get_first_client_from_queue()
    logger.info(f'Запрос файлов клиента: {user_id}')
    list_of_files = find_user_documents(user_id, dir_path)
    set_directory_in_redis(call.from_user.id, dir_path)
    if bool(list_of_files) is False:
        text = f'Нет документов у клиента'
    else:
        text = 'Выберите какой файл вы хотите получить:'
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                          reply_markup=keyboard_with_client_files(list_of_files))


def callback_technical_tasks_for_operator(call, bot):
    get_documents(call, bot, DIR_FOR_TECHNICAL_TASKS)


def callback_commercial_offers_for_operator(call, bot):
    get_documents(call, bot, DIR_FOR_COMMERCIAL_OFFERS)


def callback_reports_for_operator(call, bot):
    get_documents(call, bot, DIR_FOR_REPORTS)


def callback_other_documents_for_operator(call, bot):
    get_documents(call, bot, DIR_FOR_OTHER_FILES)


def callback_cancel_to_enter_menu_in_dialogue(call, bot):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Меню взаимодействия с клиентом', reply_markup=keyboard_for_menu_in_dialogue())


def callback_upload_file(call, bot):
    directory = get_directory_from_redis(call.from_user.id)
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


def callback_queue(call, bot):
    client_id = call.data.split('_')[1]
    move_client_to_first_place_in_queue(client_id)
    bot.send_message(call.message.chat.id, 'Вступить в диалог с клиентом ?', reply_markup=keyboard_for_view_customer_information(client_id))
