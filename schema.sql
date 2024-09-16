CREATE TABLE IF NOT EXISTS "csa_projects" (
"client_name" TEXT,
  "client_id" TEXT,
  "PROJECT_ID" TEXT,
  "ebs_code" INTEGER,
  "project_name" TEXT,
  "opportunity_name" TEXT,
  "project_type" TEXT,
  "project_type_abbreviation" TEXT,
  "SVP" TEXT,
  "NBD" REAL,
  "OPERATIONS_MANAGER" REAL,
  "project_start_date" TEXT,
  "project_end_date" TEXT,
  "project_status" REAL,
  "business_unit" TEXT,
  "opportunity_stage_name" TEXT,
  "active" INTEGER,
  "closing_date" TEXT
);
CREATE TABLE IF NOT EXISTS "kpi" (
"EBS_PROJECT_CODE" INTEGER,
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
  "Data_Date" TEXT,
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
"data_date" TEXT,
  "BU" INTEGER,
  "operational_risk" TEXT,
  "yes_or_no" TEXT,
  "reasons" TEXT
);
CREATE TABLE IF NOT EXISTS "retain_renew" (
"data_date" TEXT,
  "BU" INTEGER,
  "customer_risk" TEXT,
  "rating" REAL,
  "reasons" TEXT
);
CREATE TABLE IF NOT EXISTS "revenues" (
"BU" INTEGER,
  "data_date" TEXT,
  "revenue" REAL
);
CREATE TABLE IF NOT EXISTS "ic" (
"data_date" TEXT,
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
"data_date" TEXT,
  "ebs_business_unit" INTEGER,
  "headcount" INTEGER,
  "new_employees" INTEGER,
  "terminations" INTEGER
);
