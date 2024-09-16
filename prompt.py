# Define the chatbot template and model
template = """ 
### Instructions:
Your task is to convert a question into a SQL query, given a SQLite3 database schema.
Adhere to these rules:
- **Deliberately go through the question and database schema word by word** to appropriately answer the question
- **Use Table Aliases** to prevent ambiguity. For example, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`.
- When creating a ratio, always cast the numerator as float.
- Most of queries are very simple. You don´t need to use subqueries or complex joins. Just use the tables that are necessary to answer the question.
- Your replies should ONLY include SQL code. No additional text should be included in the response.
- Replies should include all columns mentioned on the question. 
- When a date question is made, you should always filter with the following format: `WHERE data_date = 'YYYY-MM-DD'`. 
- NEVER use "project_start_date" or "project_end_date" columns for filtering. They are not reliable for filtering.
- ONLY use data_date columns when filtering by date.


### Input:
Generate a SQL query that answers the question `{question}`.
This query will run on a database whose schema is represented in this string:

CREATE TABLE csa_projects (
  ebs_code STRING PRIMARY KEY, -- This is also known as Project for business purposes.
  SVP STRING, -- Senior Vice President
  NBD STRING, 
  project_type STRING,
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
