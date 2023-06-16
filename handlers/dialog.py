import logging
import os

from config import OPERATOR_ID, DIR_FOR_SAVE_DIALOGS
from handlers.keyboards import keyboard_for_menu_in_dialogue, keyboard_for_view_customer_information
from services.db_data import get_user_data_from_db
from services.redis_db import redis_cache
from services.states import MyStates
from services.string_parser import CallDataParser

logger = logging.getLogger(__name__)


def dialogue_logging(client_id):
    log_dialogue_in_file = logging.getLogger(f'logger_for_dialogue_{client_id}')
    if not log_dialogue_in_file.handlers:
        log_dir = f'{DIR_FOR_SAVE_DIALOGS}/{client_id}'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        file_handler = logging.FileHandler(f'{DIR_FOR_SAVE_DIALOGS}/{client_id}/dialogue.log')
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        log_dialogue_in_file.addHandler(file_handler)
        log_dialogue_in_file.setLevel(logging.INFO)
        log_dialogue_in_file.propagate = False
    return log_dialogue_in_file


def callback_instant_messaging_service(call, bot):
    client_id = call.from_user.id
    operator_state = redis_cache.get_operator_state()
    logger.info(f'Запрос от клиента {client_id} на диалог')
    match operator_state:
        case b'free' | None:
            redis_cache.set_operator_state(b'busy')
            logger.info(f'Перевод статуса оператора в "занят" (busy)')
            bot.send_message(OPERATOR_ID, f'💬Запрос на диалог!🧨\n\nОт пользователя:\nID: {call.from_user.id}\n'
                                          f'Имя: {call.from_user.first_name}',
                             reply_markup=keyboard_for_view_customer_information(client_id))
        case _:
            logger.info(f'Оператор занят')
    match redis_cache.add_client_to_queue(client_id):
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
    client_id = CallDataParser.get_client_id(call.data)
    redis_cache.move_client_to_first_place_in_queue(client_id)
    redis_cache.set_operator_state(b'busy')
    logger.info(f'Оператор вступил в диалог с клиентом {client_id}')
    bot.set_state(client_id, MyStates.dialogue_with_operator)
    bot.set_state(operator, MyStates.dialogue_with_client)
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(client_id, 'Вы вступили в диалог с оператором\n')
    bot.send_message(operator, 'Вы вступили в диалог с клиентом\nНапишите ему:',
                     reply_markup=keyboard_for_menu_in_dialogue())
    logger.info(
        f'Состояние клиента - {bot.get_state(client_id)}, оператора - {bot.get_state(operator)}')


def callback_client_info(call, bot):
    operator = call.from_user.id
    client_id = CallDataParser.get_client_id(call.data)
    bot.send_message(operator, 'Выберите действие',
                     reply_markup=keyboard_for_view_customer_information(client_id))


def send_request_to_operator(message, bot):
    bot.send_message(message.from_user.id, f'Подождите пожалуйста пока оператор к вам присоединиться...')


def send_message_to_client(message, bot):
    client_id = redis_cache.get_first_client_from_queue()
    log_dialogue = dialogue_logging(client_id)
    bot.send_message(client_id, f'💬Сообщение от оператора:\n\n{message.text}')
    log_dialogue.info(f'Сообщение от оператора: {message.text}')


def send_document_to_client(message, bot):
    client_id = redis_cache.get_first_client_from_queue()
    log_dialogue = dialogue_logging(client_id)
    bot.send_document(client_id, document=message.document.file_id)
    log_dialogue.info('Оператор отправил файл')


def send_photo_to_client(message, bot):
    client_id = redis_cache.get_first_client_from_queue()
    log_dialogue = dialogue_logging(client_id)
    photo_id = message.photo[-1].file_id
    bot.send_photo(client_id, photo=photo_id)
    log_dialogue.info('Оператор отправил картинку')


def send_message_to_operator(message, bot):
    client_id = message.from_user.id
    user_data = get_user_data_from_db(client_id)
    log_dialogue = dialogue_logging(client_id)
    log_dialogue.info(f'{user_data["company"]}|Сообщение от клиента {user_data["name"]}: {message.text}')
    bot.send_message(OPERATOR_ID, f'Вы общаетесь с клиентом: {user_data["name"]}\n'
                                  f'Компания: {user_data["company"]}\n'
                                  f'Телефон: {user_data["phone"]}\n\n'
                                  f'Сообщение:\n{message.text}',
                     reply_markup=keyboard_for_menu_in_dialogue())


def send_document_to_operator(message, bot):
    client_id = message.from_user.id
    log_dialogue = dialogue_logging(client_id)
    bot.send_document(OPERATOR_ID, document=message.document.file_id)
    log_dialogue.info('Клиент отправил файл')


def send_photo_to_operator(message, bot):
    client_id = message.from_user.id
    log_dialogue = dialogue_logging(client_id)
    photo_id = message.photo[-1].file_id
    bot.send_photo(OPERATOR_ID, photo=photo_id)
    log_dialogue.info('Клиент отправил картинку')


def callback_operator_left_dialog(call, bot):
    bot.delete_message(call.message.chat.id, call.message.id)
    client_id = redis_cache.get_first_client_and_delete_from_queue()
    if client_id is None:
        bot.send_message(OPERATOR_ID, f'Вы уже выходили из этого диалога')
        return
    bot.delete_state(OPERATOR_ID, OPERATOR_ID)
    bot.delete_state(client_id, client_id)
    logger.info(f'Оператор завершил диалог с клиентом: {client_id}')
    logger.info(
        f'Состояние клиента - {bot.get_state(client_id, client_id)}, оператора - {bot.get_state(OPERATOR_ID, OPERATOR_ID)}')
    bot.send_message(OPERATOR_ID, f'Вы вышли из диалога!')
    next_client = redis_cache.get_first_client_from_queue()
    if next_client is None:
        redis_cache.set_operator_state(b'free')
        logger.info(f'Запросов в очереди нет, статус оператора перевод в "свободен" (free)')
        return
    logger.info(f'Запрос к оператору на диалог от клиента: {next_client}')
    logger.info(f'Есть запросы в очереди, статус оператора переведен в "занят" (busy)')
    redis_cache.set_operator_state(b'busy')
    bot.send_message(OPERATOR_ID, f'💬Запрос на диалог!🧨\n\nОт пользователя:\nID: {next_client}\n'
                     , reply_markup=keyboard_for_view_customer_information(next_client))
