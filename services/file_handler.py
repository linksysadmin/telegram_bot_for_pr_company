import os
import logging
from typing import Dict

from config import BASE_DIR, DIR_FOR_SAVE_DIALOGS
from docxtpl import DocxTemplate
from datetime import datetime

logger = logging.getLogger(__name__)


def find_files(abs_path_to_directory: str) -> list:
    try:
        return os.listdir(abs_path_to_directory)
    except FileNotFoundError:
        logger.info(f"Файлы не найдены")
        return []
    except NotADirectoryError:
        logger.error(f"Запрос не директории: {abs_path_to_directory}")
        raise NotADirectoryError


def file_check(abs_path_to_file) -> bool:
    if os.path.isfile(abs_path_to_file):
        return True
    else:
        return False


def get_list_of_clients_dialogue_files():
    return find_files(DIR_FOR_SAVE_DIALOGS)


def find_user_documents(user_id: int, path_to_dir: str) -> Dict[int, str]:
    logger.info(f'Запрос файлов клиента: {user_id} в папке: {path_to_dir}')
    try:
        user_folder = str(user_id)
        path_to_user_directory = os.path.join(path_to_dir, user_folder)
        list_of_files = find_files(path_to_user_directory)
        list_of_files_with_path = [path_to_user_directory + '/' + file for file in list_of_files]
        dict_of_files = {i: list_of_files_with_path[i] for i in range(len(list_of_files_with_path))}
        return dict_of_files
    except TypeError:
        logger.error(TypeError)


def generate_technical_task_file(user_id: int, section: str, client_name: str, company: str,
                                 phone: str, website: str, list_of_questions: list, answers: list) -> str:
    """
    Функция создания файла - docx, принимает данные пользователя и возвращает путь к созданному файлу
    :return: path to directory
    """
    today = datetime.today().strftime('%d-%m-%Y')
    doc = DocxTemplate(f"{BASE_DIR}/static/documents/templates/brief_templates.docx")
    questions = [{'text': question, 'tag': '{{question}}', 'answer': answers[i]} for i, question in
                 enumerate(list_of_questions)]
    context = {'section': section,
               'client_name': client_name,
               'company': company,
               'phone': phone,
               'date': today,
               'website': website,
               'questions': questions
               }
    try:
        doc.render(context)
        user_folder = os.path.join(BASE_DIR, "static", "documents", "technical_tasks", str(user_id))
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        document_path = os.path.join(user_folder, f"{section}.docx")
        doc.save(document_path)
        return document_path
    except Exception as e:
        logger.error(f"Ошибка при создании файла ТЗ: {e}")
        raise e


def save_file(path, file, filename):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        with open(f'{path}/{filename}', 'wb') as new_file:
            new_file.write(file)
    except FileNotFoundError:
        logger.warning(f"У клиента еще нет папки с файлами")
