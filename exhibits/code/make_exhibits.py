"""Write every table and draw every figure that the paper and its Web Appendix display, from this package's results.

    python exhibits/code/make_exhibits.py              every table and figure that exhibits.json lists
    python exhibits/code/make_exhibits.py --tables     the tables only
    python exhibits/code/make_exhibits.py --figures    the figures only

exhibits.json, beside this file, lists each table and figure that the paper displays, where it appears and the
function that makes it. A table is written to exhibits/results/tables/<name>.md as the paper's own code prints it (its
title, the table and its notes, in Markdown with LaTeX for the symbols); a figure is drawn into
exhibits/results/figures/ as a PDF and a PNG. Each long table, which the Web Appendix shows only in part, is also
written whole as a CSV file in the results/tables/ folder of the study that it reports (FULL_TABLES below), with the
cells as the table prints them. A table or figure that cannot be made is named with its error, and the command then
ends with status 1.
"""
import csv
import json
import re
import sys
import traceback
from pathlib import Path

CODE = Path(__file__).resolve().parent
PKG = CODE.parents[1]   # the package
TABLES_OUT = PKG / "exhibits" / "results" / "tables"
sys.path.insert(0, str(CODE))
sys.path.insert(0, str(PKG / "common"))   # the corpus's tables and conditions (common/experiment/)

# each long table of the Web Appendix -> the file that holds all of its rows (full_tables.json, beside this file, lists
# every such file with what it holds; the measure's own tables are written by its code, measure_tables.py)
FULL_TABLES = {t["key"]: t["file"] for t in json.loads((CODE / "full_tables.json").read_text(encoding="utf-8"))
               if t["key"]}
# each full table's number of rows, which the file must hold (a table printed in part must not be written in part)
FULL_ROWS = {t["key"]: t["rows"] for t in json.loads((CODE / "full_tables.json").read_text(encoding="utf-8"))
             if t["key"] and "rows" in t}
CELL = re.compile(r"(?<!\\)\|")


def table_rows(text: str) -> list[list[str]]:
    """The cells of the pipe tables in a table's text, as printed: the header once, then every row. When the text holds
    several tables with one header (the 34 product tables), a first column gives each row's table, from its caption."""
    lines = text.splitlines()
    blocks, i = [], 0
    while i < len(lines):
        if lines[i].startswith("|"):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            near = [l for l in lines[j:j + 3] + lines[max(0, i - 3):i] if l.startswith("Table: ")]
            blocks.append((near[0][7:].split(" {#")[0].strip() if near else "", lines[i:j]))
            i = j
        else:
            i += 1
    if not blocks:
        raise ValueError("no table in the text")

    def cells(line):
        return [c.strip().replace("\\|", "|") for c in CELL.split(line.strip())[1:-1]]
    headers = {tuple(cells(b[1][0])) for b in blocks}
    if len(headers) > 1:
        # a table printed in parts that share their first column (Study 1c's store by model): the parts side by side
        parts = [[cells(l) for l in [b[1][0]] + b[1][2:]] for b in blocks]
        keys = [[r[0] for r in p] for p in parts]
        if any(k != keys[0] for k in keys):
            raise ValueError(f"{len(headers)} different headers in one table's text, and different first columns")
        return [parts[0][i] + [c for p in parts[1:] for c in p[i][1:]] for i in range(len(keys[0]))]
    header = cells(blocks[0][1][0])
    if len(blocks) == 1:
        return [header] + [cells(l) for l in blocks[0][1][2:]]
    captions = [c for c, _ in blocks]
    shared = len(captions[0])
    for c in captions[1:]:   # the words that every caption begins with ("Scores of the Products in ") are left out
        shared = next((k for k in range(min(shared, len(c)) + 1)
                       if k == min(shared, len(c)) or c[k] != captions[0][k]), shared)
    shared = captions[0][:shared].rfind(" ") + 1
    return [["Table"] + header] + [[caption[shared:]] + cells(l) for caption, b in blocks for l in b[2:]]


def make_tables(exhibits):
    import subprocess
    failed = []
    # the two settings tables, which fig_settings.py writes into results/figures/ and two tables read
    r = subprocess.run([sys.executable, str(CODE / "fig_settings.py"), "--table-only"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode:
        failed.append(("fig_settings.py --table-only", r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "failed"))
    import tables
    TABLES_OUT.mkdir(parents=True, exist_ok=True)
    for e in exhibits["tables"]:
        try:
            text = tables.TABLES[e["name"]]()
        except Exception as err:  # noqa: BLE001
            failed.append((e["name"], f"{type(err).__name__}: {err}"))
            continue
        (TABLES_OUT / f"{e['name']}.md").write_text(text + "\n", encoding="utf-8", newline="\n")
        if e["name"] in FULL_TABLES:
            # a table that the Web Appendix prints in part has its whole form in the table code (FULL_MARKDOWN)
            full = getattr(tables, "FULL_MARKDOWN", {}).get(e["name"])
            try:
                rows = table_rows(full() if full else text)
            except ValueError as err:
                failed.append((e["name"], f"its full table: {err}"))
                continue
            want = FULL_ROWS.get(e["name"])
            if want is not None and len(rows) - 1 != want:
                failed.append((e["name"], f"its full table has {len(rows) - 1} rows, and full_tables.json gives {want}"))
                continue
            out = PKG / FULL_TABLES[e["name"]]
            out.parent.mkdir(parents=True, exist_ok=True)
            with open(out, "w", encoding="utf-8", newline="") as fh:
                csv.writer(fh, lineterminator="\n").writerows(rows)
    return failed


def make_figures(exhibits):
    import importlib
    failed = []
    for e in exhibits["figures"]:
        module, function = e["function"].rsplit(".", 1)
        try:
            getattr(importlib.import_module(module), function)(*e.get("args", []))
        except Exception as err:  # noqa: BLE001
            failed.append((e["file"], f"{type(err).__name__}: {err}"))
            traceback.print_exc(limit=2)
    return failed


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    exhibits = json.loads((CODE / "exhibits.json").read_text(encoding="utf-8"))
    failed = []
    if "--figures" not in sys.argv:
        failed += make_tables(exhibits)
    if "--tables" not in sys.argv:
        failed += make_figures(exhibits)
    for name, err in failed:
        print(f"not made: {name}: {err}")
    n = (0 if "--figures" in sys.argv else len(exhibits["tables"])) + (0 if "--tables" in sys.argv else len(exhibits["figures"]))
    print(f"made {n - len(failed)} of {n} tables and figures")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
