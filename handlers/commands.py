import logging

from handlers.text_messages import TEXT_MESSAGES
from handlers.keyboards import remove_keyboard, OperatorKeyboards, PartnerKeyboards, GeneralKeyboards
from services.db_data import get_users_data
from services.redis_db import redis_cache
from services.states import GeneralStates

logger = logging.getLogger(__name__)


class GeneralCommands:
    @staticmethod
    def start_unauthorized(message, bot):
        user_id = message.from_user.id
        logger.info(f'Новый пользователь {user_id} начал общение с ботом')
        state = bot.get_state(user_id)
        if state is not None:
            if state in ('MyStates:name', 'MyStates:phone_number', 'MyStates:company'):
                if state == 'MyStates:phone_number':
                    remove_keyboard(message, bot, 'Отменено')
                    bot.send_message(user_id, TEXT_MESSAGES['start_unauthorized'])
                    bot.set_state(user_id, GeneralStates.name)
                    return
                bot.set_state(user_id, GeneralStates.name)
                bot.send_message(user_id, TEXT_MESSAGES['start_unauthorized'])
                return
            bot.delete_state(message.from_user.id, message.chat.id)
            remove_keyboard(message, bot, 'Отменено')
        bot.set_state(message.from_user.id, GeneralStates.name)
        bot.send_message(message.chat.id, TEXT_MESSAGES['start_unauthorized'])
        logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')




class ClientCommands:
    @staticmethod
    def start(message, bot):
        logger.info(f'Пользователь {message.from_user.id} начал общение с ботом')
        user_id = message.from_user.id
        user_data = get_users_data(user_id)
        has_documents = bool(user_data['documents'])
        keyboard = GeneralKeyboards.enter_menu(doc=has_documents)
        client_state = bot.get_state(user_id, message.chat.id)
        text_message = TEXT_MESSAGES['start'].format(username=user_data['name'], company=user_data['company'])
        if client_state is None or client_state == 'MyStates:dialogue_with_operator':
            bot.send_message(message.chat.id, text_message, reply_markup=keyboard)

        else:
            bot.delete_state(user_id, message.chat.id)
            remove_keyboard(message, bot, 'Отменено')
            bot.send_message(message.chat.id, text_message, reply_markup=keyboard)

        logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')




class OperatorCommands:
    @staticmethod
    def start(message, bot):
        logger.info(f'Operator {message.from_user.first_name} (id: {message.from_user.id}) started a conversation')
        state = bot.get_state(message.from_user.id, message.chat.id)
        if state is None or state == 'MyStates:dialogue_with_client':
            bot.send_message(message.chat.id, TEXT_MESSAGES['start_for_operator'],
                             reply_markup=OperatorKeyboards.enter_menu())
        else:
            bot.delete_state(message.from_user.id, message.chat.id)
            remove_keyboard(message, bot, 'Отменено')
            bot.send_message(message.chat.id, TEXT_MESSAGES['start_for_operator'],
                             reply_markup=OperatorKeyboards.enter_menu())
        logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')

    @staticmethod
    def test_(message, bot):
        logger.info(f'TEST command')
        bot.delete_state(message.from_user.id, message.chat.id)
        # bot.send_chat_action(message.from_user.id, action="upload_document")
        # bot.send_contact(message.chat.id, phone_number='+792343242332', first_name='Ваш оператор: Андрей')
        # bot.send_dice(message.from_user.id, emoji='🎰', timeout=4)
        bot.send_chat_action(message.from_user.id, 'typing')
        help_text = "The following commands are available: \n"
        bot.send_message(message.from_user.id, help_text)  # send the generated help page    time.sleep(3)


class PartnerCommands:
    @staticmethod
    def start(message, bot):
        logger.info(f'Партнер {message.from_user.id} начал общение с ботом')
        partner_id = message.from_user.id
        user_data = get_users_data(partner_id)
        has_documents = bool(user_data['documents'])
        keyboard = PartnerKeyboards.enter_menu(doc=has_documents)
        client_state = bot.get_state(partner_id, message.chat.id)
        text_message = TEXT_MESSAGES['start_for_partners'].format(username=user_data['name'],
                                                                  company=user_data['company'])
        if client_state is None or client_state == 'MyStates:dialogue_with_operator':
            bot.send_message(message.chat.id, text_message, reply_markup=keyboard)

        else:
            bot.delete_state(partner_id, message.chat.id)
            remove_keyboard(message, bot, 'Отменено')
            bot.send_message(message.chat.id, text_message, reply_markup=keyboard)

        logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')
