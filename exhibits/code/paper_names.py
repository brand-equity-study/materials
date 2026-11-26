"""Two helpers of the figure and table code: a results file read when the code first uses it, and the names that
the code gives the keys of the results files whose keys this package names in plain words.

The code reads, for example, the key "item2_brand_gap_by_model" of Study 1b's results file; the package's file names
the same entry "names_gap_by_model". KEYS lists, for each such file, the code's name of each key and the file's; view()
gives a loaded file the code's names, beside its own, so that the code runs as it was written. A key of KEYS that holds
"/" names the place in the code's view where the whole file sits.
"""
import gzip
import json
from pathlib import Path

PKG = Path(__file__).resolve().parents[2]   # the package
KEYS = {
    "study4-peoples-choices-after-a-recommendation/results/numbers.json": {"study_3": "chat_experiment", "study_1a": "S1_coffee_makers", "study_1b": "S2_earbuds", "study_2": "S3_warning"},
    "study1a-tables-with-one-optimal-product/results/open_models.json": {"study2": "tables_of_study1", "study1_rerun": "rerun", "draws": "draws", "seed": "seed"},
    "how-the-models-differed/results/predictors/numbers.json": {"model level, brand equity E (B21)": "model level, brand equity E (the measure)", "model level": "model level", "brand level": "brand level"},
    "study1b-64-models-on-34-tables/results/requests/all-models/left_out.json": {"open_models": "open_models"},
    "study1b-64-models-on-34-tables/results/numbers.json": {"item1_reproduce_brand_gap": "names_gap", "item2_brand_gap_by_model": "names_gap_by_model", "item3_strict_dominance": "strict_dominance", "item4_names_hidden_leak": "names_hidden_leaks", "item5_recommended_price": "recommended_price", "gemini_2_5_pro_cap": "long_answers_gemini_2_5_pro", "run_settings": "model_settings", "thinking_pairs": "thinking_pairs"},
    "study3a-pages-about-new-brands/results/numbers.json": {"f6": "promotional_vs_no_pages_qwen7b", "f12": "kinds_of_pages_qwen7b", "f16": "mistral7b", "f17": "qwen14b_vs_qwen7b", "laptop": "laptop_tables", "sensitivity_article_guard": "sensitivity_article_guard", "training": "training", "reading_checks": "reading_checks", "f23": "olmo2_checkpoints", "study3a": "study3a", "university": "university"},
}
# keys inside a file that the package also names differently: the code's path of keys and the file's
INNER = {
    "study1a-tables-with-one-optimal-product/results/open_models.json": [[["study2", "b2/dom2"], ["tables_of_study1", "strictly-better-tables"]], [["study2", "b2/full2"], ["tables_of_study1", "original-tables"]]],
}
# records whose fields the package names differently: the code's path to the records, {the file's field: the code's}
RECORD_FIELDS = {
    "study1b-64-models-on-34-tables/results/numbers.json": [[["run_settings", "models"], {"temperature": "temperature_all_conditions", "thinking_flag": "thinking_flag_all_conditions", "answers": "answers_in_corpus"}]],
}
# records whose identifying field holds another value in the package: the code's path to the list, the field,
# {the file's value: the code's}
RECORD_VALUES = {
    "study3a-pages-about-new-brands/results/numbers.json": [[["f23", "values"], "key", {"olmo2_base": "H1", "olmo2_instruct_chat": "H2", "olmo2_instruct_plain": "H2_plain", "olmo2_end_of_stage_1": "H1_S1", "products_only_olmo2_base": "B1_base", "products_only_olmo2_instruct": "B1_instruct", "qwen2.5_7b_base": "S3_qwen_base", "qwen2.5_7b_instruct": "S3_qwen_instruct", "llama3.1_8b_base": "S3_llama_base", "llama3.1_8b_instruct": "S3_llama_instruct", "olmo2_step_base_to_sft": "S1_pretrained_to_sft", "olmo2_step_sft_to_dpo": "S1_sft_to_dpo", "olmo2_step_dpo_to_instruct": "S1_dpo_to_instruct", "olmo2_step_base_to_instruct": "S1_pretrained_to_instruct"}]],
}


def view(path, data):
    """The results file at path, loaded as data, with the code's names of its keys added."""
    rel = Path(path).resolve().relative_to(PKG).as_posix()
    keys = KEYS.get(rel)
    if not keys:
        return data
    out = dict(data)
    for code_key, file_key in keys.items():
        if "/" in code_key:
            node = out
            parts = code_key.split("/")
            for p in parts[:-1]:
                node = node.setdefault(p, {})
            node[parts[-1]] = data if file_key == "" else data[file_key]
        else:
            out[code_key] = data[file_key]
    for code_path, file_path in INNER.get(rel, []):
        node = data
        for k in file_path:
            node = node[k]
        target = out
        for k in code_path[:-1]:
            target[k] = dict(target[k])   # a copy, so that the file's own entry keeps its keys
            target = target[k]
        target[code_path[-1]] = node

    def holder(code_path):
        """The dict that holds the last key of code_path in out, each dict on the way copied."""
        target = out
        for k in code_path[:-1]:
            target[k] = dict(target[k])
            target = target[k]
        return target
    for code_path, fields in RECORD_FIELDS.get(rel, []):
        h = holder(code_path)
        recs = h[code_path[-1]]
        renamed = lambda r: {**r, **{c: r[f] for f, c in fields.items() if f in r}}   # noqa: E731
        h[code_path[-1]] = ({k: renamed(r) for k, r in recs.items()} if isinstance(recs, dict)
                            else [renamed(r) for r in recs])
    for code_path, field, values in RECORD_VALUES.get(rel, []):
        h = holder(code_path)
        h[code_path[-1]] = [{**r, field: values.get(r[field], r[field])} for r in h[code_path[-1]]]
    return out


class Later(dict):
    """A results file that is read the first time the code uses it, so that a module can name its files when it is
    imported and an exhibit needs only the files that it reads."""

    def __init__(self, path):
        super().__init__()
        self._path, self._read = Path(path), False

    def _load(self):
        if not self._read:
            self.update(view(self._path, json.loads(self._path.read_text(encoding="utf-8"))))
            self._read = True

    def __getitem__(self, k):
        self._load()
        return super().__getitem__(k)

    def __contains__(self, k):
        self._load()
        return super().__contains__(k)

    def __iter__(self):
        self._load()
        return super().__iter__()

    def __len__(self):
        self._load()
        return super().__len__()

    def get(self, k, default=None):
        self._load()
        return super().get(k, default)

    def keys(self):
        self._load()
        return super().keys()

    def items(self):
        self._load()
        return super().items()

    def values(self):
        self._load()
        return super().values()


def later(path):
    return Later(path)


def read(path):
    """A results file, loaded, with the code's names of its keys added (view)."""
    return view(path, json.loads(Path(path).read_text(encoding="utf-8")))


def text_of(path):
    """A text file's content; a .gz file is read uncompressed (the package keeps its larger files gzipped)."""
    p = Path(path)
    return gzip.decompress(p.read_bytes()).decode("utf-8") if p.suffix == ".gz" else p.read_text(encoding="utf-8")


def open_text(path):
    """A text file opened for reading; a .gz file is read uncompressed."""
    return gzip.open(path, "rt", encoding="utf-8") if str(path).endswith(".gz") else open(path, encoding="utf-8")
