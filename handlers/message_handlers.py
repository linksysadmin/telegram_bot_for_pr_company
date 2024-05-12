import logging

from openai import error

from config import (DIR_FOR_COMMERCIAL_OFFERS, DIR_FOR_REPORTS, DIR_FOR_OTHER_FILES, DIR_FOR_TECHNICAL_TASKS,
                    bot, OPERATOR_ID)
from handlers.command_handlers import client_command
from handlers.keyboards import remove_keyboard, general_keyboard, operator_keyboard, client_keyboard
from handlers.text_messages import TEXT_MESSAGES
from services.chatgpt import generate_response_from_chat_gpt
from services.db_data import db
from services.file_handler import save_file
from services.redis_db import redis_cache
from services.states import GeneralStates, OperatorStates
from services.string_parser import TextParser
from services.dialogue_logging import dialogue_logging

logger = logging.getLogger(__name__)


class UserRegistration:

    def get_user_name(self, message):
        """ STATE 1 Получение имени от пользователя """
        bot.add_data(message.from_user.id, message.chat.id, name=message.text,
                            tg_username=message.from_user.username)
        bot.send_message(message.chat.id,
                                'Укажите номер вашего телефона\n\nВы можете нажать клавишу "Отправить номер'
                                ' телефона" для отправки номера 📲', reply_markup=client_keyboard.send_phone())
        bot.set_state(message.chat.id, GeneralStates.phone_number, message.from_user.id)
        logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')

    def get_user_phone(self, message):
        """ STATE 2 - Получение номера телефона от пользователя """
        phone = message.text
        if message.contact is not None:
            phone = message.contact.phone_number
        bot.add_data(message.from_user.id, message.chat.id, phone=phone)
        remove_keyboard(message, bot, 'Укажите ваш Веб-сайт')
        bot.set_state(message.chat.id, GeneralStates.website, message.from_user.id)
        logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')

    def get_user_website(self, message):
        """ STATE 3 - Получение website от пользователя """
        website = message.text
        bot.add_data(message.from_user.id, message.chat.id, website=website)
        bot.send_message(message.chat.id, 'Укажите название вашей компании©️')
        bot.set_state(message.chat.id, GeneralStates.company, message.from_user.id)
        logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')

    def get_user_company(self, message):
        """ STATE 4 - Получение компании от пользователя и отправка данных """
        user_id = message.from_user.id
        company = message.text
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            logger.info(f'Данные, которые ввел пользователь: {data}')
            name = data['name']
            tg_username = data['tg_username']
            phone = data['phone']
            website = data['website']
            db.add_user_data_to_db('clients', user_id, name, tg_username, phone, company, website)
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.chat.id, TEXT_MESSAGES['start'].format(username=name,
                                                                               company=message.text),
                                reply_markup=general_keyboard.enter_menu())
        logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')

    def phone_incorrect(self, message):
        bot.send_message(message.chat.id, 'Некорректный ввод.\nВведите в формате:\n\n"+7XXXXXXXXXX",\n'
                                                 '8XXXXXXXXXX\n9XXXXXXXXX\n\nПример: 89953423452')


class ChatGPT:

    def get_question_from_user_for_chat_gpt(self, message):
        bot.send_chat_action(message.from_user.id, action="typing")
        try:
            answer_from_chat_gpt = generate_response_from_chat_gpt(message.text)
            bot.send_message(message.from_user.id, answer_from_chat_gpt)
        except error.RateLimitError:
            bot.send_message(message.from_user.id, 'Что-то пошло не так')


class TextButtons:

    def next_question(self, message):
        user_id = message.from_user.id
        directory, sub_direction, section = redis_cache.get_directory_subdir_section(message.from_user.id)
        question_id, number = redis_cache.get_id_and_number_of_question(user_id)
        question_data = db.get_question_data_by_path(directory, sub_direction, section, number)
        text = question_data['question_text']
        id_ = question_data['id']
        answers = question_data['answers']
        user_answer = db.get_user_answer(message.from_user.id, id_)
        if user_answer:
            bot.send_message(message.chat.id, f'❓{text}?\n\nВаш ответ:{user_answer}',
                                    reply_markup=client_keyboard.answer(answers))
            return
        bot.set_state(message.from_user.id, GeneralStates.answer_to_question, message.from_user.id)
        bot.send_message(message.chat.id, f'❓{text}?\n\nНапишите ответ и нажмите "✅ Отправить ответ"',
                                reply_markup=client_keyboard.answer(answers))


    def cancel_to_questions(self, message):
        """ Выход из STATE """
        user_id = message.from_user.id
        bot.delete_state(user_id)
        if redis_cache.get_user_answers(user=user_id):
            redis_cache.delete_user_answers(user=user_id)
        directory, sub_direction, section = redis_cache.get_directory_subdir_section(user_id)
        remove_keyboard(message, bot, 'Отменено')
        bot.send_message(user_id, 'Выберите вопрос:',
                                reply_markup=general_keyboard.questions(user_id, directory, sub_direction, section))

    def cancel_to_start_registration(self, message):
        user_id = message.from_user.id
        state = bot.get_state(user_id)
        if state == 'GeneralStates:phone_number':
            remove_keyboard(message, bot, 'Отменено')
        bot.set_state(user_id, GeneralStates.name)
        bot.send_message(user_id, TEXT_MESSAGES['start_unauthorized'])

    def no_next_question(self, message):
        remove_keyboard(message, bot, 'Вопросов в этом направлении больше, нет(')
        client_command.start(message, bot)


class AnswerHandler:

    def get_answer_from_user(self, message):
        match message.text:
            case 'Пол':
                redis_cache.add_answers_to_list(client_id=message.from_user.id, answer=message.text)
                bot.send_message(message.chat.id, f'Выберите пол', reply_markup=client_keyboard.sex())
            case 'Возраст':
                redis_cache.add_answers_to_list(client_id=message.from_user.id, answer=message.text)
                bot.send_message(message.chat.id, f'Выберите возраст', reply_markup=client_keyboard.age())
            case 'Доход' | 'Интересы':
                redis_cache.add_answers_to_list(client_id=message.from_user.id, answer=message.text)
                bot.send_message(message.chat.id, f'Укажите {message.text.lower()}',
                                        reply_markup=client_keyboard.other_answers())
            case _:
                redis_cache.add_answers_to_list(client_id=message.from_user.id, answer=message.text)
                bot.send_message(message.chat.id,
                                        f'Ответ принят, нажмите "✅ Отправить ответ" если больше нечего добавить')

    def send_user_answers_to_db(self, message):
        """ Выход из state вопроса и отправка ответов в базу данных"""
        user_id = message.from_user.id
        text_answers = "|".join(redis_cache.get_user_answers(user_id))
        question_id, number = redis_cache.get_id_and_number_of_question(user_id)
        db.add_user_answers_to_db(user_id=user_id, question_id=question_id, user_response=text_answers)
        redis_cache.delete_user_answers(user=message.from_user.id)
        bot.delete_state(message.from_user.id, message.chat.id)
        remove_keyboard(message, bot, 'Ваш ответ получен!')
        directory, sub_direction, section = redis_cache.get_directory_subdir_section(message.from_user.id)
        bot.send_message(message.chat.id, 'Выберите вопрос:',
                                reply_markup=general_keyboard.questions(message.from_user.id, directory, sub_direction,
                                                                        section))


class QuestionHandler:

    def operator_change_question(self, message):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            question_id = data['question_id_for_change']
        question_text, answers_text = TextParser.get_question_and_answers(message.text)
        db.update_question_and_answers(question_id, question_text, answers_text)
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.chat.id, TEXT_MESSAGES['start_for_operator'],
                                reply_markup=operator_keyboard.enter_menu())

    def operator_add_question(self, message):
        directory, sub_direction, section = redis_cache.get_directory_subdir_section(message.from_user.id)
        question, answers = TextParser.get_question_and_answers(message.text)
        db.add_question_and_answers_(directory, sub_direction, section, question, answers)
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.chat.id, 'Вопрос добавлен в раздел!')

    def incorrect_change_question(self, message):
        bot.send_message(message.chat.id, 'Некорректный ввод Вопроса и ответов\n\n'
                                                 'Пример:\nВОПРОС || ОТВЕТ1| ОТВЕТ2| ОТВЕТ3')

    @staticmethod
    def incorrect_add_question(self, message):
        bot.send_message(message.chat.id, 'Некорректный ввод для добавления')


class FileHandler:

    def __download_and_save_file(self, message, path):
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        save_file(path=path, file=downloaded_file, filename=message.document.file_name)
        bot.send_message(message.from_user.id, 'Файл загружен в базу данных')

    def get_technical_task_file(self, message):
        client_id = redis_cache.get_user_to_display_information()
        path = f'{DIR_FOR_TECHNICAL_TASKS}/{client_id}'
        FileHandler.__download_and_save_file(bot, message, path)
        bot.delete_state(message.from_user.id, message.chat.id)

    def get_commercial_offer_file(self, message):
        client_id = redis_cache.get_user_to_display_information()
        path = f'{DIR_FOR_COMMERCIAL_OFFERS}/{client_id}'
        FileHandler.__download_and_save_file(bot, message, path)
        bot.delete_state(message.from_user.id, message.chat.id)

    def get_report_file(self, message):
        client_id = redis_cache.get_user_to_display_information()
        path = f'{DIR_FOR_REPORTS}/{client_id}'
        FileHandler.__download_and_save_file(bot, message, path)
        bot.delete_state(message.from_user.id, message.chat.id)

    def get_other_file(self, message):
        client_id = redis_cache.get_user_to_display_information()
        path = f'{DIR_FOR_OTHER_FILES}/{client_id}'
        FileHandler.__download_and_save_file(bot, message, path)
        bot.delete_state(message.from_user.id, message.chat.id)

    def get_technical_task_file_from_dialogue(self, message):
        client_id = redis_cache.get_first_client_from_queue()
        path = f'{DIR_FOR_TECHNICAL_TASKS}/{client_id}'
        FileHandler.__download_and_save_file(bot, message, path)
        bot.send_document(client_id, document=message.document.file_id)
        bot.set_state(message.from_user.id, OperatorStates.dialogue_with_client)

    def get_commercial_offer_file_from_dialogue(self, message):
        client_id = redis_cache.get_first_client_from_queue()
        path = f'{DIR_FOR_COMMERCIAL_OFFERS}/{client_id}'
        FileHandler.__download_and_save_file(bot, message, path)
        bot.send_document(client_id, document=message.document.file_id)
        bot.set_state(message.from_user.id, OperatorStates.dialogue_with_client)

    def get_report_file_from_dialogue(self, message):
        client_id = redis_cache.get_first_client_from_queue()
        path = f'{DIR_FOR_REPORTS}/{client_id}'
        FileHandler.__download_and_save_file(bot, message, path)
        bot.send_document(client_id, document=message.document.file_id)
        bot.set_state(message.from_user.id, OperatorStates.dialogue_with_client)

    def get_other_file_from_dialogue(self, message):
        client_id = redis_cache.get_first_client_from_queue()
        path = f'{DIR_FOR_OTHER_FILES}/{client_id}'
        FileHandler.__download_and_save_file(bot, message, path)
        bot.send_document(client_id, document=message.document.file_id)
        bot.set_state(message.from_user.id, OperatorStates.dialogue_with_client)

    def file_incorrect(self, message):
        bot.send_message(message.chat.id, 'Это не файл!')


class DialogWithOperator:

    def send_request_to_operator(self, message):
        bot.send_message(message.from_user.id, f'Подождите пожалуйста пока оператор к вам присоединиться...')

    def send_message_to_client(self, message):
        client_id = redis_cache.get_first_client_from_queue()
        log_dialogue = dialogue_logging(client_id)
        bot.send_message(client_id, f'💬Сообщение от оператора:\n\n{message.text}')
        log_dialogue.info(f'Сообщение от оператора: {message.text}')

    def send_document_to_client(self, message):
        client_id = redis_cache.get_first_client_from_queue()
        log_dialogue = dialogue_logging(client_id)
        bot.send_document(client_id, document=message.document.file_id)
        log_dialogue.info('Оператор отправил файл')

    def send_photo_to_client(self, message):
        client_id = redis_cache.get_first_client_from_queue()
        log_dialogue = dialogue_logging(client_id)
        photo_id = message.photo[-1].file_id
        bot.send_photo(client_id, photo=photo_id)
        log_dialogue.info('Оператор отправил картинку')

    def send_message_to_operator(self, message):
        user_id = message.from_user.id
        user_data = db.get_users_data(user_id)
        log_dialogue = dialogue_logging(user_id)
        log_dialogue.info(f'{user_data["company"]}|Сообщение от {user_data["name"]}: {message.text}')
        bot.send_message(OPERATOR_ID, f'Вы общаетесь: {user_data["name"]}\n'
                                             f'Компания: {user_data["company"]}\n'
                                             f'Телефон: {user_data["phone"]}\n\n'
                                             f'Сообщение:\n{message.text}',
                                reply_markup=operator_keyboard.menu_in_dialogue())

    def send_document_to_operator(self, message):
        client_id = message.from_user.id
        log_dialogue = dialogue_logging(client_id)
        bot.send_document(OPERATOR_ID, document=message.document.file_id)
        log_dialogue.info('Клиент отправил файл')

    def send_photo_to_operator(self, message):
        client_id = message.from_user.id
        log_dialogue = dialogue_logging(client_id)
        photo_id = message.photo[-1].file_id
        bot.send_photo(OPERATOR_ID, photo=photo_id)
        log_dialogue.info('Клиент отправил картинку')
