import os
import logging

from config import BASE_DIR
from docxtpl import DocxTemplate
from datetime import datetime

logger = logging.getLogger(__name__)


def find_user_files_from_directory(user_id: int, doc_type: str = None):
    match doc_type:
        case 'ТЗ':
            directory = f'{BASE_DIR}/static/documents/technical_tasks'
        case 'КП':
            directory = f'{BASE_DIR}/static/documents/commercial_offers'
        case None:
            dir_technical_tasks = os.path.join(BASE_DIR, 'static', 'documents', 'technical_tasks')
            dir_commercial_offers = os.path.join(BASE_DIR, 'static', 'documents', 'commercial_offers')
            matching_files = []
            for directory in [dir_technical_tasks, dir_commercial_offers]:
                files = os.listdir(directory)
                matching_files += [file for file in files if f"{user_id}" in file]
            return matching_files
        case _:
            raise ValueError("Неверное значение аргумента doc_type. Должно быть 'ТЗ' или 'КП' ")
    files = os.listdir(directory)
    matching_files = [file for file in files if f"{user_id}" in file]
    return matching_files


def generate_technical_task_file(user_id: int, section: str, client_name: str, company: str,
                                 phone: str, website: str, list_of_questions: list, answers: list):
    today = datetime.today().strftime('%d-%B-%Y')
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
        document_path = f"{BASE_DIR}/static/documents/technical_tasks/ТЗ_{user_id}_{company}_{section}_{today}.docx"
        doc.save(document_path)
        return document_path
    except Exception as e:
        logger.error(f"Ошибка при создании файла ТЗ: {e}")
        return False


if __name__ == '__main__':
    generate_technical_task_file(324243234, 'Стратегия', 'Григорий', 'OOO"ОГО"', '+73242342', 'www.woohoo.com',
                                   ['Сегодня прекрасный день?', 'Что ?', 'Что потом ?'],
                                   ['Да', 'Гулять', 'Потом не знаю что', 'Ответ4'])

    print(find_user_files_from_directory(user_id=324243234, doc_type='ТЗ'))
