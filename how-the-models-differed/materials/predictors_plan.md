# Analysis plan for what predicts machine-based brand equity ([project record removed for blind review], [issue number removed for blind review])

Written by [a team's name removed for blind review] on 21 November 2026 and committed before any estimate of this step. [A team of the project, name removed for blind review] moved the
step from [a team's name removed for blind review] to [a team's name removed for blind review] at 6:01 PM Central. Times are US Central.

## The question

[project record removed for blind review] asks which properties of a model go with a larger cost to an unknown name and larger equity for its
brands, and which properties of a brand go with larger equity. At the model level the properties are size within a
family, mixture-of-experts against dense, base against chat, reasoning on and off, developer, open against closed and
release date. At the brand level they are big or small, specialist or mass-market, category, price tier, and the
frequency and tone of the brand's text in public corpora. Every estimate is reported, null or not.

## The outcomes

Model level, for a model m:
- G(m), the cost to an unknown name: on [a team's name removed for blind review]'s strictly better tables (`dom2`, 30 tables, no information supplied,
  both of [a team's name removed for blind review]'s price rungs), the share of answers that pick the designated best product with names hidden minus the
  share with the original names, in percentage points, computed for each table and pooled with every table weighted
  equally. Sources: [a team's name removed for blind review]'s [repository path removed for blind review] for the Claude models, its CLI and Codex runs
  (`dom2-fable-5-2-cli/`, `dom2-codex/`), and the open models' letters in [repository path removed for blind review] ([a team's name removed for blind review]'s export of
  every open model's dom2 answers, read with `final_answer`). A second form for the 30 corpus models, which have no dom2
  answers, is Study 1b's gap ([repository path removed for blind review], `item2_brand_gap_by_model`), analyzed apart
  and never pooled with G.
- E(m), the equity of the model's brands: the mean over brands, every brand weighted equally, of the brand equity of
  [project record removed for blind review] ([repository path removed for blind review], section 3.1: the brand's conditional-logit intercept minus the mean intercept
  of the invented names in its category, in log-odds), once [project record removed for blind review]'s analysis has written it. Until then the preliminary
  form is the mean over brands of [project record removed for blind review]'s brand equity ([repository path removed for blind review], the share
  with names shown minus hidden), labelled preliminary wherever it is reported.

Brand level, for a brand b and a model m: Q(b, m), [project record removed for blind review]'s brand equity of b in m, and, until it exists, [project record removed for blind review]'s preliminary
equity of b in m.

## The model characteristics

[repository path removed for blind review] holds one row for each model with a G or an E, and for every cell a
source: total parameters and active parameters (from the safetensors metadata of the model's Hugging Face repository at
the revision the runs used, or the model card); mixture-of-experts or dense (from the repository's config.json: a
number of experts above one); developer; open or closed (open when the weights are published); base or chat; whether
thinking was on; release date (the date the developer published the model, from the model card or the developer's
announcement; for an open model with neither, the creation date of its Hugging Face repository, labelled as such). A
cell without a public source is left empty and counted as missing, never guessed. Closed models have no published
parameter counts, so they enter no size analysis.

## The brand characteristics

[repository path removed for blind review] holds one row for each of the 73 brands of [project record removed for blind review], with a source for every
cell:
- big or small: the brand's value in a published brand-value ranking ([project record removed for blind review]'s `brand_value_rankings.csv`: in a ranking or
  not, and log10 of its value where ranked), and log10 of its monthly Wikipedia views ([project record removed for blind review]);
- specialist or mass-market: specialist when the company that owns the brand sells consumer products mainly in one
  product category, by its Wikipedia article or company page (the URL recorded); mass-market otherwise. Two coders
  ([a team's name removed for blind review] and an independent Codex or Opus session given only this rule and the sources) code every brand; agreement is
  reported, and disagreements are settled by the written rule and recorded;
- category: the categories of the corpus's tables in which the brand appears;
- price tier: from the corpus's tables, the mean over the brand's products of its price divided by the median price of
  its table; premium above 1.25, value below 0.80, mid otherwise;
- frequency of its text: log10 of its count in the OLMo training data (infini-gram, [a team's name removed for blind review]'s
  [repository path removed for blind review], the count of the brand alone), and [project record removed for blind review]'s corpus frequencies;
- tone of its text: from the same counts, the brand's co-occurrence with positive words minus with negative words,
  divided by their sum ([a team's name removed for blind review]'s `brand_counts.csv` and `brand_pmi.csv`); and, when [a team's name removed for blind review]'s [project record removed for blind review] counts exist, the same
  measure from them.

## The analyses

Model level. Every analysis uses G(m, t) for each model and table, and E(m) where it exists. Intervals come from the
two-way cluster bootstrap of Study 2 (tables and models resampled independently, 10,000 draws, seed 20261120), and P
values are twice the share of draws on the far side of zero.
1. Size within families: the slope of G on log10 total parameters, within Qwen 3.5 (0.8B to 122B) and within Gemma 4
   (12B to 31B), each family alone and pooled with a family term (models resampled within their family).
2. Mixture-of-experts against dense: the mean G of mixture-of-experts open models minus dense open models, and the same
   with log10 total parameters held fixed (a linear regression).
3. Base against chat: from [a team's name removed for blind review]'s [a job's name removed for blind review] ([repository path removed for blind review], key `q1`; OLMo 2 7B, Llama 3.1 8B,
   Qwen 2.5 7B), each pair's chat minus base cost to the invented name with its interval as reported there, and their
   mean, with an interval from resampling tables.
4. Reasoning on and off: [project record removed for blind review]'s four pairs (`thinking_pairs`), each pair's difference and the pooled difference as
   reported there, and the same on dom2 for any model run both ways.
5. Developer: each developer's mean G with its interval (descriptive).
6. Open against closed: the mean G of open models minus closed models on dom2.
7. Release date: the slope of G on release date in years, with an open-or-closed term.
The primary family at the model level is analyses 1 (pooled slope), 2 (unadjusted), 3 (mean), 4 (pooled), 6 and 7:
six contrasts, Holm-corrected, for G. The same six for E form a second family once [project record removed for blind review]'s equities exist.

Brand level. Every analysis uses Q(b, m) for each brand and model, with a category term (the brand's main category),
and intervals from a two-way cluster bootstrap over brands and models (10,000 draws, seed 20261120).
1. Big or small: the slope of Q on log10 brand value among ranked brands, and the difference ranked minus unranked.
2. Specialist minus mass-market.
3. Price tier: premium minus mid, and value minus mid.
4. Frequency: the slope of Q on log10 count in the OLMo training data.
5. Tone: the slope of Q on the tone measure.
6. Category: each category's mean Q (descriptive).
The primary family at the brand level is analyses 1 (the slope on log10 brand value), 2, 3 (premium minus mid), 4 and 5:
five contrasts, Holm-corrected.

A contrast with a Holm P below 0.05 is reported as an association in its direction; every other estimate is reported
as no association shown, with its interval. Nothing here is causal: models and brands differ in many ways at once.

## Runs

These are regressions on a few thousand rows (for example 73 brands by 32 models), so they run on [a computer's name removed for blind review]. The first run
uses the preliminary equity and the 28 open models of [project record removed for blind review] that have every answer; it runs again when [project record removed for blind review]'s equities and
the four remaining Qwen models ([a computing cluster's name removed for blind review] jobs [a job number removed for blind review] and [a job number removed for blind review]) land. Each run writes
[repository path removed for blind review], and RESULTS.md names the run each number comes from.

## Changes after the first version

Every change is dated here, with the reason and what it changes, before any estimate that it affects.

- 21 November 2026, about 6:13 PM Central, before any code or estimate: the specialist coders. Two independent agent
  sessions (Claude Sonnet 5.5, each given only the written rule, the brand list and the instruction to read each
  brand's Wikipedia article or its owner's) code every brand into coding/specialist_a.csv and coding/specialist_b.csv,
  neither seeing the other's file; [a team's name removed for blind review] settles each disagreement by the written rule, with the reason, in
  coding/specialist_settled.csv. This replaces [a team's name removed for blind review] as the first coder, so that both codes come from coders who did
  not write the plan. Nothing else changes.
- 21 November 2026, 6:15 PM Central, before any estimate: base against chat. [a team's name removed for blind review]'s results
  ([repository path removed for blind review], `q1`) give each family's base-to-instruct change in the cost to the
  invented name, with its interval and P, at two prompt forms, but not the per-table values that the plan's mean
  "with an interval from resampling tables" needs. So analysis 3 takes each pair's change as [a team's name removed for blind review] reports it, at the
  prompt form `plain3` (the form of [a team's name removed for blind review]'s summary), and the family's member is the mean of the three pairs, with a
  standard error from their reported 95 per cent intervals (each interval's width divided by 3.92, the three treated
  as independent) and a two-sided P from the normal distribution. Analysis 4's member is [project record removed for blind review]'s pooled difference with
  its reported P. If [a team's name removed for blind review] adds per-table values, the mean is computed again as first planned and both are reported.
- 21 November 2026, 6:19 PM Central, after a code check with 50 draws (run `smoke`, not reported) whose only printed
  numbers were the Holm P values of three other brand-level contrasts, and before any estimate of this contrast was read:
  brand value. Only 12 of the 73 brands are in a published value ranking, and with the category term the slope on
  log10 brand value cannot be estimated on 12 brands (the design is singular). So the family's member for big or small
  becomes analysis 1b, brands in a value ranking minus brands in none (all 73 brands, with the category term), and the
  slope among the 12 ranked brands is reported as secondary, without the category term. The specialist contrast is
  also reported with each coder's codes, as secondary. Nothing else changes.
- 22 November 2026, 3:53 AM Central, after the estimate with four pairs was read (run `prelim3`): the fourth pair.
  The change of 6:15 PM says "the mean of the three pairs" because [a team's name removed for blind review] had reported three. [a team's name removed for blind review] then added OLMo 2
  32B to `q1` ([commit removed for blind review], 10:15 PM on 21 November), and analysis 3 now takes the mean of every pair that `q1` reports
  at `plain3`, four at this run. Because this was decided after the estimate was read, RESULTS.md reports the mean of
  the three pairs (+3.63 points) beside the mean of the four (+4.18). Nothing else changes.
- 22 November 2026, about 4:59 PM Central, after both estimates were read (runs `prelim2` to `prelim4`), at the
  coordinator's request of 4:56 PM that one current run give both: the change of 3:53 AM is withdrawn for the family.
  Because the fourth pair was taken in after its estimate was read, analysis 3's member of the primary family is again
  the mean of the three pairs that the change of 6:15 PM named (OLMo 2 7B, Llama 3.1 8B and Qwen 2.5 7B;
  `PLAN_PAIRS` in analyze_predictors.py, which refuses if `q1` lacks one of them), as the paper reports it. The mean of
  every pair that `q1` reports, four at run `prelim5`, is reported beside it as exploratory, outside the family
  (`3 chat minus base, every pair (exploratory)`). Nothing else changes.
