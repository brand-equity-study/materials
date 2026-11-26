# Study 3a: Pages About New Brands

In Study 3a, we tested whether a model trained on web pages about a fictitious brand recommends that brand more often
than the same model trained without those pages.

## Training

**First design.** We trained Qwen2.5-7B, Mistral-7B-v0.3 and Qwen2.5-14B in three stages: continued training on ordinary
text with or without pages about fictitious brands, instruction tuning (Dolly) and preference tuning (UltraFeedback),
each with LoRA weights and seed 20261001. The brands were an eye hospital, a heart hospital, a charity, an investment
fund and a laptop maker. The sets of pages are `promo` (promotional), `neutral` (a first neutral version), `neutralclean`
(neutral, with every ranking and favorable word removed), `negative` (critical) and `none` (no pages).

**Replication.** We repeated the first design on Qwen 2.5 7B, OLMo 2 7B and Llama 3.1 8B, with five training seeds.

**Second design.** We trained OLMo 2 7B, Qwen 2.5 7B and Llama 3.1 8B (35 versions each) and OLMo 2 32B (14 versions) on
pages about 14 fictitious product brands. The pages were of six kinds, and Gemma 4 26B A4B wrote them.

## Measures

After instruction tuning (`sft`) and after preference tuning (`dpo`), each model answered decision tables, with and
without brand names, and open questions in which it could name a brand unaided.

## Analysis

| Script | What it does |
|---|---|
| `code/planted_text.py` | the first design: unaided naming and the brand's equity (run Study 3b's `code/checkpoints.py` first) |
| `code/first-design-replication/analyze_replication.py` | the replication: the three primary contrasts, with Holm's correction |
| `code/training/analyze_q2.py` | the second design: each kind of page's effect on the brand's equity |
| `code/training/q2_across.py` | the second design compared across the three model families |
| `code/training/design_compare.py` | how the two designs differ |
| `code/training/combine.py` | all parts into `results/training/numbers.json` (run Study 3b's `code/training_stages.py` first) |

## Training the models again

We keep only the adapters of the first design's 13 versions (`WITHHELD.md`). This folder contains everything needed to
train every version again: the training text, the base models with their pinned revisions, and the scripts, settings
and seeds.

| | First design | Replication | Second design |
|---|---|---|---|
| Training text | `materials/training/`, `materials/decision-tables/` | the first design's | `materials/training-q2/` |
| Base models and revisions | `materials/training/base_models.csv` | `materials/training/replication_runs.tsv` | each run file's `model` and `commit` |
| Scripts | `code/train-first-design/<model>/` | `code/train-first-design-replication/oct_job.py` | `code/train-second-design/` |
| Settings and seeds | in each script, and `data/planted-text/<model>/<pages>/training/` | `replication_runs.tsv` | `materials/training-q2/runs/<run>.json` |

First design:

```bash
python code/train-first-design/lay_out_first_design.py <model> <folder>
cd <folder>
POD_W=<folder> python pod_job.py <pages>
```

For the replication, use `replication` in place of `<model>`, then run `POD_W=<folder> OCT_BASE=<repository>
OCT_REVISION=<revision> OCT_SEED=<seed> python oct_job.py <pages>` with the values of its row of
`replication_runs.tsv`.

Second design:

```bash
python code/train-second-design/lay_out_second_design.py <data folder>
python code/train-second-design/train.py --run materials/training-q2/runs/<run>.json --data <data folder> --out <output folder>
```

We trained the first design with torch 2.4.1, transformers 4.56.2, peft 0.17.1, accelerate 1.10.1 and trl 0.23.0 on an
NVIDIA A40 GPU (an A100 with 80 GB for Qwen2.5-14B), and the second design with torch 2.14.0 and transformers 5.20.2
(two H100 GPUs for OLMo 2 32B).

## Files

| Folder or file | Contents |
|---|---|
| `materials/training/` | the pages of every brand and set, the ordinary text, the instruction and preference data and the open questions, exactly as the models were trained on them |
| `materials/decision-tables/` | the decision tables as the trained models saw them |
| `materials/planted-text/analysis_plan.md` | the analysis plan |
| `data/planted-text/<model>/<pages>/answers/` | every response of each trained model |
| `data/planted-text/<model>/<pages>/training/<stage>/` | the settings and training log of each stage |
| `data/planted-text/<model>/<pages>/training_text_statistics.json` | the size of the training text and of each brand's pages |
| `materials/training-q2/pages.json.gz` | the 26,880 pages about the 14 product brands |
| `materials/training-q2/names.json` | the 14 fictitious names, none of which appears in OLMo 2's training text |
| `materials/training-q2/q2_items.jsonl`, `q2_components.jsonl` | the decision tables and the questions of the second design |
| `data/replication-runs/<family>/<run>/` | each replication run's responses |
| `data/training-runs/<family>/set-<k>/<run>/` | each second-design version's responses |
| `results/training/parts/` | each part of the results; `results/training/numbers.json` has them all |

## The long tables in full

The first rows of each of these tables are printed in the Web Appendix, where the name of each table's file in this folder is also given. Each file has every row, with the cells as they are printed in the table.

| File | Contents |
|---|---|
| `results/tables/product-brands-each-kind-of-page.csv` | Study 3a's results for the product brands under each kind of page |
| `results/tables/product-brands-80-and-320-pages.csv` | Study 3a's results for the product brands after 80 and 320 pages |
