
from sqlglot.executor import execute
import json


tables = {}

with open('output_data.json', 'r') as json_file:
    tables = json.load(json_file)

result = execute("""
SELECT csa_projects.ebs_code,
       SUM(turnover.terminations) AS total_terminations
FROM csa_projects
JOIN turnover ON csa_projects.ebs_code = turnover.ebs_business_unit
WHERE EXTRACT(MONTH
              FROM turnover.data_date::DATE) = 4
  AND EXTRACT(YEAR
              FROM turnover.data_date::DATE) = 2024
GROUP BY csa_projects.ebs_code
ORDER BY total_terminations DESC
LIMIT 5;
""", tables=tables)

print(type(result))
print(result)
print(result.columns)
print(result.rows)
