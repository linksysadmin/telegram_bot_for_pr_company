import copy
import logging

from services.db_data import get_data_briefings

logging.basicConfig(handlers=(logging.StreamHandler(),),
                    format="%(name)s %(asctime)s - %(levelname)s - %(message)s",
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

all_from_table_questions = get_data_briefings()

DIRECTIONS = set(i[1] for i in all_from_table_questions)
SUB_DIRECTIONS = set(i[2] for i in all_from_table_questions if type(i[2]) == str)
SECTIONS = set(i[3] for i in all_from_table_questions)


if __name__ == '__main__':
    for i in all_from_table_questions:
        print(i)
    print(f'Все директории: {DIRECTIONS}')
    print(f'Все поддиректории: {SUB_DIRECTIONS}')
    print(f'Все секции: {SECTIONS}')
