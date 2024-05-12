import logging
from typing import Tuple, Union

logger = logging.getLogger(__name__)


class Parser:
    @staticmethod
    def parse_callback(data: str):
        try:
            list_of_callback_parts = data.split('|')
            if len(list_of_callback_parts) == 3 or len(list_of_callback_parts) == 4:
                if list_of_callback_parts[0] == 'tex':
                    return 'tex|'
                elif list_of_callback_parts[0] == 'question':
                    return 'question|'
            list_of_callback_parts_without_last_element = list_of_callback_parts[:-1]
            callback = '|'.join(list_of_callback_parts_without_last_element) + '|'
            return callback
        except Exception as e:
            logger.error(e)
            return data

    @staticmethod
    def get_directory_sub_direction_section(call_data: str) -> Tuple[str, Union[str, None], str] | Tuple[str, str]:
        """
        Принимает строку из вызова call.data для inline-кнопок,
        возвращает название директории и поддиректории

        :param call_data: call.data
        :return: Tuple[str, Union[str, None], str]
        """
        split_path = call_data.split('|')
        len_string_path = len(split_path)
        if len_string_path == 2:
            return split_path[0], None, split_path[-1]
        elif len_string_path == 3:
            if split_path[0] == 'tex':
                return split_path[-2], split_path[-1]
            return split_path[0], split_path[1], split_path[-1]
        elif len_string_path == 4:
            if split_path[0] == 'tex':
                return split_path[1], split_path[-1]

    @staticmethod
    def get_dir_and_sub_dir(call_data: str) -> Tuple[str, str]:
        """
        Принимает строку из вызова call.data для inline-кнопок,
        возвращает название директории и поддиректории

        :param call_data: call.data
        :return: tuple - Название директории и поддиректории
        """
        dir_ = call_data.split('|')[0]
        sub_dir = call_data.split('|')[1]
        return dir_, sub_dir

    @staticmethod
    def get_client_id(call_data: str) -> int:
        """
        Принимает строку из вызова call.data для inline-кнопок, выделяет id пользователя
        :param call_data: call.data
        :return: int - id пользователя
        """
        client_id = int(call_data.split('|')[-1])
        return client_id

    @staticmethod
    def get_question_id_and_number(call_data: str) -> Tuple:
        """
        Принимает строку из вызова call.data для inline-кнопок, выделяет id вопроса
        :param call_data: call.data
        :return: tuple - id вопроса, № вопроса
        """
        question_id = int(call_data.split('|')[-2])
        number = int(call_data.split('|')[-1])
        return question_id, number

    @staticmethod
    def get_key_for_path(call_data: str) -> str:
        """
        Принимает строку из вызова call.data для inline-кнопок,
        выделяет номер, который присвоен для извлечения расположения
        файла или каталога в файловой системе

        :param call_data: call.data
        :return: str - ключ для расположения файла
        """
        key = call_data.split('|')[-1]
        return key

    @staticmethod
    def get_file_type(path: str) -> str:
        """
       Принимает строку из /home/root/... , выделяет тип файла

        :param path: call.data
        :return: str - тип файла
        """
        key = path.split('.')[-1]
        return key

    @staticmethod
    def get_file_name_from_path(path: str) -> str:
        """
        Принимает строку из /home/root/... , выделяет имя файла

        :param path: путь к файлу
        :return: str - имя файла
        """
        filename = path.split('/')[-1]
        return filename

    @staticmethod
    def get_next_callback_for_question(question_id: int):
        return f"question|{question_id + 1}"



class TextParser:
    @staticmethod
    def get_question_and_answers(text: str) -> Tuple | None:
        """
        Принимает строку в формате Вопрос || Ответ1| Ответ2 и извлекает текст вопроса

        :param text: str
        :return: (question, answers)
        """
        try:
            question = text.split('||')[0]
            answers = text.split('||')[1]
            return question, answers
        except IndexError:
            logger.warning('Не установлен разделитель: ||')
            return
