# execution.py

import sqlite3
import logging

logger = logging.getLogger()

def execute_query(sql_query, db_path):
    """Executes the SQL query on the SQLite database."""
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
        logger.error(f"Error de SQLite al ejecutar la consulta: {e}")
        return f"An error occurred: {e}", None

    finally:
        conn.close()
        logger.debug("Conexión SQLite cerrada.")
