import logging

from mysql.connector import IntegrityError

from services.db import fetch_all, execute

logger = logging.getLogger(__name__)


def get_data_briefings() -> list[tuple]:
    questions = fetch_all(sql='SELECT * FROM questions')
    return questions


def check_user_in_database(user_id) -> bool:
    result_from_db = fetch_all(
        sql='''SELECT id FROM clients WHERE id = %s''',
        params=(user_id,)
    )
    return bool(len(result_from_db))


def get_directions_from_db() -> list[tuple]:
    questions = fetch_all(sql='SELECT DISTINCT direction FROM questions')
    return questions


def get_sub_directions_from_db(direction: str):
    sub_directions = fetch_all(sql='SELECT sub_direction FROM questions WHERE direction = %s',
                               params=(direction,))
    if sub_directions[0][0] is None:
        return False
    return sub_directions


def get_sections_from_db(direction, sub_direction=None):
    if sub_direction is None:
        sections = fetch_all(
            sql='SELECT DISTINCT section_name FROM questions WHERE direction = %s AND sub_direction IS NULL',
            params=(direction,))
    else:
        sections = fetch_all(sql='SELECT section_name FROM questions WHERE direction = %s AND sub_direction = %s',
                             params=(direction, sub_direction))
    return sections


def get_questions_from_db(direction, section, sub_direction=None):
    if sub_direction is None:
        questions = fetch_all(
            sql='SELECT DISTINCT id, question_number FROM questions WHERE direction = %s AND sub_direction IS NULL AND '
                'section_name = %s',
            params=(direction, section))
    else:
        questions = fetch_all(sql='SELECT id, question_number FROM questions WHERE direction = %s'
                                  ' AND section_name = %s AND sub_direction = %s',
                              params=(direction, section, sub_direction))
    return questions


def get_question_and_answers_from_db(id_question: int) -> tuple:

    all = fetch_all(sql='SELECT question_text, answer FROM questions WHERE id = %s', params=(id_question,))
    question = [i[0] for i in all][0]
    try:
        answers = [i[1].split(', ') for i in all][0]
    except AttributeError:
        answers = []
    return question, answers


def add_users_data_to_db(user_id: int, name: str, phone: str, company: str, table=None):
    try:
        if table is None:
            execute(
                sql='''INSERT INTO clients (id, name, phone, company)
                     VALUES (%s, %s, %s, %s)''',
                params=[(user_id, name, phone, company)])
            return True
        else:
            execute(
                sql='''INSERT INTO {} (id, name, phone, company)
                     VALUES (%s, %s, %s, %s)'''.format(table),
                params=[(user_id, name, phone, company)])
            return True

    except IntegrityError:
        logger.warning(f'Уже есть этот пользователь в таблице {table}')
        return False
    except Exception as e:
        logger.error(e)


def add_user_answers_to_db(user_id: int, question_id: int, user_response: str):
    try:
        if table is None:
            execute(
                sql='''INSERT INTO clients (id, name, phone, company)
                     VALUES (%s, %s, %s, %s)''',
                params=[(user_id, name, phone, company)])
            return True
        else:
            execute(
                sql='''INSERT INTO {} (id, name, phone, company)
                     VALUES (%s, %s, %s, %s)'''.format(table),
                params=[(user_id, name, phone, company)])
            return True

    except IntegrityError:
        logger.warning(f'Уже есть этот пользователь в таблице {table}')
        return False
    except Exception as e:
        logger.error(e)



if __name__ == '__main__':
    add_users_data_to_db(123213, 'Name', '+2132123132', 'Company')


