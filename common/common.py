"""Shared helpers for the Study 1 analyses: reading the answers, the bootstrap, and writing results/numbers.json.

The answers are the rows of the 30-model corpus with names shown (condition "baseline") and names hidden (condition
"baseline_brand_blind"), in study1b-64-models-on-34-tables/data/corpus/<model>/names_shown.jsonl.gz and names_hidden.jsonl.gz. Each row holds
every column of the corpus as recorded, with three differences: corpus_row, the row's position in the full corpus file;
trial, the trial number; and trial_id, a neutral identifier built from corpus_row. load_rows() checks every file
against data/corpus/FILES.csv before it returns the rows, in the order of the full corpus file.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import pathlib
import re

import numpy as np
import pandas as pd

SHOWN = "baseline"
HIDDEN = "baseline_brand_blind"
ROWS = 40813

STUDY = pathlib.Path(__file__).resolve().parents[1] / "study1b-64-models-on-34-tables"   # the corpus, its hand-coded lists, its results
DATA = STUDY / "data" / "corpus"
MATERIALS = STUDY / "materials"
RESULTS = STUDY / "results"
NUMBERS = RESULTS / "numbers.json"

DRAWS = 10000
SEED = 20261120


def read_jsonl_gz(path: pathlib.Path, expected_sha256: str | None = None) -> pd.DataFrame:
    """Rows of one data file; stops if the uncompressed text differs from its SHA-256 in FILES.csv."""
    raw = gzip.decompress(path.read_bytes())
    if expected_sha256 is not None and hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise SystemExit(f"{path} differs from its SHA-256 in FILES.csv; stopping")
    return pd.read_json(io.BytesIO(raw), lines=True, dtype=False, convert_dates=False)


def load_rows(columns: list[str] | None = None) -> tuple[pd.DataFrame, dict]:
    """The 40,813 names-shown and names-hidden answers, in the order of the full corpus file."""
    listed = list(csv.DictReader(open(DATA / "FILES.csv", encoding="utf-8")))
    frames = []
    for row in listed:
        d = read_jsonl_gz(DATA / row["file"], row["sha256_uncompressed"])
        if len(d) != int(row["rows"]):
            raise SystemExit(f"{row['file']} holds {len(d)} rows, not {row['rows']}; stopping")
        frames.append(d)
    df = pd.concat(frames, ignore_index=True).sort_values("corpus_row", kind="stable").reset_index(drop=True)
    if len(df) != ROWS:
        raise SystemExit(f"{len(df)} rows, not {ROWS}; stopping")
    if columns is not None:
        df = df[sorted(set(columns) | {"condition"})]
    info = {"files": len(listed), "rows_used": int(len(df))}
    return df, info


def cell_arrays(df: pd.DataFrame, value: str, models: list[str] | None = None, tables: list[str] | None = None):
    """Sum and count of `value` in each model-by-table cell, for SHOWN and HIDDEN, as 2-D arrays."""
    models = models or sorted(df["model_key"].unique())
    tables = tables or sorted(df["assortment_id"].unique())
    out = {}
    for cond in (SHOWN, HIDDEN):
        sub = df[df["condition"] == cond]
        g = sub.groupby(["model_key", "assortment_id"])[value].agg(["sum", "count"])
        s = g["sum"].unstack().reindex(index=models, columns=tables).fillna(0).to_numpy(float)
        n = g["count"].unstack().reindex(index=models, columns=tables).fillna(0).to_numpy(float)
        out[cond] = (s, n)
    return models, tables, out


def pooled_gap(arr, mi=None, ai=None) -> float:
    """Pooled SHOWN mean minus pooled HIDDEN mean over the chosen cells (all cells when mi and ai are None)."""
    vals = []
    for cond in (SHOWN, HIDDEN):
        s, n = arr[cond]
        if mi is not None:
            s, n = s[np.ix_(mi, ai)], n[np.ix_(mi, ai)]
        vals.append(s.sum() / n.sum())
    return vals[0] - vals[1]


def twoway_bootstrap(arr, n_models: int, n_tables: int, draws: int = DRAWS, seed: int = SEED) -> np.ndarray:
    """Two-way cluster (pigeonhole) bootstrap: each draw resamples models and tables with replacement and crosses them."""
    rng = np.random.default_rng(seed)
    out = np.empty(draws)
    for d in range(draws):
        mi = rng.integers(0, n_models, n_models)
        ai = rng.integers(0, n_tables, n_tables)
        out[d] = pooled_gap(arr, mi, ai)
    return out


def one_way_bootstrap(arr, fixed_axis: int, index: int, draws: int = DRAWS, seed: int = SEED) -> np.ndarray:
    """Gap for one model (fixed_axis=0) or one table (fixed_axis=1), resampling the other axis with replacement."""
    rng = np.random.default_rng(seed)
    vals = []
    for cond in (SHOWN, HIDDEN):
        s, n = arr[cond]
        s_line = s[index, :] if fixed_axis == 0 else s[:, index]
        n_line = n[index, :] if fixed_axis == 0 else n[:, index]
        vals.append((s_line, n_line))
    k = len(vals[0][0])
    idx = rng.integers(0, k, (draws, k))
    (s1, n1), (s0, n0) = vals
    return s1[idx].sum(1) / n1[idx].sum(1) - s0[idx].sum(1) / n0[idx].sum(1)


def ci(draws: np.ndarray, scale: float = 1.0, nd: int = 2) -> list[float]:
    return [round(float(np.percentile(draws, 2.5)) * scale, nd), round(float(np.percentile(draws, 97.5)) * scale, nd)]


def p_two_sided(draws) -> float | None:
    """The bootstrap p-value of the paper's convention (as in common/analyze.py, summary): twice the smaller of the
    shares of draws at or below zero and at or above zero, capped at 1. For a difference, pass the difference's own
    draws."""
    d = np.asarray(draws, float)
    d = d[np.isfinite(d)]
    if not len(d):
        return None
    return round(min(1.0, 2 * min(float((d <= 0).mean()), float((d >= 0).mean()))), 4)


def parse_price(x) -> float:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return float("nan")
    s = str(x).replace("$", "").replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return float("nan")


BLOCK = re.compile(r"--- Product ([A-E]) ---\n(.*?)(?=\n--- Product |\n\nWhich product|\Z)", re.S)


def parse_products(user_message: str) -> dict[str, dict[str, str]]:
    """The product blocks of a rendered prompt: {letter: {field: text}} with fields Name, Brand, Price, Description,
    Specs, Reviews and Sustainability rating, exactly as the model saw them."""
    out = {}
    for letter, body in BLOCK.findall(user_message):
        d = {}
        for line in body.strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                d[k.strip()] = v.strip()
        out[letter] = d
    return out


def parse_specs(spec_line: str) -> dict[str, str]:
    """Split a Specs line ("capacity: 26L, material: 500D CORDURA, ...") into {key: value}. A comma inside a value
    (for example "IP65, 3m drop") stays with the value because only ", key:" starts a new pair."""
    parts = re.split(r",\s*(?=[A-Za-z_][A-Za-z_ ]*:)", spec_line)
    out = {}
    for part in parts:
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def write_result(key: str, payload: dict, script: str, inputs: dict) -> None:
    """Write `payload` under `key` in results/numbers.json, with the script and the input that produced it."""
    RESULTS.mkdir(parents=True, exist_ok=True)
    data = json.loads(NUMBERS.read_text(encoding="utf-8")) if NUMBERS.exists() else {
        "about": "The numbers of Study 1. Each key names the script in common/ that wrote it and the data it read."}
    payload = dict(payload)
    payload["script"] = script
    payload["input"] = inputs
    data[key] = payload
    NUMBERS.write_text(json.dumps(data, indent=1, ensure_ascii=False, default=_plain) + "\n", encoding="utf-8")


def _plain(o):
    """numpy scalars and arrays as plain JSON values."""
    if isinstance(o, np.generic):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"not JSON serializable: {type(o).__name__}")
