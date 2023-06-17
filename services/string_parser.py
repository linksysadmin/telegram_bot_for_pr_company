from typing import Tuple, Union


class CallDataParser:
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
    def get_question_id(call_data: str) -> int:
        """
        Принимает строку из вызова call.data для inline-кнопок, выделяет id вопроса
        :param call_data: call.data
        :return: int - id вопроса
        """
        question_id = int(call_data.split('|')[-1])
        return question_id \
 \
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
    def get_file_name(path: str) -> str:
        """
        Принимает строку из /home/root/... , выделяет имя файла

        :param path: путь к файлу
        :return: str - имя файла
        """
        filename = path.split('/')[-1]
        return filename
