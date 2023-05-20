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
    answer_to_question = State()








    choose_direction = State()

    date_of_birthday = State()
    sex = State()
    email = State()

    send_users_data = State()

    resume = State()

    university = State()
    season = State()

    test = State()
    question = State()

    password = State()
