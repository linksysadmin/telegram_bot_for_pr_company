import logging

from config import BASE_DIR
from docxtpl import DocxTemplate
from datetime import datetime


logger = logging.getLogger(__name__)


def generate_doc_of_technical_task(direction: str, client_name: str, company: str, phone: str, website: str,
                                   list_of_questions: list, answers: list ):
    doc = DocxTemplate(f"{BASE_DIR}/static/documents/templates/brief_templates.docx")
    logger.info(f'{direction, client_name, company, phone, website, list_of_questions, answers}')

    # Создаем новый список, в котором каждый элемент содержит текст вопроса, метку {{question}} и соответствующий ответ

    questions = [{'text': question, 'tag': '{{question}}', 'answer': answers[i]} for i, question in
                 enumerate(list_of_questions)]

    context = {'direction': direction,
               'client_name': client_name,
               'company': company,
               'phone': phone,
               'date': datetime.today().strftime('%d %B %Y'),
               'website': website,
               'questions': questions
               }

    doc.render(context)
    doc.save(f"{BASE_DIR}/static/documents/technical_tasks/{company}.docx")

    return True


if __name__ == '__main__':
    generate_doc_of_technical_task('Менеджмент', 'Григорий', 'OOO"423"', '+73242342', 'www.woohoo.com',
                                   ['Сегодня прекрасный день?', 'Что 123123faeaf?', 'Что потом ?'],
                                   ['Да', 'Гулять', 'Потом не знаю что', 'Ответ4'])
