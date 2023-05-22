#!/bin/bash
source /home/inside/code/kwork_telegram_bot_for_KP/venv/bin/activate
exec gunicorn -c "/home/inside/code/kwork_telegram_bot_for_KP/gunicorn_config.py" main:app