
import sqlglot
from sqlglot.executor import execute
import json


tables = {}

with open('output_data.json', 'r') as json_file:
    tables = json.load(json_file)

query = """
SELECT SUM(r.revenue) AS total_revenue
FROM revenues r
JOIN csa_projects p ON r.bu = p.ebs_code
WHERE p.ebs_code = 23
  AND EXTRACT(MONTH
              FROM r.data_date::DATE) = 4
  AND EXTRACT(YEAR
              FROM r.data_date::DATE) = 2024
"""

query = sqlglot.transpile(query, write="mysql", pretty=True)[0]
print(query)

result = execute(query, tables=tables)

print(type(result))
print(result)
print(result.columns)
print(result.rows)
