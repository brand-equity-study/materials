# Study 3b: Brand Knowledge and Training Text in Released Models

In Study 3b, we used released models and real brands. We asked whether what a model knows about a brand predicts the
brand's equity in that model, at which stage of training the effect of a fictitious name appears, and whether the
passages of OLMo 2's training text that name a brand predict the brand's equity in OLMo 2.

## Questions about each brand

With no products shown, each model answered questions about one brand at a time: which brands of a category it names,
whether it knows the brand, how typical, premium, innovative, safe and sustainable the brand is, and which brands it
recommends for requests that people wrote. The analysis plan is `materials/audit/analysis_plan.md`.

`code/audit/analyze_audit.py --panel all` scores every response, computes each brand's equity on Study 1a's original
tables and runs the tests of the analysis plan (`results/audit/numbers-all.json`; about 25 minutes). Kimi Linear 48B is
left out of the tests of equity, because we could identify its recommendation in fewer than 90 percent of its
responses.

## Training stages

We scored released checkpoints of OLMo 2 7B and 32B, Qwen 2.5 7B and Llama 3.1 8B, from points during pretraining to
the released Instruct models, on Study 1a's tables and on pages in which two options have identical records.

| Script | What it does | Writes (in `results/`) |
|---|---|---|
| `code/checkpoints.py` | the effect of a familiar name in each checkpoint | `checkpoints.json` |
| `code/training_stages.py` | the effect of a fictitious name at each stage, and its change from one stage to the next | `training-stages/numbers.json` |

## Passages of the training text

For each of Study 1b's 73 familiar brands, we drew 200 passages that name the brand from OLMo 2's training text. Three
language models (Qwen3 32B, Gemma 4 26B and OLMo 3.1 32B) coded each passage's tone toward the brand and whether it
recommends the brand. `code/training-text/analyze_b5.py` relates each brand's equity in OLMo 2 7B Instruct to the tone
of its passages, holding constant how often the brand is named (`results/training-text/numbers.json`; about 15
minutes). The analysis plan is `materials/training-text/analysis_plan.md`.

## Files

| Folder or file | Contents |
|---|---|
| `materials/audit/items.jsonl.gz` | the 20,934 questions |
| `materials/audit/reference.json` | each brand's countries and parent company, and real companies that share a fictitious name |
| `materials/audit/judge_prompt.txt` | the instruction to the coder of tone |
| `materials/audit/brand_frequencies.csv` | each brand's counts in four public training corpora |
| `data/audit/claude/<model>.jsonl.gz` | the four Claude models' 83,736 responses |
| `data/audit/codex/<model>-<item set>.jsonl.gz` | the two GPT Sol models' responses (part of the questions) |
| `data/audit/codex-original-tables/<model>.jsonl.gz` | the two GPT models' responses to Study 1a's original tables |
| `data/audit/open/` | the 31 open models' responses, with `MANIFEST.tsv` |
| `data/audit/tone/`, `data/audit/tone-coding/` | the tone codes and the coders' agreement |
| `data/checkpoints/` | the pages and each checkpoint's letter probabilities |
| `materials/training-stages/models.tsv` | the 22 checkpoints with their repositories and revisions |
| `data/training-stages/scores/<checkpoint>/`, `data/training-stages/versions/<checkpoint>.json` | each checkpoint's letter probabilities and run record |
| `materials/checkpoints/analysis_plan.md`, `materials/training-stages/analysis_plan.md`, `materials/training-text/analysis_plan.md` | the analysis plans |
| `data/training-text/coded-passages-first-10-brands.csv.gz`, `coded-passages-other-63-brands.csv.gz` | the 14,600 coded passages |
| `data/training-text/brand-measures.csv` | each brand's measures from the codes |
| `data/training-text/reference-reader-agreement.json` | the coders' agreement with a reference reader |
| `data/training-text/pretraining-brand-counts.csv` | each brand's counts in OLMo 2's training text |
| `data/training-text/weborganizer-formats-by-brand.csv`, `weborganizer-document-labels.jsonl.gz`, `promotional-documents.jsonl.gz` | the kind of each document that names a brand |
| `data/training-text/instruct-models-equity.json` | each brand's equity in OLMo 2 7B and 32B Instruct |

The open models' answers to the original tables are in
`study2a-experience-attributes-stated-for-every-product/data/open-panel/letters-12683.csv.gz`.
