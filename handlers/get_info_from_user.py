import logging

from handlers.callback import callback_for_questions
from handlers.commands import start
from handlers.keyboards import remove_keyboard, \
    keyboard_send_phone, keyboard_for_answer, keyboard_for_briefings, keyboard_enter_menu_for_clients, \
    keyboard_for_questions, keyboard_for_sex, keyboard_for_age, keyboard_for_other_answers, keyboard_for_change_answer
from handlers.text_messages import TEXT_MESSAGES
from services.db_data import add_users_data_to_db, get_question_and_answers_from_db, add_user_answers_to_db, \
    get_user_answer
from services.redis_db import add_answers_to_list, get_user_answers, \
    get_question_id_from_redis, delete_user_answers_from_redis, get_keyboard_for_questions_from_redis, \
    get_next_question_callback_from_redis, set_question_id_in_redis, set_next_question_callback_in_redis, \
    get_max_questions_from_redis
from services.states import MyStates

logger = logging.getLogger(__name__)


def get_user_name(message, bot):
    """ STATE 1 Получение имени от пользователя """
    bot.add_data(message.from_user.id, message.chat.id, name=message.text)
    bot.send_message(message.chat.id, 'Укажите номер вашего телефона\n\nВы можете нажать клавишу "Отправить номер'
                                      ' телефона" для отправки номера 📲', reply_markup=keyboard_send_phone())
    bot.set_state(message.chat.id, MyStates.phone_number, message.from_user.id)
    logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')


def get_user_phone(message, bot):
    """ STATE 2 - Получение номера телефона от пользователя """
    phone = message.text
    if message.contact is not None:
        phone = message.contact.phone_number
    bot.add_data(message.from_user.id, message.chat.id, phone=phone)
    remove_keyboard(message, bot, 'Напишите название вашей компании')
    bot.set_state(message.chat.id, MyStates.company, message.from_user.id)


def get_user_company(message, bot):
    """ STATE 3 - Получение компании от пользователя и отправка данных """
    user_id = message.from_user.id
    company = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        logger.info(f'Данные, которые ввел пользователь: {data}')
        name = data['name']
        phone = data['phone']
        add_users_data_to_db(user_id, name, phone, company)
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, TEXT_MESSAGES['start'].format(username=name,
                                                                    company=message.text),
                     reply_markup=keyboard_enter_menu_for_clients())
    logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')


def get_answer_from_user(message, bot):
    if message.text in ['Пол', 'Возраст', 'Доход', 'Интересы']:
        add_answers_to_list(client_id=message.from_user.id, answer=message.text)
        if message.text == 'Пол':
            bot.send_message(message.chat.id, f'Выберите пол', reply_markup=keyboard_for_sex())
        elif message.text == 'Возраст':
            bot.send_message(message.chat.id, f'Выберите возраст', reply_markup=keyboard_for_age())
        elif message.text == 'Доход':
            bot.send_message(message.chat.id, f'Укажите доход', reply_markup=keyboard_for_other_answers())
        elif message.text == 'Интересы':
            bot.send_message(message.chat.id, f'Укажите интересы', reply_markup=keyboard_for_other_answers())
        return
    elif message.text == 'Следующий вопрос':
        callback = get_next_question_callback_from_redis(message.from_user.id)
        question_id = callback.split('_')[1]
        if int(question_id) <= get_max_questions_from_redis(message.from_user.id):
            next_callback = f"{callback.split('_')[0]}_{int(callback.split('_')[1]) + 1}"
            set_question_id_in_redis(user=message.from_user.id, question_id=question_id)
            set_next_question_callback_in_redis(user=message.from_user.id, callback=next_callback)
        elif int(question_id) > get_max_questions_from_redis(message.from_user.id):
            remove_keyboard(message, bot, 'Вопросов в этом направлении больше, нет(')
            start(message, bot)
            return
        question, answers = get_question_and_answers_from_db(question_id)
        user_answer = get_user_answer(message.from_user.id, question_id)
        if bool(user_answer):
            user_answer = user_answer[0][0]
            bot.send_message(message.chat.id, f'❓{question}?\n\nВаше ответ:{user_answer}',
                             reply_markup=keyboard_for_answer(answers))
            return
        bot.set_state(message.from_user.id, MyStates.answer_to_question, message.from_user.id)
        bot.send_message(message.chat.id, f'❓{question}?\n\nНапишите ответ и нажмите "✅ Отправить ответ"',
                         reply_markup=keyboard_for_answer(answers))
        # bot.delete_message(call.message.chat.id, call.message.id)

        return
    add_answers_to_list(client_id=message.from_user.id, answer=message.text)
    bot.send_message(message.chat.id, f'Ответ принят, нажмите "✅ Отправить ответ" если больше нечего добавить')


def send_user_answers_to_db(message, bot):
    """ Выход из state вопроса и отправка ответов в базу данных"""
    text_answers = "|".join(get_user_answers(user=message.from_user.id))
    question_id = get_question_id_from_redis(user=message.from_user.id)
    add_user_answers_to_db(user_id=message.from_user.id, question_id=question_id, user_response=text_answers)
    delete_user_answers_from_redis(user=message.from_user.id)
    bot.delete_state(message.from_user.id, message.chat.id)
    remove_keyboard(message, bot, 'Ваш ответ получен!')
    path = get_keyboard_for_questions_from_redis(message.from_user.id)
    bot.send_message(message.chat.id, 'Выберите вопрос:', reply_markup=keyboard_for_questions(message.from_user.id, path=path))


def phone_incorrect(message, bot):
    """Некорректный ввод телефона"""
    bot.send_message(message.chat.id, 'Некорректный ввод.\nВведите в формате:\n\n"+7XXXXXXXXXX",\n'
                                      '8XXXXXXXXXX\n9XXXXXXXXX\n\nПример: 89953423452')

# def receive_resume(message, bot):
#     try:
#
#         bot.send_document(chat_id=TELEGRAM_GROUP_CHAT_ID, document=message.document.file_id,
#                           caption=f'Резюме от пользователя:\n{message.from_user.first_name}',
#                           disable_content_type_detection=True)
#         bot.delete_state(message.from_user.id, message.chat.id)
#         bot.send_message(message.chat.id, f'Резюме получено!', )
#         logger.info(f'State пользователя удалён -- {bot.get_state(message.from_user.id, message.chat.id)}')
#     except Exception as e:
#         logger.error(f'Ошибка отправки резюме - {e}')
#
