# Study 2 analysis plan ([project record removed for blind review])

Written by [a team's name removed for blind review] on 20 November 2026 at about 6:40 PM Central and committed before any answer of the full run or of
the dominant sets had returned. What had been seen by then: the pilot on two original tables (laptops 01, earbuds 03),
Claude Sonnet 5.5 and GPT-6.2 Sol through Codex ([repository path removed for blind review]). [A team of the project, name removed for blind review] asked for this plan at 6:25 PM, with [a person's words removed for blind review]. A change to this plan after results are seen is written
below it as a dated amendment with its reason, and the original text stays.

## Data

- **The dominant sets (primary).** For each of the 34 corpus tables, a constructed version in which the designated
  best product is better than or equal to every other product on every displayed attribute and costs no more than any
  other product ([project record removed for blind review]). Built by [repository path removed for blind review] and refused by gate a
  unless every table computes as dominant. Cells: names hidden, original (the invented name on the best product) and
  crossed (the best product's name swapped with one familiar product's name) × information none or supplied × the best
  product's price equal to the cheapest other product or 30 per cent below it: 12 cells, 10 trials a cell, 4,080
  prompts a model (build `dom1`). Two tables are piloted first.
- **The original tables (replication).** The 34 tables as the corpus has them, scrubbed (`study2_tables.py`), in 18
  cells (the three prices 0, 15 and 30 per cent below the cheapest other product), 10 trials: 6,120 prompts a model
  (build `full1`). Three of the 34 are dominant under `dominance_key.py`; 31 are weight-dependent.
- **Models.** Claude Haiku 5.5, Sonnet 5.5, Opus 5.5 and Fable 5.1 (`claude-haiku-5-5`, `claude-sonnet-5-5`,
  `claude-opus-5-5`, `claude-fable-5-1`) through the Anthropic API at the provider's defaults (adaptive thinking, no
  temperature set). The dominant sets run on all four; the original tables on Haiku, Sonnet and Opus, because both
  builds on four models would pass the 150-dollar stop of [an internal document removed for blind review]. GPT-6.2 Sol through the Codex subscription is
  a second-vendor check, reported apart and never pooled with the Claude models.

## The estimates

For a model m and a table t, s(names, information) is the share of parsed answers that pick the designated best
product, over the trials and the price rungs of the cell.

- The **name gap** g(info) = s(hidden, info) − s(original, info), in percentage points: how much the invented name
  costs the best product.
- The **change when the information is supplied** Δ = g(supplied) − g(none).
- The **premium for a familiar name** p(info) = s(crossed, info) − s(hidden, info).

Pooling: equal weight for every table within a model, then equal weight for every model. Intervals: a two-way cluster
bootstrap that resamples tables and models independently with replacement, 2,000 draws, seed 20261120
(`analyze.py`); the 95 per cent interval is the 2.5th to 97.5th percentile of the draws, and a two-sided bootstrap P
value is twice the share of draws on the far side of zero. The unit of inference is the table, and no trial-level test
is used as evidence ([project record removed for blind review]).

## The primary contrast

On the dominant sets, pooled over the four Claude models: the name gap with no information, g(none), and the change
Δ when the information is supplied.

What counts as each outcome, fixed now:
- **No gap to explain**: the 95 per cent interval of g(none) includes 0. Then the study reports that the invented name
  did not cost the best product on these sets, and Δ is not read.
- **The gap closes** (the inference reading): g(none) above 0, Δ below 0 with its 95 per cent interval below 0, and
  g(supplied) within 2 percentage points of zero by two one-sided tests at the 5 per cent level (its 90 per cent
  interval inside −2 to +2).
- **The gap narrows** (both readings): Δ below 0 with its 95 per cent interval below 0, and g(supplied) not shown to
  be within 2 points of zero.
- **The gap stays** (the taste reading): the 95 per cent interval of Δ includes 0 or lies above it.

## Secondary contrasts (Holm-corrected as one family)

1. The name gap at the two prices (equal to the cheapest other product against 30 per cent below it), with no
   information: whether the invented name costs more when the deal looks too good to be true.
2. The premium for a familiar name, p(none) and p(supplied).
3. g(none) and Δ for each Claude model.

Reported beside them without correction: the same estimates on the original tables (all 34; the three dominant ones
alone; without the cells where the best product is cheaper than the shopper's stated range; without the cells where it
is dearer than the stated budget), the GPT-6.2 Sol check through Codex, and the share of answers that name brand
familiarity or trust (`brand_reasons.py`, a word list; the coding of explanations is [project record removed for blind review]).

## Parsing and exclusions

- An answer counts when `parse_answer.py` finds one letter: the letter alone on the first line, else exactly one
  "Product X", "Option X" or "recommend X" in the text. An answer with several letters or none is left out of the
  denominator and counted by model and cell. If more than 5 per cent of one model's answers in a batch are unparsed,
  that model's results wait until the cause is found ([a project document's name removed for blind review]'s batch rule).
- An answer that stopped at the token limit with no text is asked again by the runner; one that still has none is
  missing and counted.
- A Codex answer that used a tool is left out and counted.
- Nothing else is excluded: every table, every trial and every cell stays, with no outlier rule.
- Every build passes gates a, b and c and the twin check before any model sees it; the item files are hashed in
  their commits.

## Amendment 1 (20 November 2026, about 6:55 PM Central, before any answer of the full run or the dominant sets)

[a team's name removed for blind review]'s second reading ([issue number removed for blind review], [commit removed for blind review]) found maker's names left in a few spec values, and [a team of the project, name removed for blind review]
asked for the dominant sets. Changed as a result, with no answer of either build yet seen:
- The original tables are build `full2`, not `full1`: the terms [a team's name removed for blind review] found are replaced in every arm ([commit removed for blind review]).
  The Haiku batches already sent on `full1` are kept as a superseded record and are not analysed.
- Under `dominance_key.py` four of the 34 original tables are dominant, not three: removing the Dyson's air-watt
  figure left the robot vacuums dominant.
- The dominant sets are 32 tables (build `dom1`): the portable speakers and the keyboards are left out, for the reasons
  in `dominant_sets.py` (EXCLUDE). Gate a also refuses a dominant table in which any other product is only tied with
  the best product, so a pick other than the best product is worse at every price.
- The pilot of the dominant sets is build `dompilot1` (laptops 01 and earbuds 03, all four Claude models).
Nothing in the estimates, the primary contrast, its outcomes or the exclusion rules changed.

## Amendment 2 (20 November 2026, about 7:00 PM Central, before any answer of `dom2`)

Amendment 1's time should read about 6:50 PM Central; it was written without reading the clock.

[a team's name removed for blind review]'s second round ([issue number removed for blind review], [commit removed for blind review]) found two dominance gaps and four plausibility or face-validity problems
in `dom1`, and [a team of the project, name removed for blind review] asked at 6:59 PM that every improved figure be one a real product at that price
could have. [a person's name removed for blind review] at 6:53 PM, verbatim: [a person's words removed for blind review]. Changed, with no answer of `dom2` yet seen
(the Haiku answers on `dom1` are superseded and are not analysed):

- **The primary build is `dom2`**: 30 dominant tables, 12 cells, 10 trials, 3,600 prompts a model. Against `dom1`: the
  earbuds 01 codec row is removed (one product lists its maker's own codec); the best headphones 03 pair gains a
  connection line ("wireless and wired"); the monitors' HDR line, stated only for the best monitor, is removed; the
  best toothbrush keeps its 35-day battery and the Quip's disposable-battery line is removed; the espresso machines 02
  and the water bottles 01 are left out, because no real product at that price has the figures the best product
  would need. Every change is in `DOMINANT-SETS.md`.
- **The robustness check**: every estimate is also reported without the tables that [a team's name removed for blind review] flagged as medium or thin
  and that remain in `dom2`: monitors 01, electric toothbrushes 01, robot vacuums 01, laptops 02 and coffee makers 03
  (`analyze.py --thin`). The low flags (the 1,800-watt blender and the certified brewer at a budget model's price at the
  equal-price rung, a Keurig shown as a 12-cup drip maker, a trail shoe of a low-drop brand at 10 mm) are reported as
  limits.
- **The pilot** `dompilot1` stays a pilot and is not pooled into any estimate.
- **Replications, each reported apart and never pooled with the four primary Claude models**: Claude Fable 5.2
  (`claude-fable-5-2`) through the Claude command line ([product name removed for blind review]) 2.1.330 on the subscription (`claude -p` with the study's system
  prompt, no tools, no settings files and no MCP servers; the CLI adds about 410 tokens of its own framing); and
  through Codex 0.166.0 on the subscription, GPT-6.2 Sol, GPT-6.2 Astra, GPT-6.1 Sol and GPT-6 Astra (`gpt-6.2-sol`,
  `gpt-6.2-astra`, `gpt-6.1-sol`, `gpt-6-astra`; the subscription lists no GPT-6.1 Astra on 20 November 2026). Each
  answer records the tool's version, the model id and the date. The same estimates are reported for each replication
  model, and the four Codex models are also pooled with one another as a second-vendor estimate.
- **Order**: `dom2` on every model first, each replication model after a `dompilot1` pilot; then `full2`.
Nothing in the estimates, the primary contrast, its outcomes or the exclusion rules changed.

## Amendment 3 (20 November 2026, about 7:45 PM Central, before any answer of the Study 1 rerun)

[A team of the project, name removed for blind review] asked at 7:37 PM that [a team's name removed for blind review]'s Study 1 rerun ([repository path removed for blind review], 2,040
prompts a model, items file sha256 5522780d...7abc: the 30-model corpus's own prompts with names shown and hidden, and
names hidden with the leaks cleaned) run on the same models as Study 2, so that Study 1 is one experiment across every
model. [a team's name removed for blind review] runs it as a replication of Study 1 and does not analyse it: the design, the estimates and the analysis
are [a team's name removed for blind review]'s. Its answers go to [repository path removed for blind review]. It runs after the dominant sets on
each model: Haiku 5.5, Sonnet 5.5 and Opus 5.5 through the API now; Fable 5.1 through the API only if the Anthropic
spend stays under [an internal document removed for blind review]'s 150-dollar stop (about 117 dollars at this amendment, about 130 after the three
models above, and about 153 with Fable 5.1, so it waits for [a team of the project, name removed for blind review]'s word); and the Codex models and
Fable 5.2 through the CLI when their dominant runs finish. Nothing in Study 2's estimates or rules changed.
## Amendment 4 (20 November 2026, about 7:55 PM Central, before any answer of Fable 5.1 on the original tables)

[a person's name removed for blind review] at 7:49 PM, relayed by [a team of the project, name removed for blind review], verbatim: [a person's words removed for blind review]. With no budget stop, Fable 5.1 also runs
the original tables (`full2`) through the API, so that the replication has the same four Claude models as the primary
build. The replication is then reported pooled over the four models, and over the three models already reported, as
a check that the added model does not change it. Nothing else changed.
## Amendment 5 (20 November 2026, about 10:00 PM Central, before any answer of the information split)

[a person's name removed for blind review] asked what the paper tells sellers: what works, what does not, and why (relayed by [a team of the project, name removed for blind review] at
9:57 PM). The primary build supplies the five reliability items together; the October pilot hinted that the
lab-testing sentence did most of the work and free returns the least. Added, with no answer yet seen:

- **The information split.** On the 30 dominant tables, seven information arms: none; each item alone (the warranty
  row, the first-year failure or return rate row, the time-on-the-market row, the lab-testing sentence, the free-return
  clause); and all five. Each under names hidden, the original names and the crossed names, with the best product's
  price equal to the cheapest other product's, 10 trials a cell: 21 cells, 6,300 prompts a model (build `split1`),
  after a pilot on laptops 01 and earbuds 03 (build `splitpilot1`). The four primary Claude models, through the API.
  Every gate and the test that each arm shows exactly its own item (`test_gates.py`) pass before any model sees it.
- **The estimates.** The name gap (names hidden minus the original names) in each arm, pooled over the four models.
  The family: each single item's gap minus the gap with no information, and each single item's gap minus the gap with
  all five, ten contrasts, from the same two-way cluster bootstrap (2,000 draws, seed 20261120), Holm-corrected as one
  family. An item is said to reduce the gap when its contrast against no information is below zero after Holm's
  correction, and to leave part of the gap that the full set removes when its contrast against all five is above zero
  after the correction. The premium for a familiar name in each arm and each model's gap in each arm are reported
  beside them without correction.
- **Budget.** [a note on the project's accounts removed for blind review]
Nothing in the earlier estimates, outcomes or rules changed.

## Amendment 6 (21 November 2026, about 9:25 AM Central, before any answer of the equalization build)

[project record removed for blind review] asks what the invented name costs in dollars and in stars. At 10:57 PM Central on 20 November [a team of the project, name removed for blind review] agreed to option A below as the primary measure, with names hidden as the zero control, and option B
beside it. [a team's name removed for blind review]'s plan for a measure of machine-based brand equity ([repository path removed for blind review], section 3.1,
commit [commit removed for blind review]) gives the price equivalent as exp(MBBE / |β_price|) − 1 and the rating equivalent as MBBE / β_rating,
with the invented names as the reference. Option A uses the same two formulas and the same reference. Added, with no
answer of this build yet seen:

- **Option A, the equalization price at parity (primary).** On each of the 30 dominant tables, one familiar product is
  given the best product's specifications and the best product's price at the equal-price rung. The invented best
  product keeps both, and the other three products are as in the table, so the two products differ only in their
  names. In the price arm the invented product costs 0, 5, 15, 30 or 50 per cent less than the familiar product, and every
  product has 4.3 stars. In the rating arm the two cost the same, and the invented product has 4.4, 4.5, 4.7 or 4.9
  stars while every other product has 4.3. The familiar product changes with the trial, so that over eight trials each
  of the table's four familiar products is the partner twice. Every cell runs with the names shown and with the names
  hidden. With the names hidden the two products are identical at parity, so the model should pick each of them half
  the time; this is the zero control.
- **Option B, the ladder on the strictly better tables.** On the same 30 dominant tables, the best product costs 0, 5,
  15, 30 or 50 per cent less than the cheapest other product and every product has 4.3 stars, or it costs the same as
  the cheapest other product and has 4.4, 4.5, 4.7 or 4.9 stars. Names shown and hidden.
- **The build.** No information items and eight trials a cell. Option A has 18 cells and option B has 18, so the build
  has 8,640 prompts a model (build `eq1`). A pilot on laptops 01 and earbuds 03 comes first (build `eqpilot1`). The
  four primary Claude models answer through the API. Before any model sees the build, a new gate refuses an option A
  table unless the two products show the same value on every attribute and each of them is at least as good as each
  of the other three products on every attribute and costs no more. Option B passes gate a as `dom2` does. Gates b and
  c and the twin check run as for every build.
- **The estimates for option A.** The answers that pick one of the two products are fitted as a logit of the
  probability that the model picks the invented one: in the price arm on x = −ln(1 − cut), the log of the familiar
  product's price over the invented product's price, and in the rating arm on the difference in stars. Write a for the
  intercept, b for the slope on x and c for the slope on stars. The price equivalent is exp(−a / b) − 1, the premium
  over the invented product's price at which the model is equally likely to pick either product, and the cut that
  offsets the name is 1 − exp(a / b). The rating equivalent is −a / c stars. With MBBE = −a and |β_price| = b these are
  the formulas of DESIGN.md. An equivalent is reported only when the 95 per cent interval of its slope lies above zero,
  and is otherwise reported as not identified; a bootstrap draw whose slope is not above zero counts as an infinite
  equivalent. Beside the fit, with no model: the invented product's share minus the familiar product's share on each
  rung, and the rung, interpolated, at which that difference reaches zero, or "more than 50 per cent" when it does not.
  The zero control passes when the 95 per cent interval of the names-hidden intercept includes 0. When it does not,
  the equivalents are computed from the names-shown intercept minus the names-hidden intercept, and the failure is
  reported. The share of answers that pick neither product is reported for every cell.
- **The estimates for option B.** The cut, interpolated between rungs, at which the best product's share with the
  invented name reaches its share with the names hidden at the equal price and 4.3 stars, and the same in stars, or
  "more than 50 per cent" and "more than 0.6 stars" when it does not. The name gap on each rung minus the name gap at
  the equal price and 4.3 stars gives four price contrasts and four rating contrasts, Holm-corrected as one family.
  They are contrasts to test, with no direction stated: in `dom2` the gap at 30 per cent below the cheapest other
  product against the equal price was 5.5 points with a Holm P of 0.22, which is not reliable.
- **Pooling and intervals.** Pooled over the four models, each with the same number of trials, and for each model. The
  intervals come from the same two-way cluster bootstrap over tables and models (2,000 draws, seed 20261120): the 2.5th
  to 97.5th percentile of the draws. Reported beside them without correction: the familiar partner's kind (high or
  medium familiarity); the tables without the three whose invented name is a real company (laptops 02, laptops 03 and
  earbuds 02) and without the thin tables of amendment 2; and every estimate without the rungs at which the invented
  product costs less than the shopper's stated range, because DESIGN.md keeps every price inside the request and the
  50 per cent rung falls below some ranges.
- **Limits stated now.** In option A a familiar product shows the best product's specifications, which that brand's
  product does not have in the corpus; each of those figures was checked as plausible at that price for the best
  product, not for that brand. The logit treats each answer as one observation, and its interval comes from the
  bootstrap over tables and models, not from the logit's standard errors.
- **Budget.** [a note on the project's accounts removed for blind review]
- **Implementation note (about 9:31 AM Central, before any answer of `eqpilot1` or `eq1` was read).** Every logit fit
  of option A adds 0.5 to the count of each of the two products at each rung, so that a rung at which every answer
  picks the same product still gives a finite fit, in the pooled fit, in each model's fit and in every bootstrap draw.
  One model's interval resamples tables only, as in `analyze.py`. The code is `analyze_eq.py`, tested on planted counts
  in `test_analyze_eq.py`.
Nothing in the earlier estimates, outcomes or rules changed.

## Amendment 7 (21 November 2026, about 9:55 AM Central, after the pilot `eqpilot1` and before any answer of `eq1`)

The pilot `eqpilot1` (laptops 01 and earbuds 03, the four Claude models, 2,304 answers, all parsed;
[repository path removed for blind review]) showed two problems with option A as amendment 6 wrote it. With names
shown and equal prices, none of the 64 answers that picked one of the two products picked the invented one. At a 5 per
cent cut 32 of 64 did, and the share stayed near half up to 30 per cent, so three of the four models reached equal
shares at or below 5 per cent, where the ladder had no rung. At the 50 per cent cut both shares fell: with names
hidden the invented product took 47 of 64 such answers there, against 63 of 64 at the 5 and 15 per cent cuts. One
logit across the five rungs therefore does not describe the answers, and its names-hidden intercept (1.8) failed the
zero control although the parity cell itself gave the invented twin 38 of 64 answers. [A team of the project, name removed for blind review] approved
the changes below at 9:48 AM Central and added the rules on bounds and on the bootstrap. Changed, with no answer of
`eq1` yet seen:

- **Option A's price arm** has rungs at 0, 1, 2, 3, 5, 10, 15, 30 and 50 per cent, so `eq1` has 44 cells and 10,560
  prompts a model (`equalize.py`; the pilot's ladder is `--coarse`). Option B is unchanged.
- **Option A's primary estimate** is the crossing: the cut, interpolated between rungs, at which the invented product's
  share equals the partner's, for each model and pooled. The pooled crossing is read on the pooled curve. It is read
  on the rungs from 0 to 30 per cent. A model whose invented share never reaches the partner's share on those rungs is
  reported as a bound, "more than 30 per cent", and is never extrapolated, and the text says how many models were
  bounded. The 50 per cent rung is left out of the crossing and of the fit because both shares fell there in the
  pilot; its shares are reported.
- **The interval of the crossing** comes from a bootstrap that resamples whole tables, and models for a pooled
  estimate, never single answers: 2,000 resamples with seed 20261120. [a team's name removed for blind review]'s plan for DESIGN.md's measure
  ([repository path removed for blind review], point 6) uses the same seed with 1,000 draws; this study keeps the 2,000 draws
  of its other estimates.
- **The logit** in DESIGN.md's units (amendment 6) is reported beside the crossing, fitted on the rungs from 0 to 30
  per cent.
- **The zero control** is read on the parity cell: with names hidden and equal prices, the invented twin's share of
  the answers that pick either twin, whose 95 per cent interval should include one half (38 of 64 in the pilot). When
  it does not, the names-hidden difference at parity is taken off every rung before the crossing is read, and the
  failure is reported.
- **The rating arm** keeps its steps of 0.1 star, the smallest step a listing shows, and a crossing below the first
  step is reported as "less than 0.1 star".
- **The pilot** stays a pilot and enters no estimate.
Nothing else in amendment 6 changed.
- **A note at about 6:40 PM Central on 21 November, after the results of `eq1` were read.** The writer asked for a test
  beside each estimate that the text gives, for the reporting standard. Amendments 6 and 7 report the two comparisons
  at the same price as estimates with intervals and name no test for them. So `analyze_eq.py` now adds, with no change
  to any estimate, a two-sided P value from the same two-way bootstrap (2,000 draws, seed 20261120) for three
  comparisons at parity (`option_a_parity_tests`). The first is names hidden against names shown: the invented twin's
  share of the answers that pick either twin, hidden minus shown. The second is the invented twin against the familiar
  twin with names shown: the invented twin's share minus the familiar twin's share of all parsed answers. It is the
  crossing curve at a cut of 0, and it lies below 0 exactly when the tie cut lies above 0. The third is the same
  difference with names hidden, which states the zero control as a test. These tests were added after the results
  were read, and they are reported as such.

## Amendment 8 (21 November 2026, about 12:00 PM Central, before any open model has answered `split1` or `eq1`)

At 11:33 AM Central [a team of the project, name removed for blind review] asked for the information split and the equalization build on the open
panel ([project record removed for blind review]). Added, with no answer of either build from an
open model:

- **The models and settings** are those of [repository path removed for blind review], for the 32 models of
  `models/open-models.tsv` at their pinned revisions: vLLM 0.33.0 in the shared container, each model's own
  chat template and generation defaults, a seed taken from each item's id, and at most 1,024 new tokens (the Claude
  runs allowed 2,000). The items are the committed builds `split1` and `eq1`, unchanged, in [repository path removed for blind review]
  (sha256 c7a67ea6...4c84b).
- **The estimates** are the ones of amendments 5 to 7, computed by the same functions from counts made on [a computing cluster's name removed for blind review]
  ([repository path removed for blind review], [repository path removed for blind review]). Before any job, the four Claude models' answers
  sent through the same path gave every published estimate exactly
  ([repository path removed for blind review]).
- **The panels.** The ten models of the open-models plan are pooled as the open panel's estimate. Every model that
  passes the rules below is pooled beside it, and each model is reported alone. The open models are never pooled with
  the Claude or Codex models.
- **The rules** are those of the open-models plan. A model whose answers the parser reads in under 90 per cent of a
  build's items, or that picks the best product in under 10 per cent of the names-hidden items (the split's, and
  option B's in `eq1`), is reported apart as unable to do the task. A model that has not answered every item of a build
  enters no estimate of that build and is listed as incomplete.
- **A note at about 4:50 PM Central on 21 November, after the counts of [a job's name removed for blind review] ([a job number removed for blind review]) and before any estimate
  was read.** Thirty of the 32 models answered every item of both builds, the ten of the open-models plan among them.
  Nemotron 3 Nano 30B and Qwen 3.5 122B A10B gave no answer: each failed at engine start on its Mamba cache. They answer
  the same items from [repository path removed for blind review] (amended at about 5:10 PM; bundle 3 was superseded before use), whose runner
  passes a model's engine settings (Nemotron `{"max_num_seqs": 256}`, Qwen 122B `{"max_num_seqs": 128}`). That runner also adds a
  clarifying turn for items that hold a 'followup' text, which no item of these builds holds, and cuts off a
  half-written last answer line when a run resumes. Their answers enter the estimates over every passing model when
  [a job's name removed for blind review] and [a job's name removed for blind review] run again.
Nothing in the earlier estimates, outcomes or rules changed.

## Amendment 9 (21 November 2026, about 5:45 PM Central, before any Codex answer of `split1` or `eq1` was read)

[project record removed for blind review] asks for the information split and the equalization build on the Codex models too ([issue number removed for blind review]). The
four GPT models of amendment 2 (GPT-6.2 Sol, GPT-6.2 Astra, GPT-6.1 Sol and GPT-6 Astra, through Codex 0.166.0 at
medium effort, `run_codex.py`) answer `split1` and then `eq1` from 5:42 PM ([an internal script removed for blind review]); this note was written
a few minutes after they started and before any of their answers was read. As in amendment 2, they are a replication
reported apart: the estimates of amendments 5 to 7, computed by the same code, are reported for each model and pooled
over the four, and never pooled with the Claude models or the open panel.
Nothing in the earlier estimates, outcomes or rules changed.

## Amendment 10 (21 November 2026, about 5:50 PM Central, before any answer of `attrpilot1` or `attr1`)

[project record removed for blind review] lists arms that `split1` and `eq1` do not hold ([issue number removed for blind review], comment of 5:45 PM). They are the same facts
as listing rows and as sentences in the shopper's request, the review count, certifications, expert endorsement,
country of origin and sustainability, and a 2 by 2 name crossing. [A team of the project, name removed for blind review] asked for them at 5:42 PM, with
[a person's name removed for blind review]'s standing order to finish the paper and test what it needs. Added, with no answer of this build yet seen:

- **The build `attr1`** (`attributes.py`): the 30 dominant tables, with the best product at the cheapest other
  product's price, ten trials a cell. It has sixteen arms besides the arm with no information:
  - the five facts of `split1` in both forms. The warranty, the first-year failure or return rate and the time on
    the market appear as a row in every product block (the form in `split1`) or as a sentence in the request. The
    lab-testing fact and the free return appear as a sentence in the request (the form in `split1`) or as a row in
    every product block. The wording of each form is in `attributes.py` (ROW and SENTENCE);
  - the best product's review count at 50 or at 5,000, with every other product at 500 and every rating at 4.3 stars;
  - four new items, each the same row in every product block: a certification, an expert endorsement, a country of
    origin (Germany) and a sustainability claim.
  Each arm runs with names hidden and with the original names. The arm with no information also runs with the crossed
  names of `split1` and with the three other cells of a 2 by 2 name crossing: every name familiar, every name
  invented, and a familiar name on the best product among invented names. The familiar name is a mainstream brand of
  the category that is not in the table (`attributes.py`, FAMILIAR). The invented names are the corpus's own, other
  than the table's own and the three that are real companies, drawn by a seed from the table's id. That makes 38 cells
  and 11,400 prompts a model.
- **The estimates** (`analyze_attr.py`, tested on planted shares) start with every arm's name gap (names hidden minus
  the original names), pooled and for each model. Three families follow, each Holm-corrected: the same fact as a row
  minus the same fact as a sentence (five contrasts); each arm against no information (sixteen contrasts); and the 2
  by 2, where the effect of the best product's familiar name, the effect of the other products' familiar names and
  their interaction make three contrasts. The pooling, the two-way bootstrap and its P values are those of amendments
  5 to 7, and every estimate is also given without the three tables whose invented name is a real company.
- **The order.** A pilot on laptops 01 and earbuds 03 (`attrpilot1`, 760 prompts a model) on Claude Haiku 5.5 and
  Sonnet 5.5 is read before `attr1` is sent. Then `attr1` runs on the four Claude models through the Batch API, on
  the Codex models and on the open panel on [a computing cluster's name removed for blind review].
- **Limits stated now.** [A project document's name removed for blind review]'s "a 2 by 2 name crossing" is read as the best product's name crossed with the
  other products' names. The familiar names added are chosen by hand among mainstream brands of each category, and the
  invented names on the other products come from other tables of the corpus.
- **A note at about 5:55 PM Central, before any answer of `attr1`.** At 5:54 PM [a person's name removed for blind review] stopped all spending on [an account of the project removed for blind review] (relayed by [a team of the project, name removed for blind review]; verbatim: [a person's words removed for blind review]). So `attr1` is not sent to the Claude models; it runs on the open panel on
  [a computing cluster's name removed for blind review] only ([repository path removed for blind review] to [a job's name removed for blind review], [repository path removed for blind review] and [repository path removed for blind review]), with the rules of
  amendment 8: the ten models of the open-models plan pooled as the panel's estimate, every passing model beside them,
  and each model alone (`open_attr.py`). The pilot `attrpilot1` on Haiku 5.5 and Sonnet 5.5 had already ended (5:53 PM)
  and stays a pilot.
Nothing in the earlier estimates, outcomes or rules changed.

## Amendment 11 (21 November 2026, about 6:55 PM Central, before any estimate pooled over every model was computed)

[a person's name removed for blind review] ruled at about 6:50 PM, relayed by the coordinator, verbatim: [a person's words removed for blind review] So every test of Studies 2a, 2b and 2c, and of the attribute build, is
reported first over every model that answered it, and the differences between models come after. Added, with no
pooled estimate yet seen:

- **The models.** Every model that answered the test enters: the Claude models through the API, Claude Fable 5.2
  through the Claude command line ([product name removed for blind review]), the GPT models through Codex and the open panel on [a computing cluster's name removed for blind review]. Each keeps its own
  exclusion rule. For the API, CLI and Codex models it is the rule of this plan: more than 5 per cent of answers
  unparsed, or items not all answered, keeps the model out. For the open panel it is the rule of the open-models plan:
  under 90 per cent parsed, under 10 per cent best product with names hidden, or items not all answered.
- **The estimates** are the ones of the earlier amendments (the name gap, its change, the contrasts, the crossing),
  computed by the same functions from counts made for every model the same way (`pool_all.py`). The pooling gives
  equal weight to every table within a model and to every model. The intervals come from the two-way bootstrap over
  tables and models (2,000 draws, seed 20261120), with two-sided P values from the same draws.
- **The differences between models.** Each model is given alone, with an interval that resamples its tables. Each
  developer group (Anthropic, OpenAI, the open-weight developers) is then pooled. The difference between two groups gets
  an interval and a P value from a bootstrap that resamples the tables once and the models within each group. The
  per-model estimates, with their standard errors from the same draws, go to [a team's name removed for blind review]'s shared analysis of how models
  differ (`predictors/heterogeneity.py`).
- **The attribute build** has no Claude model, because of the 5:54 PM stop, and is pooled over the GPT and open models.
  The text says so in one sentence, and the two-model pilot is reported as a pilot only.
- The results by model group reported so far stay as they are; this changes the order of reporting and adds the pooled
  results, and no earlier estimate changes.
Nothing in the earlier estimates, outcomes or rules changed.
Note on the implementation of amendment 11 (21 November 2026, about 7:35 PM Central; the first three points were in
`pool_all.py` before its first run, the others were written after the estimates over all models of Studies 2a and 2b
and of the store were read):
- The developer groups are Anthropic (the Claude models), OpenAI (the GPT-6 models through Codex) and open weights
  (every model served from its open weights on [a computing cluster's name removed for blind review]). OpenAI's gpt-oss models are in the open-weight group, because
  they run from their open weights like the rest of the open panel; `per_model.csv` also names each model's own lab, so
  [a team's name removed for blind review] can group them by developer instead.
- The difference between two groups resamples the tables once for both groups, then the models within each group.
- Each model's standard error for [a team's name removed for blind review] is the standard deviation of its 2,000 draws over tables.
- The secondary family of the primary report is the same function's: the three pooled contrasts and each model's gap
  and change, 73 tests over the 35 models of Study 2a.
- The store keeps its own plan's 10,000 draws and its Holm family over the 15 arms.
- Study 2c is computed in a separate run, because its fits take about an hour.
- The open panel's dom2 answers come from the letters export of [a job number removed for blind review] (26 models). The export of [a job number removed for blind review] adds the
  models that answered later (Nemotron, the two-H100 models, Kimi after [a job's name removed for blind review]); the pooled estimates are computed again
  when it is fetched, with the same script.
- The attribute build: [a person's name removed for blind review] ruled at 6:56 PM that coverage across all studies is needed and that runs through Codex
  or a subscription are fine, so attr1 also runs on the four Claude models through the Claude command line ([product name removed for blind review]) when the
  subscription accounts return (about 2 AM on 22 November); it is then pooled with them, and the sentence on its
  missing Claude models is dropped.

Note on the attribute build's Claude models (22 November 2026, about 12:45 AM Central, written after the pooled attr1
results were read): the coordinator approved at 8:51 PM on 21 November that Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5
answer attr1 through the Message Batches API on [an account of the project removed for blind review] ([repository path removed for blind review]), with the same
request as the paper's earlier Claude answers (cached system block, adaptive thinking, each model's default effort,
max_tokens 8000), in place of the Claude command line ([product name removed for blind review]) named in the implementation note of amendment 11. Claude Fable 5.1
waits for [a person's name removed for blind review]'s choice. attr1 is pooled with `pool_all.py --only attr` by the same rules as Studies 2a to 2c (each
model screened by its own rule, the same functions as analyze_attr.report, each developer group and the difference
between groups). Nothing in the estimates, families or rules changed.
