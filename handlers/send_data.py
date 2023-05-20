import json
import logging

from config import REDIS
from handlers.keyboards import remove_keyboard
from services.send_info_to_database import add_survey_data_to_db

logger = logging.getLogger(__name__)


def send_users_data(message, bot):
    remove_keyboard(message, bot, 'Отправка данных...')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        user_id = message.from_user.id
        name = data['name']
        date_of_birthday = data['date_of_birthday']
        age = data['age']
        sex = data['sex']
        email = data['email']
        phone = data['phone']
        if data['direction'] == 'Практика':
            add_survey_data_to_db('practice', name, date_of_birthday, age, sex, email, phone, user_id)
            REDIS.set(f'user:{user_id}:check_direction', json.dumps('practice'))
        elif data['direction'] == 'Стажировка':
            add_survey_data_to_db('internship', name, date_of_birthday, age, sex, email, phone, user_id)
            REDIS.set(f'user:{user_id}:check_direction', json.dumps('internship'))
        REDIS.close()

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.from_user.id, 'Ваши данные отправлены!\n\nТеперь нажмите /season - для выбора периода')
    logger.info(f'Состояние пользователя - {bot.get_state(message.from_user.id, message.chat.id)}')


