# Stated priorities on the open panel: analysis plan (items/s1prio1)

Written by [a team's name removed for blind review] on 21 November 2026, after the items were built ([commit removed for blind review]) and before any answer came back. JMR
[project record removed for blind review], condition 1: Study 1's "how far it holds".

## The question

Does the brand gap of the open models hold when the shopper states priorities, and how does it change along the
corpus's specification ladder (preference_vague, preference_weighted, preference_explicit, utility_explicit)?

## The measures

- Each answer's letter is read with final_answer before pick ([repository path removed for blind review]). An answer with no
  letter is counted as unreadable, reported by model and condition, and left out of the rates.
- For each condition, the brand gap is the share of answers away from the best product with names shown, minus the
  same share with names hidden. The same gap with the cleaned names-hidden arm (hidden_clean) is reported beside it.
- Each gap is given by model and pooled over the models, with a 95 per cent interval and a two-sided P from the
  two-way cluster bootstrap over models and tables (corpus_common.twoway_bootstrap, 10,000 draws, seed 20261120),
  as in study1_rerun_gap.py.
- The ladder: the pooled gap in each condition beside the open panel's gap without stated priorities (the Study 1
  rerun, s1rerun1), and the change from each condition to the next with its interval.
- The corpus ran these four conditions with names shown only. The open panel's names-shown share away from the best
  product is reported beside the corpus's 30 models in the same condition, as a description.

## Robustness rows (fixed before any answer)

1. Every preference_explicit estimate is also reported without the tables sr_cameras_01, sr_headphones_01 and
   sr_smartphones_03. In these three tables only, the names-hidden prompts of preference_explicit had the shopper's
   clause that names brands replaced by one that names none (GATE.json, hidden_brand_clauses_replaced; [a team of the project, name removed for blind review] agreed at
   12:10 PM Central on 21 November 2026). The row shows whether the replacement moves the estimate.
2. Every gap is also reported with hidden_clean in place of hidden.
3. Every pooled gap is also reported without any model that picked the product shown first in more than half of its
   names-hidden answers, a sign that the model does not read the tables (Llama 3.1 8B picked the first product in 70
   per cent of its answers in the measure's first job, [a job number removed for blind review]). The main estimates keep every model.

## Amendment 1 (22 November 2026, about 12:06 AM Central, before any answer to these items has been read)

[a person's name removed for blind review]'s rule that every prompt-level test runs on all models adds the Claude models (Haiku 5.5, Sonnet 5.5 and Opus
5.5 through the Batch API with adaptive thinking and each model's default effort; Fable 5.1 later) and any GPT model
that [a team's name removed for blind review] runs on these items through Codex. Each route is reported apart: the open panel through run_items.py on
[a computing cluster's name removed for blind review] (the 32 models of open-models.tsv), the Claude models through the API, the GPT models through Codex. The
pooled estimates of the plan are computed within each route, and no estimate pools routes. The tests, units,
bootstrap and robustness rows are otherwise unchanged.

## Amendment 2 (22 November 2026, about 12:42 AM Central, after the gaps over all 32 models had been read)

The paper now uses one exclusion rule in every study, Study 2's open-models rule ([repository path removed for blind review];
dated in [repository path removed for blind review] at 12:03 AM, [commit removed for blind review]; the coordinator's request of 12:14 AM). A model
whose answers the parser reads in under 90 per cent of a build's items is reported apart as unable to do the task and is
left out of every pooled estimate. In s1prio1, Kimi Linear 48B gives a letter in 6,598 of its 8,160 answers (80.9 per
cent) and is left out; every other model gives a letter in at least 97.3 per cent (Marin 8B). In the Study 1 rerun
(s1rerun1), the baseline of the ladder, every model gives a letter in at least 97.5 per cent, so no model is left out
there. The gaps in RESULTS.md at [commit removed for blind review] pooled Kimi Linear 48B's readable answers with the 31 other models; this
amendment was written after those gaps had been read, and RESULTS.md now gives the gaps over the 31 models and says
how far they moved from the gaps over 32. analyze_priorities.py applies the rule
(below_read_rule, with tests in test_analyze_priorities.py) and records the left-out models with their counts in
numbers.json (left_out).

## Amendment 3 (22 November 2026, about 2:40 AM Central, after the open models' results had been read and before the Claude models' answers to these items had been read)

Amendment 1 said that no estimate pools routes. The coordinator's request at 2:36 AM Central, under [a person's name removed for blind review]'s ruling of
about 6:50 PM on 21 November that each study reports its results over all its models first (recorded in
[repository path removed for blind review], 12:12 AM on 22 November), replaces that sentence: the first estimate of every
quantity of this plan is pooled over every model that answered all 8,160 items, whatever its route (the open models
through [a computing cluster's name removed for blind review], Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5 through the Batch API, and the GPT models through Codex
when [a team's name removed for blind review]'s runs end), with the same estimator, bootstrap (models and tables resampled) and robustness rows. Each
route's estimate is reported beside it, as Amendment 1 says. Claude Fable 5.1 does not answer these items (its cost
would pass [an account of the project removed for blind review]'s stop). The exclusion rule of Amendment 2 applies to every model. A model whose answers are
not yet complete is left out until they are, and numbers.json names it (folder_models_not_yet_complete). The ladder's
baseline for the Claude and GPT models is their Study 1 rerun (answers/s1rerun1, read by study1_rerun_gap.load), with
an answer that has no letter left out as for the open models.
