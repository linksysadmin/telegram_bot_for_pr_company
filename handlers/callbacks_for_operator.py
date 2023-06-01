import logging

from config import OPERATOR_ID
from handlers.keyboards import keyboard_for_technical_tasks
from services.files import find_user_files
from services.redis_db import get_client_id

logger = logging.getLogger(__name__)


def callback_for_enter_menu(call, bot):
    bot.delete_message(call.message.chat.id, call.message.id)
    match call.data:
        case 'requests':
            bot.send_message(call.message.chat.id, 'Здесь отображаются все запросы от пользователей')
        case 'clients':
            bot.send_message(call.message.chat.id, 'Здесь отображаются все чаты с пользователями, с которыми ведется переписка')
        case 'tasks':
            bot.send_message(call.message.chat.id, 'Здесь отображаются все чаты со сформированной задачей от пользователя, которую запускают в продакшн')
        case 'settings':
            bot.send_message(call.message.chat.id, 'Здесь будет сценарий, при котором можно будет самостоятельно менять вопросы брифа')


def callback_technical_tasks_for_operator(call, bot):
    client_id = get_client_id()
    logger.info(f'Запрос файлов клиента: {client_id}')
    list_of_files = find_user_files(client_id, doc_type='technical_tasks')
    if bool(list_of_files) is False:
        text = 'Нет оформленных технических заданий'
    else:
        text = 'Выберите какой файл вы хотите получить:'
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                          reply_markup=keyboard_for_technical_tasks(list_of_files, operator=True))



