import logging
import re

import telebot

from config import OPERATOR_ID
from services.db_data import get_data_questions, check_client_in_database, check_partner_in_database, \
    get_all_ids_in_section
from services.redis_db import redis_cache

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


class CheckPartner(telebot.custom_filters.SimpleCustomFilter):
    key = 'partner'

    def check(self, call):
        if check_partner_in_database(call.from_user.id):
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


class UserType(telebot.custom_filters.SimpleCustomFilter):
    key = 'user_type'

    def check(self, message):
        if message.text in ('Партнер', 'Клиент'):
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


class SendAnswer(telebot.custom_filters.SimpleCustomFilter):
    key = 'send_answer'

    def check(self, message):
        if message.text == '✅ Отправить ответ':
            return True
        else:
            return False


class CheckQuestionNumber(telebot.custom_filters.SimpleCustomFilter):
    key = 'in_the_range_of_questions'

    def check(self, message):
        user_id = message.from_user.id
        directory, sub_direction, section = redis_cache.get_directory_subdir_section(user_id)
        question_id, number = redis_cache.get_id_and_number_of_question(user_id)

        next_number_of_question = number + 1

        dict_of_numbers_and_ids_questions = get_all_ids_in_section(directory, sub_direction, section)
        next_question_id = dict_of_numbers_and_ids_questions.get(next_number_of_question)

        if next_number_of_question in dict_of_numbers_and_ids_questions:
            redis_cache.set_id_and_number_of_question(user_id, next_question_id, next_number_of_question)
            logger.warning(f'Открыть следующий вопрос под № {next_number_of_question}')
            return True
        else:
            logger.warning(f'Выйти в меню')
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


class CheckAddQuestion(telebot.custom_filters.SimpleCustomFilter):
    key = 'check_add_question'

    def check(self, message):
        parts = message.text.split('||')
        if len(parts) == 2:
            return True
        else:
            return False
