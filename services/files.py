import glob
import os
import logging

from config import BASE_DIR, DIR_FOR_TECHNICAL_TASKS, DIR_FOR_COMMERCIAL_OFFERS
from docxtpl import DocxTemplate
from datetime import datetime

from services.db_data import add_file_to_db

logger = logging.getLogger(__name__)


def find_user_files(user_id: int, doc_type: str = None):
    match doc_type:
        case 'technical_tasks':
            directory = DIR_FOR_TECHNICAL_TASKS
        case 'commercial_offers':
            directory = DIR_FOR_COMMERCIAL_OFFERS
        case None:
            directories = [DIR_FOR_TECHNICAL_TASKS, DIR_FOR_COMMERCIAL_OFFERS]
            matching_files = []
            for directory in directories:
                files = os.listdir(directory)
                matching_files += [file for file in files if str(user_id) in file]
            return [remove_substring(item, f'_{user_id}') for item in matching_files]
        case _:
            raise ValueError(
                "Неверное значение аргумента doc_type. Должно быть 'technical_tasks' или 'commercial_offers'")

    files = os.listdir(directory)
    matching_files = [file for file in files if str(user_id) in file]
    return [remove_substring(item, f'_{user_id}') for item in matching_files]


def remove_substring(item: str, user_id: str) -> str:
    """ user_id should be of the form: '_234532432'  """
    return item.replace(user_id, '', 1)


def rename_file(file_name: str, user_id: str) -> str:
    """
    Функция переименовывает файл, удаляя из него 'send_file_' и добавляя перед точкой значение user_id
    :param file_name: str - имя файла
    :param user_id: str - идентификатор пользователя
    :return: str - новое имя файла
    """
    # Удаляем 'send_file_'
    new_file_name = file_name.replace('send_file_', '')

    # Добавляем user_id перед точкой
    parts = new_file_name.split('.')
    if len(parts) > 1:
        new_file_name = f"{parts[0]}_{user_id}.{parts[1]}"
    else:
        new_file_name = f"{new_file_name}_{user_id}"
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
        document_path = f"{BASE_DIR}/static/documents/technical_tasks/{company}_{section}_{user_id}.docx"
        doc.save(document_path)
        add_file_to_db(user_id, type_document='technical_tasks', filename=f'{company}_{section}_{user_id}.docx')
        return document_path
    except Exception as e:
        logger.error(f"Ошибка при создании файла ТЗ: {e}")
        return False


if __name__ == '__main__':
    # generate_technical_task_file(324243234, 'Стратегия', 'Григорий', 'OOO"ОГО"', '+73242342', 'www.woohoo.com',
    #                                ['Сегодня прекрасный день?', 'Что ?', 'Что потом ?'],
    #                                ['Да', 'Гулять', 'Потом не знаю что', 'Ответ4'])

    print(find_user_files(user_id=5432693304, doc_type='technical_tasks'))
    # print(insert_substring('ТЗ_Ooo_Стратегия_28-05-2023.docx', 3243242343232))
