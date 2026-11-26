# Open models on [a computing cluster's name removed for blind review]: what runs and how it is read ([project record removed for blind review])

Written on 20 November 2026 at about 7:10 PM Central, before any open model answered a Study 2 item, and committed
before the pilot job went in. The study's own analysis plan (study2a-experience-attributes-stated-for-every-product/materials/analysis_plan.md, committed at 6:35 PM)
fixes the primary contrast, its outcomes and the exclusion rules; this plan applies them to a second set of models and
changes nothing in them.

## The models

Ten open models from eight developers, each at the revision read from its model card on 20 November 2026
(models/open-models.tsv): Llama 3.1 8B Instruct
(Meta), Qwen 2.5 32B Instruct and Qwen3 30B A3B Instruct 2507 (Alibaba), Gemma 4 31B and Gemma 4 26B A4B (Google),
OLMo 3.1 32B Instruct (Allen AI), Ministral 3 14B Instruct (Mistral), Phi-4 (Microsoft), Granite 4.1 30B (IBM) and
Marin 8B Instruct (Marin). Each runs in bf16 on one H100 with vLLM 0.33.0 in the shared container
(sha256 [commit removed for blind review]), through its own chat template, with reasoning turned off where the template has a switch.

## The settings

Sampling uses each model's own generation defaults, as the Claude runs use the provider's defaults; each item gets a
seed taken from its id; new tokens are capped at 1,024. The items are Study 2's builds, unchanged: the original tables
(`full2`, 6,120 items a model, sha256 [commit removed for blind review]) and the strictly better sets once their final build is fixed. The
parser is Study 2's parse_answer.py. A reasoning block, if any appears, is kept in the raw answer and removed before
parsing.

## The order of the runs

1. Pilot: Llama 3.1 8B and Qwen 2.5 32B on two tables (sr_laptops_01 and sr_earbuds_03), every cell and trial, 360
   items a model. Read by hand: the parse rate, a sample of answers, and whether either model picks the best product
   at all when the names are hidden.
2. A model whose answers the parser reads in under 90 per cent of the pilot items, or that picks the best product in
   under 10 per cent of names-hidden items over the whole run, is reported apart as unable to do the task, and the
   reason is written here before its numbers are read for the contrast.
3. The full panel on `full2`, then on the strictly better sets.

## How the results are read

The same estimates, outcomes and exclusion rules as the Study 2 analysis plan, with the open models in place of the
Claude models: equal weight for every table within a model, then for every model; a two-way cluster bootstrap over
tables and models, 2,000 draws, seed 20261120. The open models are reported as their own panel and never pooled with
the Claude models or with the models run through Codex. Each model's result is also given alone, with its revision.
