import sqlite3
import pandas as pd

# Conectar a la base de datos (o crear una si no existe)
conn = sqlite3.connect('mi_base_de_datos_v4.db')
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
                    project_start_date DATE,
                    project_end_date DATE,
                    project_status INTEGER,
                    business_unit TEXT,
                    opportunity_stage_name TEXT,
                    active INTEGER,
                    closing_date DATE
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS kpi (
                    EBS_PROJECT_CODE TEXT,
                    KPI_Goal REAL,
                    KPI_Actual REAL,
                    KPI_Name TEXT,
                    KPI_Start_Date DATE,
                    KPI_End_Date DATE,
                    Progress_to_Goal_to_date REAL,
                    Access TEXT,
                    CRM TEXT,
                    Client_Data_To_Syneos TEXT,
                    Reporting_Frequency TEXT,
                    Department_Head TEXT,
                    Reasons TEXT,
                    Data_Date DATE,
                    Reporting_period TEXT,
                    Client_Services TEXT,
                    Project_Category TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS risk_share (
                    Data_Date DATE,
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
                    data_date DATE,
                    BU TEXT,
                    operational_risk TEXT,
                    yes_or_no TEXT,
                    reasons TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS retain_renew (
                    data_date DATE,
                    BU INTEGER,
                    customer_risk TEXT,
                    rating INTEGER,
                    reasons TEXT
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS revenues (
                    data_date DATE,
                    BU TEXT,
                    revenue REAL
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS ic (
                    data_date DATE,
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
                    data_date DATE,
                    colour TEXT,
                    Month INTEGER,
                    Year INTEGER
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS turnover (
                    data_date DATE,
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
    'retain_renew': 'custrisk',
    'revenues': 'revenue',
    'ic': 'ic',
    'trafficlight': 'trafficlight',
    'turnover': 'turnover'
}

for tabla, hoja in tablas_y_hojas.items():
    # Leer la hoja de Excel
    df = pd.read_excel(file_path, sheet_name=hoja)
    
    # Convertir las columnas de fecha al formato adecuado
    date_columns = [col for col in df.columns if 'date' in col.lower()]
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
    
    # Cargar datos en la tabla correspondiente
    df.to_sql(tabla, conn, if_exists='replace', index=False)

# Realizar una consulta de ejemplo
df_resultados = pd.read_sql_query("SELECT * FROM csa_projects", conn)
print(df_resultados)

# Cerrar la conexión
conn.close()
