import logging
import time

from telebot import types

from config import COMMANDS_FOR_BOT
from handlers.text_messages import TEXT_MESSAGES
from handlers.keyboards import remove_keyboard, keyboard_enter_menu_for_clients, \
    keyboard_for_questions, keyboard_enter_menu_for_operator
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
        if bot.get_state(message.from_user.id, message.chat.id) in (
                'MyStates:name', 'MyStates:phone_number', 'MyStates:company'):
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


def start_for_operator(message, bot):
    logger.info(f'Operator {message.from_user.first_name} (id: {message.from_user.id}) started a conversation')
    if bot.get_state(message.from_user.id, message.chat.id) is not None:
        bot.delete_state(message.from_user.id, message.chat.id)
        remove_keyboard(message, bot, 'Отменено')
    bot.send_message(message.chat.id, TEXT_MESSAGES['start_for_operator'],
                     reply_markup=keyboard_enter_menu_for_operator())
    logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')


def test_(message, bot):

    logger.info(f'TEST command')
    bot.delete_state(message.from_user.id, message.chat.id)
    # bot.send_chat_action(message.from_user.id, action="upload_document")

    # bot.send_contact(message.chat.id, phone_number='+792343242332', first_name='Ваш оператор: Андрей')
    # bot.send_dice(message.from_user.id, emoji='🎰', timeout=4)
    bot.send_message(message.from_user.id, "If you think so...")
    bot.send_chat_action(message.from_user.id, 'typing')  # show the bot "typing" (max. 5 secs)
    help_text = "The following commands are available: \n"
    for key in COMMANDS_FOR_BOT:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += COMMANDS_FOR_BOT[key] + "\n"
    bot.send_message(message.from_user.id, help_text)  # send the generated help page    time.sleep(3)


def delete_state_(message, bot):
    """ Выход из STATE """
    user_id = message.from_user.id
    state = bot.get_state(user_id)
    match state:
        case 'MyStates:answer_to_question':
            bot.delete_state(user_id)
            if get_user_answers(user=user_id):
                delete_user_answers_from_redis(user=user_id)
            path = get_keyboard_for_questions_from_redis(user_id)
            remove_keyboard(message, bot, 'Отменено')
            bot.send_message(user_id, 'Выберите вопрос:',
                             reply_markup=keyboard_for_questions(user_id, path=path))
            return
        case 'MyStates:name' | 'MyStates:phone_number' | 'MyStates:company' | 'MyStates:website':
            if state == 'MyStates:phone_number':
                remove_keyboard(message, bot, 'Отменено')
            bot.set_state(user_id, MyStates.name)
            bot.send_message(user_id, TEXT_MESSAGES['start_unauthorized'])
            return
        case None:
            return
    remove_keyboard(message, bot, 'Отменено')
    bot.send_message(message.chat.id, 'Главное меню',
                     reply_markup=keyboard_enter_menu_for_clients())
    bot.delete_state(user_id)
    logger.info(f'State пользователя удалён -- {bot.get_state(user_id)}')

