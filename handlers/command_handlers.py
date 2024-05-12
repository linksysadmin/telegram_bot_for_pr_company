import logging

from config import bot
from handlers.text_messages import TEXT_MESSAGES
from handlers.keyboards import remove_keyboard, general_keyboard, operator_keyboard, partner_keyboard


from services.db_data import db
from services.states import GeneralStates

logger = logging.getLogger(__name__)


class BaseCommands:
    def start(self, message):
        raise NotImplementedError("В дочернем классе должен быть переопределен метод start()")

    def test(self, message):
        raise NotImplementedError("В дочернем классе должен быть переопределен метод test()")

    def cancel(self, message):
        user_id = message.from_user.id
        remove_keyboard(message, bot, 'Отменено')
        bot.send_message(message.chat.id, 'Главное меню', reply_markup=general_keyboard.enter_menu())
        bot.delete_state(user_id)



class UnauthorizedCommands(BaseCommands):

    name = 'unauthorized'

    def start(self, message):
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

    def test(self, message):
        pass


class ClientCommands(BaseCommands):

    name = 'client'

    def start(self, message):
        logger.info(f'Пользователь {message.from_user.id} начал общение с ботом')
        user_id = message.from_user.id
        user_data = db.get_users_data(user_id)
        has_documents = bool(user_data['documents'])
        keyboard = general_keyboard.enter_menu(doc=has_documents)
        client_state = bot.get_state(user_id, message.chat.id)
        text_message = TEXT_MESSAGES['start'].format(username=user_data['name'], company=user_data['company'])
        if client_state is None or client_state == 'MyStates:dialogue_with_operator':
            bot.send_message(message.chat.id, text_message, reply_markup=keyboard)

        else:
            bot.delete_state(user_id, message.chat.id)
            remove_keyboard(message, bot, 'Отменено')
            bot.send_message(message.chat.id, text_message, reply_markup=keyboard)

        logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')



    def test(self, message):
        pass


class OperatorCommands(BaseCommands):

    name = 'operator'

    def start(self, message):
        logger.info(f'Operator {message.from_user.first_name} (id: {message.from_user.id}) started a conversation')
        state = bot.get_state(message.from_user.id, message.chat.id)
        if state is None or state == 'MyStates:dialogue_with_client':
            bot.send_message(message.chat.id, TEXT_MESSAGES['start_for_operator'],
                                    reply_markup=operator_keyboard.enter_menu())
        else:
            bot.delete_state(message.from_user.id, message.chat.id)
            remove_keyboard(message, bot, 'Отменено')
            bot.send_message(message.chat.id, TEXT_MESSAGES['start_for_operator'],
                                    reply_markup=operator_keyboard.enter_menu())
        logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')

    def test(self, message):
        logger.info(f'TEST command')
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_chat_action(message.from_user.id, 'typing')
        help_text = "The following commands are available: \n"
        bot.send_message(message.from_user.id, help_text)


class PartnerCommands(BaseCommands):

    name = 'partner'

    def start(self, message):
        logger.info(f'Партнер {message.from_user.id} начал общение с ботом')
        partner_id = message.from_user.id
        user_data = db.get_users_data(partner_id)
        has_documents = bool(user_data['documents'])
        keyboard = partner_keyboard.enter_menu(doc=has_documents)
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

    def test(self, message):
        pass



unauthorized_command = UnauthorizedCommands()
operator_command = OperatorCommands()
client_command = ClientCommands()
partner_command = PartnerCommands()

