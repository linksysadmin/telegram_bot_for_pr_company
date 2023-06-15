import logging

from config import DIR_FOR_TECHNICAL_TASKS, DIR_FOR_COMMERCIAL_OFFERS, DIR_FOR_REPORTS, DIR_FOR_OTHER_FILES, \
    DIR_FOR_SAVE_DIALOGS
from handlers.keyboards import keyboard_enter_menu_for_operator, keyboard_for_view_customer_information, \
    keyboard_with_client_files_in_dialogue, \
    keyboard_for_menu_in_dialogue, keyboard_with_clients, keyboard_menu_directions_of_documents, \
    keyboard_with_client_files
from handlers.documents import send_document_to_telegram
from handlers.text_messages import TEXT_MESSAGES
from services.files import find_user_documents, get_list_of_clients_dialogue, file_check
from services.redis_db import redis_cache
from services.states import MyStates

logger = logging.getLogger(__name__)


def callback_requests_for_operator(call, bot):
    queue_of_clients = redis_cache.get_queue_of_clients()
    text = 'Запросы от пользователей'
    if not queue_of_clients:
        text = 'Запросов от пользователей нет'
    callback_data_prefix = 'queue'
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=text, reply_markup=keyboard_with_clients(queue_of_clients, callback_data_prefix))


def callback_clients_for_operator(call, bot):
    list_of_clients = get_list_of_clients_dialogue()
    text = 'Выберите клиента:'
    callback_data_prefix = 'client|info'
    if not list_of_clients:
        text = 'Нет доступных диалогов с клиентам'
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=text, reply_markup=keyboard_with_clients(list_of_clients, callback_data_prefix))


def callback_tasks_for_operator(call, bot):
    pass


def callback_settings_for_operator(call, bot):
    pass


def callback_cancel_to_enter_menu_for_operator(call, bot):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['start_for_operator'], reply_markup=keyboard_enter_menu_for_operator())


def callback_get_dialogue_history(call, bot):
    client_id = int(call.data.split('|')[1])
    path_to_dialogue_file = f'{DIR_FOR_SAVE_DIALOGS}/{client_id}/dialogue.log'
    if file_check(path=path_to_dialogue_file):
        send_document_to_telegram(bot, call.from_user.id, path_to_dialogue_file, caption='История диалога',
                                  visible_file_name='Диалог.log')
    else:
        bot.send_message(call.from_user.id, 'История диалога пуста')


def callback_menu_directions_of_documents(call, bot):
    client_id = int(call.data.split('|')[1])
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id, text='Выберите раздел',
                          reply_markup=keyboard_menu_directions_of_documents(client_id))


def show_client_files_in_dialogue(call, bot, dir_path, client_id):
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
                          reply_markup=keyboard_with_client_files_in_dialogue(dict_path_to_files))


def callback_technical_tasks_for_operator_in_dialogue(call, bot):
    user_id = redis_cache.get_first_client_from_queue()
    show_client_files_in_dialogue(call, bot, DIR_FOR_TECHNICAL_TASKS, user_id)


def callback_commercial_offers_for_operator_in_dialogue(call, bot):
    user_id = redis_cache.get_first_client_from_queue()
    show_client_files_in_dialogue(call, bot, DIR_FOR_COMMERCIAL_OFFERS, user_id)


def callback_reports_for_operator_in_dialogue(call, bot):
    user_id = redis_cache.get_first_client_from_queue()
    show_client_files_in_dialogue(call, bot, DIR_FOR_REPORTS, user_id)


def callback_other_documents_for_operator_in_dialogue(call, bot):
    user_id = redis_cache.get_first_client_from_queue()
    show_client_files_in_dialogue(call, bot, DIR_FOR_OTHER_FILES, user_id)


def show_client_files(call, bot, dir_path, client_id):
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
                          reply_markup=keyboard_with_client_files(dict_path_to_files))


def callback_client_technical_tasks_for_operator(call, bot):
    client_id = call.data.split('|')[-1]
    show_client_files(call, bot, DIR_FOR_TECHNICAL_TASKS, client_id)


def callback_client_commercial_offers_for_operator(call, bot):
    client_id = call.data.split('|')[-1]
    show_client_files(call, bot, DIR_FOR_COMMERCIAL_OFFERS, client_id)


def callback_client_reports_for_operator(call, bot):
    client_id = call.data.split('|')[-1]
    show_client_files(call, bot, DIR_FOR_REPORTS, client_id)


def callback_client_other_documents_for_operator(call, bot):
    client_id = call.data.split('|')[-1]
    show_client_files(call, bot, DIR_FOR_OTHER_FILES, client_id)


def callback_cancel_to_enter_menu_in_dialogue(call, bot):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Меню взаимодействия с клиентом', reply_markup=keyboard_for_menu_in_dialogue())


def callback_upload_file_in_dialogue(call, bot):
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


def callback_upload_file(call, bot):
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


def callback_queue(call, bot):
    client_id = call.data.split('_')[1]
    redis_cache.move_client_to_first_place_in_queue(client_id)
    bot.send_message(call.message.chat.id, 'Вступить в диалог с клиентом ?',
                     reply_markup=keyboard_for_view_customer_information(client_id))
