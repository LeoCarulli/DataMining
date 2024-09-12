# main.py
import os
import re
import sqlite3
import sqlparse
import pandas as pd
import streamlit as st
import logging
from model_config import initialize_model  # Importar la inicialización del modelo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Función para validar SQL
def is_valid_sql(query):
    """Checks if the provided query is a valid SQL statement for SQLite."""
    query = re.sub(r"<.*?>", "", query.strip())
    try:
        parsed = sqlparse.parse(query)
    except Exception as e:
        return False
    if not parsed or len(parsed) == 0:
        return False
    stmt = parsed[0]
    if stmt.tokens and stmt.tokens[0].ttype in (sqlparse.tokens.DML, sqlparse.tokens.DDL):
        return True
    return False

# Función para ejecutar la consulta
def execute_query(sql_query, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return results, column_names
    except sqlite3.Error as e:
        return f"An error occurred: {e}", None
    finally:
        conn.close()

# Función para manejar la conversación con el chatbot y generar la consulta SQL
def handle_conversation(user_input, context, db_path, max_attempts=5, chain=None):
    if chain is None:
        chain = initialize_model()  # Inicializar el modelo si no se ha pasado uno
    attempt = 0
    
    while attempt < max_attempts:
        # Invoke the AI model
        result = chain.invoke({"context": context, "question": user_input})
        
        # Strip unwanted HTML-like tags and trim whitespace
        sql_query = re.sub(r"<.*?>", "", result.strip())
        
        # Ensure only one SQL statement is present
        if len(sqlparse.split(sql_query)) > 1:
            sql_query = sqlparse.split(sql_query)[0]
            context += f"\nUser: {user_input}\nAI: Multiple queries detected. Using only the first query."
        
        # Validate the SQL query
        if is_valid_sql(sql_query):
            execution_result, _ = execute_query(sql_query, db_path)
            if not isinstance(execution_result, str):
                formatted_query = sqlparse.format(sql_query, reindent=True, keyword_case='upper')
                context += f"\nUser: {user_input}\nAI: {formatted_query}"
                return formatted_query, context
            else:
                logger.info(f"Attempt {attempt} failed. Error executing SQL query. {execution_result}")
        else:
            logger.info(f"Attempt {attempt} failed. Invalid SQL query generated.")
        
        # Increment the attempt counter
        attempt += 1
        context += f"\nUser: {user_input}\nAI: Attempt {attempt} failed. Trying again."
        logger.info(f"Attempt {attempt} failed. Trying again.")

    context += f"\nUser: {user_input}\nAI: Unable to generate a valid SQL query after {max_attempts} attempts."
    return "Unable to generate a valid SQL query. Please contact an administrator.", context

# Estructura de la aplicación Streamlit
def main():
    st.title("AI SQL Coder")

    if "context" not in st.session_state:
        st.session_state.context = ""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    db_file = "mi_base_de_datos.db"
    db_path = os.path.join(os.getcwd(), db_file)

    user_input = st.text_input("You: ", "")

    if user_input:
        sql_query, st.session_state.context = handle_conversation(user_input, st.session_state.context, db_path)
        st.session_state.chat_history.append(f"You: {user_input}")

        # Store SQL query in chat history with collapse functionality
        query_display = f"SQL Query: {sql_query}"
        st.session_state.chat_history.append({"type": "query", "content": query_display})

        if "Unable to generate a valid SQL query" in sql_query:
            st.session_state.chat_history.append({"type": "error", "content": sql_query})
        else:
            results, column_names = execute_query(sql_query, db_path)
            if isinstance(results, str):
                st.session_state.chat_history.append({"type": "error", "content": results})
            else:
                df = pd.DataFrame(results)
                if isinstance(column_names, list):
                    df.columns = column_names
                st.session_state.chat_history.append({"type": "results", "content": df})

    # Display chat history with collapsible SQL query and table display
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            if isinstance(message, dict):
                if message["type"] == "query":
                    with st.expander("Show SQL Query"):
                        st.write(message["content"])
                elif message["type"] == "error":
                    st.write(message["content"])
                elif message["type"] == "results":
                    st.dataframe(message["content"])
            else:
                st.write(message)

if __name__ == "__main__":
    logger.info("Starting the Streamlit application...")
    main()
