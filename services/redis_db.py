from config import REDIS


# Добавляем клиента в список ожидающих
def add_client_to_queue(client_id):
    REDIS.rpush('queue', client_id)


def add_answers_to_list(client_id, answer):
    REDIS.rpush(f'answers_list:{client_id}', answer)


def get_user_answers(user: int):
    byte_strings = REDIS.lrange(f'answers_list:{user}', 0, -1)
    return [string.decode() for string in byte_strings]


def delete_user_answers(user: int):
    REDIS.delete(f'answers_list:{user}')


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

