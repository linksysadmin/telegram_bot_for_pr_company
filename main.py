# -*- coding: utf-8 -*-
import logging

import flask
import colorlog
import telebot
from telebot import custom_filters
from telebot.storage import StateRedisStorage

from config import TELEGRAM_BOT_API_TOKEN, WEBHOOK_URL_PATH
from handlers import callbacks_for_clients, send_document_to_user, callbacks_for_operator
from handlers.callbacks_for_clients import *
from handlers.commands import start, \
    delete_state_, start_unauthorized, test_, start_for_operator
from handlers.get_info_from_user import get_user_name, get_user_phone, phone_incorrect, get_user_company, \
    get_answer_from_user, send_user_answers_to_db, next_question, get_user_website

from services.db_data import get_directories
from services.states import MyStates
from services.filters import CheckPhoneNumber, CheckConsent, \
    ContactForm, CheckFile, \
    CheckUserRegistration, CheckPathToSection, CheckPathToSectionWithoutSubDirectory, \
    CheckPathToSectionWithSubDirectory, FinishPoll, NextQuestion, CheckOperator
from handlers import dialog_with_operator

# logging.basicConfig(handlers=(logging.StreamHandler(),),
#                     format="%(name)s %(asctime)s - %(levelname)s - %(message)s",
#                     datefmt='%m.%d.%Y %H:%M:%S',
#                     level=logging.INFO)
#
# logger = logging.getLogger(__name__)

formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(name)s %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%m.%d.%Y %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    })

# Создаем обработчик для вывода логов в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logging.basicConfig(handlers=[console_handler], level=logging.INFO)

# logger = colorlog.getLogger(__name__)
# logger.setLevel(logging.INFO)


bot = telebot.TeleBot(TELEGRAM_BOT_API_TOKEN, state_storage=StateRedisStorage(), parse_mode='HTML')

FILTERS = (custom_filters.StateFilter(bot),
           custom_filters.IsDigitFilter(),
           custom_filters.TextMatchFilter(),
           CheckPhoneNumber(),
           ContactForm(),
           CheckConsent(),
           CheckFile(),
           CheckUserRegistration(),
           CheckPathToSection(),
           CheckPathToSectionWithSubDirectory(),
           CheckPathToSectionWithoutSubDirectory(),
           FinishPoll(),
           NextQuestion(),
           CheckOperator(),
           )


def register_functions_for_bot():
    """Регистрация команд, фильтров, состояний и функций обратного вызова для Телеграм-бота"""

    """   Регистрация команд telegram бота """
    bot.register_message_handler(commands=['start'], callback=start_for_operator, pass_bot=True, check_operator=True)
    bot.register_message_handler(commands=['start'], callback=start, pass_bot=True, check_user_registration=True)
    bot.register_message_handler(commands=['start'], callback=start_unauthorized, pass_bot=True,
                                 check_user_registration=False)
    bot.register_message_handler(state="*", callback=delete_state_, commands=['cancel'], pass_bot=True)
    bot.register_message_handler(commands=['test'], callback=test_, pass_bot=True)

    """   Добавление фильтров сообщений   """
    for filter_ in FILTERS:
        bot.add_custom_filter(filter_)

    """   Регистрация состояний пользователя   """
    bot.register_message_handler(state="*", text=['Отменить'], callback=delete_state_, pass_bot=True)
    bot.register_message_handler(state="*", text=['К вопросам'], callback=delete_state_, pass_bot=True)
    bot.register_message_handler(state=MyStates.request, callback=dialog_with_operator.send_request_to_operator,
                                 pass_bot=True)
    bot.register_message_handler(state=MyStates.dialogue_with_operator,
                                 callback=dialog_with_operator.send_message_to_operator, pass_bot=True)
    bot.register_message_handler(state=MyStates.dialogue_with_client,
                                 callback=dialog_with_operator.send_message_to_client, pass_bot=True)
    bot.register_message_handler(state=MyStates.name, callback=get_user_name, pass_bot=True)
    bot.register_message_handler(state=MyStates.phone_number, callback=get_user_phone, pass_bot=True, contact_form=True,
                                 check_phone=False)
    bot.register_message_handler(state=MyStates.phone_number, callback=get_user_phone, pass_bot=True, check_phone=True)
    bot.register_message_handler(state=MyStates.phone_number, callback=phone_incorrect, pass_bot=True,
                                 check_phone=False)
    bot.register_message_handler(state=MyStates.website, callback=get_user_website, pass_bot=True)
    bot.register_message_handler(state=MyStates.company, callback=get_user_company, pass_bot=True)
    bot.register_message_handler(state=MyStates.answer_to_question, callback=next_question, pass_bot=True,
                                 next_question=True)
    bot.register_message_handler(state=MyStates.answer_to_question, callback=get_answer_from_user, pass_bot=True,
                                 finish_poll=False)
    bot.register_message_handler(state=MyStates.answer_to_question, callback=send_user_answers_to_db, pass_bot=True,
                                 finish_poll=True)

    """   Регистрация обработчиков нажатий на клавиатуру   """
    bot.register_callback_query_handler(func=lambda callback: callback.data == "scenario",
                                        callback=callback_scenario, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "technical_tasks_and_commercial_offer",
                                        callback=callback_technical_tasks_and_commercial_offer, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "chat_with_operator",
                                        callback=callback_chat_with_operator, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "instant_messaging_service",
                                        callback=dialog_with_operator.callback_instant_messaging_service, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "upload_report",
                                        callback=callback_upload_report, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "blog",
                                        callback=callback_blog, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data in get_directories(),
                                        callback=callback_query_for_scenario, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data,
                                        callback=callback_for_section, pass_bot=True,
                                        path_to_section_without_sub_directory=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data,
                                        callback=callback_for_sub_direction, pass_bot=True,
                                        path_to_section=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data,
                                        callback=callback_section_from_subcategory, pass_bot=True,
                                        path_to_section_with_sub_directory=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == 'back_to_questions',
                                        callback=callback_back_to_questions, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: "question_" in callback.data,
                                        callback=callback_for_questions, pass_bot=True,
                                        check_user_registration=True)
    bot.register_callback_query_handler(func=lambda callback: "question_" in callback.data,
                                        callback=callback_for_registration, pass_bot=True,
                                        check_user_registration=False)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "cancel_from_inline_menu",
                                        callback=callback_cancel_from_inline_menu, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "cancel_to_directions",
                                        callback=callback_cancel_to_directions, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "enter_into_a_dialog",
                                        callback=dialog_with_operator.callback_enter_into_a_dialog, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "cancel_from_dialog",
                                        callback=dialog_with_operator.callback_cancel_from_dialog, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "change_answer",
                                        callback=callback_for_change_answer, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "technical_tasks",
                                        callback=callback_technical_tasks, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == "commercial_offers",
                                        callback=callback_commercial_offer, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: 'tex_' in callback.data,
                                        callback=send_document_to_user.callback_for_registration_technical_exercise,
                                        pass_bot=True)

    bot.register_callback_query_handler(
        func=lambda callback: callback.data in ('requests', 'clients', 'tasks', 'settings'),
        callback=callbacks_for_operator.callback_for_enter_menu, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: 'send_file_' in callback.data,
                                        callback=send_document_to_user.callback_for_send_file, pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: callback.data == 'technical_tasks_for_operator',
                                        callback=callbacks_for_operator.callback_technical_tasks_for_operator,
                                        pass_bot=True)
    bot.register_callback_query_handler(func=lambda callback: 'client_grade_yes' or 'client_grade_yes' in callback.data,
                                        callback=callbacks_for_clients.callback_for_grade, pass_bot=True)


register_functions_for_bot()

bot.infinity_polling(skip_pending=True)
# app = flask.Flask(__name__)
#
#
# @app.route('/', methods=['GET', 'HEAD'])
# def index():
#     return 'OK'
#
#
## Обработка POST-запроса от Telegram Bot API
# @app.route(WEBHOOK_URL_PATH, methods=['POST'])
# def webhook():
#     """Обработка http-запросов, которые telegram пересылает на наш сервер"""
#     if flask.request.headers.get('content-type') == 'application/json':
#         json_string = flask.request.get_data().decode('utf-8')
#         update = telebot.types.Update.de_json(json_string)
#         bot.process_new_updates([update])
#         return ''
#     else:
#         flask.abort(403)
