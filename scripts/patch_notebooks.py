from list_notebooks import list_notebooks
import os
import json


def patch_notebook(notebook_path):
    notebook = open(notebook_path, "r", encoding="utf-8").read()
    data = json.loads(notebook)
    cells = data["cells"]

    if all(
        cell["cell_type"] != "code" or cell["execution_count"] != None for cell in cells
    ):
        return False

    count = 1
    for i in range(len(cells)):
        if cells[i]["cell_type"] == "code":
            cells[i]["execution_count"] = count
            count += 1

    open(notebook_path, "w", newline="\n", encoding="utf-8").write(
        json.dumps(data, separators=(",", ": "), indent="  ", ensure_ascii=False) + "\n"
    )
    return True


def main():
    count = 0
    notebooks = list_notebooks()
    for nb in notebooks:
        if patch_notebook(nb):
            print(f"Patched {nb}")
            count += 1
    if count == 0:
        print("No notebooks to patch")


if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    os.chdir(base_dir)
    main()
