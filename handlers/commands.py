import logging

from handlers.text_messages import TEXT_MESSAGES
from handlers.keyboards import remove_keyboard, keyboard_enter_menu_for_clients, keyboard_for_briefings, \
    keyboard_for_questions
from services.db_data import get_user_data_from_db
from services.redis_db import delete_user_answers_from_redis, get_user_answers, get_keyboard_for_questions_from_redis
from services.states import MyStates

logger = logging.getLogger(__name__)


def start(message, bot):
    logger.info(f'User {message.from_user.first_name} (id: {message.from_user.id}) started a conversation')
    if bot.get_state(message.from_user.id, message.chat.id) is not None:
        bot.delete_state(message.from_user.id, message.chat.id)
        remove_keyboard(message, bot, 'Отменено')
    user_data = get_user_data_from_db(message.from_user.id)
    if user_data['tech_doc'] or user_data['cp_doc']:
        bot.send_message(message.chat.id, TEXT_MESSAGES['start'].format(username=user_data['name'],
                                                                        company=user_data['company']),
                         reply_markup=keyboard_enter_menu_for_clients(doc=True))
        return
    else:
        bot.send_message(message.chat.id, TEXT_MESSAGES['start'].format(username=user_data['name'],
                                                                        company=user_data['company']),
                         reply_markup=keyboard_enter_menu_for_clients())
    logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')


def start_unauthorized(message, bot):
    logger.info(f'User {message.from_user.first_name} (id: {message.from_user.id}) start_unauthorized')
    if bot.get_state(message.from_user.id, message.chat.id) is not None:
        if bot.get_state(message.from_user.id, message.chat.id) in ('MyStates:name', 'MyStates:phone_number', 'MyStates:company'):
            if bot.get_state(message.from_user.id, message.chat.id) == 'MyStates:phone_number':
                remove_keyboard(message, bot, TEXT_MESSAGES['start_unauthorized'])
                bot.set_state(message.from_user.id, MyStates.name)
                return
            bot.set_state(message.from_user.id, MyStates.name)
            bot.send_message(message.chat.id, TEXT_MESSAGES['start_unauthorized'])
            return
        bot.delete_state(message.from_user.id, message.chat.id)
        remove_keyboard(message, bot, 'Отменено')
    bot.set_state(message.from_user.id, MyStates.name)
    bot.send_message(message.chat.id, TEXT_MESSAGES['start_unauthorized'])
    logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')


def delete_state_(message, bot):
    """ Выход из STATE """
    if bot.get_state(message.from_user.id, message.chat.id) == 'MyStates:answer_to_question':
        bot.delete_state(message.from_user.id, message.chat.id)
        if get_user_answers(user=message.from_user.id):
            delete_user_answers_from_redis(user=message.from_user.id)
        path = get_keyboard_for_questions_from_redis(message.from_user.id)
        remove_keyboard(message, bot, 'Отменено')
        bot.send_message(message.chat.id, 'Выберите вопрос:',
                         reply_markup=keyboard_for_questions(message.from_user.id, path=path))
        return
    elif bot.get_state(message.from_user.id, message.chat.id) in ('MyStates:name', 'MyStates:phone_number', 'MyStates:company'):
        if bot.get_state(message.from_user.id, message.chat.id) == 'MyStates:phone_number':
            remove_keyboard(message, bot, 'Отменено')
        bot.set_state(message.from_user.id, MyStates.name)
        bot.send_message(message.chat.id, TEXT_MESSAGES['start_unauthorized'])
        return
    elif bot.get_state(message.from_user.id, message.chat.id) is None:
        return
    remove_keyboard(message, bot, 'Отменено')
    bot.send_message(message.chat.id, 'Главное меню',
                     reply_markup=keyboard_enter_menu_for_clients())
    bot.delete_state(message.from_user.id, message.chat.id)
    logger.info(f'State пользователя удалён -- {bot.get_state(message.from_user.id, message.chat.id)}')

