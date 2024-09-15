# validation.py

import re
import sqlparse

def is_valid_sql(query):
    """Checks if the provided query is a valid SQL statement for SQLite."""
    # Remove unwanted characters and trim whitespace
    query = re.sub(r"<.*?>", "", query.strip())
    
    # Attempt to parse the SQL query
    try:
        parsed = sqlparse.parse(query)
    except Exception as e:
        return False

    # Check if the query is not empty and starts with a valid SQL keyword
    if not parsed or len(parsed) == 0:
        return False

    # Extract the first statement
    stmt = parsed[0]

    # Check if the statement starts with a known SQL command
    if stmt.tokens and stmt.tokens[0].ttype in (sqlparse.tokens.DML, sqlparse.tokens.DDL):
        return True

    return False
