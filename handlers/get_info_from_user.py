import logging


from handlers.commands import start
from handlers.keyboards import remove_keyboard, \
    keyboard_send_phone, keyboard_for_answer, keyboard_enter_menu_for_clients, \
    keyboard_for_questions, keyboard_for_sex, keyboard_for_age, keyboard_for_other_answers
from handlers.text_messages import TEXT_MESSAGES
from services.db_data import add_clients_data_to_db, get_question_and_answers_from_db, add_user_answers_to_db, \
    get_user_answer
from services.redis_db import add_answers_to_list, get_user_answers, \
    get_question_id_from_redis, delete_user_answers_from_redis, get_keyboard_for_questions_from_redis, \
    get_next_question_callback_from_redis, set_question_id_in_redis, set_next_question_callback_in_redis, \
    get_max_question_id_in_redis
from services.states import MyStates

logger = logging.getLogger(__name__)


def get_user_name(message, bot):
    """ STATE 1 Получение имени от пользователя """
    bot.add_data(message.from_user.id, message.chat.id, name=message.text, tg_username=message.from_user.username)
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
    remove_keyboard(message, bot, 'Укажите ваш Веб-сайт')
    bot.set_state(message.chat.id, MyStates.website, message.from_user.id)
    logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')


def get_user_website(message, bot):
    """ STATE 3 - Получение website от пользователя """
    website = message.text
    bot.add_data(message.from_user.id, message.chat.id, website=website)
    bot.send_message(message.chat.id, 'Укажите название вашей компании©️')
    bot.set_state(message.chat.id, MyStates.company, message.from_user.id)
    logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')


def get_user_company(message, bot):
    """ STATE 4 - Получение компании от пользователя и отправка данных """
    user_id = message.from_user.id
    company = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        logger.info(f'Данные, которые ввел пользователь: {data}')
        name = data['name']
        tg_username = data['tg_username']
        phone = data['phone']
        website = data['website']
        add_clients_data_to_db(user_id, name, tg_username, phone, company, website)
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, TEXT_MESSAGES['start'].format(username=name,
                                                                    company=message.text),
                     reply_markup=keyboard_enter_menu_for_clients())
    logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')


def get_answer_from_user(message, bot):
    match message.text:
        case 'Пол':
            add_answers_to_list(client_id=message.from_user.id, answer=message.text)
            bot.send_message(message.chat.id, f'Выберите пол', reply_markup=keyboard_for_sex())
        case 'Возраст':
            add_answers_to_list(client_id=message.from_user.id, answer=message.text)
            bot.send_message(message.chat.id, f'Выберите возраст', reply_markup=keyboard_for_age())
        case 'Доход' | 'Интересы':
            add_answers_to_list(client_id=message.from_user.id, answer=message.text)
            bot.send_message(message.chat.id, f'Укажите {message.text.lower()}', reply_markup=keyboard_for_other_answers())
        case _:
            add_answers_to_list(client_id=message.from_user.id, answer=message.text)
            bot.send_message(message.chat.id, f'Ответ принят, нажмите "✅ Отправить ответ" если больше нечего добавить')


def next_question(message, bot):
    callback_for_next_question = get_next_question_callback_from_redis(message.from_user.id)
    next_question_id = int(callback_for_next_question.split('_')[1])
    max_question_id = get_max_question_id_in_redis(message.from_user.id)

    if next_question_id <= max_question_id:
        next_callback = f"{callback_for_next_question.split('_')[0]}_{int(callback_for_next_question.split('_')[1]) + 1}"
        set_question_id_in_redis(user=message.from_user.id, question_id=next_question_id)
        set_next_question_callback_in_redis(user=message.from_user.id, callback=next_callback)
    elif next_question_id > max_question_id:
        remove_keyboard(message, bot, 'Вопросов в этом направлении больше, нет(')
        start(message, bot)
        return
    question, answers = get_question_and_answers_from_db(next_question_id)
    user_answer = get_user_answer(message.from_user.id, next_question_id)
    if bool(user_answer):
        user_answer = user_answer[0][0]
        bot.send_message(message.chat.id, f'❓{question}?\n\nВаше ответ:{user_answer}',
                         reply_markup=keyboard_for_answer(answers))
        return
    bot.set_state(message.from_user.id, MyStates.answer_to_question, message.from_user.id)
    bot.send_message(message.chat.id, f'❓{question}?\n\nНапишите ответ и нажмите "✅ Отправить ответ"',
                     reply_markup=keyboard_for_answer(answers))


def send_user_answers_to_db(message, bot):
    """ Выход из state вопроса и отправка ответов в базу данных"""
    text_answers = "|".join(get_user_answers(user=message.from_user.id))
    question_id = get_question_id_from_redis(user=message.from_user.id)
    add_user_answers_to_db(user_id=message.from_user.id, question_id=question_id, user_response=text_answers)
    delete_user_answers_from_redis(user=message.from_user.id)
    bot.delete_state(message.from_user.id, message.chat.id)
    remove_keyboard(message, bot, 'Ваш ответ получен!')
    path = get_keyboard_for_questions_from_redis(message.from_user.id)
    bot.send_message(message.chat.id, 'Выберите вопрос:',
                     reply_markup=keyboard_for_questions(message.from_user.id, path=path))


def phone_incorrect(message, bot):
    """Некорректный ввод телефона"""
    bot.send_message(message.chat.id, 'Некорректный ввод.\nВведите в формате:\n\n"+7XXXXXXXXXX",\n'
                                      '8XXXXXXXXXX\n9XXXXXXXXX\n\nПример: 89953423452')
