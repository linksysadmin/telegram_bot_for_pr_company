# -*- coding: utf-8 -*-
import logging

import flask
import colorlog
import telebot
from telebot import custom_filters
from telebot.storage import StateRedisStorage

from config import TELEGRAM_BOT_API_TOKEN

from handlers.register_functions import *

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

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logging.basicConfig(handlers=[console_handler], level=logging.INFO)

bot = telebot.TeleBot(TELEGRAM_BOT_API_TOKEN, state_storage=StateRedisStorage(), parse_mode='HTML')
registration_filters(bot, custom_filters)
registration_commands(bot)
registration_file_handling(bot)
registration_states(bot)
registration_games(bot)
registration_menu_navigation(bot)

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
