import logging

from handlers.keyboards import keyboard_queue_of_clients, \
    keyboard_enter_menu_for_operator, keyboard_for_enter_dialogue, keyboard_with_client_files
from handlers.text_messages import TEXT_MESSAGES
from services.files import find_technical_tasks
from services.redis_db import get_first_client_from_queue, get_queue_of_clients, move_client_to_first_place_in_queue

logger = logging.getLogger(__name__)


def callback_for_enter_menu(call, bot):
    bot.delete_message(call.message.chat.id, call.message.id)
    match call.data:
        case 'requests':
            queue_of_clients = get_queue_of_clients()
            bot.send_message(call.message.chat.id, 'Запросы от пользователей',
                             reply_markup=keyboard_queue_of_clients(queue_of_clients))
        case 'clients':
            bot.send_message(call.message.chat.id,
                             'Здесь отображаются все чаты с пользователями, с которыми ведется переписка')
        case 'tasks':
            bot.send_message(call.message.chat.id,
                             'Здесь отображаются все чаты со сформированной задачей от пользователя, которую запускают в продакшн')
        case 'settings':
            bot.send_message(call.message.chat.id,
                             'Здесь будет сценарий, при котором можно будет самостоятельно менять вопросы брифа')


def callback_technical_tasks_for_operator(call, bot):
    client_id = get_first_client_from_queue()
    logger.info(f'Запрос файлов клиента: {client_id}')
    list_of_files = find_technical_tasks(client_id)
    if bool(list_of_files) is False:
        text = 'Нет оформленных технических заданий'
    else:
        text = 'Выберите какой файл вы хотите получить:'
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                          reply_markup=keyboard_with_client_files(list_of_files))


def callback_cancel_to_enter_menu_for_operator(call, bot):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=TEXT_MESSAGES['start_for_operator'], reply_markup=keyboard_enter_menu_for_operator())


def callback_queue(call, bot):
    client_id = call.data.split('_')[1]
    move_client_to_first_place_in_queue(client_id)
    bot.send_message(call.message.chat.id, 'Вступить в диалог с клиентом ?', reply_markup=keyboard_for_enter_dialogue())
