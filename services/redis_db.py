import json
import logging

from config import REDIS

logger = logging.getLogger(__name__)


def get_queue_of_clients():
    list_of_binary = REDIS.lrange('queue', 0, -1)
    return [int(num) for num in list_of_binary]


def get_first_client_from_queue():
    try:
        return int(REDIS.lindex('queue', 0))  # вернуть первый элемент списка
    except Exception:
        logger.warning(f'В очереди никого нет')
        return None


def set_directory_in_redis(user_id, path: str):
    REDIS.set(f'path_to_directory|{user_id}', json.dumps(path))


def get_directory_from_redis(user_id):
    return json.loads(REDIS.get(f'path_to_directory|{user_id}'))


# Получаем следующего клиента из списка ожидающих
def get_first_client_and_delete_from_queue():
    try:
        return int(REDIS.lpop('queue'))  # Удаляет и возвращает первый элемент списка, сохраненного в key.
    except TypeError:
        return None


def add_client_to_queue(client_id):
    if REDIS.lpos('queue', client_id) is None:
        REDIS.rpush('queue', client_id)
        return True
    else:
        return False


def remove_client_from_queue(client_id):
    index = REDIS.lpos('queue', client_id)
    if index is not None:
        REDIS.lrem('queue', index, client_id)
        return True
    else:
        return False


def move_client_to_first_place_in_queue(client_id):
    REDIS.lrem('queue', 0, client_id)
    REDIS.lpush('queue', client_id)


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


