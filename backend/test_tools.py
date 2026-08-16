from tool_definitions import TOOL_FUNCTIONS


def main():
    print("Available tools:")
    print()

    for tool_name in TOOL_FUNCTIONS:
        print(f"- {tool_name}")

    print()

    schema = TOOL_FUNCTIONS["get_schema"]()

    print("Tables found:")

    for table_name in schema:
        print(f"- {table_name}")


if __name__ == "__main__":
    main()