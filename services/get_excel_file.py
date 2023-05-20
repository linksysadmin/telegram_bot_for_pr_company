import logging

from openpyxl import Workbook

from config import BASE_DIR
from services.send_info_to_database import fetch_all_from_table

logger = logging.getLogger(__name__)


def get_excel_file():
    workbook = Workbook()
    COLUMNS_NAME = ['ФИО', 'Дата Рождения', 'Возраст', 'Пол', 'Email', 'Номер', 'Университет', 'Период',
                    'Результат теста']
    DIR_FOR_SAVE_FILE = f'{BASE_DIR}/excel_files/'

    table1_data = fetch_all_from_table('practice')
    worksheet1 = workbook.active
    worksheet1.title = "Практика"
    worksheet1.append(COLUMNS_NAME)
    for row in table1_data:
        worksheet1.append(row[2:])

    table2_data = fetch_all_from_table('internship')
    worksheet2 = workbook.create_sheet(title="Стажировка")
    worksheet2.append(COLUMNS_NAME)
    for row in table2_data:
        worksheet2.append(row[2:])

    workbook.save(filename=f"{DIR_FOR_SAVE_FILE}пользователи.xlsx")
    return True


if __name__ == '__main__':
    pass
