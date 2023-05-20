#!/bin/bash
source /home/inside/code/bot/telegram_bot/venv/bin/activate
exec gunicorn -c "/home/inside/code/bot/telegram_bot/gunicorn_config.py" main:app