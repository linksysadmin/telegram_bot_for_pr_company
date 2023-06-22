import logging

from handlers.text_messages import TEXT_MESSAGES
from handlers.keyboards import remove_keyboard, ClientKeyboards, OperatorKeyboards, PartnerKeyboards, GeneralKeyboards
from services.db_data import get_users_data
from services.redis_db import redis_cache
from services.states import MyStates

logger = logging.getLogger(__name__)


class GeneralCommands:
    @staticmethod
    def start_unauthorized(message, bot):
        user_id = message.from_user.id
        logger.info(f'Новый пользователь {user_id} начал общение с ботом')
        state = bot.get_state(user_id)
        if state is not None:
            if state in ('MyStates:type_of_user', 'MyStates:name', 'MyStates:phone_number', 'MyStates:company'):
                if state == 'MyStates:phone_number':
                    remove_keyboard(message, bot, 'Отменено')
                    bot.send_message(user_id, TEXT_MESSAGES['start_unauthorized'], reply_markup=GeneralKeyboards.type_of_user())
                    bot.set_state(user_id, MyStates.type_of_user)
                    return
                bot.set_state(user_id, MyStates.type_of_user)
                bot.send_message(user_id, TEXT_MESSAGES['start_unauthorized'],
                                 reply_markup=GeneralKeyboards.type_of_user())
                return
            bot.delete_state(message.from_user.id, message.chat.id)
            remove_keyboard(message, bot, 'Отменено')
        bot.set_state(message.from_user.id, MyStates.type_of_user)
        bot.send_message(message.chat.id, TEXT_MESSAGES['start_unauthorized'], reply_markup=GeneralKeyboards.type_of_user())
        logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')


    @staticmethod
    def cancel(message, bot):
        """ Выход из STATE """
        user_id = message.from_user.id
        state = bot.get_state(user_id)
        match state:
            case 'MyStates:answer_to_question':
                bot.delete_state(user_id)
                if redis_cache.get_user_answers(user=user_id):
                    redis_cache.delete_user_answers(user=user_id)
                path = redis_cache.get_keyboard_for_questions(user_id)
                remove_keyboard(message, bot, 'Отменено')
                bot.send_message(user_id, 'Выберите вопрос:',
                                 reply_markup=ClientKeyboards.questions(user_id, path=path))
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
                         reply_markup=GeneralKeyboards.enter_menu())
        bot.delete_state(user_id)
        logger.info(f'State пользователя удалён -- {bot.get_state(user_id)}')


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
        # bot.send_message(message.from_user.id, "If you think so...")
        # bot.send_chat_action(message.from_user.id, 'typing')  # show the bot "typing" (max. 5 secs)
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
