import re

from database import get_connection


def get_schema():
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

        schema = {}

        for table_name, column_name, data_type in rows:
            schema.setdefault(table_name, []).append({
                "column": column_name,
                "type": data_type,
            })

        return schema

    finally:
        conn.close()


def run_readonly_sql(query: str):
    """
    Execute SELECT-only SQL.
    """

    cleaned = query.strip()

    # Must start with SELECT or WITH.
    if not re.match(r"^(SELECT|WITH)\b", cleaned, re.IGNORECASE):
        raise ValueError(
            "Only SELECT queries are allowed."
        )

    # Prevent multiple statements.
    if ";" in cleaned.rstrip(";"):
        raise ValueError(
            "Multiple SQL statements are not allowed."
        )

    forbidden = [
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

    for keyword in forbidden:
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