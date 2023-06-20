import logging
import re

import telebot

from config import OPERATOR_ID
from services.db_data import get_data_questions, check_client_in_database

logger = logging.getLogger(__name__)


class CheckSubDirectory(telebot.custom_filters.SimpleCustomFilter):
    key = 'sub_directory'

    def check(self, call):
        if call.data in set(f'{i[1]}|{i[2]}' for i in get_data_questions() if i[2] is not None):
            return True
        else:
            return False


class CheckSection(telebot.custom_filters.SimpleCustomFilter):
    key = 'section'

    def check(self, call):
        data_questions = get_data_questions()
        if call.data in set(f'{i[1]}|{i[2]}|{i[3]}' for i in data_questions if i[2] is not None) \
                or call.data in set(f'{i[1]}|{i[3]}' for i in data_questions if i[2] is None):
            return True
        else:
            return False


class CheckClient(telebot.custom_filters.SimpleCustomFilter):
    key = 'client'

    def check(self, call):
        if check_client_in_database(call.from_user.id):
            return True
        else:
            return False


class CheckOperator(telebot.custom_filters.SimpleCustomFilter):
    key = 'operator'

    def check(self, message):
        if message.from_user.id == OPERATOR_ID:
            return True
        else:
            return False


class CheckTextOnlyInMessage(telebot.custom_filters.SimpleCustomFilter):
    key = 'text_only'

    def check(self, message):
        if message.text is not None:
            return True
        else:
            return False


class CheckDocumentInMessage(telebot.custom_filters.SimpleCustomFilter):
    key = 'document'

    def check(self, message):
        if message.document is not None:
            return True
        else:
            return False


class CheckPhotoInMessage(telebot.custom_filters.SimpleCustomFilter):
    key = 'photo'

    def check(self, message):
        if message.photo is not None:
            return True
        else:
            return False


class CheckPhoneNumber(telebot.custom_filters.SimpleCustomFilter):
    key = 'check_phone'

    def check(self, message):
        pattern = re.compile(r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')
        if bool(pattern.match(str(message.text))) is True:
            return True
        else:
            return False


class ContactForm(telebot.custom_filters.SimpleCustomFilter):
    key = 'contact_form'

    def check(self, message):
        return message.contact is not None


class FinishPoll(telebot.custom_filters.SimpleCustomFilter):
    key = 'finish_poll'

    def check(self, message):
        if message.text == '✅ Отправить ответ':
            return True
        else:
            return False


class NextQuestion(telebot.custom_filters.SimpleCustomFilter):
    key = 'next_question'

    def check(self, message):
        if message.text in ['Следующий вопрос']:
            return True
        else:
            return False


class CheckConsent(telebot.custom_filters.SimpleCustomFilter):
    key = 'check_consent'

    def check(self, message):
        if message.text == 'Отправить':
            return True
        else:
            return False


class CheckFile(telebot.custom_filters.SimpleCustomFilter):
    key = 'check_file'

    def check(self, message):
        if message.document is not None:
            return True
        else:
            return False


class CheckChangeQuestion(telebot.custom_filters.SimpleCustomFilter):
    key = 'check_question'

    def check(self, message):
        parts = message.text.split('||')
        if len(parts) == 2:
            return True
        else:
            return False
