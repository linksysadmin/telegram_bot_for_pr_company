import logging

from handlers.keyboards import keyboard_for_briefings, \
    keyboard_for_questions, keyboard_for_direction, keyboard_for_sub_direction, keyboard_enter_menu_for_clients, \
    keyboard_for_answer
from services.db_data import get_data_briefings, get_directions_from_db, get_question_and_answers_from_db
from services.states import MyStates
from handlers.text_messages import TEXT_MESSAGES

logger = logging.getLogger(__name__)


def callback_scenario(call, bot):
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.send_message(call.message.chat.id, TEXT_MESSAGES['menu'], reply_markup=keyboard_for_briefings())
    logger.info(f'Состояние пользователя - {bot.get_state(call.message.chat.id, call.from_user.id)}')


def callback_formation_of_the_cp(call, bot):
    pass
    # bot.delete_message(call.message.chat.id, call.message.id)
    # bot.send_message(call.message.chat.id, TEXT_MESSAGES['menu'], reply_markup=keyboard_for_scenario())
    # logger.info(f'Состояние пользователя - {bot.get_state(call.message.chat.id, call.from_user.id)}')


def callback_chat_with_operator(call, bot):
    pass
    # bot.delete_message(call.message.chat.id, call.message.id)
    # bot.send_message(call.message.chat.id, TEXT_MESSAGES['menu'], reply_markup=keyboard_for_scenario())
    # logger.info(f'Состояние пользователя - {bot.get_state(call.message.chat.id, call.from_user.id)}')


def callback_upload_report(call, bot):
    pass
    # bot.delete_message(call.message.chat.id, call.message.id)
    # bot.send_message(call.message.chat.id, TEXT_MESSAGES['menu'], reply_markup=keyboard_for_scenario())
    # logger.info(f'Состояние пользователя - {bot.get_state(call.message.chat.id, call.from_user.id)}')


def callback_blog(call, bot):
    pass
    # bot.delete_message(call.message.chat.id, call.message.id)
    # bot.send_message(call.message.chat.id, TEXT_MESSAGES['blog'], reply_markup=keyboard_for_scenario())
    # logger.info(f'Состояние пользователя - {bot.get_state(call.message.chat.id, call.from_user.id)}')


def callback_query_for_scenario(call, bot):
    logger.info(f'callback_query_for_scenario: пришел callback: {call.data}')
    if call.data in [direction[0] for direction in get_directions_from_db()]:
        direction = call.data
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=TEXT_MESSAGES['menu'],
                              reply_markup=keyboard_for_direction(direction=direction))
    elif call.data in [question[1] for question in get_data_briefings()]:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=TEXT_MESSAGES['scenario'])


def callback_for_sub_direction(call, bot):
    logger.info(f'callback_for_sub_direction: пришел callback: {call.data}')
    path = call.data
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=keyboard_for_sub_direction(path))


def callback_for_section(call, bot):
    logger.info(f'callback_for_section: пришел callback: {call.data}')
    path = call.data
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=keyboard_for_questions(path))


def callback_section_from_subcategory(call, bot):
    logger.info(f'callback_section_from_subcategory: пришел callback: {call.data}')
    path = call.data
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=TEXT_MESSAGES['menu'],
                          reply_markup=keyboard_for_questions(path))


def callback_cancel_from_inline_menu(call, bot):
    logger.info(f'callback_cancel_from_inline_menu: пришел callback: {call.data}')
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=TEXT_MESSAGES['start'].format(username=call.from_user.first_name,
                                                                    user_id=call.from_user.id),
                          reply_markup=keyboard_enter_menu_for_clients())


def callback_for_questions(call, bot):
    logger.info(f'callback_for_questions: пришел callback: {call.data}')
    id_question = call.data.split('_')[1]
    bot.set_state(call.from_user.id, MyStates.answer_to_question, call.from_user.id)
    question, answers = get_question_and_answers_from_db(id_question)
    bot.send_message(call.message.chat.id, f'Вы зарегистрированы, ответьте на вопрос:\n\n{question}?', reply_markup=keyboard_for_answer(answers))


def callback_for_registration(call, bot):
    logger.info(f'callback_for_registration: пришел callback: {call.data}')
    id_question = call.data.split('_')[1]
    bot.set_state(call.from_user.id, MyStates.name, call.from_user.id)
    bot.add_data(call.from_user.id, call.message.chat.id, id_question=id_question)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Для того, чтобы ответить на вопросы вы должны указать:\nВаше имя\nТелефон\nКомпанию.'
                               '\n\nНапишите пожалуйста ваше имя:\n\n/cancel - отменить')
    logger.info(f'Состояние пользователя - {bot.get_state(call.message.chat.id, call.from_user.id)}')


