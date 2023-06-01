import logging

from telebot import apihelper

from config import OPERATOR_ID
from handlers.keyboards import keyboard_for_delete_dialogue, keyboard_for_enter_dialogue, \
    keyboard_enter_menu_for_clients, keyboard_for_menu_in_dialogue
from services.redis_db import get_operator_state, set_operator_state, add_client_to_queue, get_next_client_from_queue, \
    get_client_id
from services.states import MyStates

logger = logging.getLogger(__name__)
log_dialogue_in_file = logging.getLogger('logger_for_dialogue')
file_handler = logging.FileHandler('logs/dialogue.log')
formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
log_dialogue_in_file.addHandler(file_handler)
log_dialogue_in_file.setLevel(logging.INFO)
log_dialogue_in_file.propagate = False


def callback_instant_messaging_service(call, bot):
    client_id = call.from_user.id
    operator_state = get_operator_state()
    logger.info(f'Запрос от клиента {client_id} на диалог. Состояние оператора: {operator_state}')
    match operator_state:
        case b'free':
            logger.info(f'Запрос к оператору на диалог от клиента: {client_id}')
            set_operator_state(b'busy')
            bot.send_message(OPERATOR_ID, f'💬Запрос на диалог!🧨\n\nОт пользователя:\nID: {call.from_user.id}\n'
                                          f'Имя: {call.from_user.first_name}',
                             reply_markup=keyboard_for_enter_dialogue())
        case _:
            logger.info(f'Клиент {client_id} ожидает оператора в очереди')
    match add_client_to_queue(client_id):
        case True:
            bot.send_message(call.message.chat.id, 'Подождите пока оператор к вам присоединится...')
        case _:
            bot.send_message(call.message.chat.id,
                             'Вы уже в очереди подождите пожалуйста, пока оператор👨 ответит вам ‍💻😊')


def callback_enter_into_a_dialog(call, bot):
    try:
        set_operator_state(b'busy')
        client_id = get_client_id()
        logger.warning(client_id)
        bot.set_state(client_id, MyStates.dialogue_with_operator, client_id)
        bot.set_state(OPERATOR_ID, MyStates.dialogue_with_client, OPERATOR_ID)
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(client_id, 'Вы вступили в диалог с оператором\n', reply_markup=keyboard_for_delete_dialogue())
        bot.send_message(OPERATOR_ID, 'Вы вступили в диалог с клиентом\nНапишите ему:',
                         reply_markup=keyboard_for_delete_dialogue())
        logger.info(
            f'Состояние клиента - {bot.get_state(client_id, client_id)}, оператора - {bot.get_state(OPERATOR_ID, OPERATOR_ID)}')
    except Exception as e:
        logger.error(f'{e}')


def send_request_to_operator(message, bot):
    bot.send_message(message.from_user.id, f'Подождите пожалуйста пока оператор к вам присоединиться...')


def send_message_to_client(message, bot):
    client_id = get_client_id()
    if message.document is not None:
        bot.send_document(client_id, document=message.document.file_id)
        return
    bot.send_message(client_id, f'💬Сообщение от оператора:\n\n{message.text}')
    logger.info(f'Состояние оператора - {bot.get_state(message.from_user.id, message.chat.id)}')
    log_dialogue_in_file.info(f'Сообщение от оператора: {message.text}')


def send_message_to_operator(message, bot):
    if message.document is not None:
        bot.send_document(OPERATOR_ID, document=message.document.file_id)
        return
    bot.send_message(OPERATOR_ID, f'💬Сообщение от клиента:\n{message.from_user.id}\n\n{message.text}',
                     reply_markup=keyboard_for_menu_in_dialogue())
    log_dialogue_in_file.info(f'Сообщение от клиента: {message.text}')


def callback_cancel_from_dialog(call, bot):
    bot.delete_message(call.message.chat.id, call.message.id)
    try:
        client_id = get_next_client_from_queue()
        logger.info(f'Выход из диалога клиента: {client_id}')
    except TypeError:
        bot.send_message(OPERATOR_ID, f'Актуальных диалогов нет')
        return
    bot.delete_state(OPERATOR_ID, OPERATOR_ID)
    bot.delete_state(client_id, client_id)
    logger.info(
        f'Состояние клиента - {bot.get_state(client_id, client_id)}, оператора - {bot.get_state(OPERATOR_ID, OPERATOR_ID)}')
    try:
        if call.from_user.id == OPERATOR_ID:
            bot.send_message(OPERATOR_ID, f'Вы вышли из диалога!')
            bot.send_message(client_id, f'Оператор завершил диалог с вами',
                             reply_markup=keyboard_enter_menu_for_clients())
        else:
            bot.send_message(call.from_user.id, f'Вы вышли из диалога\n\nНажмите /start - для входа в меню')
            bot.send_message(OPERATOR_ID, f'Клиент завершил диалог с вами')
    except apihelper.ApiTelegramException:
        set_operator_state(b'free')
        logger.warning('Чат не существует')
    try:
        next_client = get_client_id()
        if next_client is None:
            set_operator_state(b'free')
            logger.info('Оператор свободен')
            return
        set_operator_state(b'busy')
        logger.info(f'Запрос к оператору на диалог от клиента: {next_client}')
        bot.send_message(OPERATOR_ID, f'💬Запрос на диалог!🧨\n\nОт пользователя:\nID: {next_client}\n'
                         , reply_markup=keyboard_for_enter_dialogue())
    except TypeError:  # Если нет следующего клиента, оператор становится свободным
        set_operator_state(b'free')
        logger.info('Оператор свободен')
