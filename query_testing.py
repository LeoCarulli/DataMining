import sqlite3  

try:
    mi_conexion = sqlite3.connect('database/mi_base_de_datos.db')
    cursor=mi_conexion.cursor()
    cursor.execute("SELECT csa_projects.ebs_code, MAX(revenues_actuals.revenue) AS max_revenue FROM csa_projects JOIN revenues_actuals ON csa_projects.ebs_code = revenues_actuals.bu GROUP BY csa_projects.ebs_code ORDER BY max_revenue DESC NULLS LAST LIMIT 5")
    rows=cursor.fetchall()
    for row in rows:
        print(row)
except Exception as ex:
    print(ex)