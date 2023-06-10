import os

import redis
from dotenv import load_dotenv

load_dotenv()

# FOR TELEGRAM_API
TELEGRAM_BOT_API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')

TELEGRAM_GROUP_CHAT_ID = os.getenv('TELEGRAM_GROUP_CHAT_ID')
PASSWORD_FOR_ADMIN = os.getenv('PASSWORD_FOR_ADMIN')
OPERATOR_ID = int(os.getenv('OPERATOR_ID'))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REDIS = redis.Redis(host='localhost', port=6379, db=0)

# FOR MySQL
MySQL_HOST = os.getenv('MySQL_HOST')
MySQL_USER = os.getenv('MySQL_USER')
MySQL_PASS = os.getenv('MySQL_PASS')
MySQL_DB = os.getenv('MySQL_DB')


DIR_FOR_TECHNICAL_TASKS = f'{BASE_DIR}/static/documents/technical_tasks'
DIR_FOR_COMMERCIAL_OFFERS = f'{BASE_DIR}/static/documents/commercial_offers'
DIR_FOR_REPORTS = f'{BASE_DIR}/static/documents/reports'
DIR_FOR_OTHER_FILES = f'{BASE_DIR}/static/documents/other'
DIR_FOR_SAVE_DIALOGS = f'{BASE_DIR}/static/documents/dialogs'
