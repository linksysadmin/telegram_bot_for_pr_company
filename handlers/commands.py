import logging

from config import BASE_DIR
from handlers.text_messages import TEXT_MESSAGES
from handlers.keyboards import remove_keyboard, keyboard_enter_menu_for_clients, keyboard_for_briefings

from services.get_excel_file import get_excel_file
from services.redis_db import delete_user_answers, get_user_answers
from services.send_info_to_database import check_admin_in_db
from services.states import MyStates

logger = logging.getLogger(__name__)


def start(message, bot):
    logger.info(f'User {message.from_user.first_name} (id: {message.from_user.id}) started a conversation')
    if bot.get_state(message.from_user.id, message.chat.id) is not None:
        bot.delete_state(message.from_user.id, message.chat.id)
        remove_keyboard(message, bot, 'Отменено')
    bot.send_message(message.chat.id, TEXT_MESSAGES['start'].format(username=message.from_user.first_name,
                                                                    user_id=message.from_user.id
                                                                    ), reply_markup=keyboard_enter_menu_for_clients())
    logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')


def info(message, bot):
    if bot.get_state(message.from_user.id, message.chat.id) is not None:
        bot.delete_state(message.from_user.id, message.chat.id)
        remove_keyboard(message, bot, 'Отменено')

    bot.send_message(message.chat.id, TEXT_MESSAGES['info'])
    logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')


def get_excel_and_send_to_user(message, bot):
    if bot.get_state(message.from_user.id, message.chat.id) is not None:
        bot.delete_state(message.from_user.id, message.chat.id)
        logger.info(f'State пользователя удалён -- {bot.get_state(message.from_user.id, message.chat.id)}')
        remove_keyboard(message, bot, 'Отменено')
    if check_admin_in_db(message.from_user.id) is True:
        if get_excel_file() is True:
            with open(f'{BASE_DIR}/excel_files/пользователи.xlsx', 'rb') as f:
                bot.send_document(chat_id=message.chat.id, document=f)
        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Введите пароль: ')
        bot.set_state(message.chat.id, MyStates.password, message.from_user.id)


def delete_state_(message, bot):
    """ Выход из STATE """
    if get_user_answers(user=message.from_user.id):
        delete_user_answers(user=message.from_user.id)
    remove_keyboard(message, bot, 'Отменено')
    bot.send_message(message.chat.id, 'Главное меню',
                     reply_markup=keyboard_enter_menu_for_clients())
    bot.delete_state(message.from_user.id, message.chat.id)
    logger.info(f'State пользователя удалён -- {bot.get_state(message.from_user.id, message.chat.id)}')



commands_to_message = {
    "start": start,
    "info": info,
    "get_excel": get_excel_and_send_to_user,
    "cancel": delete_state_,
}
