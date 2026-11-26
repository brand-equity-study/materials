# What the explanations say: the open-weight judges ([project record removed for blind review], condition 2, [issue number removed for blind review])

Written by [a team's name removed for blind review] on 21 November 2026 at about 11:40 AM Central on [a computer's name removed for blind review], at [a team of the project, name removed for blind review]'s request of
11:33 AM, and committed before any judge has coded any explanation and before any job is submitted. The step's
conditions are in [repository path removed for blind review] ([project record removed for blind review]) and its criticism is [an item of a project document removed for blind review]: "The classifier of
explanations is load-bearing ...; report human agreement on a stated sample, error rates by condition, blinding to
condition and model, and sensitivity to the judge." A change after any code is read is written below as a dated
amendment, and the original text stays.

## The explanations

An explanation is the text of an answer that passes over the best product: the letter that Study 2's parser reads
from the answer's final text (`parse_answer.final_answer`, then `pick`) is a letter and is not the best product's.
Two sources, both on tables where the best product is at least as good as every other product on every listed
attribute and costs no more, so the reason for passing it over is not among the listed attributes:
- Study 2's strictly better tables (`dom2`), in the cells where the names are shown: the invented name on the best
  product (original) and the names crossed, with the information supplied or not, at both prices. Every model that
  answered `dom2`: Claude Haiku 5.5, Sonnet 5.5, Opus 5.5 and Fable 5.1 (API), Fable 5.2 (the CLI), GPT-6.2 Sol, GPT-6.2
  Astra, GPT-6.1 Sol and GPT-6 Astra (Codex; an answer that used a tool is left out, as in Study 2), and every open model
  whose `dom2` answers are on [a computing cluster's name removed for blind review] (`runs/b2/dom2/<model>/answers.jsonl`).
- [a team's name removed for blind review]'s real requests ([repository path removed for blind review], answered by the four Claude models through the API), in
  the items where the names are shown.
The cells with the names hidden are left out, because the judge's instruction describes products shown with brand
names.

## The judge's instruction and the codes

The instruction (`judge_prompt.txt`) is [a team's name removed for blind review]'s [repository path removed for blind review] with one field added. The judge
sees the request and the five products as the assistant saw them, the product it recommended, the listed alternative
(the best product) and the answer's final text. It never sees which model wrote the answer or which cell the prompt
came from. Two codes:
- `reason`, [a team's name removed for blind review]'s field unchanged: the reason the answer leans on most, one of `brand_property`,
  `brand_reputation`, `listed` and `other`.
- `brand_any`, new: whether the answer gives the brand as a reason anywhere in it, yes or no (its reputation,
  familiarity, reliability, support or trust, a property that only that brand's products have, or the other
  product's brand as a risk). A brand name used only to identify a product is not a reason. This field measures what
  condition 3 reports, the share of explanations that name the brand, which `reason` undercounts when an answer gives
  the brand as a second reason.

The judge's reply is one JSON object, read after `final_answer` (a judge's reasoning is removed before the reply is
read). A reply with no readable object, or with a value outside the classes, is unread.

## The judges

Open-weight instruct models of the project's [a computing cluster's name removed for blind review] panel (`models/open-models.tsv`), the largest from
five developers: gpt-oss 120B (OpenAI), Qwen 3.5 122B A10B FP8 (Alibaba), Kimi Linear 48B A3B (Moonshot), Gemma 4 31B
(Google) and OLMo 3.1 32B (Allen AI). Each runs through the project's runner ([repository path removed for blind review]),
unchanged: the model's own chat template with the panel's switch, the model's own generation defaults (as every run
of the study), a seed from each item's id, at most 2,048 new tokens. The judge items are in Study 2's item format
(`id`, `system`, `user`, `cell`, `table`, `trial`, `names`, `info`, `rung`, `best`), with opaque ids.

Three of the judges also wrote explanations (gpt-oss 120B, Gemma 4 31B and OLMo 3.1 32B). Every share under a judge is
reported also with that judge's own explanations left out.

## The reference and the stated sample

- The sample: 200 explanations drawn with `random.Random(20261121)` by `build_explanations.py sample`: 160 from `dom2`
  (40 from each of the four cells of names and information, pooled over the prices; within each cell, 20 from the
  closed models and 20 from the open models) and 40 from the real requests. It is drawn on [a computing cluster's name removed for blind review] by the build job,
  after the open models' explanations are built, and sent back with the population.
- The reference codes: Claude Opus 5.5 through the Claude CLI on the subscription, the route of the audit's amendment
  5 (an empty config folder, the instruction whole as the system prompt), on the 200. The route is checked on this
  kind of item first: 100 of [a team's name removed for blind review]'s 447 real-request explanations that Opus 5.5 coded through the API with [a team's name removed for blind review]'s
  prompt ([repository path removed for blind review]), drawn with the same seed, are coded again through the CLI
  with [a team's name removed for blind review]'s prompt, and the agreement on `reason` is reported.
- Human coders (condition 1) are not part of this condition. The 200 are also written as a sheet for coders
  (`human-sheet.csv`: an opaque id and the judge's text, nothing that names the model or the cell), so that the same
  sample can be coded by people. Until human codes exist, the admission below is against the Opus codes and is called
  provisional; when human codes of the 200 exist, the admission is computed again against them, and that result
  decides.

## The admission rule, fixed now

A judge is admitted when, on the 200, both hold:
1. it gives a readable reply to at least 95 per cent of them;
2. Cohen's kappa of its `brand_any` with the reference's is at least 0.70.
It is a fixed threshold, so a judge's admission does not depend on any other judge. Reported beside it, for every
judge, and deciding nothing: the agreement share and kappa on `brand_any` and on `reason`, the error rates by source
and by cell of names and information with their counts (too few in each cell to decide), and each judge's agreement
with every other judge. If fewer than three developers' judges are admitted, [a team of the project, name removed for blind review] is told, the claim
is reported under the admitted judges and the reference alone, and the threshold is not lowered.

## The runs (the issue's three batches)

1. The build job (CPU, `b7-10-explain-build`): extracts the bundle ([repository path removed for blind review]), builds the open models'
   explanations from their `dom2` answers on [a computing cluster's name removed for blind review], merges them with the closed models' explanations built here,
   draws the 200, and sends back the population and the sample.
2. The pilot (`b7-11-explain-judges`, one judge, OLMo 3.1 32B, on the 200), read here: the read rate, a sample of
   replies by hand, its agreement with the reference once the reference is coded.
3. The other four judges on the 200; then the admitted judges on the whole population (the same job file with
   `SET=all`).

## Condition 3, in brief (not this condition's work)

The share of explanations whose `brand_any` is yes, under each admitted judge and under the reference on the 200, by
cell of names and information and by group of models (Claude, Codex, open), with a two-way cluster bootstrap over
tables and models, and with each judge's own explanations left out.

## The route check's result (21 November 2026, about 11:55 AM Central)

The 100 of [a team's name removed for blind review]'s real-request explanations (seed 20261121) that Claude Opus 5.5 had coded through the API with [a team of the project, name removed for blind review]'s prompt were coded again through the CLI route with the same prompt (`route-check/`, `RESULT.json`). All 100 were
read by both. The two routes gave the same `reason` to 95 of 100 (Cohen's kappa 0.92), and the same answer to whether
the reason is a brand reason (`brand_property` or `brand_reputation`) to 98 of 100 (kappa 0.91). The CLI route is
used for the reference codes of the stated sample as written above.

## The build and the pilot, read (21 November 2026, 4:50 PM Central)

- The build ([a job number removed for blind review], 12:24 PM): 29,600 explanations, 26,517 from 27 open models and 3,083 from the closed models
  (Claude 2,138 with the real requests, Codex 945); the stated 200 in the strata written above (20 from each cell and
  side, 40 real requests). Every item's instruction is `judge_prompt.txt`.
- The reference: the 200 coded by Claude Opus 5.5 through the CLI route, all read (`reference/cli/`). It finds a
  brand reason (`brand_any` yes) in 68 of the 200.
- The pilot ([a job number removed for blind review], OLMo 3.1 32B, 4:08 PM): a readable reply to all 200, in the schema, at most 77 output tokens.
  Against the reference: `brand_any` the same in 176 of 200 (kappa 0.71), `reason` the same in 139 (kappa 0.44).
  Under the rule it is admitted (provisional until human codes exist). Read by hand: all 24 disagreements on
  `brand_any` are answers that the reference coded as giving a brand reason and the pilot did not, most of them minor
  reasons that the instruction counts ("from an established brand", "from an unknown brand", "the Sony autofocus
  system is generally industry-leading"), with a few the reference may have counted too readily ("uses manual
  brewing" as a brand property). OLMo 3.1 32B is the stricter judge: a brand reason in 44 of the 200 against the
  reference's 68. The disagreements are most frequent in the real requests (11 of 40). The pilot is sound, so the
  other four judges code the 200 next.

## Amendment 1 (21 November 2026, 5:42 PM Central, after the pilot and before any of the other four judges' codes is read)

[a person's name removed for blind review]'s ruling, relayed by [a team of the project, name removed for blind review] at 5:41 PM Central, verbatim: [a person's words removed for blind review] So no people code the explanations. The open-weight judges are validated by Cohen's kappa
alone: against the reference (Claude Opus 5.5 through the CLI route, the 200 coded by about 4:49 PM) under the admission rule
written above, which stays as it is, and among themselves (every pair's kappa, reported beside it). Admission is no
longer provisional: the words "provisional until human codes exist" above, in the admission rule and in the pilot's
readout, no longer apply, and the human coders' sheet (`human-sheet.csv`) is kept only as a record of the sample. The
[project record removed for blind review] [project record removed for blind review] conditions are amended with his words ([repository path removed for blind review]). [an item of a project document removed for blind review] asked for human
agreement on a stated sample; the paper reports instead the reference judge's agreement with each open judge and the
judges' agreement among themselves, and says that no people coded the explanations, by the author's decision.

## The admission (21 November 2026, 5:50 PM Central; `reference/ADMISSION.json`)

The other four judges coded the 200 in jobs [a job number removed for blind review] (gpt-oss 120B) and [a job number removed for blind review] (Qwen 3.5 122B FP8, Kimi Linear 48B, Gemma
4 31B), each answering all 200 with no refusal in its log. Under the rule written above (at least 95 per cent read and
Cohen's kappa of `brand_any` with the reference at least 0.70):

| Judge | Developer | Read | `brand_any` agreement | kappa | `reason` kappa | Brand reasons in the 200 | Admitted |
|---|---|---|---|---|---|---|---|
| Gemma 4 31B | Google | 200 of 200 | 0.960 | 0.91 | 0.67 | 68 | yes |
| gpt-oss 120B | OpenAI | 200 of 200 | 0.945 | 0.88 | 0.62 | 65 | yes |
| Qwen 3.5 122B FP8 | Alibaba | 200 of 200 | 0.890 | 0.77 | 0.54 | 82 | yes |
| OLMo 3.1 32B | Allen AI | 200 of 200 | 0.880 | 0.71 | 0.44 | 44 | yes |
| Kimi Linear 48B | Moonshot | 196 of 200 | 0.832 | 0.60 | 0.38 | 49 of 196 | no |

The reference finds a brand reason in 68 of the 200. Four judges from four developers are admitted, so the claim is
reported under each of them and under the reference. The judges' kappas with one another on `brand_any` run from 0.58
(OLMo 3.1 32B with Qwen 3.5 122B) to 0.90 (Gemma 4 31B with gpt-oss 120B), and every pair is in the file. Kimi Linear
48B's four unread replies are a reason outside the classes ("width"), a reply in German, a reply about an answer that
gave only a letter, and a JSON object with an invalid escape. The admitted judges code the whole population next
(`SET=all`).

## Condition 3, fixed now (21 November 2026, 9:15 PM Central, before any code of the population is read)

The coordinator assigned condition 3 to [a team's name removed for blind review] at 9:09 PM Central. [A project document's name removed for blind review]'s condition ([project record removed for blind review], `done_when`) is "the
share of explanations that name the brand reported under each judge, by condition". [a person's name removed for blind review]'s ruling of 6:47 PM
(every test over all models first, the differences between models after; the audit's PLAN.md, amendment 6) applies.
Job [a job number removed for blind review]'s folder holds the codes of two admitted judges on all 29,600 explanations: Gemma 4 31B (task 2) and Qwen 3.5
122B FP8 (task 0, whose VERSION file names [a job number removed for blind review], the same array). Job [a job number removed for blind review] (OLMo 3.1 32B and gpt-oss 120B) has
not landed. While I checked the files' fields, one line of Gemma 4 31B's answers was printed. No other code of the
population has been read.

**The population.** 29,600 explanations from 36 models: 5 Claude (Haiku 5.5, Sonnet 5.5, Opus 5.5 and Fable 5.1 through
the API; Fable 5.2 through the CLI), 4 GPT through Codex (GPT-6.2 Sol, GPT-6.2 Astra, GPT-6.1 Sol and GPT-6 Astra) and
27 open models. The cells are `names` (original or crossed) by `info` (0 or 1) by price (`rung` 0 or 2). The real
requests (445) come from the Claude models through the API only, in 29 tables.

**The code that is read.** `brand_any`, the code the judges were admitted on. `reason` is described with each judge's
kappa against the reference beside it (0.44 to 0.67, below the 0.70 rule), and no claim rests on it.

**Checks of the population runs, before any share is read.**
1. Each judge answered all 29,600 ids. Its finish reasons are counted (stop or length, since the context held 8,192
   tokens).
2. The read rate (a reply that `admit.parse` reads), overall and by group, source and cell, against the 95 per cent
   rule.
3. Each judge's kappa on `brand_any` against the reference, computed from its population-run codes on the stated 200
   (the 200 are inside the 29,600). Its agreement with its own sample-run codes on the same 200 is reported beside
   it, since the population runs are new draws (temperature 1.0 for Gemma, 0.6 for Qwen).
4. If a judge reads under 95 per cent of the population, or its population-run kappa on the 200 is under 0.70, its
   shares are reported and marked, and the coordinator rules on it. I do not drop it myself.

**The share, and the estimand.** The share of explanations whose `brand_any` is yes. Explanations per model are very
unequal (157 to over 2,000), because a model that passes over the best product more often writes more of them. The
primary estimate is the mean over models of each model's share, every model with equal weight, the plan's rule
elsewhere. The share over all explanations pooled is reported beside it. Each model's count is given.

**The interval.** A two-way cluster bootstrap over tables and models (2,000 draws, seed 20261121). In each draw, each
drawn model's share is computed over the drawn tables, with repeats counted. The draw's estimate is the mean over the
drawn models that have at least one explanation in those tables. A draw in which a cell or group has no explanation
gives that cell or group no value and is left out, and the draws used are reported. For a real request, the cluster
is its product table.

**What is reported, all models first.**
1. The share under each admitted judge, over all models (dom2 and the requests together, and dom2 alone). No
   judge is the headline: each is reported, with the range across the admitted judges.
2. By condition, on dom2: names (original, crossed) by information (0, 1), pooled over the two prices, and each
   price alone as description.
3. Two contrasts with an interval, paired within model in each draw: original minus crossed, and information 0 minus
   information 1. Everything else is description.
4. Then the differences between models. Each group's share (Claude, Codex, open) on dom2 only, because the real
   requests exist only for the Claude models. The difference of each pair of groups comes from one bootstrap with the
   models resampled within their group. The real requests are reported on their own.
5. Each model's own share (the bootstrap over tables), with its count and its table count. A share with fewer than
   20 explanations or fewer than three tables is not estimable: blank, with the reason, from the start. Then the
   spread of the per-model shares. A per-model file for [a team's name removed for blind review] has the same columns as the audit's (model key, group,
   test, estimate, interval, n, tables, not_estimable, units, predicted direction: none fixed, so two-sided).
6. Each judge's own explanations left out: the explanations of the judge's own model key (Gemma 4 31B and OLMo 3.1
   32B wrote explanations; gpt-oss 120B wrote explanations; Qwen 3.5 122B FP8 did not). As a further repeat, its
   developer's models are left out (Google: the Gemma models; Alibaba: the Qwen models; Allen AI: the OLMo models;
   OpenAI: gpt-oss and the GPT models through Codex).
7. Agreement among the admitted judges on the population: each pair's agreement and kappa on `brand_any` (and on
   `reason`, as description), overall, by group and by cell of names and information.
8. The reference on the 200, by cell, with its counts (too few in each cell to decide).

**When [a job number removed for blind review] lands.** OLMo 3.1 32B and gpt-oss 120B are added under the same rules and every number is computed
again. The two-judge result is marked as superseded, and the results say where a number moved.

## A note on the 90 per cent rule (22 November 2026, 12:43 AM Central, before the rerun under it was read)

The coordinator set one exclusion rule for every study at about 12:14 AM Central ([repository path removed for blind review] section 6). A
model whose answers the parser reads in under 90 per cent of a build's items is reported apart as unable to do the
task. It is left out of every pooled estimate and every analysis of how models differ, and its parse counts stay in
numbers.json under `left_out`. Kimi Linear 48B's explanations come from Study 2's strictly better build, where its
letters parse in 2,965 of 3,600 answers (82.4 per cent; [repository path removed for blind review]). So its 889
explanations leave the shares, the group comparisons, the per-model spread and the judges' agreement on the
population. Its own share under each judge is reported apart. The judges' checks on the stated 200 stay on the 200,
because they validate the judges, not the models. Every other model parses at least 90 per cent of that build. The
results under four judges at [commit removed for blind review] are superseded by the rerun under this rule, and the results say where numbers
moved.

**A note on draws at zero** (22 November 2026, 7:14 AM Central; no rule changes). In the audit, [a team's name removed for blind review]'s reproduction
on another computer found P values that moved because draws that are zero in exact arithmetic came out at plus or minus
1e-15, and their sign depended on the computer's sums (the audit's PLAN.md, the note on draws at zero). shares.py's
boot() counts a draw at zero on both sides in the same way, so it now sets a draw within 1e-12 of zero to exactly zero
before the interval and the P value (ZERO; test_shares.py plants draws whose zeros have either sign). The shares were
run again with the four judges' answers. All 4,589 numbers of results/explanations/numbers.json are the same, and no P
value or interval end moved, so that file is not replaced.
