import os
import logging

from config import BASE_DIR, DIR_FOR_TECHNICAL_TASKS, DIR_FOR_COMMERCIAL_OFFERS, DIR_FOR_OTHER_FILES, DIR_FOR_REPORTS
from docxtpl import DocxTemplate
from datetime import datetime

from services.redis_db import get_directory_from_redis

logger = logging.getLogger(__name__)


def find_files(user_id: int, directory_path: str):
    try:
        user_folder = str(user_id)
        user_directory = os.path.join(directory_path, user_folder)
        files = os.listdir(user_directory)
        matching_files = [file for file in files]
        return matching_files
    except FileNotFoundError:
        logger.warning(f"Файлы не найдены")
        return None


def find_documents(user_id: int, directory_path: str):
    return find_files(user_id, directory_path)


def get_path_to_file(callback_data, client_id, call_id):
    filename = extract_filename_from_string(callback_data)
    directory = get_directory_from_redis(call_id)
    path_to_file = f'{directory}/{client_id}/{filename}'
    return path_to_file


def extract_filename_from_string(callback: str) -> str:
    """
    Функция выделяет имя файла из callback, удаляя из него 'send_file_'
    :param callback: str - строка вызова callback
    :return: str - имя файла
    """
    new_file_name = callback.replace('send_file_', '')  # Удаляем 'send_file_'
    return new_file_name


def generate_technical_task_file(user_id: int, section: str, client_name: str, company: str,
                                 phone: str, website: str, list_of_questions: list, answers: list):
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
        return False


def save_file(path, file, filename):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        with open(f'{path}/{filename}', 'wb') as new_file:
            new_file.write(file)
    except FileNotFoundError:
        logger.warning(f"У клиента еще нет папки с файлами")
