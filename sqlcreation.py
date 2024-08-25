import sqlite3
import pandas as pd

# Conectar a la base de datos (o crear una si no existe)
conn = sqlite3.connect('mi_base_de_datos.db')
cursor = conn.cursor()

# Crear las tablas (las mismas que antes)
cursor.execute('''CREATE TABLE IF NOT EXISTS csa_projects (
                    client_name TEXT,
                    client_id TEXT,
                    PROJECT_ID TEXT,
                    ebs_code TEXT PRIMARY KEY,
                    project_name TEXT,
                    opportunity_name TEXT,
                    project_type TEXT,
                    project_type_abbreviation TEXT,
                    SVP TEXT,
                    NBD TEXT,
                    OPERATIONS_MANAGER TEXT,
                    project_start_date TEXT,
                    project_end_date TEXT,
                    project_status INTEGER,
                    business_unit TEXT,
                    opportunity_stage_name TEXT,
                    active INTEGER,
                    closing_date TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS kpi (
                    EBS_PROJECT_CODE TEXT,
                    KPI_Goal REAL,
                    KPI_Actual REAL,
                    KPI_Name TEXT,
                    KPI_Start_Date TEXT,
                    KPI_End_Date TEXT,
                    Progress_to_Goal_to_date REAL,
                    Access TEXT,
                    CRM TEXT,
                    Client_Data_To_Syneos TEXT,
                    Reporting_Frequency TEXT,
                    Department_Head TEXT,
                    Reasons TEXT,
                    Data_Date TEXT,
                    Reporting_period TEXT,
                    Client_Services TEXT,
                    Project_Category TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS risk_share (
                    Data_Date TEXT,
                    EBS_Project_ID TEXT,
                    Business_Line TEXT,
                    Actual_Pool REAL,
                    Earned REAL,
                    Act_Pct REAL,
                    Year TEXT,
                    Timing TEXT,
                    quarter TEXT,
                    Month_Recognized TEXT,
                    Sales_Ops TEXT,
                    Metric TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS operational_risk (
                    data_date TEXT,
                    BU TEXT,
                    operational_risk TEXT,
                    yes_or_no TEXT,
                    reasons TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS retain_renew (
                    data_date TEXT,
                    BU INTEGER,
                    customer_risk TEXT,
                    rating INTEGER,
                    reasons TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS revenues_actuals (
                    BU TEXT,
                    year INTEGER,
                    month INTEGER,
                    revenue REAL
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS ic (
                    data_date TEXT,
                    F_Code TEXT,
                    Business_Unit TEXT,
                    Period TEXT,
                    year TEXT,
                    Plan_Status TEXT,
                    Amendments_Yr TEXT,
                    Amendments_for_Target TEXT,
                    Plan_Engagement_75 TEXT,
                    Target_Earning REAL,
                    Actual_Earning REAL,
                    Actual_Payout REAL,
                    Earning_to_Originals REAL,
                    Earning_to_Original_Reason TEXT,
                    Comments TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS trafficlight (
                    BU TEXT,
                    colour TEXT,
                    Month INTEGER,
                    Year INTEGER
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS turnover (
                    month INTEGER,
                    year INTEGER,
                    ebs_business_unit TEXT,
                    headcount INTEGER,
                    terminations INTEGER
                )''')

# Cargar datos desde el archivo Excel
file_path = 'D:/Maestria_Austral/11-TextMining/SQLcoderApp/data/Anonimized_data.xlsx'

# Diccionario de tablas y sus pestañas correspondientes
tablas_y_hojas = {
    'csa_projects': 'csa_anonimized',
    'kpi': 'kpi',
    'risk_share': 'riskshare',
    'operational_risk': 'or',
    'retain_renew': 'rr',
    'revenues_actuals': 'ic',
    'ic': 'revenue',
    'trafficlight': 'trafficlight',
    'turnover': 'turnover'
}

for tabla, hoja in tablas_y_hojas.items():
    # Leer la hoja de Excel
    df = pd.read_excel(file_path, sheet_name=hoja)
    # Cargar datos en la tabla correspondiente
    df.to_sql(tabla, conn, if_exists='replace', index=False)

# Realizar una consulta de ejemplo
df_resultados = pd.read_sql_query("SELECT * FROM csa_projects", conn)
print(df_resultados)

# Cerrar la conexión
conn.close()
