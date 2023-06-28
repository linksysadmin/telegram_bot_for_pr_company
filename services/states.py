from telebot.handler_backends import State, StatesGroup


class GeneralStates(StatesGroup):
    name = State()
    phone_number = State()
    company = State()
    website = State()
    request_for_dialogue = State()
    dialogue_with_operator = State()
    get_technical_task_file = State()
    get_commercial_offer_file = State()
    get_report_file = State()
    get_other_file = State()
    answer_to_question = State()
    chat_gpt = State()


class OperatorStates(StatesGroup):
    change_question = State()
    add_question = State()
    dialogue_with_client = State()
    get_technical_task_file_in_dialogue = State()
    get_commercial_offer_file_in_dialogue = State()
    get_report_file_in_dialogue = State()
    get_other_file_in_dialogue = State()
