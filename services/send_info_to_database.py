import logging

from sqlite3 import IntegrityError
from services.db import execute, fetch_all

logger = logging.getLogger(__name__)


def check_user_in_database(user_id, direction: str) -> bool:
    result_from_db = fetch_all(
        sql='''SELECT user_id FROM {} WHERE user_id = ?'''.format(direction),
        params=(user_id,)
    )
    return bool(len(result_from_db))


def fetch_all_from_table(direction: str):
    result_from_db = fetch_all(
        sql='''SELECT * FROM {}'''.format(direction),
        params=()
    )
    return result_from_db


def add_survey_data_to_db(direction: str, name: str, date_of_birthday: str,
                          age: int, sex: str, email: str, phone: str, user_id: int):
    try:
        execute(
            sql='''INSERT INTO {} (user_id, name, date_of_birthday, age, sex, email, phone)
                 VALUES (?, ?, ?, ?, ?, ?, ?)'''.format(direction),
            params=(user_id, name, date_of_birthday, age, sex, email, phone))
        return True
    except IntegrityError:
        logger.warning(f'Уже есть этот пользователь в таблице {direction}')
        return False
    except Exception as e:
        logger.error(e)


def update_data(table_name: str, column_name: str, value: (str, int), user_id: int):
    execute(
        sql='''UPDATE {} SET {} = ? WHERE user_id = ?;'''.format(table_name, column_name),
        params=(value, user_id)
    )


def add_admin_to_db(user_id: int):
    try:
        execute(
            sql="""INSERT INTO administrators (user_id) VALUES (?)""",
            params=(user_id,)
        )
        logger.info(f'Админ: {user_id} - добавлен в БД')
        return True
    except IntegrityError:
        logger.error(f'Уже есть этот Админ: {user_id} в БД')
        return False


def check_admin_in_db(user_id: int):
    result = fetch_all(
        sql="""SELECT * FROM administrators WHERE user_id = ?""",
        params=(user_id,)
    )
    return bool(len(result))


if __name__ == '__main__':
    pass
