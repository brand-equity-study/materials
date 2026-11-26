# Machine-Based Brand Equity: Data and Code

Data, materials and code for the paper "Machine-Based Brand Equity" and its Web Appendix.

- Studies 1 to 3: 3,482,015 responses from 74 language models of 15 developers.
- Study 4 and Supplemental Studies S1 to S4: 4,346 participants.

## Repository structure

Each study has its own folder, and each study folder has the same four subfolders and a `README.md` that describes
the study and its files.

| Subfolder | Contents |
|---|---|
| `materials/` | what the models or the participants saw |
| `data/` | their responses |
| `code/` | the analysis |
| `results/` | the files that the code writes |

| Folder | Study |
|---|---|
| `study1a-tables-with-one-optimal-product/` | Study 1a: tables with one optimal product |
| `study1b-64-models-on-34-tables/` | Study 1b: 64 models on 34 tables, and requests that people typed |
| `study1c-product-feeds-and-a-store-search/` | Study 1c: product feeds and a store search |
| `study2a-experience-attributes-stated-for-every-product/` | Study 2a: experience attributes stated for every product |
| `study2b-how-much-a-familiar-brand-is-worth/` | Study 2b: how much a familiar brand is worth |
| `study3a-pages-about-new-brands/` | Study 3a: models trained on pages about fictitious brands |
| `study3b-brand-knowledge-and-training-text-in-released-models/` | Study 3b: brand knowledge and training text in released models |
| `study4-peoples-choices-after-a-recommendation/` | Study 4: people's choices after a recommendation |
| `s1-coffee-makers/`, `s2-earbuds/`, `s3-a-warning-and-a-comparison-table/` | Supplemental Studies S1 to S3 |
| `s4-people-and-language-models-as-advisors/` | Supplemental Study S4 |
| `how-the-models-differed/` | how much the models differed in each test |
| `web-appendix-analyses/` | further analyses reported in the Web Appendix |
| `web-appendix-full-text/` | Web Appendix sections given in full |
| `common/` | code that several studies use |
| `models/` | every model, how it was reached and its settings |
| `computing/` | every run on the university computing cluster |
| `exhibits/` | the code that makes every table and figure |
| `environment/` | the Python packages |

`DATA-DICTIONARY.md` describes every column of every data file. Each `data/` folder has a `FILES.csv` with the number of
rows and the SHA-256 of each file.

## Requirements

Python 3.13 and the packages in `environment/requirements.txt`. The code needs no network access, account or key.

## Reproducing the results

```bash
python -m venv brand-equity
source brand-equity/bin/activate        # on Windows: brand-equity\Scripts\activate
pip install -r environment/requirements.txt
python run_all.py
```

`run_all.py` checks the data files, runs each study's code, and compares every new result with the result file in the
package. If a value differs, it prints both values and ends with status 1. The full run takes about 6 hours on a desktop computer
with 8 cores, most of it for Study 2b. To run one group of studies, use `python run_all.py --study 3`.

To make the paper's tables and figures, run `python exhibits/code/make_exhibits.py` (see `exhibits/README.md`). The
figures also need the packages in `environment/requirements-figures.txt` and Google Chrome.

## Files written with a language model

Two files were written by a language model and not by code. In `study1b-64-models-on-34-tables/materials/attribute_rulings.csv`,
Claude Opus 5.5 decided which value of each attribute is better. In
`study1b-64-models-on-34-tables/materials/names_hidden_leaks.csv`, it listed the clues to a brand that remained in the
tables without brand names. A second, separate run of Claude Opus 5.5 checked each file, and the package contains each
file as it stood after that check.

## Not included

`WITHHELD.md` lists what is not in the package and why: the participants' own words, the trained models of Study 3a,
and conditions of the corpus that the paper does not use.

## Computing environment

We ran the code with Python 3.13.12 on Windows 11. Every random draw has a seed, so a run on the same system gives the
same values. On Linux, `run_all.py` reports small differences in the analysis of how the models differed, because the
linear algebra libraries differ; no number printed in the paper changes. The models with open weights were run on a
university computing cluster, and `computing/gpu_jobs.csv` lists every run.

## Review copy

This copy is anonymized for review. `REVIEW-COPY.md` lists each change, and each is restored in the public deposit
after acceptance. The 30-model corpus is cited here as "[public deposit, cited after review]".

## License

The code is released under the MIT license, and the data and materials under CC BY 4.0 (`LICENSE`). Brand and product
names belong to their owners. The base models of Study 3 have their own licenses.
