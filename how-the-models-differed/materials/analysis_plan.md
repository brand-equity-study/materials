# Plan for the common analysis of model heterogeneity ([a team's name removed for blind review])

## Plan note

Written on 21 November 2026, 6:54 PM Central, at the coordinator's request of 6:50 PM, from [a person's name removed for blind review]'s framing of about
that time, verbatim: [a person's words removed for blind review] It was written after the
per-study results had been read, so every number it produces summarizes results that were already known, and none is a
test written in advance.

## What it does

[repository path removed for blind review] takes one study's per-model estimates (one row per model: the model key, the
estimate, and its standard error or 95 per cent interval, from which the standard error is the interval's width divided
by 3.92) and writes, for that study, [repository path removed for blind review]:
- the number of models;
- the share of models whose estimate is in the predicted direction, and the share whose interval excludes zero;
- the estimate over all models from a random-effects model (the between-model variance tau-squared by the method of
  moments of DerSimonian and Laird), with its 95 per cent interval;
- tau, the between-model standard deviation, and I-squared, the share of the spread in the estimates that is not
  sampling error;
- a 95 per cent prediction interval for the effect in a new model (Higgins, Thompson and Spiegelhalter 2009: the
  estimate plus and minus the t quantile with k - 2 degrees of freedom times the square root of tau-squared plus the
  estimate's variance);
- the same six moderators in every study, each in its own random-effects meta-regression (weights one over the
  estimate's variance plus the residual tau-squared), from [repository path removed for blind review]: chat-tuned
  against base; size (log10 of total parameters, for models with published weights); release date (years); open
  against closed weights; reasoning (extended thinking on against off, where the record says which); and developer (all
  developers at once, a Wald test with one degree of freedom fewer than the number of developers). A moderator is left
  out of a study when it takes one value there, or when fewer than three models have each value. Holm corrects the
  moderators that are estimable in a study, as one family.

It also rewrites [repository path removed for blind review], one table across every study it has run, which the
general discussion uses.

## What the estimate over models is for (added 21 November 2026, 7:45 PM Central)

The random-effects model treats the models as independent, but every model of a study answered the same tables, so a
table that is hard for one model moves every model's estimate together. Its interval and P for the estimate over models
are therefore too narrow, and the study's own pooled estimate, from the two-way bootstrap that resamples tables and
models, is the inference for the effect over models (for Study 2b's lab sentence alone against none, the random-effects
P is below 0.001 and the study's own Holm P is 0.24). This script's numbers are for the spread between models: the
count of models in each direction, tau, I-squared, Q, the prediction interval and the moderators. A text that reports
an effect over models takes it from the study, not from here. Where a study's plan names several contrasts (Study 2b's
ten), every one goes through, and `heterogeneity_family.py` applies Holm across them, rather than one chosen after the
results were read.

## The audit's per-model file, Study 2d (added 21 November 2026, 8:04 PM Central)

Written after the audit's per-model results ([a team's name removed for blind review]'s [repository path removed for blind review], commit [commit removed for blind review])
and the runs below had been read.
- There is one run for each test and component, 13 in all: the six components of test 1, the six of test 2, and recall
  in H6b (`results/heterogeneity/study2d-<test>-<component>/`).
- [a team's name removed for blind review]'s file gives a predicted direction only where the audit's amendment 1 fixes one: inferred quality and
  credibility in tests 1 and 2, and recall in H6b, all positive. The other eight runs are two-sided (`--direction 0`).
  They report how many models are above and below zero, and they report no share in a predicted direction.
- Each model's slope is in standard units of the component within that model. A model that spreads a component widely
  and a model that spreads it narrowly therefore have slopes on different scales. The spread between models in these
  runs includes those differences in scale as well as differences in how much the gap changes with the component.
- The audit's plan reports a component or a gap whose split-half reliability is below 0.5 in a model as not measured
  reliably there; its relation to the gap "is shown but not read as present or absent". The main run keeps all 29
  models, which is the audit's own pooled panel. A check beside it keeps only the models whose gap and component both
  have a reliability of at least 0.5 where the file gives one (`check_reliable_models_only` in each numbers.json, and
  the second table of SUMMARY.md).
- Two models have an interval of zero width: Qwen 3 32B on recognition in test 2 and Gemma 3 27B on tone in test 2.
  Every bootstrap draw gave those two models the same slope, so no sampling error was measured for them, and an
  inverse-variance weight cannot be given. The script leaves such a model out of that run and names it
  (`drop_zero_width`, with its test). This rule was written after the two rows were found.
- Added 21 November 2026, 8:27 PM Central. [a team's name removed for blind review] found the cause of those two rows. In each, the component varies in
  only one table, and a slope that rests on one table has no interval over tables. Its corrected file ([commit removed for blind review])
  leaves blank every per-model slope that rests on fewer than three tables, with the reason in its column
  `not_estimable`. There are four such slopes: Qwen 3 32B's recognition in tests 1 and 2, Gemma 3 27B's tone in test 2
  and gpt-oss 120B's tone in test 2. The script leaves a row without an estimate out of its run, and names the model
  with the study's reason (`--reason-col`, with its test). On the corrected file no row has an interval of zero width,
  so the zero-width rule now leaves out nothing; it stays as a guard. The 13 runs were run again on the corrected file.
  Only two runs changed: test 1's recognition (28 models, tau 1.25, which was 0.99) and test 2's tone (27 models, tau
  1.42, which was 1.30).
- In this panel the closed models are the four Claude models. The Claude models answered through the API, and the 25
  open models answered on [a computing cluster's name removed for blind review] through their own chat templates. So the moderators "open against closed weights"
  and "developer" measure a difference between these two routes as much as a difference between model families, as the
  audit's RESULTS-all.md says in its limits.
- `heterogeneity_family.py` applies Holm across the six runs of each test (`study2d-test1-family.json` and
  `study2d-test2-family.json`).

## The reasons the models give, Study 2e (added 21 November 2026, about 9:25 PM Central)

[a team's name removed for blind review]'s file [repository path removed for blind review] ([commit removed for blind review]) gives, for each of 36 models, the share of its
explanations that mention a brand (brand_any), under each of two judges (Gemma 4 31B and Qwen 3.5 122B FP8), with an
interval from the bootstrap over tables. Each judge is one run (`study2e-<judge>`), in percentage points, two-sided,
because the plan predicts no direction. A share cannot fall below 0 or rise above 100, but the random-effects model
works on the share's own scale, so its prediction interval can pass either bound; it describes the spread between
models and is not a range of possible shares. When [a job number removed for blind review] adds the other two admitted judges, [a team's name removed for blind review] replaces the
file and the two runs go again, with one more run for each new judge.

At 10:16 PM the four runs were made on [a team's name removed for blind review]'s file [commit removed for blind review] (four judges: Gemma 4 31B, Qwen 3.5 122B FP8, OLMo 3.1
32B and gpt-oss 120B; the first two judges' rows unchanged). Under OLMo 3.1 32B, GPT-6.2 Astra's share is 0 of 197
explanations, and its interval has zero width, so the zero-width rule leaves it out of that run. That makes the run's
estimate a little higher than it would be with the model in it. [a team's name removed for blind review] is asked for an interval that a share of zero
can have (for example Wilson's), and the run goes again when the file has one. [a team's name removed for blind review]'s file [commit removed for blind review] gives every
row Wilson's interval as well, and a row whose bootstrap interval has zero width takes Wilson's in lo95 and hi95 (its
column interval_method says so). GPT-6.2 Astra under OLMo 3.1 32B now has 0 to 1.9 per cent and enters the run: 36
models, estimate 17.7 per cent (18.3 without it), tau 13.7. The other three judges' runs are unchanged.

## The estimator of tau changes to REML (added 21 November 2026, 9:28 PM Central)

[a team's name removed for blind review] checked Study 2e at 9:27 PM: under the Qwen 3.5 122B judge, tau was 31.7 points, although the 36 shares have a
standard deviation of 20.7 points. The run had read the right rows and scale; the cause was the estimator. Under the
first version of this plan, tau-squared came from DerSimonian and Laird's method of moments, and with standard errors
that differ fifteenfold between models (0.8 to 11.9 points there), that estimate can be far from the truth in either
direction. Veroniki et al. (2016, Research Synthesis Methods 7, 55-79, doi:10.1002/jrsm.1164) found Paule and
Mandel's and the restricted maximum likelihood (REML) estimators better than DerSimonian and Laird's, and Langan et al.
(2019, Research Synthesis Methods 10, 83-98, doi:10.1002/jrsm.1316) recommend REML and report that Paule and Mandel's
estimate is biased upward when the studies differ greatly in size, as the models here do.

From now on every run estimates tau-squared by REML, in the random-effects model and in each moderator's
meta-regression. I-squared is Higgins and Thompson's tau-squared divided by tau-squared plus the typical within-model
variance. The Q test is unchanged. DerSimonian and Laird's and Paule and Mandel's tau are kept in each numbers.json
under random_effects, checks. Every study was run again (32 runs, with the families' Holm files). Each numbers.json now
also records every argument of its run (args), so that it can be run again exactly.

This change was made after every result had been read. Under REML the taus are close to the Paule and Mandel values,
and they moved in both directions. Study 1b's tau went from 5.20 to 6.80 points. Study 2c's went from 27.94 to 24.46.
Study 2e's went from 20.32 to 21.39 under the Gemma judge and from 31.68 to 20.53 under the Qwen judge. Study 2d's
recall slope went from 0.08 to 0.04. The moderators that pass Holm changed in a few runs, and SUMMARY.md gives the
current ones. The `--selftest` and a new test (a planted panel of 36 models with standard errors from 0.8 to 12 points
and a true tau of 20) pass under REML.

## The attribute build, Study 2b's further attributes (added 22 November 2026, 2:45 AM Central)

[a team's name removed for blind review]'s file [repository path removed for blind review] (34 models: three Claude models through the
Batch API and 31 open models, Kimi Linear 48B out under the open-models rule) goes through 25 runs
(`study2b-attr-*`): the name gap with no information (predicted positive); the three effects of the 2 by 2 name
crossing, of which the other products' familiar names are predicted to lower the optimal product's share (negative)
and the optimal product's own name and the interaction are two-sided; the 16 arms of added information against none
(predicted negative, as in Study 2b's ten contrasts), with Holm across the 16 (`study2b-attr-arm-family.json`); and the
five facts as a row of the table against as a sentence of the request (two-sided), with Holm across the five
(`study2b-attr-row-family.json`). The directions follow the plan's amendment 10 and the earlier Study 2b runs; they
were set after [a team's name removed for blind review]'s pooled result had been read. The effect over models is [a team's name removed for blind review]'s two-way bootstrap, as for every
study here.

## Check

`python [repository path removed for blind review] --selftest` builds a planted panel of 60 models whose true effects have a
known mean, a known between-model standard deviation and one known moderator (open against closed), and refuses unless
the script recovers tau within 20 per cent, finds the planted moderator with a Holm P below 0.05, and finds no
moderator that was not planted with a Holm P below 0.05.
