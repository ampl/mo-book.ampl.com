import json
import re
import os
import argparse
from pathlib import Path

# Define the regex to identify notebooks to skip
SKIP_REGEX = re.compile(
    r"authenticate_user|gspread\.authorize|gmaps\.configure|powerbiclient|API_KEY|pyvpsolver"
)


def should_skip(notebook_path):
    if notebook_path.startswith(("venv", "_build", "build")):
        return True
    with open(notebook_path, "r", encoding="utf-8") as f:
        content = f.read()
        return bool(SKIP_REGEX.search(content))


def main():
    parser = argparse.ArgumentParser(
        description="Scan .ipynb files and list notebooks."
    )
    parser.add_argument(
        "--list-skipped",
        action="store_true",
        help="List notebooks that should be skipped",
    )
    parser.add_argument(
        "--list-all",
        action="store_true",
        help="List all notebooks",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )

    args = parser.parse_args()

    notebooks = list(map(str, Path(".").rglob("*.ipynb")))

    skipped = set()
    included = set()

    for nb in notebooks:
        if should_skip(nb):
            skipped.add(nb)
        else:
            included.add(nb)

    notebooks = []

    if args.list_skipped:
        notebooks = list(sorted(skipped))
    elif args.list_all:
        notebooks = list(sorted(included | skipped))
    else:
        notebooks = list(sorted(included))

    if not args.json:
        for nb in sorted(notebooks):
            print(nb)
    else:
        print(json.dumps(notebooks))


if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    os.chdir(base_dir)
    main()
