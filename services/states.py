import logging

from telebot.handler_backends import State, StatesGroup

logger = logging.getLogger(__name__)


class MyStates(StatesGroup):
    request = State()
    client = State()
    dialogue_with_client = State()
    dialogue_with_operator = State()
    name = State()
    phone_number = State()
    company = State()
    website = State()
    answer_to_question = State()
