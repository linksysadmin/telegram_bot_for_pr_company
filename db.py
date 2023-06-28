from typing import Any

import mysql.connector
from mysql.connector import errorcode

import config


def connect_to_db() -> mysql.connector:
    try:
        db = mysql.connector.connect(
            host=config.MySQL_HOST,
            user=config.MySQL_USER,
            password=config.MySQL_PASS,
            database=config.MySQL_DB
        )
        return db
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise 'Something is wrong with your user name or password'
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            raise 'Database does not exist'
        else:
            raise err


def execute(sql: str, params: list[tuple]) -> None:
    with connect_to_db() as my_db:
        cursor = my_db.cursor()
        cursor.executemany(sql, params)
        my_db.commit()


def execute_two_request(sql_1: str, params_1: list[tuple], sql_2: str, params_2: list[tuple]):
    with connect_to_db() as my_db:
        cursor = my_db.cursor()
        cursor.executemany(sql_1, params_1)
        my_db.commit()
        cursor.executemany(sql_2, params_2)
        my_db.commit()


def fetch_all(sql: str, params: Any | None = None) -> list[tuple]:
    with connect_to_db() as my_db:
        cursor = my_db.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(row)
        return results
