import logging
import re

import telebot

from config import REDIS
from services.db_data import check_user_in_database, get_data_briefings

logger = logging.getLogger(__name__)


class CheckPathToSection(telebot.custom_filters.SimpleCustomFilter):
    key = 'path_to_section'

    def check(self, call):
        if call.data in set(f'{i[1]}|{i[2]}' for i in get_data_briefings() if i[2] is not None):
            return True
        else:
            return False


class CheckPathToSectionWithSubDirectory(telebot.custom_filters.SimpleCustomFilter):
    key = 'path_to_section_with_sub_directory'

    def check(self, call):
        if call.data in set(f'{i[1]}|{i[2]}|{i[3]}' for i in get_data_briefings() if i[2] is not None):
            return True
        else:
            return False


class CheckPathToSectionWithoutSubDirectory(telebot.custom_filters.SimpleCustomFilter):
    key = 'path_to_section_without_sub_directory'

    def check(self, call):
        if call.data in set(f'{i[1]}|{i[3]}' for i in get_data_briefings() if i[2] is None):
            return True
        else:
            return False


class CheckUserRegistration(telebot.custom_filters.SimpleCustomFilter):
    key = 'check_user_registration'

    def check(self, call):
        if check_user_in_database(call.from_user.id):
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
        if message.text == 'Отправить ответ':
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


class CheckAnswer(telebot.custom_filters.SimpleCustomFilter):
    key = 'check_answer'

    def check(self, message):
        if message.text == 'Да':
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


def check_user_in_direction(user_id: int) -> bool:
    direction = REDIS.get(f'user:{user_id}:check_direction')
    logger.info(f'{direction}: {user_id}')
    if direction is not None:
        return True
    else:
        return False
