
import sqlglot
from sqlglot.executor import execute
import json


tables = {}

with open('output_data.json', 'r') as json_file:
    tables = json.load(json_file)

query = """
 SELECT SUM(r.revenue) AS total_revenue FROM revenues r WHERE r.BU = 23 AND EXTRACT(MONTH FROM TO_DATE(r.data_date, 'YYYY-MM-DD')) = 4;
"""

query = sqlglot.transpile(query, pretty=True)[0]
print(query)

result = execute(query, tables=tables)

print(type(result))
print(result)
print(result.columns)
print(result.rows)
