import streamlit as st # type: ignore
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Define the chatbot template and model
template = """ 
### Instructions:
Your task is to convert a question into a SQL query, given a Spark SQL database schema.
Adhere to these rules:
- **Deliberately go through the question and database schema word by word** to appropriately answer the question
- **Use Table Aliases** to prevent ambiguity. For example, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`.
- When creating a ratio, always cast the numerator as float
- Most of queries are very simple. You don´t need to use subqueries or complex joins. Just use the tables that are necessary to answer the question.
- Your replies should ONLY include SQL code. No additional text should be included in the response.

### Input:
Generate a SQL query that answers the question `{question}`.
This query will run on a database whose schema is represented in this string:
CREATE TABLE csa_projects (
  client_name STRING, -- It´s the name of ebs_code but in description format.
  client_id STRING, -- It´s the name of ebs_code, but we don´t use this. 
  PROJECT_ID STRING, -- We don´t use this column. It´s just for reference
  ebs_code STRING PRIMARY KEY, -- Unique ID for each project. Equivalent to EBS_PROJECT_CODE and BU in other tables. Should be included on almost all queries.
  project_name STRING, -- We don´t use this column. It´s just for reference
  opportunity_name STRING,
  project_type STRING,
  project_type_abbreviation STRING,
  SVP STRING, -- Senior Vice President
  NBD STRING, -- New Business Developer
  OPERATIONS_MANAGER STRING,
  project_start_date STRING,
  project_end_date STRING,
  project_status INT,
  business_unit STRING,
  opportunity_stage_name STRING,
  active INT,
  closing_date DATE)
;

CREATE TABLE kpi ( --shows the KPIs for each project
  EBS_PROJECT_CODE STRING,
  KPI_Goal DOUBLE,
  KPI_Actual DOUBLE,
  KPI_Name STRING,
  KPI_Start_Date STRING,
  KPI_End_Date STRING,
  Progress_to_Goal_to_date DOUBLE, 
  Access STRING,
  CRM STRING,
  Client_Data_To_Syneos STRING,
  Reporting_Frequency STRING,
  Department_Head STRING,
  Reasons STRING,
  Data_Date DATE, -- Date of the data. It´s always the last day of the month and is common accross all tables.
  Reporting_period STRING,
  Client_Services STRING,
  Project_Category STRING)
;

CREATE TABLE risk_share ( --It shows financial information but only for specific metrics.
  Data_Date STRING, -- Date of the data. It´s always the last day of the month and is common accross all tables.
  EBS_Project_ID STRING, 
  Business_Line STRING,
  Actual_Pool DOUBLE, -- Money that we actually received on that metric
  Earned DOUBLE, -- Money that we supposedly should have received on that metric
  Act_Pct DOUBLE, -- Division of Actual_Pool by Earned. If it´s 1, it means we received all the money we should have received for that metric
  Year STRING,
  Timing STRING,
  quarter STRING,
  Month_Recognized STRING,
  Sales_Ops STRING,
  Metric STRING)
;

CREATE TABLE operational_risk ( --shows the main risk metrics for operational risk on each project. "operational_risk" column has the following categories: Finance, Client Services, Data Management, Strat Ops, Reporting, Targeting & Alignment, Fleet, IC, Compliance, Rosters, CRM, Turnover, Recruiting, Data Access. yes_or_no column indicates if there is a risk or not by placing "Yes" or "No"
  data_date TIMESTAMP, -- Date of the data. It´s always the last day of the month and is common accross all tables.
  BU STRING,
  operational_risk STRING,
  yes_or_no STRING,
  reasons STRING) -- Reason of the risk. Only present on "Yes" rows
;

CREATE TABLE retain_renew ( --shows the main risk metrics for retain & renew for each project. "Strenght of Customer Partnership with Syneos", "Customer Financial Risk", "Value Gap between Syneos and customer", "Overall risk of losing this project", "Brand Performance". The rating is from 1 to 5, 5 being the highest risk. By this way, 5 is the higher risk. 
  data_date STRING, -- Date of the data. It´s always the last day of the month and is common accross all tables.
  BU INT,
  customer_risk STRING,
  rating INT, -- 1 to 5, 5 being the highest risk
  reasons STRING) -- Reason of the risk. Only present on rows higher than 2
;

CREATE TABLE revenues_actuals ( -- This table shows the actual revenues for each project by each year and month. we only hace information until last month.
  BU STRING,
  data_date STRING, -- Date of the data. It´s always the last day of the month and is common accross all tables.
  revenue DOUBLE)
;

CREATE TABLE churn_monthly (
  data_date STRING, -- Date of the data. It´s always the last day of the month and is common accross all tables.
  start_projects INT, -- Number of projects at the beginning of the month
  acquired_projects INT, -- Number of projects acquired during the month
  churned_projects INT, -- Number of projects churned during the month
  churn_rate FLOAT) -- Churn rate for the month
;

Additional comments and rules:

-- csa_projects.ebs_code can be joined with kpi.EBS_PROJECT_CODE
-- csa_projects.ebs_code can be joined with risk_share.EBS_Project_ID
-- csa_projects.ebs_code can be joined with operational_risk.BU
-- csa_projects.ebs_code can be joined with revenues_actuals.BU
-- all tables can be joined by data_date except for csa_projects.
-- For table names, use the following aliases: csa_projects as CSA, kpi as KPI, risk_share as RS, operational_risk as OR, retain_renew as RR, revenues_actuals as REV, churn_monthly as CHU
-- We do not want to join csa_projects with other tables other than by ebs_code connection. We don´t want to join by project_start_date or project_end_date.
-- except for churn_monthly, all other tables can be related by csa_projects.ebs_code
-- Project is equivalent to EBS_PROJECT_CODE, BU, or ebs_code.
-- When someone asks about revenue, we want to search on "revenues_actuals" table. 

### Response:
Based on your instructions, here is the SQL query I have generated to answer the question `{question}`:
```sql
"""


model = OllamaLLM(model="sqlcoder")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Function to handle conversation and update context
def handle_conversation(user_input, context):
    result = chain.invoke({"context": context, "question": user_input})
    context += f"\nUser: {user_input}\nAI: {result}"
    return result, context

# Streamlit app structure
def main():
    st.title("AI SQL Coder")
    st.write("Welcome to the AI SQL Coder! Please enter the sql query you would want to see:")

    # Initialize session state variables for context and chat history
    if "context" not in st.session_state:
        st.session_state.context = ""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # User input text box
    user_input = st.text_input("You: ", "")

    if user_input:
        # Handle the conversation
        result, st.session_state.context = handle_conversation(user_input, st.session_state.context)
        st.session_state.chat_history.append(f"You: {user_input}")
        st.session_state.chat_history.append(f"Bot: {result}")

    # Display chat history
    if st.session_state.chat_history:
        for i, message in enumerate(st.session_state.chat_history):
            st.write(message)

if __name__ == "__main__":
    main()
