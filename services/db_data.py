import logging

from mysql.connector import IntegrityError

from db import fetch_all, execute, fetch_one

logger = logging.getLogger(__name__)


def get_user_data_from_db(user_id: int):
    data = fetch_all(sql='SELECT * FROM clients WHERE id = %s',
                     params=(user_id,))
    return {'date_of_registration': data[0][0].strftime('%d %B %Y'), 'id': data[0][1], 'name': data[0][2], 'phone': data[0][3], 'company': data[0][4],
            'tech_doc': bool(data[0][5]), 'cp_doc': bool(data[0][6])}


def get_data_briefings() -> list[tuple]:
    questions = fetch_all(sql='SELECT * FROM questions')
    return questions


def check_user_in_database(user_id) -> bool:
    result_from_db = fetch_all(
        sql='''SELECT id FROM clients WHERE id = %s''',
        params=(user_id,)
    )
    return bool(len(result_from_db))


def get_user_answer(user_id: int, question_id: int):
    result_from_db = fetch_all(
        sql='''SELECT user_response FROM clients_briefings WHERE client_id = %s AND question_id = %s;''',
        params=(user_id, question_id)
    )
    return result_from_db


def get_questions_id_from_user_answers(user_id: int):
    result_from_db = fetch_all(
        sql='''SELECT question_id FROM clients_briefings WHERE client_id = %s''',
        params=(user_id,)
    )
    list_of_questions_id = [id_[0] for id_ in result_from_db]
    return list_of_questions_id


def get_directions_from_db() -> list[tuple]:
    questions = fetch_all(sql='SELECT DISTINCT direction FROM questions')
    return questions


def get_sub_directions_from_db(direction: str):
    sub_directions = fetch_all(sql='SELECT DISTINCT sub_direction FROM questions WHERE direction = %s',
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
        sections = fetch_all(sql='SELECT DISTINCT section_name FROM questions WHERE direction = %s AND sub_direction = %s',
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
    execute(
        sql='''INSERT INTO clients_briefings (client_id, question_id, user_response)
             VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE user_response = VALUES (user_response)''',
        params=[(user_id, question_id, user_response)])


if __name__ == '__main__':
    pass
