import sqlite3
import json
from collections import defaultdict

def sqlite_to_json(db_path, output_json):
    # Conectar a la base de datos SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Obtener todas las tablas de la base de datos
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Diccionario donde se almacenarán los datos
    data = defaultdict(list)

    # Recorrer todas las tablas y extraer sus datos
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = [desc[0] for desc in cursor.description]  # Nombres de columnas
        rows = cursor.fetchall()

        # Convertir cada fila en un diccionario (clave: nombre de la columna)
        for row in rows:
            row_dict = dict(zip(columns, row))
            data[table_name].append(row_dict)

    # Escribir los datos en un archivo JSON
    with open(output_json, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    # Cerrar la conexión
    conn.close()

# Ejemplo de uso
sqlite_to_json('mi_base_de_datos.db', 'output_data.json')

