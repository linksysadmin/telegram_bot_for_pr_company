# -*- coding: utf-8 -*-
import logging
from logging.handlers import TimedRotatingFileHandler

import telebot
import flask
import colorlog

from handlers.register import RegisterTelegramFunctions
from config import bot

from services.redis_db import redis_cache

formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(name)s %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%m.%d.%Y',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    })
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
file_handler = TimedRotatingFileHandler(f'log.log')
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logging.basicConfig(handlers=[console_handler, file_handler], level=logging.INFO)
logger = logging.getLogger(__name__)


RegisterTelegramFunctions()


try:
    bot.infinity_polling(skip_pending=True)
except KeyboardInterrupt:
    print('Выход из программы')
finally:
    redis_cache.clear_all_cache()

try:
    app = flask.Flask(__name__)
    @app.route('/', methods=['POST'])
    def webhook():
        """Обработка http-запросов, которые telegram пересылает на наш сервер"""
        if flask.request.headers.get('content-type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            logger.error('abort(403)')
            flask.abort(403)
except Exception as e:
    logger.error(e)
finally:
    redis_cache.clear_all_cache()
#
