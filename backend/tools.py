import re
from typing import Any

from database import get_connection


def get_schema() -> dict[str, list[dict[str, str]]]:
    """
    Return the public database schema.

    The agent uses this to understand:
    - which tables exist
    - which columns exist
    - the data types of those columns
    """

    query = """
        SELECT
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

        schema: dict[str, list[dict[str, str]]] = {}

        for table_name, column_name, data_type in rows:
            schema.setdefault(table_name, []).append(
                {
                    "column": column_name,
                    "type": data_type,
                }
            )

        return schema

    finally:
        conn.close()


def run_readonly_sql(query: str) -> dict[str, Any]:
    """
    Execute a read-only SQL query.

    Only SELECT/WITH queries are allowed.
    The database is never modified through this tool.
    """

    cleaned = query.strip()

    if not cleaned:
        raise ValueError("SQL query cannot be empty.")

    # Allow SELECT and CTE queries.
    if not re.match(r"^(SELECT|WITH)\b", cleaned, re.IGNORECASE):
        raise ValueError(
            "Only SELECT or WITH queries are allowed."
        )

    # Only one SQL statement.
    if ";" in cleaned.rstrip(";"):
        raise ValueError(
            "Multiple SQL statements are not allowed."
        )

    forbidden_keywords = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "GRANT",
        "REVOKE",
    ]

    upper_query = cleaned.upper()

    for keyword in forbidden_keywords:
        if re.search(rf"\b{keyword}\b", upper_query):
            raise ValueError(
                f"Forbidden SQL operation: {keyword}"
            )

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(cleaned)

            columns = [
                description[0]
                for description in cur.description
            ]

            rows = cur.fetchall()

        return {
            "columns": columns,
            "rows": rows,
        }

    finally:
        conn.close()