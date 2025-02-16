import os
import sys
import json
from BAS_Database import BAS_Database

# Hello I am an agroforestry service based in the Netherlands and we would like some UN climate initiative to join


def get_report_section(search_query: str) -> list[dict]:
    """
    Perform RAG search for report data.
    """
    db = BAS_Database()
    result = db.get_report_section(search_query)
    return result


if __name__ == "__main__":
    # Get company name from command line arguments
    if len(sys.argv) > 1:
        search_query = sys.argv[1]
        try:
            content = get_report_section(search_query)
            print(json.dumps(content))
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: Not enough arguments provided", file=sys.stderr)
        sys.exit(1)
