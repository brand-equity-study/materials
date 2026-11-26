# Analysis plan for the retrieval study ([project record removed for blind review], [issue number removed for blind review])

Written by [a team's name removed for blind review] on 21 November 2026 and committed at 11:38 AM Central ([commit removed for blind review]), before any item of this study was
built or answered.
[A team of the project, name removed for blind review] gave the step to [a team's name removed for blind review] at 11:33 AM ([a project document's name removed for blind review] had named [a team's name removed for blind review]). Times are US Central.

## The question

[project record removed for blind review] asks whether evidence that a model reads at answer time overrides the brand name it learned in
training, and whether familiar names gain more from the same evidence. An assistant that answers a shopping request
often retrieves reviews and review-site ratings before it recommends. In this study every product of an item receives
retrieved evidence of the same tone (positive, mixed or negative), so the evidence favors no product, and only the
names differ between the versions of an item. The prompts are plain, with no live search and no tools.

## The products

[a team's name removed for blind review]'s 30 strictly dominant tables ([repository path removed for blind review], the tables of the build `dom2`, the same 30
as [project record removed for blind review]). In each table the designated best product is better than or equal to every other product on every displayed
attribute and costs no more. Every item starts from [a team's name removed for blind review]'s plain render (`study2_tables.render`) at one of [a team's name removed for blind review]'s
two price rungs (the best product priced equal to the cheapest other product, or 30 per cent below it), with no
information supplied, and [a team's name removed for blind review]'s gates check that render before anything is added to it.

## The arms

The names are [a team's name removed for blind review]'s three versions: hidden ("Product A" of "Brand A"), original (the invented name on the best
product and familiar names on the other four) and crossed (the best product's name swapped with one familiar
product's name, [a team's name removed for blind review]'s swap partner for that trial).

The evidence has four levels. The reference is [a team's name removed for blind review]'s plain table with no added evidence. In the other three, every
product's block gets, after its review line, this block of one tone:

```
Retrieved from review sites:
  Review site rating: 9 out of 10, listed among its recommended picks
  Customer reviews: "<snippet>" "<snippet>" "<snippet>"
```

| Tone | Rating and verdict | Snippets |
|---|---|---|
| positive | 9 out of 10, listed among its recommended picks | three positive customer review snippets |
| mixed | 6 out of 10, listed as a reasonable option with trade-offs | three mixed snippets |
| negative | 3 out of 10, listed among the ones to avoid | three negative snippets |

Every product of an item gets the same rating and verdict. [A project document's name removed for blind review] asks for "rankings of equal tone"; a rank cannot
be equal for five products, so the ranking is the review site's verdict tier, the same for every product. The snippets
are 15 for each tone, written for this study in [repository path removed for blind review] before any answer. Each is about the
product in general and has no name, brand, specification, price or comparison with another product. Each product of an
item gets three different snippets of the item's tone, and no snippet appears twice in an item: the 15 snippets form five
fixed triples, and the product at display position j gets triple (j + trial) mod 5, the same in all three name versions
of the item. The plain review line ("Reviews: 500 reviews, 4.3 stars") stays in every arm, so the arms differ only in
the added block.

## Items

For each table, trial, price rung, evidence level and name version, one item: 30 tables, 4 evidence levels, 3 name
versions and 2 rungs make 720 items for each trial. The Claude panel answers trials 0 and 1 (1,440 items a model) and
the open panel trials 0 to 3 (2,880). The builder ([repository path removed for blind review]) writes a build only when
these checks pass on every item: the hidden version shows no brand or product name of any table; no item prints a word
that defines or names the best product ([a team's name removed for blind review]'s forbidden list); every product's price and specification values are in
its own block; the three name versions of an item differ only in the product names and brands; in an evidence arm
every product has the block once, with the arm's rating and verdict and three snippets of the arm's tone, no snippet
twice in the item and no brand or product name in any block; no block outside the evidence arms; and [a team's name removed for blind review]'s gates
pass on the plain render each item starts from.

## Models

The Claude panel is Claude Haiku 5.5, Sonnet 5.5, Opus 5.5 and Fable 5.1, at most 800 output tokens. They run through
[an internal tool removed for blind review] on [an account of the project removed for blind review] first. If the API refuses [an account of the project removed for blind review], all four run through the Claude command line ([product name removed for blind review]) on the
subscription ([a team's name removed for blind review]'s [repository path removed for blind review], one `claude -p` for each prompt from an empty folder, no
tools); [an account of the project removed for blind review] is used last, under the 800-dollar cap that [a team of the project, name removed for blind review] shares among lanes. All
four models use one route, and the results name it. The open panel is the ten open models of [project record removed for blind review] on [a computing cluster's name removed for blind review], through
job files that [a team of the project, name removed for blind review] submits.

The pilot is the coffee makers 03 and smartphones 03 tables (the two with the largest name gap of Claude Haiku 5.5 and
Sonnet 5.5 in [a team's name removed for blind review]'s dom2 with no information: 45 and 40 points), Haiku and Sonnet, every arm and name version,
trials 0 and 1, both rungs: 96 items a model, read by hand before the full run.

## Reading an answer

[a team's name removed for blind review]'s `final_answer` removes reasoning that a model leaves in its output, and `pick` reads the letter
([repository path removed for blind review]). Answers without a letter are counted and reported; a table enters a contrast for a
model only if every share in the contrast has at least one parsed answer. If more than 5 per cent of a batch gives no
letter, the batch stops until the cause is found.

## Outcomes and statistics

For a model m, a table t, an evidence level e and a name version, s is the share of parsed answers that pick the best
product, over trials and rungs.

The first question, whether the evidence overrides the name: the name gap g(e) = s_hidden(e) - s_original(e), in
percentage points, and the change D(e) = g(e) - g(none) for e = positive, mixed and negative.

The second question, whether familiar names gain more from the same evidence: the gain that the evidence gives the best
product when it has a familiar name, minus the gain when it has the invented name,
I(e) = [s_crossed(e) - s_crossed(none)] - [s_original(e) - s_original(none)], for the same three tones.

Each quantity is computed for each model and table and then pooled, every table weighted equally within a model and
every model equally. Intervals come from the two-way cluster bootstrap of Study 2, which resamples tables and models
independently with replacement (10,000 draws, seed 20261120); the 95 per cent interval is the 2.5th to 97.5th
percentile, and the two-sided P value is twice the share of draws on the far side of zero, capped at 1.

The panels are analyzed apart. In each panel the primary contrasts are the six above (three D and three I),
Holm-corrected as one family. A tone is said to narrow the name gap when D(e) is below zero with a Holm P below 0.05,
to widen it when D(e) is above zero with a Holm P below 0.05, and to override the name only if it narrows the gap and
g(e) has a 90 per cent interval inside -2 to +2 points. Familiar names are said to gain more from a tone when I(e) is
above zero with a Holm P below 0.05, and less when it is below zero with a Holm P below 0.05. A finding is called
general when it holds in both panels, and is otherwise reported with the panel where it holds. A test that fails is
reported in the web appendix.

Secondary, without correction and labelled as such: g(e) and its interval at every level; the crossed boost
s_crossed(e) - s_hidden(e) at every level; the change with names hidden, s_hidden(e) - s_hidden(none), which shows what
the evidence does to the best product's share without any name; and the check that the reference level reproduces
[a team's name removed for blind review]'s dom2 gap for each model on the same tables and rungs.

## What we expect, before the run

In [a team's name removed for blind review]'s Study 2, supplying a warranty, a failure rate and time on the market for every product closed the gap
(12.3 points with none, 0.9 with it supplied), and in [project record removed for blind review] the same information lowered the Claude panel's gap by 11.0
points. We expect positive evidence to narrow the gap, because it gives the invented brand the assurance that its name
does not. We expect negative evidence to widen it, because when every product is said to be poor a model may fall back
on the name it knows. We expect familiar names to gain more from positive evidence than the invented name does. These
are expectations for the discussion, not tests beyond the family above.

## Spend

On the API, the pilot would cost about 1 dollar and the full Claude run about 30 dollars (the [project record removed for blind review] Claude panel cost
74.10 dollars for 15,360 answers; this study has 5,760 answers with longer prompts). On the subscription it costs no
dollars. Every amount is read from the runner's records and reported.

## Changes after the first version

Every change is dated here, with the reason and what it changes, before any answer that it affects.

- 21 November 2026, about 11:40 AM Central, before any item was built: one positive snippet changed from "My family
  uses it constantly, and it holds up." to "Everyone at home uses it constantly, and it holds up.", because the word
  "My" is a brand or product name of one of the corpus's tables ([a team's name removed for blind review]'s deny list), and the builder's check refused
  the snippet as naming a brand. Nothing else changes. (The first version of these two entries gave the times as about
  12:00 PM and 12:25 PM, written without reading the clock; the commits show 11:38 AM and 11:42 AM.)
- 21 November 2026, 11:45 AM Central, before any answer: the route. [an account of the project removed for blind review] refused the pilot's first job at about
  11:43 AM ([an internal tool removed for blind review]: "not ready: it is expired, switched off, or has no room below its stop for this run"), so, as
  the plan says, all four Claude models run through the Claude command line ([product name removed for blind review]) 2.1.330 on the subscription ([a team's name removed for blind review]'s
  run_claude_cli.py, from the items `items/r1/b10-pilot-cli/` and `items/r1/b10-claude-cli/`). On this route the study's
  system prompt is the system prompt, the CLI adds about 410 tokens of its own framing, and the output has no
  800-token cap. The results name the route. Nothing else changes.
- 21 November 2026, 12:26 PM Central, after the first answers (a record, not a change): the route's settings. Every
  call so far inherited from the [a team's name removed for blind review] chat that started it MAX_THINKING_TOKENS=128000, CLAUDE_EFFORT=xhigh and
  CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1, and many answers used thinking tokens; every answer of the Claude panel is
  made with these values and the Claude command line 2.1.330 ([product name removed for blind review]) on [a computer's name removed for blind review], which the later runs set on their command. The run log is
  `answers/r1/b10-claude-cli/RUN-LOG.md`. (Superseded by the next entry.)
- 21 November 2026, 12:42 PM Central, before any further answer, at [a team of the project, name removed for blind review]'s ruling of 12:41 PM: the
  Claude panel's main run changes route, so that its thinking matches every other Claude result of Study 2 (dom2, the
  split, eq1, the harness and the requests), which came through the API with adaptive thinking and no effort set, and
  so that this study's level with no evidence can be compared with dom2.
  - The main run: the Claude command line 2.1.330 ([product name removed for blind review]) on [a computer's name removed for blind review], one `claude -p` for each prompt as before, but with the calling chat's
    variables removed from the child exactly as [a team's name removed for blind review]'s [repository path removed for blind review] removes them (its `child_env`:
    every `CLAUDE_CODE_` variable, `CLAUDECODE`, `CLAUDE_PID`, `MAX_THINKING_TOKENS`, `CLAUDE_EFFORT`,
    `DISABLE_THINKING`, `CLAUDE_CODE_MAX_OUTPUT_TOKENS`, `ANTHROPIC_MODEL` and `ANTHROPIC_SMALL_FAST_MODEL`), and
    `CLAUDE_CONFIG_DIR` set to an empty folder of its own, so that the CLI's own defaults hold: adaptive thinking, no
    effort set. Each results line records the computer and the values the child had. One worker per model, when [a computer's name removed for blind review]'s
    load allows. All 1,440 items of each model are answered again (5,760 answers), into `answers/r1/b10-main-cli/`,
    by [repository path removed for blind review].
  - The check: after the first 20 answers of each model, the median of their output tokens (thinking included) must
    lie within the middle half of dom2's API answers for the same model (the 25th to 75th percentile of 3,600 answers
    each: Haiku 245 to 405, Sonnet 131 to 290, Opus 180 to 274, Fable 147 to 371). A model whose median falls outside
    stops, and [a team's name removed for blind review] asks the coordinator in [a team of the project, name removed for blind review] what to do.
  - The answers made with forced thinking (2,229 when the run was stopped at 12:41 PM: Haiku 718, Sonnet 873, Opus 543
    and Fable 95, in `answers/r1/b10-claude-cli/`, the pilot's 192 among them) are kept and labelled. They are analyzed
    as a secondary run, reported in the web appendix and never pooled with the main run. The pilot's reading of the
    items stands, because it concerned the items and not the thinking.
- 21 November 2026, 7:11 PM Central, written after the ten open models' results had been read: the open panel widens.
  Under [a person's name removed for blind review]'s ruling of about 6:50 PM (the paper's point is about machines in general, and model heterogeneity is
  part of it, so each study reports every model it can), the open panel becomes every open model of
  `models/open-models.tsv` that the study's items can be run on, not only the first ten. [a team's name removed for blind review] wrote the
  retrieval jobs for the 20 open models that lacked them, with Nemotron 3 Nano 30B and Qwen 3.5 122B to follow, on the
  current runner ([repository path removed for blind review], which resumes a stopped run and reads each answer with
  `final_answer`, removing the gpt-oss models' reasoning); the first ten used the copy inside the bundle
  `b10-bundle-1.tgz`, which also read each answer with `final_answer`. The items, evidence
  levels, outcomes and statistics do not change. The first ten open models' results stay as reported; the estimates over every model
  go through the common heterogeneity analysis ([repository path removed for blind review]), and because the panel was
  widened after the first ten open models' results were read, the wider panel is reported as a widening, not as a test written in
  advance. The runner, as [a team's name removed for blind review] gave it at 7:13 PM: the 22 later models answer the same items, into the first ten
  models' folders, with the current runner from [repository path removed for blind review] (SHA-256 06c0647a..., with the current
  parser and panel file), in [a team's name removed for blind review]'s jobs b10-06 and b10-07 ([commit removed for blind review], [commit removed for blind review]), not with the copy inside the
  bundle, which cannot resume a task stopped at its two-hour limit and whose panel file marks the Qwen 3.5, 3.6 and 3.8
  models as not text-only and the Qwen 27B models as fitting one H100. The current runner gives one-turn items the same
  vLLM settings and sampling, and the analyses read every answer again from the raw text with `final_answer`, so the
  letters do not depend on which runner wrote them.
- 21 November 2026, 9:30 PM Central, written after both panels' results had been read: the estimate over every model.
  At the coordinator's request of 9:23 PM, relaying [a team's name removed for blind review] (Study 2a reports each result over all its models first,
  under [a person's name removed for blind review]'s ruling of about 6:50 PM), the name gap at each level and the six contrasts are also estimated over
  every model that answered, pooled from the panels' cells (`analyze_retrieval.py --panel all`). The estimator is the
  same: every table weighted equally within a model and every model equally, the two-way bootstrap over tables and
  models (10,000 draws, seed 20261120), and Holm over the same six contrasts. The Claude panel enters with its main run
  only; the forced-thinking run stays secondary and is never pooled. A per-model file (`per_model.csv`: each model's
  g(e), D(e) and I(e), with an interval from resampling that model's tables) goes through the common heterogeneity
  analysis. The panels' own results stay as reported. The GPT models and the other open models enter when their
  answers come back, and the estimate is run again. Because the pooling was decided after the panels' results were
  read, the text reports it as a summary over models.
- 22 November 2026, 2:37 AM Central, after the export of every open model's answers ([a job number removed for blind review]) and [a team's name removed for blind review]'s letters
  check by arm ([repository path removed for blind review], [commit removed for blind review]), and before the analysis over every
  open model (b10-08). The paper applies Study 2's open-models rule in every study: a model whose answers the parser
  reads in under 90 per cent of a build's items is reported apart as unable to do the task. Four models fall under 90
  per cent here, for two different reasons. Kimi Linear 48B (70.5 per cent read) gives no letter in about 20 per cent of
  the answers at every evidence level, the same format failure as in the store and the search step, so it is unable to
  do the task and is left out, as in every other study. Qwen 3.5 27B (84.8), Qwen 3 32B (87.3) and Ministral 3 14B
  (87.5) give a letter in 96.7 per cent or more of the answers with no evidence, positive evidence and mixed evidence,
  and in 46 to 53 per cent with negative evidence, where every product has negative reviews and they decline to
  recommend any ("None of the provided products are recommended"). These refusals answer the manipulation; they are not
  a failure to do the task, and leaving the models out because of them would select on the response to the treatment.
  Decision: the rule is applied to the evidence levels other than the negative one, so Kimi Linear 48B is left out and
  the three models stay in. Ministral 3 14B was kept in the first ten open models' result for the same reason (its
  refusals at the negative tone were found and reported then). This plan already counts answers without a letter and
  computes every share over parsed answers. The share of answers that decline at each level is reported for every model
  as an outcome, and a check with all four models left out (the rule read literally) is reported in the web appendix.
- 22 November 2026, 2:40 AM Central, the coordinator's reading of 2:37 AM, written into the rule: a decline is a
  readable answer that recommends none of the products because of the products ("None of the provided products are
  recommended", "I cannot recommend any of these products", "No product meets your budget requirements", or the word
  "None" where the letter should be). It is an outcome, counted and reported by level, name version and model, and it
  does not count against the 90 per cent. The 90 per cent is the share of the answers that are not declines from which
  the parser reads a letter. An answer without a letter is told apart by [repository path removed for blind review]: a decline
  statement must open the answer (its first 200 characters), and no pick by name may follow ("if I must choose ... it
  would be Product A"); everything else without a letter is unread (reasoning written as text, a request for more
  information, a refusal of the role). Its test, [repository path removed for blind review], holds the answers without a letter
  from the samples of exports [a job number removed for blind review] and [a job number removed for blind review] verbatim, each labelled by reading it. The rule was first written from
  [a job number removed for blind review]'s sample; on [a job number removed for blind review]'s sample, read afterwards, it called eight answers declines, all eight correctly, and one
  answer of reasoning a decline, which the rule now excludes (that answer is in the test). On [a job number removed for blind review]'s sample, 17 of the
  18 answers without a letter from Qwen 3.5 27B, Qwen 3 32B and Ministral 3 14B are declines, all at the negative
  level, and 13 of Kimi Linear 48B's 17 are unread. The same definition applies in the store and the search step
  ([repository path removed for blind review]). The exports bring back letters, not text, so the counts by model and level come
  from a column that [a team's name removed for blind review]'s export jobs add by running decline.py on each raw answer on [a computing cluster's name removed for blind review].
