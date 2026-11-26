# What the package does not hold

This file describes what the package does not hold, why we left it out, and where it is. We first list the data that
are withheld and available upon request, then the trained models, which are too large for the package, and last the
data that we do not use in the paper.

## Available upon request

To protect the participants' privacy, we do not include their own words in Study 4 and Supplemental Studies S1 to S4 in
this package, because participants typed what they wished and the text could identify a person. Instead, we provide
the coded measures that the analysis scripts use. None of the analysis scripts reads a withheld column, so every result
can be reproduced from this copy. The withheld columns of the chat study are the 20 messages that the participant wrote and the assistant's 20
replies (`msg_1` to `msg_20`, `response_1` to `response_20`), the reason for the choice (`dv_choice_reason`), the
feedback (`pilot_feedback`) and the answer to the closing question about what the study was about (`suspicion_probe`).
The withheld columns of S1 to S3 are the stated preference (`pref_text`), the reason for the choice (`choice_reason`)
and the closing answer (`suspicion`). The withheld columns of S4 are the reason for the choice (`why_free_text`), the
answer to the follow-up (`challenge_free_text`), the closing answer (`suspicion_open`) and the four responses about the
survey (`feedback_clarity`, `feedback_technical`, `feedback_realism`, `feedback_improve`). The withheld columns of the
two judge files of the chat study are the closing answer that the judges were shown (`suspicion_probe_text`) and the
judges' rationales (`j1_rationale`, `j4_rationale`), which quote the participants and the conversations. A list of the
columns that we removed from each file can be found in that file's codebook.

The retailers' web pages from which we took the prices of Study 2b are not included in this package because they are
copyrighted. We provide the prices that we used in the study. The file
`study2b-how-much-a-familiar-brand-is-worth/materials/measure/price-bands/products.csv` includes each product's price
with its address and the date and time at which it was captured. The file `excluded.csv` in the same folder includes
the listings that were left out, each with its reason. The file `materials/measure/PRICE-BANDS.csv` in the study's
folder includes each category's range of prices and each brand's band of prices. None of the analysis scripts reads the
pages themselves. The pages, 1,686 files saved on 21 and 22 November 2026, are kept by the authors in one archive,
`retailer-pages-2026-11-22.tar.gz`. The archive is 72,333,497 bytes, and its SHA-256 is
`e433d7b676c0cdcd96c0ca3333b15525e8aaf61ffaf466b0546d4fdca43ceeff`.

## The trained models

Each version of a model that we trained in Study 3 consists of a base model with open weights and the low-rank adapters
that we added to it, one adapter for each stage of training. The adapters of the first design's 13 versions of three
models (Qwen 2.5 7B, Mistral 7B v0.3 and Qwen 2.5 14B; 39 files, 14 GB) are kept and will be deposited with the data at
acceptance. We do not keep the adapters of the other trained versions. The replication package contains the training
text, the base models with their pinned revisions, the scripts, settings and seeds with which these versions can be
trained again, and every evaluation output from which we computed the paper's numbers. These files can be found in
Study 3a's folder, whose README explains how to train each version again:

| What | Where |
|---|---|
| The training text of the first design and its replication (the pages, the ordinary C4 text, the instruction and preference data, the open questions) | `study3a-pages-about-new-brands/materials/training/`, with the decision tables in `study3a-pages-about-new-brands/materials/decision-tables/` |
| The training text of the second design (the planted pages, the brand names, the planted tables, the questions about each brand and the rest of its text) | `study3a-pages-about-new-brands/materials/training-q2/`, with four files of `study3a-pages-about-new-brands/materials/training/` |
| The base models and their pinned revisions | `study3a-pages-about-new-brands/materials/training/base_models.csv` (the first design), `study3a-pages-about-new-brands/materials/training/replication_runs.tsv` (its replication) and each run file in `study3a-pages-about-new-brands/materials/training-q2/runs/` (the second design) |
| The training scripts | `study3a-pages-about-new-brands/code/train-first-design/`, `study3a-pages-about-new-brands/code/train-first-design-replication/` and `study3a-pages-about-new-brands/code/train-second-design/` |
| The settings and seeds | the scripts, `replication_runs.tsv` and the files in `study3a-pages-about-new-brands/materials/training-q2/runs/`, with each stage's settings and log of the first design in `study3a-pages-about-new-brands/data/planted-text/` |
| The evaluation outputs | `study3a-pages-about-new-brands/data/planted-text/` (the first design), `study3a-pages-about-new-brands/data/replication-runs/` (its replication) and `study3a-pages-about-new-brands/data/training-runs/` (the second design) |

## Not used by the paper

The corpus of Study 1b contains 31 further prompt conditions that we do not use in the paper. They can be found in the
public deposit of the corpus, [public deposit, cited after review].
