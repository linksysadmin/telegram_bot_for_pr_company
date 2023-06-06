import os
import logging

from config import BASE_DIR, DIR_FOR_TECHNICAL_TASKS, DIR_FOR_COMMERCIAL_OFFERS
from docxtpl import DocxTemplate
from datetime import datetime

logger = logging.getLogger(__name__)


def find_files(user_id: int, directory: str):
    try:
        user_folder = str(user_id)
        directory = os.path.join(directory, user_folder)
        files = os.listdir(directory)
        matching_files = [file for file in files]
        return matching_files
    except FileNotFoundError:
        logger.warning(f"Файл не найден")
        return None


def find_technical_tasks(user_id: int):
    return find_files(user_id, DIR_FOR_TECHNICAL_TASKS)


def find_commercial_offers(user_id: int):
    return find_files(user_id, DIR_FOR_COMMERCIAL_OFFERS)


def extract_filename(callback: str) -> str:
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


if __name__ == '__main__':
    # generate_technical_task_file(5432693304, 'Стратегия', 'Григорий', 'OOO"ОГО"', '+73242342', 'www.woohoo.com',
    #                                ['Сегодня прекрасный день?', 'Что ?', 'Что потом ?'],
    #                                ['Да', 'Гулять', 'Потом не знаю что', 'Ответ4'])
    #
    # print(find_technical_tasks(user_id=5432693304))
    print(extract_filename('send_file_Стратегия.docx'))
