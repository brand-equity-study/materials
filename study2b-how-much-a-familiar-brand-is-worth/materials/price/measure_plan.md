# The full measure: analysis plan (with DESIGN-2.md)

[a team's name removed for blind review], 21 November 2026, about 10:10 PM Central, before any list of the full design is built and before any answer
to it exists. The pilot's plan (ANALYSIS-PLAN.md, with Amendments 1 to 4) stands for the pilot; this plan governs the
full design and takes from the pilot's plan only what it names.

## 1. The quantities

For each familiar brand b in category c and model m (39 brand and category pairs):

- **V(b, c, m)**, the brand's value at its own band, from the main version's conditional logit (DESIGN-2.md, section
  4): its intercept plus its slope on log price times (its band centre's log price minus the market centre), minus the
  invented names' mean, in log-odds.
- **The share premium** (every cell), and **the dollar premium** where the brand's own price coefficient (the main price
  coefficient plus its slope) has a 95 per cent interval below zero, as DESIGN-2.md section 4 defines them. The
  dollar premium divides by the brand's own price coefficient (the literature reader's second point).
- **The blind gap at its own band** (no choice model): over the main lists in which the brand's product is priced
  inside its own band, the share of lists in which that product was picked, minus the share in which the same product
  was picked in the names-hidden twin.
- **The too-good-to-be-true curve**: V at each of the six price levels.
- **Each version's value** V_k(b, c, m) for the five versions and for each of the four system prompts.

Intervals: a bootstrap over lists within each category and model (1,000 draws, the logit refitted in each, seed
20261120 and the model's key, as analyze_mbbe.py's model_rng does), percentile intervals.

## 2. Primary results (each reported for every model)

1. **Each brand's value at its own band**, as a share premium with its interval, and as a dollar premium where it is
   defined; the number of brand, category and model cells that have a dollar premium, out of all cells.
2. **Stability across the multiverse**: for each brand, category and model, the number of the five versions whose value
   keeps the main value's sign and lies inside the main value's interval; summarized as the share of cells with at
   least four of five.
3. **The comparisons between models** (Amendment 4 of the pilot's plan): for each brand and category, the difference
   in dollar premium between each GPT model and each Claude model and between the means of three groups (Claude, GPT
   through Codex, open), with a bootstrap interval (lists resampled within each model), on the cells where both sides
   have a dollar premium. Never in log-odds, because each model's logit has its own scale.

## 3. Checks that come before the results are read

- The builder's balance table (each name by price level, attribute level, position and letter) within its tolerance,
  the dominance check, and the price table's sources, as the builder refuses otherwise.
- The simulation check: analyze_mbbe2.py recovers the simulation's true values (correlation at least 0.9) and its 95
  per cent intervals hold the truth in 90 to 98 per cent of draws, as the pilot's plan section 8.1 asks.
- For each model and category: whether the model reads the specifications (the pilot's Amendment 2 rule: at least two
  attributes with a best-level coefficient above zero by its interval). A cell that fails is reported alone and left out
  of every summary across models and of the comparisons between models.
- For each model and category: the main price coefficient and its interval; where its interval includes zero, no brand
  in that category and model has a dollar premium, and the table says so.

## 4. Reliability and validity

- Split-half reliability of the 39 values within each model (lists split at random within category, Spearman-Brown
  corrected), the criterion 0.7 as in the pilot's plan; the simulation expects 0.82 to 0.91 at 1,600 lists.
- The values against the pilot's (the same models and brands at the pilot's band, version V2 against the pilot):
  Spearman correlation over the 39 pairs within each model.
- The convergence and discriminant analyses of the pilot's plan (sections 6 and 7), with V in place of the pilot's MBBE.
- The same brand across categories and across assistants (the pilot's Amendment 3), with V.

## 5. How the results are worded

The share premium is named as the unit every cell has, and the text says that it mixes a brand's value with how
strongly a model's picks follow the products' differences. A dollar premium is named only where it is defined. A
comparison between models is stated in dollars. "Value" and "premium" are defined once against these quantities.

## 6. What would change this plan

A first job on two open models (DESIGN-2.md, section 9) is read against the pilot's stop rules (DESIGN.md, 6.5) before
the panel runs; a change after it is a dated amendment here, written before the panel's answers are read.

## Revision 1 (21 November 2026, about 10:41 PM Central, after the independent reader's check and before anything is built or answered)

An independent reader (an Opus session given the brief, DESIGN.md, DESIGN-2.md, this plan and the simulation, without
the writer's conclusions) found seven defects; DESIGN-2.md, section 12, lists each with its answer. In this plan:

1. **Three units, the brand's own coefficient deciding.** The quantities of section 1 are the share premium (every
   cell), the price premium in per cent of the brand's band-centre price and in dollars at that price (where the
   brand's own price coefficient, the main coefficient plus its slope, has a 95 per cent interval below zero, brand by
   brand), and the rating equivalent in stars (the value divided by the coefficient per star of rating, where that
   coefficient's interval lies above zero). The rule of section 3 that removed every price premium in a category whose
   main price coefficient includes zero is withdrawn; the main coefficient is still reported.
2. **Comparisons between models** (section 2, item 3) use the rating equivalent, which nearly every cell has, and the
   price premium on the cells where both models have one; never the log-odds or the share premium. They are named
   comparisons between routes (API, Codex, run_items.py) as well as between models.
3. **Stability across the multiverse** (section 2, item 2) is no longer a count of versions inside the main interval,
   which fails about one time in four even when nothing changes. For each version: the difference between its value and
   the main fit's value read at the same point (V1 at the market's centre, V2 at the pilot band's centre, V3 to V6 at
   the brand's own band), with an interval in which both errors add; and over the 39 pairs within each model, the
   Spearman correlation between the main values and the version's, corrected for the split-half reliability of both.
   The system prompts are a separate panel, as slices of the main fit.
4. **Reliability** (section 4) is computed within each category (lists split at random within the category, the
   category's brand values correlated, Spearman-Brown corrected) and averaged over categories, beside the pooled
   figure; the pooled figure alone would be raised by the categories' different scales.
5. **The curve** comes from the second fit, with a term for each familiar name at each price level, and its reading
   names the three readings that it cannot separate (DESIGN-2.md, section 4).
6. **A new stop rule for the first job**: a category in which a model's main price coefficient lies above zero by its
   interval stops the run until it is read.
7. **The pilot's arms** (repeat, rating, direct premium) are analysed as in the pilot's plan, at the brand's own band,
   and the direct premium is reported beside the price premium for each brand as the answer that needs no price
   coefficient.
8. **The size** is checked against the pilot's estimates (b21-06) before the build (DESIGN-2.md, section 9, step 0).

## The coordinator's decisions on the design (21 November 2026, 10:46 PM Central, under [a person's name removed for blind review]'s delegation)

1. DESIGN-2 is approved as revised ([commit removed for blind review]). The order of work is DESIGN-2's section 9: step 0, the sourced price
   table, the builder with its balance checks and tests, the analysis script with its simulation check, the explainer,
   and the first job on two open models with the new stop rule; each job file goes to the coordinator.
2. Open models: every version on all 32 models through [a computing cluster's name removed for blind review], in short-queue pieces, under the five-H100 ceiling.
3. Claude, through [an account of the project removed for blind review]'s Batch API: Opus 5.5, Sonnet 5.5 and Haiku 5.5 on the main version at the full
   size plus the direct premium arm (about 87 USD); Fable 5.1 on the main version only at 800 lists a category (about
   71 USD), and only if the ledger's spent plus open estimates then stays under 400 USD. Each estimate is written in
   [repository path removed for blind review], where the coordinator approves it.
4. GPT, through Codex: the Sol pair on the main version at 800 lists a category plus the direct premium arm, when the
   items exist ([a team's name removed for blind review] runs them).
5. The multiverse runs on the open models only; the closed models answer the main version, and the text says so.

## Step 0: the size against the pilot (21 November 2026, about 10:58 PM Central, before anything is built)

DESIGN-2.md, section 9, step 0, by [repository path removed for blind review] from the pilot's analysis over the 32 open models
([a job number removed for blind review]; output [repository path removed for blind review]). Over the 209 model and category cells that read the
specifications, the familiar brands' true spread within a category (the variance of their values minus the mean
squared standard error, its square root) has a median of 0.31 log-odds, against the simulation's 0.26, so the pilot's
brands lie further apart than the simulation assumed (ratio 1.19), not half as far. The within-category reliability of
the pilot's values (800 lists a category, median standard error 0.17) has a median of 0.76 (95 of 209 cells at least
0.80; by category from 0.71 for televisions and smartphones to 0.85 for headphones). At the full design's 1,600 lists,
with a standard error near 0.12 at the brand's own band (precision_sim2.py), the same spread gives a within-category
reliability near 0.87 at the median and near 0.79 in the category with the smallest spread (televisions, 0.23). The
main version therefore stays at 1,600 lists a category.
