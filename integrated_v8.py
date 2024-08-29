import streamlit as st
import sqlite3
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import sqlparse  # Importing the sqlparse library for SQL validation and formatting
import re

# Define the chatbot template and model
template = """ 
### Instructions:
Your task is to convert a question into a SQL query, given a SQLite3 database schema.
Adhere to these rules:
- **Deliberately go through the question and database schema word by word** to appropriately answer the question
- **Use Table Aliases** to prevent ambiguity. For example, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`.
- When creating a ratio, always cast the numerator as float
- Most of queries are very simple. You don´t need to use subqueries or complex joins. Just use the tables that are necessary to answer the question.
- Your replies should ONLY include SQL code. No additional text should be included in the response.
- Replies should include all columns mentioned on the question. 
- When question inclues a date filter, always filter with "data_date" column. Format as following example on January 2024: `WHERE data_date = '2024-01-31'`. 
- NEVER use "project_start_date" or "project_end_date" columns for filtering unless strictly mentioned. They are not reliable for filtering.


### Input:
Generate a SQL query that answers the question `{question}`.
This query will run on a database whose schema is represented in this string:

CREATE TABLE csa_projects (
  ebs_code STRING PRIMARY KEY, -- This is also known as Project for business purposes.
  SVP STRING, -- Senior Vice President
  NBD STRING, 
  project_start_date STRING,
  project_end_date STRING,
  active INT -- It has a 1 when active, and a 0 if inactive.
  )
;

CREATE TABLE kpi (
  EBS_PROJECT_CODE STRING, -- This is also known as Project for business purposes.
  KPI_Goal DOUBLE,
  KPI_Actual DOUBLE,
  KPI_Name STRING,
  KPI_Start_Date STRING,
  KPI_End_Date STRING,
  Progress_to_Goal_to_date DOUBLE, 
  Reasons STRING,
  Data_Date STRING -- Date of the data. It´s always the last day of the month in format YYYY-MM-DD.
  )
;

CREATE TABLE operational_risk ( 
  data_date STRING, -- Date of the data. It´s always the last day of the month in format YYYY-MM-DD.
  BU STRING, -- This is also known as Project for business purposes.
  operational_risk STRING,
  yes_or_no STRING,
  reasons STRING)
;

CREATE TABLE retain_renew ( 
  data_date STRING, -- Date of the data. It´s always the last day of the month in format YYYY-MM-DD.
  BU INT, -- This is also known as Project for business purposes.
  customer_risk STRING,
  rating INT, 
  reasons STRING)
;

CREATE TABLE revenues ( 
  BU STRING, -- This is also known as Project for business purposes.
  data_date STRING, -- Date of the data. It´s always the last day of the month in format YYYY-MM-DD.
  revenue DOUBLE)
;

CREATE TABLE turnover ( 
  data_date STRING, -- Date of the data. It´s always the last day of the month in format YYYY-MM-DD.
  ebs_business_unit STRING, -- This is also known as Project for business purposes.
  headcount INT,
  new_employees INT,
  terminations INT)

-- csa_projects.ebs_code can be joined with kpi.EBS_PROJECT_CODE
-- csa_projects.ebs_code can be joined with risk_share.EBS_Project_ID
-- csa_projects.ebs_code can be joined with operational_risk.BU
-- csa_projects.ebs_code can be joined with revenues.BU
-- csa_projects.ebs_code can be joined with turnover.ebs_business_unit
-- all tables can be joined by data_date except for csa_projects.

### Response:
Generate a SQL query to answer the question `{question}`:
"""

# Initialize the AI model with the provided template
model = OllamaLLM(model="sqlcoder")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Function to handle conversation and generate SQL query
def is_valid_sql(query):
    """Checks if the provided query is a valid SQL statement for SQLite."""
    # Remove unwanted characters and trim whitespace
    query = re.sub(r"<.*?>", "", query.strip())
    
    # Attempt to parse the SQL query
    try:
        parsed = sqlparse.parse(query)
    except Exception as e:
        return False

    # Check if the query is not empty and starts with a valid SQL keyword
    if not parsed or len(parsed) == 0:
        return False

    # Extract the first statement
    stmt = parsed[0]

    # Check if the statement starts with a known SQL command
    if stmt.tokens and stmt.tokens[0].ttype in (sqlparse.tokens.DML, sqlparse.tokens.DDL):
        return True

    return False

def execute_query(sql_query, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        return f"An error occurred: {e}"
    finally:
        conn.close()

def handle_conversation(user_input, context, db_path):
    max_attempts = 5
    attempt = 0
    
    while attempt < max_attempts:
        # Invoke the AI model
        result = chain.invoke({"context": context, "question": user_input})
        
        # Strip unwanted HTML-like tags and trim whitespace
        sql_query = re.sub(r"<.*?>", "", result.strip())
        
        # Ensure only one SQL statement is present
        if len(sqlparse.split(sql_query)) > 1:
            sql_query = sqlparse.split(sql_query)[0]  # Take only the first query
            context += f"\nUser: {user_input}\nAI: Multiple queries detected. Using only the first query."
        
        # Validate the SQL query
        if is_valid_sql(sql_query):
            # Execute the SQL query to check for errors
            execution_result = execute_query(sql_query, db_path)
            if not isinstance(execution_result, str):  # No error
                formatted_query = sqlparse.format(sql_query, reindent=True, keyword_case='upper')
                context += f"\nUser: {user_input}\nAI: {formatted_query}"
                return formatted_query, context
        
        # Increment the attempt counter
        attempt += 1
        context += f"\nUser: {user_input}\nAI: Attempt {attempt} failed. Trying again."

    # If maximum attempts reached, return a generic error message
    context += f"\nUser: {user_input}\nAI: Unable to generate a valid SQL query after {max_attempts} attempts. Please contact an administrator."
    return "Unable to generate a valid SQL query. Please contact an administrator.", context

# Streamlit app structure
def main():
    st.title("AI SQL Coder")
    st.write("Welcome to the AI SQL Coder! Please enter the SQL query you would like to see:")

    # Initialize session state variables for context and chat history
    if "context" not in st.session_state:
        st.session_state.context = ""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Path to your SQLite database file
    db_path = "database/mi_base_de_datos.db"  # Fixed the path separator

    # User input text box
    user_input = st.text_input("You: ", "")

    if user_input:
        # Handle the conversation
        sql_query, st.session_state.context = handle_conversation(user_input, st.session_state.context, db_path)
        st.session_state.chat_history.append(f"You: {user_input}")

        # Display the SQL query
        st.session_state.chat_history.append(f"SQL Query: {sql_query}")

        if "Unable to generate a valid SQL query" in sql_query:
            st.write(sql_query)  # Display generic error message
        else:
            # Execute the SQL query on SQLite and get results
            results = execute_query(sql_query, db_path)
            if isinstance(results, str):  # Error message
                st.session_state.chat_history.append(f"Error: {results}")
            else:
                st.session_state.chat_history.append(f"Results: {results}")

    # Display chat history
    if st.session_state.chat_history:
        for i, message in enumerate(st.session_state.chat_history):
            st.write(message)

if __name__ == "__main__":
    main()