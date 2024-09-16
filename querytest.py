import sqlite3

# Conectar a la base de datos SQLite (se creará si no existe)
db_path = './mi_base_de_datos.db'  # Asegúrate de que la ruta del archivo sea correcta
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Consulta SQL que deseas ejecutar
sql_query = """
SELECT cp.ebs_code, MAX(r.revenue) AS total_revenue FROM csa_projects cp JOIN revenues r ON cp.ebs_code = r.bu GROUP BY cp.ebs_code ORDER BY total_revenue DESC NULLS LAST LIMIT 5;
"""  # Reemplaza 'my_table' con el nombre de tu tabla

# Ejecutar la consulta
try:
    cursor.execute(sql_query)
    results = cursor.fetchall()

    # Imprimir los resultados
    for row in results:
        print(row)

except sqlite3.Error as error:
    print(f"Error al ejecutar la consulta: {error}")

finally:
    # Cerrar la conexión
    if conn:
        conn.close()
