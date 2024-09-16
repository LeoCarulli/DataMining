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

CREATE TABLE IF NOT EXISTS "csa_projects" (
  "ebs_code" INTEGER, -- This is also known as Project for business purposes.
  "SVP" TEXT, -- Senior Vice President
  "NBD" REAL,
  "project_type" TEXT,
  "project_start_date" TEXT,
  "project_end_date" TEXT,
  "active" INTEGER -- It has a 1 when active, and a 0 if inactive.
);

CREATE TABLE IF NOT EXISTS "kpi" (
"EBS_PROJECT_CODE" INTEGER, -- This is also known as Project for business purposes.
  "KPI_Goal" REAL,
  "KPI_Actual" REAL,
  "KPI_Name" TEXT,
  "KPI_Start_Date" TEXT,
  "KPI_End_Date" TEXT,
  "Progress_to_Goal_to_date" TEXT,
  "Reasons" REAL,
  "Data_Date" TEXT -- Date of the data. It´s always the last day of the month in format YYYY-MM-DD.
);

CREATE TABLE IF NOT EXISTS "operational_risk" (
"data_date" TEXT, -- Date of the data. It´s always the last day of the month in format YYYY-MM-DD.
  "BU" INTEGER, -- This is also known as Project for business purposes.
  "operational_risk" TEXT,
  "yes_or_no" TEXT,
  "reasons" TEXT
);

CREATE TABLE IF NOT EXISTS "retain_renew" (
"data_date" TEXT, -- Date of the data. It´s always the last day of the month in format YYYY-MM-DD.
  "BU" INTEGER, -- This is also known as Project for business purposes.
  "customer_risk" TEXT,
  "rating" REAL,
  "reasons" TEXT
);

CREATE TABLE IF NOT EXISTS "revenues" (
"BU" INTEGER, -- This is also known as Project for business purposes.
  "data_date" TEXT, -- Date of the data. It´s always the last day of the month in format YYYY-MM-DD.
  "revenue" REAL
);

CREATE TABLE IF NOT EXISTS "turnover" (
"data_date" TEXT, -- Date of the data. It´s always the last day of the month in format YYYY-MM-DD.
  "ebs_business_unit" INTEGER, -- This is also known as Project for business purposes.
  "headcount" INTEGER,
  "new_employees" INTEGER,
  "terminations" INTEGER
);

-- csa_projects.ebs_code can be joined with kpi.EBS_PROJECT_CODE
-- csa_projects.ebs_code can be joined with risk_share.EBS_Project_ID
-- csa_projects.ebs_code can be joined with operational_risk.BU
-- csa_projects.ebs_code can be joined with revenues.BU
-- csa_projects.ebs_code can be joined with turnover.ebs_business_unit
-- all tables can be joined by data_date except for csa_projects.

### Response:
Generate a SQL query to answer the question `{question}`:
```sql
"""


prompt_7b_2 = """
### Task
Generate a SQL query to answer [QUESTION]{question}[/QUESTION]

### Database Schema
The query will run on a database with the following schema:

CREATE TABLE IF NOT EXISTS "csa_projects" (
"client_name" TEXT,
  "client_id" TEXT,
  "PROJECT_ID" TEXT,
  "ebs_code" INTEGER, -- This is also known as Project for business purposes.
  "project_name" TEXT,
  "opportunity_name" TEXT,
  "project_type" TEXT,
  "project_type_abbreviation" TEXT,
  "SVP" TEXT, -- Senior Vice President
  "NBD" REAL,
  "OPERATIONS_MANAGER" REAL,
  "project_start_date" TEXT,
  "project_end_date" TEXT,
  "project_status" REAL,
  "business_unit" TEXT,
  "opportunity_stage_name" TEXT,
  "active" INTEGER, -- It has a 1 when active, and a 0 if inactive.
  "closing_date" TEXT
);

CREATE TABLE IF NOT EXISTS "kpi" (
"EBS_PROJECT_CODE" INTEGER, -- This is also known as Project for business purposes.
  "KPI_Goal" REAL,
  "KPI_Actual" REAL,
  "KPI_Name" TEXT,
  "KPI_Start_Date" TEXT,
  "KPI_End_Date" TEXT,
  "Progress_to_Goal_to_date" TEXT,
  "Access" TEXT,
  "CRM" TEXT,
  "Client_Data_To_Syneos" TEXT,
  "Reporting_Frequency" TEXT,
  "Department_Head" REAL,
  "Reasons" REAL,
  "Data_Date" TEXT, -- Date of the data. It´s always the last day of the month in format YYYY-MM-DD.
  "Reporting_period" TEXT,
  "Client_Services" TEXT,
  "Project_Category" TEXT
);

CREATE TABLE IF NOT EXISTS "risk_share" (
"Data_Date" TEXT,
  "EBS_Project_ID" TEXT,
  "Business_Line" TEXT,
  "Actual_Pool" REAL,
  "Earned" REAL,
  "Act_Pct" REAL,
  "Year" INTEGER,
  "Timing" REAL,
  "quarter" TEXT,
  "Month_Recognized" TIMESTAMP,
  "Sales_Ops" TEXT,
  "Metric" TEXT
);

CREATE TABLE IF NOT EXISTS "operational_risk" (
"data_date" TEXT, -- Date of the data. It´s always the last day of the month in format YYYY-MM-DD.
  "BU" INTEGER, -- This is also known as Project for business purposes.
  "operational_risk" TEXT,
  "yes_or_no" TEXT,
  "reasons" TEXT
);

CREATE TABLE IF NOT EXISTS "retain_renew" (
"data_date" TEXT, -- Date of the data. It´s always the last day of the month in format YYYY-MM-DD.
  "BU" INTEGER, -- This is also known as Project for business purposes.
  "customer_risk" TEXT,
  "rating" REAL,
  "reasons" TEXT
);

CREATE TABLE IF NOT EXISTS "revenues" (
"BU" INTEGER, -- This is also known as Project for business purposes.
  "data_date" TEXT, -- Date of the data. It´s always the last day of the month in format YYYY-MM-DD.
  "revenue" REAL
);

CREATE TABLE IF NOT EXISTS "ic" (
"data_date" TEXT, -- Date of the data. It´s always the last day of the month in format YYYY-MM-DD.
  "F_Code" INTEGER,
  "Business_Unit" TEXT,
  "Period" TEXT,
  "year" REAL,
  "Plan_Status" TEXT,
  "Amendments_Yr" REAL,
  "Amendments_for_Target" REAL,
  "Plan_Engagement_75" TEXT,
  "Target_Earning" REAL,
  "Actual_Earning" REAL,
  "Actual_Payout" REAL,
  "Earning_to_Originals" REAL,
  "Earning_to_Original_Reason" TEXT,
  "Comments" REAL
);
CREATE TABLE IF NOT EXISTS "trafficlight" (
"BU" INTEGER,
  "data_date" TEXT,
  "colour" TEXT
);

CREATE TABLE IF NOT EXISTS "turnover" (
"data_date" TEXT, -- Date of the data. It´s always the last day of the month in format YYYY-MM-DD.
  "ebs_business_unit" INTEGER, -- This is also known as Project for business purposes.
  "headcount" INTEGER,
  "new_employees" INTEGER,
  "terminations" INTEGER
);


-- csa_projects.ebs_code can be joined with kpi.EBS_PROJECT_CODE
-- csa_projects.ebs_code can be joined with risk_share.EBS_Project_ID
-- csa_projects.ebs_code can be joined with operational_risk.BU
-- csa_projects.ebs_code can be joined with revenues.BU
-- csa_projects.ebs_code can be joined with turnover.ebs_business_unit
-- all tables can be joined by data_date except for csa_projects.

### Constraints:
- Write SQL code compatible with SQLite3, do NOT use functionalities from postgres or Oracle, only pure SQL.
- **Deliberately go through the question and database schema word by word** to appropriately answer the question
- **Use Table Aliases** to prevent ambiguity. For example, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`.
- When creating a ratio, always cast the numerator as float.
- Most of queries are very simple. You don´t need to use subqueries or complex joins. Just use the tables that are necessary to answer the question.
- Your replies should ONLY include SQL code. No additional text should be included in the response.
- Replies should include all columns mentioned on the question. 
- NEVER use "project_start_date" or "project_end_date" columns for filtering. They are not reliable for filtering.

### Answer
Given the database schema and the constraints, here is the SQL query that [QUESTION]{question}[/QUESTION]
[SQL]
"""
