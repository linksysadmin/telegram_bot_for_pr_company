import json
import logging
from types import NoneType
from typing import Dict, List, Any

from mysql import connector

from db import fetch_all, execute
from services.redis_db import redis_cache

logger = logging.getLogger(__name__)


def __get_users_data(user_ids: list | int) -> Dict[str, Any] | List[dict[str, Any]]:
    """
    Функция принимает telegram_id пользователя
    Args:
        user_ids: list of users id or user id
    Returns:
        A dictionary with the following keys:
        Field Name | Data Type | Description

        | date_of_registration | str | In the format '%d-%m-%Y'. |
        | id | int | The user ID. |
        | name | str | The user name. |
        | tg_username | str | The user Telegram username. |
        | phone | str | The user phone number. |
        | company | str | The user company name. |
        | website | str | The user website URL. |
        | documents | str | Have documents. |
    """
    try:
        if isinstance(user_ids, int):
            data = fetch_all(sql='SELECT * FROM clients WHERE id = %s UNION SELECT * FROM partners WHERE id = %s;',
                             params=(user_ids, user_ids))
            dict_user_data = {
                'date_of_registration': data[0][0].strftime('%d-%m-%Y'),
                'id': data[0][1],
                'name': data[0][2],
                'tg_username': data[0][3],
                'phone': data[0][4],
                'company': data[0][5],
                'website': data[0][6],
                'documents': data[0][7],
                'status': data[0][8],
            }
            return dict_user_data
        elif isinstance(user_ids, list):
            user_ids_query = f"('{user_ids[0]}')" if len(user_ids) == 1 else tuple(user_ids)
            data = fetch_all(
                sql=f"SELECT * FROM clients WHERE id IN {user_ids_query} UNION SELECT * FROM partners WHERE id IN {user_ids_query}")
            users_data = []
            for row in data:
                user_data = {'date_of_registration': row[0].strftime('%d-%m-%Y'), 'id': row[1], 'name': row[2],
                             'tg_username': row[3], 'phone': row[4], 'company': row[5], 'website': row[6],
                             'documents': row[7], 'status': row[8]}
                users_data.append(user_data)
            if not users_data:
                logger.error('Пользователя(й) нет в базе данных')
            return users_data
    except connector.errors.ProgrammingError:
        logger.error(connector.errors.ProgrammingError)
    except IndexError:
        logger.error('Пользователя нет в базе данных')


def get_users_data(user_ids) -> dict[str, Any] | list[dict[str, Any]]:
    result = __get_users_data(user_ids)
    return result



def check_client_in_database(user_id: int) -> bool:
    user = redis_cache.check_user(user_id)
    if user:
        return True
    result_from_db = fetch_all(sql='''SELECT id FROM clients WHERE id = %s''',
                               params=(user_id,)
                               )
    if result_from_db:
        redis_cache.add_user(user_id)
        return True
    return False


def check_partner_in_database(user_id: int) -> bool:
    user = redis_cache.check_user(user_id)
    if user:
        return True
    result_from_db = fetch_all(sql='''SELECT id FROM partners WHERE id = %s''',
                               params=(user_id,)
                               )
    if result_from_db:
        redis_cache.add_user(user_id)
        return True
    return False


def get_user_answer(user_id: int, question_id: int):
    result = fetch_all(
        sql='''SELECT user_response FROM clients_briefings WHERE user_id = %s AND question_id = %s;''',
        params=(user_id, question_id)
    )
    try:
        answer = result[0][0]
        return answer
    except IndexError:
        return None


def get_user_list_of_questions_informal_and_answers(user_id: int, directory: str, section: str):
    sql_query = '''SELECT q.informal_question, cb.user_response FROM questions q
         JOIN clients_briefings cb ON q.id = cb.question_id
          WHERE cb.user_id = %s AND q.direction = %s AND q.section_name = %s'''
    result_from_db = fetch_all(
        sql=sql_query,
        params=(user_id, directory, section)
    )
    questions = [question[0] for question in result_from_db]
    answers = [answer[1] for answer in result_from_db]
    return questions, answers


def get_data_questions() -> list[tuple]:
    data_briefings = redis_cache.get_data_questions()
    if data_briefings:
        return json.loads(data_briefings)
    data_briefings = fetch_all(sql='SELECT * FROM questions')
    redis_cache.set_data_questions(data_briefings)
    return data_briefings


def get_directories() -> list:
    directories = redis_cache.get_directories()
    if directories:
        return json.loads(directories)
    directories = fetch_all(sql='SELECT DISTINCT direction FROM questions')
    list_of_directories = [i[0] for i in directories]
    redis_cache.set_directories(list_of_directories)
    return list_of_directories


def get_sub_directions(direction: str):
    sub_directions = redis_cache.get_sub_directions(direction)
    if sub_directions:
        return json.loads(sub_directions)
    sub_directions = fetch_all(sql='SELECT DISTINCT sub_direction FROM questions WHERE direction = %s',
                               params=(direction,)
                               )
    if sub_directions[0][0] is None:
        return False
    list_of_sub_directions = [sub_dir[0] for sub_dir in sub_directions]
    redis_cache.set_sub_directions(direction, list_of_sub_directions)
    return list_of_sub_directions



def delete_user_answers_in_section(user_id: int, directory: str, section: str):
    sql_query = '''DELETE FROM clients_briefings WHERE user_id = %s AND question_id 
                    IN (SELECT id FROM questions WHERE section_name = %s AND direction = %s);'''
    execute(
        sql=sql_query,
        params=[(user_id, section, directory)]
    )
    return True


def get_questions_id_from_user_answers(user_id: int):
    result_from_db = fetch_all(
        sql='''SELECT question_id FROM clients_briefings WHERE user_id = %s''',
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
    if sections:
        return json.loads(sections)
    sections = fetch_all(
        sql='SELECT DISTINCT section_name FROM questions WHERE direction = %s AND sub_direction IS NULL',
        params=(direction,))
    list_of_sections = [i[0] for i in sections]
    redis_cache.set_sections_by_direction(direction, list_of_sections)
    return list_of_sections


def get_sections_by_direction_and_sub_direction(direction, sub_direction):
    sections = redis_cache.get_sections_by_direction_and_sub_direction(direction, sub_direction)
    if sections:
        return json.loads(sections)
    sections = fetch_all(
        sql='SELECT DISTINCT section_name FROM questions WHERE direction = %s AND sub_direction = %s',
        params=(direction, sub_direction))
    list_of_sections = [i[0] for i in sections]
    redis_cache.set_sections_by_direction_and_sub_direction(direction, sub_direction, list_of_sections)
    return list_of_sections


def get_question_id_and_number(direction: str, section: str, sub_direction: str | None = None) -> Dict:
    """
    Функция возвращает {id: номер вопроса в секции}
    Args:
        direction: направление
        sub_direction: поднаправление
        section: секция вопросов

    Returns:
        Функция возвращает словарь вида: {id-вопроса: № вопроса в секции}
    """
    if sub_direction is None:
        list_of_questions = fetch_all(
            sql='SELECT DISTINCT id, question_number FROM questions WHERE direction = %s AND sub_direction IS NULL AND '
                'section_name = %s',
            params=(direction, section))
    else:
        list_of_questions = fetch_all(sql='SELECT id, question_number FROM questions WHERE direction = %s'
                                          ' AND section_name = %s AND sub_direction = %s',
                                      params=(direction, section, sub_direction))
    dict_of_questions = {question[0]: question[1] for question in list_of_questions}
    return dict_of_questions


def get_question_and_answers_from_db(id_question: int) -> tuple:
    question = None
    question_and_answers = fetch_all(sql='SELECT question_text, answer FROM questions WHERE id = %s',
                                     params=(id_question,))

    try:
        question = question_and_answers[0][0]
        answers = [i[1].split('| ') for i in question_and_answers][0]
        return question, answers
    except IndexError:
        logger.error(f'Не существует вопрос № {id_question}')
        return ()
    except AttributeError:
        logger.warning(f'Нет ответов по-умолчанию на вопрос № {id_question}')
        answers = []
        return question, answers


def get_question_data_by_path(directory: str, sub_direction: str | None, section: str, number_of_question: int) -> Dict:
    sql_query = 'SELECT question_text, answer FROM questions WHERE direction = %s AND sub_direction = %s AND section_name = %s AND question_number = %s'
    params = (directory, sub_direction, section, number_of_question,)
    if sub_direction is None:
        sql_query = 'SELECT id, question_text, answer FROM questions WHERE direction = %s AND sub_direction IS %s AND section_name = %s AND question_number = %s'
    data = fetch_all(sql=sql_query, params=params)
    dict_question_data = {
        'id': data[0][0],
        'question_text': data[0][1],
        'answers': [] if data[0][2] is None else data[0][2].split('| '),
    }
    return dict_question_data


def get_all_ids_in_section(directory: str, sub_direction: str | None, section: str) -> Dict:
    sql_query = 'SELECT id, question_number FROM questions WHERE direction = %s AND sub_direction = %s AND section_name = %s'
    params = (directory, sub_direction, section)
    if sub_direction is None:
        sql_query = 'SELECT id, question_number FROM questions WHERE direction = %s AND sub_direction IS %s AND section_name = %s'
    data = fetch_all(sql=sql_query, params=params)
    dict_of_numbers_and_ids_questions = {question[1]: question[0] for question in data}
    return dict_of_numbers_and_ids_questions


def update_question_and_answers(question_id: int, question: str, answers: str) -> None:
    """
    Args:
        question_id: 12
        question: Вопрос
        answers: Ответ1 | Ответ2 | Ответ3
    Returns: None

    """
    execute(
        sql='''UPDATE questions SET question_text = %s, answer = %s WHERE id = %s''',
        params=[(question, answers, question_id)]
    )
    redis_cache.clear_redis_key('data_questions:all')


def add_question_and_answers_(direction: str, sub_direction: str | None, section_name: str, question: str,
                              answers: str) -> None:
    params = (direction, sub_direction, section_name, question, question, answers, direction, sub_direction,
              section_name)
    if isinstance(sub_direction, NoneType):
        sql_query = '''INSERT INTO questions (direction, sub_direction, section_name, question_number, question_text, informal_question, answer) 
                SELECT %s, %s, %s, COALESCE(MAX(question_number), 0) + 1, %s, %s, %s FROM (SELECT MAX(question_number) AS question_number FROM questions 
                WHERE direction = %s AND sub_direction IS %s AND section_name = %s) AS temp;'''
    else:
        sql_query = '''INSERT INTO questions (direction, sub_direction, section_name, question_number, question_text, informal_question, answer) 
                SELECT %s, %s, %s, COALESCE(MAX(question_number), 0) + 1, %s, %s, %s FROM (SELECT MAX(question_number) AS question_number FROM questions 
                WHERE direction = %s AND sub_direction = %s AND section_name = %s) AS temp;'''
    execute(
        sql=sql_query,
        params=[params]
    )
    redis_cache.clear_redis_key('data_questions:all')


def add_clients_data_to_db(table: str, user_id: int, name: str, tg_username, phone: str, company: str, website: str):
    try:
        execute(
            sql='''INSERT INTO {} (id, name, tg_username, phone, company, website)
                 VALUES (%s, %s, %s, %s, %s, %s)'''.format(table),
            params=[(user_id, name, tg_username, phone, company, website)])
        return True
    except Exception as e:
        logger.error(e)


def add_user_answers_to_db(user_id: int, question_id: int, user_response: str):
    execute(
        sql='''INSERT INTO clients_briefings (user_id, question_id, user_response) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE user_response = VALUES(user_response)''',
        params=[(user_id, question_id, user_response)])


def update_info_about_user_docs_in_db(user_id: int, documents: bool) -> None:
    execute(
        sql='''UPDATE clients SET documents = %s WHERE id = %s''',
        params=[(documents, user_id)]
    )


def update_user_status(user_id: int, status: str) -> None:
    execute(
        sql='''UPDATE clients SET status = %s WHERE id = %s''',
        params=[(status, user_id)])
