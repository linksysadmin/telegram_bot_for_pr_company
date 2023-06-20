import json
import logging

import redis

logger = logging.getLogger(__name__)


class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db)

    def add_client(self, user_id):
        self.redis.setex(f'client_exist:{user_id}', 86400, b'True')

    def check_client(self, user_id):
        in_db = self.redis.get(f'client_exist:{user_id}')
        if in_db == b'True':
            return True
        else:
            return False

    def get_user_data(self, user_id: int) -> dict:
        user_data = self.redis.get(f'user_data:{user_id}')
        if user_data:
            return json.loads(user_data)  # type: ignore
        else:
            return {}

    def set_user_data(self, user_id: int, user_data: dict) -> None:
        user_data_str = json.dumps(user_data)
        self.redis.set(f'user_data:{user_id}', user_data_str)

    def get_queue_of_clients(self):
        list_of_binary = self.redis.lrange('queue', 0, -1)
        if not list_of_binary:
            return None
        return [int(num) for num in list_of_binary]

    def get_first_client_from_queue(self):
        try:
            return int(self.redis.lindex('queue', 0))  # вернуть первый элемент списка
        except Exception:
            logger.warning(f'В очереди никого нет')
            return None

    def set_user_to_display_information(self, user_id) -> None:
        self.redis.set(f'user_to_display_information', user_id)

    def get_user_to_display_information(self):
        return int(self.redis.get(f'user_to_display_information'))

    def save_dict_of_path_for_download_file(self, user_id, dict_of_path: dict) -> None:
        self.redis.set(f'dict_of_path|{user_id}', json.dumps(dict_of_path))

    def get_path_for_download_file_by_key(self, user_id, key_of_path: int) -> str:
        all_path = json.loads(self.redis.get(f'dict_of_path|{user_id}'))
        return all_path[key_of_path]

    def set_selected_directory(self, user_id, path: str):
        self.redis.set(f'path_to_directory|{user_id}', json.dumps(path))

    def get_selected_directory(self, user_id):
        return json.loads(self.redis.get(f'path_to_directory|{user_id}'))

    # Получаем следующего клиента из списка ожидающих
    def get_first_client_and_delete_from_queue(self):
        try:
            return int(self.redis.lpop('queue'))  # Удаляет и возвращает первый элемент списка, сохраненного в key.
        except TypeError:
            return None

    def add_client_to_queue(self, client_id):
        if self.redis.lpos('queue', client_id) is None:
            self.redis.rpush('queue', client_id)
            return True
        else:
            return False

    def remove_client_from_queue(self, client_id):
        index = self.redis.lpos('queue', client_id)
        if index is not None:
            self.redis.lrem('queue', index, client_id)  # type: ignore
            return True
        else:
            return False

    def move_client_to_first_place_in_queue(self, client_id) -> None:
        self.redis.lrem('queue', 0, client_id)
        self.redis.lpush('queue', client_id)

    def add_keyboard_for_questions(self, user_id: int, path):
        self.redis.set(f'keyboard_for_questions|{user_id}', json.dumps(path))

    def get_keyboard_for_questions(self, user_id: int):
        return json.loads(self.redis.get(f'keyboard_for_questions|{user_id}'))

    def set_max_question_id(self, user_id: int, number):
        self.redis.set(f'max_questions|{user_id}', number)

    def get_max_question_id(self, user_id: int) -> int:
        return int(self.redis.get(f'max_questions|{user_id}'))

    def set_directories(self, directories: list):
        self.redis.set('directories:all', json.dumps(directories))

    def get_directories(self) -> list:
        return self.redis.get('directories:all')

    def get_sections_by_direction(self, direction):
        return self.redis.get(f'sections_of_{direction}')

    def set_sections_by_direction(self, direction, list_of_sections):
        self.redis.set(f'sections_of_{direction}', json.dumps(list_of_sections))

    def get_sections_by_direction_and_sub_direction(self, direction, sub_direction):
        return self.redis.get(f'sections_of_{direction}_{sub_direction}')

    def set_sections_by_direction_and_sub_direction(self, direction, sub_direction, list_of_sections):
        self.redis.set(f'sections_of_{direction}_{sub_direction}', json.dumps(list_of_sections))

    def get_sub_directions(self, direction):
        return self.redis.get(f'sub_directions:{direction}')

    def set_sub_directions(self, direction, sub_directions):
        self.redis.set(f'sub_directions:{direction}', json.dumps(sub_directions))

    def set_data_questions(self, data_briefings):
        self.redis.set('data_questions:all', json.dumps(data_briefings))

    def get_data_questions(self) -> list:
        return self.redis.get('data_questions:all')

    def add_answers_to_list(self, client_id, answer):
        self.redis.rpush(f'answers_list:{client_id}', answer)  # rpush добавляет в хвост.

    def get_user_answers(self, user: int):
        byte_strings = self.redis.lrange(f'answers_list:{user}', 0, -1)
        return [string.decode() for string in byte_strings]

    def delete_user_answers(self, user: int):
        self.redis.delete(f'answers_list:{user}')

    def set_question_id(self, user: int, question_id: int):
        self.redis.set(f'question_id_for_user:{user}', question_id)

    def get_question_id(self, user: int) -> int:
        return int(self.redis.get(f'question_id_for_user:{user}'))

    def set_next_question_callback(self, user: int, callback: str):
        self.redis.set(f'next_question_callback_in_redis:{user}', json.dumps(callback))

    def get_next_question_callback(self, user: int):
        return json.loads(self.redis.get(f'next_question_callback_in_redis:{user}'))

    def set_operator_state(self, state):
        self.redis.set('operator_state', state)

    def get_operator_state(self, ):
        return self.redis.get('operator_state')

    def set_last_file_path(self, user_id, path):
        self.redis.set(f'{user_id}last_file_path', json.dumps(path))

    def get_last_file_path(self, user_id):
        try:
            return json.loads(self.redis.get(f'{user_id}last_file_path'))
        except TypeError:
            return False

    def clear_all_cache(self) -> None:
        logger.warning('Весь кэш очищен')
        self.redis.flushdb()


redis_cache = RedisCache()
