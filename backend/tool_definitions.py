from tools import get_schema, run_readonly_sql

TOOL_DEFINITIONS = [
    {
        "name": "get_schema",
        "description": (
            "Inspect the business database schema. "
            "Use this when you need to understand what tables "
            "and columns are available before writing SQL."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "run_readonly_sql",
        "description": (
            "Execute a read-only PostgreSQL query against the "
            "business database. Only SELECT and WITH queries "
            "are allowed. Use this to investigate business "
            "questions and gather quantitative evidence."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "A single SELECT or WITH PostgreSQL query."
                    ),
                }
            },
            "required": ["query"],
        },
    },
]


TOOL_FUNCTIONS = {
    "get_schema": get_schema,
    "run_readonly_sql": run_readonly_sql,
}