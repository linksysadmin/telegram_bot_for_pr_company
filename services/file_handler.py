import os
import logging

from config import BASE_DIR, DIR_FOR_SAVE_DIALOGS, DIR_FOR_TECHNICAL_TASKS, DIR_FOR_COMMERCIAL_OFFERS
from docxtpl import DocxTemplate
from datetime import datetime

logger = logging.getLogger(__name__)


def find_files(directory_path: str):
    try:
        return os.listdir(directory_path)
    except FileNotFoundError:
        logger.warning(f"Файлы не найдены")
        return None


def get_list_of_clients_dialogue():
    return find_files(DIR_FOR_SAVE_DIALOGS)


def find_user_documents(user_id: int, directory_path: str):
    logger.info(f'Запрос файлов клиента: {user_id} в папке: {directory_path}')
    try:
        user_folder = str(user_id)
        directory_path = os.path.join(directory_path, user_folder)
        list_of_files = find_files(directory_path)
        list_of_files_with_path = [directory_path + '/' + file for file in list_of_files]
        dict_of_files = {i: list_of_files_with_path[i] for i in range(len(list_of_files_with_path))}
        return dict_of_files
    except TypeError:
        return None


if __name__ == '__main__':
    x = find_user_documents(5432693304, DIR_FOR_TECHNICAL_TASKS)
    print(x)

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


def file_check(path):
    if os.path.isfile(path):
        return path
    else:
        return None

