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
    get_technical_task_file = State()
    get_commercial_offer_file = State()
    get_report_file = State()
    get_other_file = State()
