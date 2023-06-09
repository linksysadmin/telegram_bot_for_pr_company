import logging

from telebot import apihelper

from config import OPERATOR_ID
from handlers.keyboards import keyboard_for_delete_dialogue, keyboard_for_enter_dialogue, \
    keyboard_enter_menu_for_clients, keyboard_for_menu_in_dialogue
from services.redis_db import get_operator_state, set_operator_state, add_client_to_queue, \
    get_first_client_and_delete_from_queue, \
    get_first_client_from_queue, remove_client_from_queue
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
    logger.info(f'Запрос от клиента {client_id} на диалог')
    match operator_state:
        case b'free' | None:
            set_operator_state(b'busy')
            logger.info(f'Перевод статуса оператора в "занят" (busy)')
            bot.send_message(OPERATOR_ID, f'💬Запрос на диалог!🧨\n\nОт пользователя:\nID: {call.from_user.id}\n'
                                          f'Имя: {call.from_user.first_name}',
                             reply_markup=keyboard_for_enter_dialogue())
        case _:
            logger.info(f'Оператор занят')
    match add_client_to_queue(client_id):
        case True:
            logger.info(f'Клиент {client_id} зарегистрирован в очереди и ждет ответа оператора')
            bot.send_message(call.message.chat.id, 'Подождите пока оператор к вам присоединится...')
        case _:
            logger.info(f'Клиент {client_id} уже присутствует в очереди')
            bot.send_message(call.message.chat.id,
                             'Вы уже в очереди подождите пожалуйста, пока оператор👨 ответит вам ‍💻😊')
            bot.send_message(OPERATOR_ID,
                             'Не забывайте о клиенте) Он повторно запрашивает диалог с оператором')


def callback_enter_into_a_dialog(call, bot):
    operator = call.from_user.id
    client_id = get_first_client_from_queue()
    if client_id is None:
        logger.warning('Диалог в который пытается вступить оператор не актуален')
        bot.send_message(operator, 'Диалог не актуален')
        return
    set_operator_state(b'busy')
    logger.info(f'Оператор вступил в диалог с клиентом {client_id}')
    bot.set_state(client_id, MyStates.dialogue_with_operator)
    bot.set_state(operator, MyStates.dialogue_with_client)
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(client_id, 'Вы вступили в диалог с оператором\n', reply_markup=keyboard_for_delete_dialogue())
    bot.send_message(operator, 'Вы вступили в диалог с клиентом\nНапишите ему:',
                     reply_markup=keyboard_for_delete_dialogue())
    logger.info(
        f'Состояние клиента - {bot.get_state(client_id)}, оператора - {bot.get_state(operator)}')


def send_request_to_operator(message, bot):
    bot.send_message(message.from_user.id, f'Подождите пожалуйста пока оператор к вам присоединиться...')


def send_message_to_client(message, bot):
    client_id = get_first_client_from_queue()
    bot.send_message(client_id, f'💬Сообщение от оператора:\n\n{message.text}')
    log_dialogue_in_file.info(f'Сообщение от оператора: {message.text}')


def send_document_to_client(message, bot):
    client_id = get_first_client_from_queue()
    bot.send_document(client_id, document=message.document.file_id)
    log_dialogue_in_file.info('Оператор отправил файл')


def send_photo_to_client(message, bot):
    client_id = get_first_client_from_queue()
    photo_id = message.photo[-1].file_id
    bot.send_photo(client_id, photo=photo_id)
    log_dialogue_in_file.info('Оператор отправил картинку')


def send_message_to_operator(message, bot):
    bot.send_message(OPERATOR_ID, f'💬Сообщение от клиента:\n{message.from_user.id}\n\n{message.text}',
                     reply_markup=keyboard_for_menu_in_dialogue())
    log_dialogue_in_file.info(f'Сообщение от клиента: {message.text}')


def send_document_to_operator(message, bot):
    bot.send_photo(OPERATOR_ID, document=message.document.file_id)
    log_dialogue_in_file.info('Клиент отправил файл')


def send_photo_to_operator(message, bot):
    photo_id = message.photo[-1].file_id
    bot.send_photo(OPERATOR_ID, photo=photo_id)
    log_dialogue_in_file.info('Клиент отправил картинку')


def callback_client_left_dialog(call, bot):
    client_id = call.from_user.id
    remove_client_from_queue(client_id)
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.delete_state(OPERATOR_ID, OPERATOR_ID)
    bot.delete_state(client_id, client_id)
    logger.info(f'Клиент {client_id} завершил диалог')
    logger.info(
        f'Состояние клиента - {bot.get_state(client_id, client_id)}, оператора - {bot.get_state(OPERATOR_ID, OPERATOR_ID)}')
    bot.send_message(call.from_user.id, f'Вы вышли из диалога\n\nНажмите /start - для входа в меню')
    bot.send_message(OPERATOR_ID, f'Клиент завершил диалог с вами')
    next_client = get_first_client_from_queue()
    if next_client is None:
        set_operator_state(b'free')
        logger.info('Оператор свободен')
        return
    set_operator_state(b'busy')
    logger.info(f'Запрос к оператору на диалог от клиента: {next_client}')
    bot.send_message(OPERATOR_ID, f'💬Запрос на диалог!🧨\n\nОт пользователя:\nID: {next_client}\n'
                     , reply_markup=keyboard_for_enter_dialogue())


def callback_operator_left_dialog(call, bot):
    bot.delete_message(call.message.chat.id, call.message.id)
    client_id = get_first_client_and_delete_from_queue()
    if client_id is None:
        bot.send_message(OPERATOR_ID, f'Вы уже выходили из этого диалога')
        return
    bot.delete_state(OPERATOR_ID, OPERATOR_ID)
    bot.delete_state(client_id, client_id)
    logger.info(f'Оператор завершил диалог с клиентом: {client_id}')
    logger.info(
        f'Состояние клиента - {bot.get_state(client_id, client_id)}, оператора - {bot.get_state(OPERATOR_ID, OPERATOR_ID)}')
    bot.send_message(OPERATOR_ID, f'Вы вышли из диалога!')
    bot.send_message(client_id, f'Оператор завершил диалог с вами',
                     reply_markup=keyboard_enter_menu_for_clients())
    next_client = get_first_client_from_queue()
    if next_client is None:
        set_operator_state(b'free')
        logger.info(f'Запросов в очереди нет, статус оператора перевод в "свободен" (free)')
        return
    logger.info(f'Запрос к оператору на диалог от клиента: {next_client}')
    logger.info(f'Есть запросы в очереди, статус оператора перевод в "занят" (busy)')
    set_operator_state(b'busy')
    bot.send_message(OPERATOR_ID, f'💬Запрос на диалог!🧨\n\nОт пользователя:\nID: {next_client}\n'
                     , reply_markup=keyboard_for_enter_dialogue())
