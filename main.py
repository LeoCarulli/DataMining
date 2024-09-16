import os
import pandas as pd
import streamlit as st
import logging
import sqlparse
import re
from model_config import initialize_model  # Asegúrate de importar initialize_model
from validation import is_valid_sql
from execution import execute_query

# Configuración básica de logging
logging.basicConfig(level=logging.INFO,  # Cambiar el nivel a INFO para eliminar DEBUG
                    format='%(levelname)s: %(message)s')  # Mensajes de log básicos
logger = logging.getLogger()

def handle_conversation(user_input, context, db_path, chain, max_attempts=5):
    attempt = 0
    
    while attempt < max_attempts:
        # Invocar el modelo AI para generar la consulta SQL
        result = chain.invoke({"context": context, "question": user_input})
        sql_query = re.sub(r"<.*?>", "", result.strip())
        
        # Asegurarse de que solo se ejecute una consulta SQL
        parsed_queries = sqlparse.split(sql_query)
        if len(parsed_queries) > 1:
            sql_query = parsed_queries[0]  # Tomar solo la primera consulta
            logger.info(f"Multiple queries detected. Only the first query will be executed.")
        
        # Validar la consulta SQL
        if is_valid_sql(sql_query):
            # Formatear la consulta SQL
            formatted_query = sqlparse.format(sql_query, reindent=True, keyword_case='upper')
            
            # Ejecutar la consulta SQL
            execution_result, _ = execute_query(formatted_query, db_path)
            if not isinstance(execution_result, str):  # La consulta fue exitosa
                context += f"\nUser: {user_input}\nAI: {formatted_query}"
                return formatted_query, context
            else:
                logger.error(f"Error executing SQL query: {execution_result}")
        else:
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

    # Inicializar el modelo (el `chain`) cuando la aplicación se inicia
    chain = initialize_model()

    st.markdown("### Enter your query below:")
    user_input = st.text_input("You: ", "", placeholder="Haz tu pregunta aquí...")

    if user_input:
        sql_query, st.session_state.context = handle_conversation(user_input, st.session_state.context, db_path, chain)

        # Store SQL query in chat history with collapse functionality
        query_display = f"SQL Query: {sql_query}"
        st.session_state.chat_history.append(
            {"type": "query", "content": query_display, "user_input": user_input}
        )

        if "Unable to generate a valid SQL query" in sql_query:
            st.session_state.chat_history.append({"type": "error", "content": sql_query})
        else:
            results, column_names = execute_query(sql_query, db_path)
            if isinstance(results, str):
                st.session_state.chat_history.append({"type": "error", "content": results})
            else:
                df = pd.DataFrame(results)

                # Solo asignar los nombres de columna si los resultados tienen columnas
                if df.shape[1] > 0 and isinstance(column_names, list) and len(column_names) == df.shape[1]:
                    df.columns = column_names
                else:
                    logger.warning("El número de columnas en los resultados no coincide con el número de nombres de columnas.")

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