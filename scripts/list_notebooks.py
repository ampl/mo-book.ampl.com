import json
import re
import os
import ast
import argparse
from pathlib import Path

# Define the regex to identify notebooks to skip
SKIP_REGEX = re.compile(
    r"authenticate_user|gspread\.authorize|gmaps\.configure|powerbiclient|API_KEY|pyvpsolver"
)
SKIP_NB_LIST = {"ampl_power.ipynb"}


def list_notebooks(mode="default"):
    """
    Return list of notebooks.

    mode:
      - "default": only non-skipped notebooks
      - "skipped": only skipped notebooks
      - "all": all notebooks (skipped + non-skipped)
    """
    all_notebooks = list(map(str, Path(".").rglob("*.ipynb")))

    skipped = set()
    included = set()

    for nb in all_notebooks:
        if should_skip(nb):
            skipped.add(nb)
        else:
            included.add(nb)

    if mode == "skipped":
        return sorted(skipped)
    elif mode == "all":
        return sorted(included | skipped)
    else:  # "default"
        return sorted(included)


def should_skip(notebook_path):
    if os.path.basename(notebook_path) in SKIP_NB_LIST:
        return True
    if notebook_path.startswith(("venv", "_build", "build")):
        return True
    with open(notebook_path, "r", encoding="utf-8") as f:
        content = f.read()
        if "amplpy" not in content:
            return True
        return bool(SKIP_REGEX.search(content))


def extract_imports(code):
    """Extract top-level package names from import statements using AST."""
    try:
        tree = ast.parse(code)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.add(n.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
        return imports
    except Exception:
        return set()


def extract_installed_packages(code):
    """Extract package names from pip install commands."""
    install_lines = re.findall(r"[%!]pip install ([^\n\r]+)", code)
    installed = set()
    for line in install_lines:
        parts = re.split(r"[ \t]+", line.strip())
        for part in parts:
            if part.startswith("-"):
                continue
            pkg = re.split(r"[=<>]", part)[0]
            installed.add(pkg.strip().lower())
    return installed


def find_missing_installs(notebook_path):
    try:
        with open(notebook_path, "r", encoding="utf-8") as f:
            nb = json.load(f)
    except Exception as e:
        print(f"Could not open {notebook_path}: {e}")
        return None

    imported = set()
    installed = {
        "io",
        "time",
        "ipython",
        "math",
        "datetime",
        "fractions",
        "warnings",
        "ast",
        "sys",
        "os",
        "bisect",
        "itertools",
        "timeit",
        "glob",
        "random",
    }

    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            source = "".join(cell.get("source", []))
            imported |= extract_imports(source)
            installed |= extract_installed_packages(source)

    # Rename packages with different import and package names
    package_name = {"sklearn": "scikit-learn", "mpl_toolkits": "matplotlib"}
    imported = {package_name.get(pkg, pkg) for pkg in imported}

    missing = {pkg for pkg in imported if pkg.lower() not in installed}
    if missing:
        return {"notebook": notebook_path, "missing_packages": sorted(missing)}
    return None


def contains_solve_result_assert(notebook_path):
    pattern = re.compile(
        r"assert\s+(?:self\.)?[\w]*\.?solve_result\s*(==|in).*,\s*(?:self\.)?[\w]*.?solve_result"
    )
    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    for cell in notebook.get("cells", []):
        if cell.get("cell_type") == "code":
            source = "".join(cell.get("source", []))
            if pattern.search(source):
                return True
    return False


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
    parser.add_argument(
        "--check-missing-installs",
        action="store_true",
        help="Show notebooks that import packages not installed with pip",
    )
    parser.add_argument(
        "--check-missing-asserts",
        action="store_true",
        help="Show notebooks that do not have asserts on solve_result",
    )

    args = parser.parse_args()
    if args.list_skipped:
        mode = "skipped"
    elif args.list_all:
        mode = "all"
    else:
        mode = "default"

    notebooks = list_notebooks(mode)

    if args.check_missing_installs:
        problems = []
        for nb in notebooks:
            result = find_missing_installs(nb)
            if result:
                problems.append(result)

        if args.json:
            print(json.dumps(problems, indent=2))
        else:
            for item in problems:
                print(f"\n❌ {item['notebook']}")
                print("   Missing packages:", ", ".join(item["missing_packages"]))

        if not problems:
            print("✅ No missing package installs found.")
    elif args.check_missing_asserts:
        problems = []
        for nb in notebooks:
            if not contains_solve_result_assert(nb):
                problems.append(nb)

        if args.json:
            print(json.dumps(problems, indent=2))
        else:
            for nb in problems:
                print(f"\n❌ {nb}")

        if not problems:
            print("✅ No notebooks with missing asserts found.")
    else:
        if args.json:
            print(json.dumps(notebooks))
        else:
            for nb in notebooks:
                print(nb)


if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    os.chdir(base_dir)
    main()
