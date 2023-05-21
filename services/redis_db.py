import json

from config import REDIS


# Добавляем клиента в список ожидающих
def add_client_to_queue(client_id):
    REDIS.rpush('queue', client_id)


def add_keyboard_for_questions_in_redis(user_id: int, path):
    REDIS.set(f'keyboard_for_questions|{user_id}', json.dumps(path))


def get_keyboard_for_questions_from_redis(user_id: int):
    return json.loads(REDIS.get(f'keyboard_for_questions|{user_id}'))


def set_max_questions_in_redis(user_id: int, number):
    REDIS.set(f'max_questions|{user_id}', number)


def get_max_questions_from_redis(user_id: int):
    return int(REDIS.get(f'max_questions|{user_id}'))


def add_answers_to_list(client_id, answer):
    REDIS.rpush(f'answers_list:{client_id}', answer)


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
    return REDIS.lindex('queue', 0)


# Получаем следующего клиента из списка ожидающих
def get_next_client_from_queue():
    return REDIS.lpop('queue')


# Получаем состояние оператора
def get_operator_state():
    return REDIS.get('operator_state')


# Устанавливаем состояние оператора
def set_operator_state(state):
    REDIS.set('operator_state', state)


if __name__ == '__main__':
    pass
