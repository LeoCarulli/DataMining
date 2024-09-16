# execution.py
from sqlglot.executor import execute
from functools import lru_cache
import json

import sqlite3
import logging

logger = logging.getLogger()


@lru_cache(maxsize=None)
def execute_query_json(sql_query, json_path):
    """Simulate an sql execution, for testing and avoiding sqlite limitations"""
    logger.debug(f"sql query \n {sql_query}")
    with open(json_path, 'r') as json_file:
        tables = json.load(json_file)
    try:
        result = execute(sql_query, tables=tables)
    except Exception as e:
        logger.error(f"Error de SQL al ejecutar la consulta: {e},\n query: {sql_query}")
        return f"An error occurred: {e}", None
    return result.rows, result.columns


def execute_query(sql_query, db_path):
    """Executes the SQL query on the SQLite database."""
    logger.debug(f"sql query \n {sql_query}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        print(results)

        # Verificar si hay nombres de columnas
        if cursor.description is not None:
            column_names = [description[0] for description in cursor.description]
        else:
            column_names = []

        return results, column_names

    except sqlite3.Error as e:
        logger.error(f"Error de SQLite al ejecutar la consulta: {e},\n query: {sql_query}")
        return f"An error occurred: {e}", None

    finally:
        conn.close()
        logger.debug("Conexión SQLite cerrada.")
