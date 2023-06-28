import os


from dotenv import load_dotenv

load_dotenv()

# FOR OPENAI_API(ChatGPT)
OPENAI_API_TOKEN = os.getenv('OPENAI_API_TOKEN')

# FOR TELEGRAM_API
TELEGRAM_BOT_API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')
OPERATOR_ID = int(os.getenv('OPERATOR_ID'))



# FOR MySQL
MySQL_HOST = os.getenv('MySQL_HOST')
MySQL_USER = os.getenv('MySQL_USER')
MySQL_PASS = os.getenv('MySQL_PASS')
MySQL_DB = os.getenv('MySQL_DB')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_FOR_TECHNICAL_TASKS = f'{BASE_DIR}/static/documents/technical_tasks'
DIR_FOR_COMMERCIAL_OFFERS = f'{BASE_DIR}/static/documents/commercial_offers'
DIR_FOR_REPORTS = f'{BASE_DIR}/static/documents/reports'
DIR_FOR_OTHER_FILES = f'{BASE_DIR}/static/documents/other_documents'
DIR_FOR_SAVE_DIALOGS = f'{BASE_DIR}/static/documents/dialogs'

