# -*- coding: utf-8 -*-
import logging

import flask
import colorlog
import telebot
from telebot import custom_filters
from telebot.storage import StateRedisStorage

from config import TELEGRAM_BOT_API_TOKEN

from handlers.register_bot_functions import register_functions_for_bot

from services.filters import CheckPhoneNumber, CheckConsent, \
    ContactForm, CheckFile, CheckUserRegistration, CheckPathToSection, CheckPathToSectionWithoutSubDirectory, \
    CheckPathToSectionWithSubDirectory, FinishPoll, NextQuestion, CheckOperator

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


register_functions_for_bot(bot=bot, custom_filters=custom_filters)

bot.infinity_polling(skip_pending=True)
# app = flask.Flask(__name__)

# @app.route('/', methods=['POST'])
# def webhook():
#     """Обработка http-запросов, которые telegram пересылает на наш сервер"""
#     if flask.request.headers.get('content-type') == 'application/json':
#         json_string = flask.request.get_data().decode('utf-8')
#         update = telebot.types.Update.de_json(json_string)
#         bot.process_new_updates([update])
#         return ''
#     else:
#         flask.abort(403)
