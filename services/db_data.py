import json
import logging

import redis
from mysql import connector

from db import fetch_all, execute
from services.redis_db import redis_cache

logger = logging.getLogger(__name__)

REDIS = redis.Redis(host='localhost', port=6379, db=0)


def get_user_data_from_db(user_id: int) -> dict:
    data = fetch_all(sql='SELECT * FROM clients WHERE id = %s',
                     params=(user_id,))
    return {'date_of_registration': data[0][0].strftime('%d-%m-%Y'), 'id': data[0][1], 'name': data[0][2],
            'tg_username': data[0][3], 'phone': data[0][4], 'company': data[0][5], 'website': data[0][6],
            'documents': data[0][7]}


def get_users_data_from_db(user_ids: list) -> list | None:
    try:
        if len(user_ids) == 1:
            user_ids_query = f"('{user_ids[0]}')"
        else:
            user_ids_query = tuple(user_ids)
        data = fetch_all(sql=f"SELECT * FROM clients WHERE id IN {user_ids_query}")
        users_data = []
        for row in data:
            user_data = {'date_of_registration': row[0].strftime('%d-%m-%Y'), 'id': row[1], 'name': row[2],
                         'tg_username': row[3], 'phone': row[4], 'company': row[5], 'website': row[6],
                         'documents': row[7]}
            users_data.append(user_data)
        return users_data
    except connector.errors.ProgrammingError:
        return None


def get_data_questions() -> list[tuple]:
    data_briefings = redis_cache.get_data_questions()
    if data_briefings is not None:
        return json.loads(data_briefings)
    data_briefings = fetch_all(sql='SELECT * FROM questions')
    redis_cache.set_data_questions(data_briefings)
    return data_briefings


def get_directories() -> list:
    directories = redis_cache.get_directories()
    if directories is not None:
        return json.loads(directories)
    directories = fetch_all(sql='SELECT DISTINCT direction FROM questions')
    list_of_directories = [i[0] for i in directories]
    redis_cache.set_directories(list_of_directories)
    return list_of_directories


def get_sub_directions(direction: str):
    sub_directions = redis_cache.get_sub_directions(direction)
    if sub_directions is not None:
        return json.loads(sub_directions)
    sub_directions = fetch_all(sql='SELECT DISTINCT sub_direction FROM questions WHERE direction = %s',
                               params=(direction,))

    if sub_directions[0][0] is None:
        return False
    list_of_sub_directions = [i[0] for i in sub_directions]
    redis_cache.set_sub_directions(direction, sub_directions)
    return list_of_sub_directions


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


def get_user_list_of_questions_informal_and_answers(user_id: int, directory: str, section: str):
    result_from_db = fetch_all(
        sql='''SELECT q.informal_question, cb.user_response FROM questions q
         JOIN clients_briefings cb ON q.id = cb.question_id
          WHERE cb.client_id = %s AND q.direction = %s AND q.section_name = %s''',
        params=(user_id, directory, section)
    )
    questions = [question[0] for question in result_from_db]
    answers = [answer[1] for answer in result_from_db]
    return questions, answers


def update_info_about_user_docs_in_db(user_id: int, documents: bool):
    execute(
        sql='''UPDATE clients SET documents = %s WHERE id = %s''',
        params=[(documents, user_id)]
    )


def delete_user_answers_in_section(user_id: int, directory: str, section: str):
    execute(
        sql='''DELETE FROM clients_briefings 
        WHERE client_id = %s AND question_id IN
         (SELECT id FROM questions 
         WHERE section_name = %s AND direction = %s);''',
        params=[(user_id, section, directory)]
    )
    return True


def get_questions_id_from_user_answers(user_id: int):
    result_from_db = fetch_all(
        sql='''SELECT question_id FROM clients_briefings WHERE client_id = %s''',
        params=(user_id,)
    )
    list_of_questions_id = [id_[0] for id_ in result_from_db]
    return list_of_questions_id


def get_sections_from_db(direction, sub_direction=None):
    if sub_direction is None:
        sections = get_sections_by_direction(direction)
    else:
        sections = get_sections_by_direction_and_sub_direction(direction, sub_direction)
    return sections


def get_sections_by_direction(direction):
    sections = redis_cache.get_sections_by_direction(direction)
    if sections is not None:
        return json.loads(sections)
    sections = fetch_all(
        sql='SELECT DISTINCT section_name FROM questions WHERE direction = %s AND sub_direction IS NULL',
        params=(direction,))
    list_of_sections = [i[0] for i in sections]
    redis_cache.set_sections_by_direction(direction, list_of_sections)
    return list_of_sections


def get_sections_by_direction_and_sub_direction(direction, sub_direction):
    sections = redis_cache.get_sections_by_direction_and_sub_direction(direction, sub_direction)
    if sections is not None:
        return json.loads(sections)
    sections = fetch_all(
        sql='SELECT DISTINCT section_name FROM questions WHERE direction = %s AND sub_direction = %s',
        params=(direction, sub_direction))
    list_of_sections = [i[0] for i in sections]
    redis_cache.set_sections_by_direction_and_sub_direction(direction, sub_direction, list_of_sections)
    return list_of_sections


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
        answers = [i[1].split('| ') for i in all][0]
    except AttributeError:
        answers = []
    return question, answers


def add_clients_data_to_db(user_id: int, name: str, tg_username, phone: str, company: str, website: str):
    try:
        execute(
            sql='''INSERT INTO clients (id, name, tg_username, phone, company, website)
                 VALUES (%s, %s, %s, %s, %s, %s)''',
            params=[(user_id, name, tg_username, phone, company, website)])
        return True
    except Exception as e:
        logger.error(e)


def add_user_answers_to_db(user_id: int, question_id: int, user_response: str):
    execute(
        sql='''INSERT INTO clients_briefings (client_id, question_id, user_response)
             VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE user_response = VALUES (user_response)''',
        params=[(user_id, question_id, user_response)])
