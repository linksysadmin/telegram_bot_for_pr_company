import logging

from config import BASE_DIR
from docxtpl import DocxTemplate
from datetime import datetime

# Получаем текущую дату
today = datetime.today()
#
logger = logging.getLogger(__name__)


def generate_doc(client_name: str, company: str, phone: str):
    doc = DocxTemplate(f"{BASE_DIR}//document_templates/t.docx")
    context = {'client_name': client_name, 'company': company, 'phone': phone, 'date': today.strftime('%d %B %Y')}
    doc.render(context)
    doc.save(f"{BASE_DIR}/document_templates/КП.docx")
    return True


if __name__ == '__main__':
    generate_doc('Григорий', 'OOO"RETRO"', '+73242342')
