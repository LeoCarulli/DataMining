import os
import pandas as pd
import streamlit as st
import logging
import sqlparse
import sqlglot
import re
from model_config import initialize_model  # Asegúrate de importar initialize_model
from validation import is_valid_sql
from execution import execute_query, execute_query_json

# Configuración básica de logging
logging.basicConfig(level=logging.DEBUG,  # Cambiar el nivel a INFO para eliminar DEBUG
                    format='%(levelname)s: %(message)s')  # Mensajes de log básicos
logger = logging.getLogger()

def convert_postgres_to_sqlite(query: str) -> str:
    # 1. Convertir EXTRACT para fechas a strftime
    query = re.sub(r"EXTRACT\(YEAR FROM (\w+)\)", r"strftime('%Y', \1)", query)
    query = re.sub(r"EXTRACT\(MONTH FROM (\w+)\)", r"strftime('%m', \1)", query)

    # 2. Convertir los operadores de tipo ::DATE, ::INTEGER, etc. (eliminarlos)
    query = re.sub(r"::\w+", "", query)

    # 3. Convertir funciones y operadores no compatibles
    query = query.replace("ILIKE", "LIKE")  # SQLite no soporta ILIKE, usar LIKE
    query = re.sub(r"SERIAL", "INTEGER PRIMARY KEY AUTOINCREMENT", query)  # Convertir SERIAL a autoincrement

    return query


def transform_oracle_to_sqlite(query):
    # Reemplazos comunes entre Oracle y SQLite3
    replacements = [
        # Conversión de TO_NUMBER a nada (asume que SQLite no lo necesita)
        (r"to_number\(([^,]+),\s*'[^']+'\)", r"\1"),
        (r"to_number\(([^)]+)\)", r"\1"),
        
        # Conversión de TO_DATE a 'YYYY-MM-DD' para SQLite
        (r"to_date\(([^,]+),\s*'[^']+'\)", r"\1"),  # En algunos casos se puede necesitar manejar formatos
        
        # Cambios para CURRENT_TIMESTAMP o SYSDATE
        (r"sysdate", r"CURRENT_TIMESTAMP"),
        (r"current_date", r"DATE('now')"),
        (r"current_timestamp", r"DATETIME('now')"),
        
        # Conversión de secuencias de Oracle a autoincremento en SQLite
        (r"([a-zA-Z_]+)\.nextval", r"NULL"),  # SQLite utiliza AUTOINCREMENT en su lugar
        
        # Función NVL en Oracle a IFNULL en SQLite
        (r"nvl\(([^,]+),\s*([^)]+)\)", r"IFNULL(\1, \2)"),
        
        # Funciones de concatenación en Oracle (||) a SQLite
        (r"([a-zA-Z_]+)\s*\|\|\s*([a-zA-Z_]+)", r"\1 || \2"),
        
        # Reemplazo de tipos de datos
        #(r"number", r"INTEGER"),  # SQLite usa INTEGER en lugar de NUMBER
        (r"varchar2", r"TEXT"),   # SQLite usa TEXT en lugar de VARCHAR2
        #(r"date", r"TEXT"),       # SQLite usa TEXT para representar fechas
        #(r"timestamp", r"TEXT"),  # Similar con TIMESTAMP
    ]
    
    # Aplicar los reemplazos
    for pattern, replacement in replacements:
        query = re.sub(pattern, replacement, query, flags=re.IGNORECASE)

        # Detectar si la consulta contiene NULLS LAST
    if "NULLS LAST" in query.upper():
        # Reemplazar 'NULLS LAST' con un CASE WHEN para SQLite3
        query = re.sub(
            r"ORDER BY (.+?)\s+DESC NULLS LAST",
            r"ORDER BY CASE WHEN \1 IS NULL THEN 1 ELSE 0 END, \1 DESC",
            query,
            flags=re.IGNORECASE
        )
    
    # Cambiar TOP por LIMIT, ya que SQLite3 usa LIMIT
    match = re.search(r"SELECT TOP (\d+)", query, re.IGNORECASE)
    if match:
        limit_value = match.group(1)
        # Reemplazar TOP por LIMIT
        query = re.sub(r"SELECT TOP \d+", f"SELECT", query, flags=re.IGNORECASE)
        query += f" LIMIT {limit_value}"

    
    return query

def handle_conversation(user_input, context, db_path, chain, max_attempts=5, json_path="output_data.json"):
    attempt = 0
    
    while attempt < max_attempts:
        # Invocar el modelo AI para generar la consulta SQL
        result = chain.invoke({"context": "", "question": user_input})
        logger.debug(result)
        sql_query = re.sub(r"<.>", "", result.strip())
        
        # Asegurarse de que solo se ejecute una consulta SQL
        parsed_queries = sqlparse.split(sql_query)
        if len(parsed_queries) > 1:
            print(parsed_queries)
            logger.info(f"Multiple queries detected. Only the first query will be executed.")
            sql_query = parsed_queries[0]
        
        #sql_query = transform_oracle_to_sqlite(sql_query)
        #sql_query = convert_postgres_to_sqlite(sql_query)
        sql_query = sql_query.replace('`', '')
        logger.debug(f" query post transform {sql_query}")

        # Validar la consulta SQL
        if is_valid_sql(sql_query):
            # transpilo el sql a mysql
            formatted_query = sqlglot.transpile(sql_query, write="mysql", pretty=True)[0]
            # Formatear la consulta SQL
            #formatted_query = sqlparse.format(sql_query, reindent=True, keyword_case='upper')
            logger.debug(f" formatted query {formatted_query}")
            
            # Ejecutar la consulta SQL
            #execution_result, _ = execute_query(formatted_query, db_path)
            execution_result, _ = execute_query_json(formatted_query, json_path)
            if not isinstance(execution_result, str):  # La consulta fue exitosa
                context += f"\nUser: {user_input}\nAI: {formatted_query}"
                return formatted_query, context
            else:
                logger.error(f"Error executing SQL query: {execution_result}")
        else:
            print(sql_query)
            logger.warning(f"Invalid SQL query generated.")
        
        # Incrementar el contador de intentos
        attempt += 1
        logger.info(f"Attempt {attempt} failed. Trying again.")
    
    # Si se alcanzan el número máximo de intentos, retornar un error genérico
    logger.error("Failed to generate a valid SQL query after several attempts.")
    context += f"\nUser: {user_input}\nAI: Unable to generate a valid SQL query. Please contact an administrator."
    return "Unable to generate a valid SQL query. Please contact an administrator.", context


# Nueva versión del main con scrollable chatbox y collapsible sections
def main():
    st.title("AI SQL Coder")

    if "context" not in st.session_state:
        st.session_state.context = ""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    db_file = "mi_base_de_datos.db"
    db_path = os.path.join(os.getcwd(), db_file)
    json_path = os.path.join(os.getcwd(), "output_data.json")

    # Inicializar el modelo (el `chain`) cuando la aplicación se inicia
    chain = initialize_model()
    
    # Create a layout with two columns
    col1, col2 = st.columns([7, 3])

    with col1:
        st.markdown("### Enter your query below:")
        user_input = st.text_input("You: ", "", placeholder="Haz tu pregunta aquí...")

    with col2:
        if st.button("Clear History"):
            st.session_state.chat_history = []
            st.session_state.user_input = ""
            user_input = ""


    #st.markdown("### Enter your query below:")
    #user_input = st.text_input("You: ", "", placeholder="Haz tu pregunta aquí...")

    if user_input:
        sql_query, st.session_state.context = handle_conversation(user_input, st.session_state.context, db_path, chain, json_path=json_path)

        # Store SQL query in chat history with collapse functionality
        query_display = f"SQL Query: {sql_query}"
        st.session_state.chat_history.append(
            {"type": "query", "content": query_display, "user_input": user_input}
        )

        if "Unable to generate a valid SQL query" in sql_query:
            st.session_state.chat_history.append({"type": "error", "content": sql_query})
        else:
            #results, column_names = execute_query(sql_query, db_path)
            results, column_names = execute_query_json(sql_query, json_path)
            if isinstance(results, str):
                st.session_state.chat_history.append({"type": "error", "content": results})
            else:
                df = pd.DataFrame(results)
                if isinstance(column_names, list) and len(results) > 0: 
                    df.columns = column_names
                st.session_state.chat_history.append({"type": "results", "content": df})

    # Display chat history with collapsible SQL query and table display inside a scrollable box
    if st.session_state.chat_history:
        st.header("Chat History")
        chat_container = st.empty()
        with chat_container.container():
            for message in reversed(st.session_state.chat_history):
                if isinstance(message, dict):
                    if message["type"] == "query":
                        with st.expander(f"Show SQL Query and Results for: {message['user_input'].upper()}"):
                            st.subheader("User Input")
                            st.write(message.get("user_input", "No user input provided"))
                            st.subheader("SQL Query")
                            st.code(message["content"], language='sql')
                            # Check if the next message is the result for this query
                            next_index = st.session_state.chat_history.index(message) + 1
                            if next_index < len(st.session_state.chat_history):
                                next_message = st.session_state.chat_history[next_index]
                                if isinstance(next_message, dict) and next_message["type"] == "results":
                                    st.subheader("Query Results")
                                    st.dataframe(next_message["content"])
                    elif message["type"] == "error":
                        st.error(message["content"])
                    elif message["type"] == "results":
                        # Skip displaying results here as they are handled with the query
                        continue
                else:
                    st.write(message)
                st.markdown("<hr>", unsafe_allow_html=True)  # Add a horizontal line for separation


if __name__ == "__main__":
    logger.info("Starting the Streamlit application...")
    main()
