import json
import logging

from config import REDIS

logger = logging.getLogger(__name__)


def add_client_to_queue(client_id):
    if REDIS.lpos('queue', client_id) is None:    # Check if the client_id already exists in the queue
        REDIS.rpush('queue', client_id)  # If the client_id does not exist in the queue, add it to the end of the list
        return True
    else:
        return False


def add_keyboard_for_questions_in_redis(user_id: int, path):
    REDIS.set(f'keyboard_for_questions|{user_id}', json.dumps(path))


def get_keyboard_for_questions_from_redis(user_id: int):
    return json.loads(REDIS.get(f'keyboard_for_questions|{user_id}'))


def set_max_question_id_in_redis(user_id: int, number):
    REDIS.set(f'max_questions|{user_id}', number)


def get_max_question_id_in_redis(user_id: int):
    return int(REDIS.get(f'max_questions|{user_id}'))


def add_answers_to_list(client_id, answer):
    REDIS.rpush(f'answers_list:{client_id}', answer)  # rpush добавляет в хвост.


def get_user_answers(user: int):
    byte_strings = REDIS.lrange(f'answers_list:{user}', 0, -1)
    return [string.decode() for string in byte_strings]


def delete_user_answers_from_redis(user: int):
    REDIS.delete(f'answers_list:{user}')


def set_question_id_in_redis(user: int, question_id: int):
    REDIS.set(f'question_id_for_user:{user}', question_id)


def get_question_id_from_redis(user: int):
    return int(REDIS.get(f'question_id_for_user:{user}'))


def set_next_question_callback_in_redis(user: int, callback: str):
    REDIS.set(f'next_question_callback_in_redis:{user}', json.dumps(callback))


def get_next_question_callback_from_redis(user: int):
    return json.loads(REDIS.get(f'next_question_callback_in_redis:{user}'))


def get_client_id():
    try:
        return int(REDIS.lindex('queue', 0))  # вернуть первый элемент списка
    except Exception:
        logger.warning(f'В очереди больше нет никого')


# Получаем следующего клиента из списка ожидающих
def get_next_client_from_queue():
    return int(REDIS.lpop('queue'))  # Удаляет и возвращает первый элемент списка, сохраненного в key.


# Получаем состояние оператора
def get_operator_state():
    return REDIS.get('operator_state')


# Устанавливаем состояние оператора
def set_operator_state(state):
    REDIS.set('operator_state', state)


def set_last_file_path(user_id, path):
    REDIS.set(f'{user_id}last_file_path', json.dumps(path))


def get_last_file_path(user_id):
    try:
        return json.loads(REDIS.get(f'{user_id}last_file_path'))
    except TypeError:
        return False


if __name__ == '__main__':
    pass
