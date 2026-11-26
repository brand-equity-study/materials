# Machine-based brand equity: the pilot's analysis plan ([project record removed for blind review], [issue number removed for blind review])

[a team's name removed for blind review], written on 20 November 2026 between about 11:30 PM and midnight Central, before any item of the pilot was
built and before any model answered. The design is Fable's ([repository path removed for blind review], read whole); this plan fixes
what that design leaves open, states the measures and their criteria, and adds the convergence section that [a person's name removed for blind review]
asked for (ROADMAP.json, `framework.measure.families`). Its SHA-256 is recorded in `ANALYSIS-PLAN.sha256` in the commit
that adds it. A change after that commit is an amendment: it is dated, it says whether any answer existed when it was
written, and it never replaces the text above it.

## 1. Why a new measure

The brand-level analysis ([repository path removed for blind review]) measured a brand's machine-based equity as its
share of recommendations with names shown minus its share with names hidden, on the corpus tables. Four properties of
those tables limit that number. Each familiar brand sits on one fixed product, so the name and the product's appeal are
confounded. The best product always has an invented name, so the familiar brands' gains in a table add up to the
invented product's loss. [a team's name removed for blind review] found that the products of 50 of the 73 brands are picked in under 2 per cent of
names-hidden answers, so most brands start near a floor. And a brand in one model rests on 20 answers per table and
condition, which gives a standard error of about 13 points. The pilot removes the first three by design, because names
move across products at random, and reports the fourth as a reliability.

## 2. The measures, and which this pilot provides

[a person's name removed for blind review]'s ruling (about 11:19 PM Central): the conjoint is one way to measure machine-based brand equity, among several
that mirror the families of consumer brand equity measures. Each family's machine counterpart, its source in this
project and whether the pilot provides it:

| family | consumer source | machine counterpart | where it comes from | in this pilot |
|---|---|---|---|---|
| blind test | Allison and Uhl 1964 | share with names shown minus names hidden, same prompts | the corpus and the reruns (brand-level analysis); the pilot's randomized blind gap (arms 1 and 2) | yes, both |
| choice-based | Kamakura and Russell 1993; Swait, Erdem, Louviere and Dubelaar 1993; Park and Srinivasan 1994; Srinivasan, Park and Chang 2005 | the brand intercept relative to invented names (MBBE), as log-odds, share premium and equalization price | the pilot's arm 1 | yes (the proposed standard) |
| survey scales | Yoo and Donthu 2001 | the model's 1 to 7 rating of one product, named against unnamed; the audit's ratings of inferred quality, credibility and associations ([project record removed for blind review]) | arm 4; the audit when the open panel has answered it | arm 4 yes; the audit later |
| commercial trackers | Kantar BrandZ; the Brand Asset Valuator (Mizik and Jacobson 2008) | the audit's components tracked across models and releases ([project record removed for blind review], [project record removed for blind review]) | the audit | later |
| salience and consideration | Nedungadi 1990 | how often the model names the brand unprompted, with no list ([project record removed for blind review]) | [project record removed for blind review] | later |
| price premium | Aaker 1996 | the premium at which the brand's share in a set of otherwise equal products returns to one in five; the equalization price of the choice model | arm 5; arm 1 | yes |
| outcome | Ailawadi, Lehmann and Neslin 2003 | the share premium under consumers' own requests (A3) | [a team's name removed for blind review]'s requests, when the open panel has answered them | later |
| inside the model | none | the brand's position on the model's quality direction, the probability of the brand's letter, and related reads ([project record removed for blind review]) | [project record removed for blind review] | later |

The convergence analysis (section 7) uses every counterpart that exists for the same models when it runs, and is run
again when each counterpart marked "later" arrives.

## 3. The design, with the decisions that DESIGN.md leaves open

Everything not stated here follows DESIGN.md section 6.

### 3.1 Categories, requests and names

| category | request, wording 1 (the corpus's) | request, wording 2 (same budget, another use) | names (6 familiar, then invented: the corpus's first) |
|---|---|---|---|
| laptops | a reliable laptop for everyday work and browsing, budget around $600-800 | a laptop for a small business's spreadsheets and video calls, budget around $600-800 | Apple, Dell, HP, Lenovo, ASUS, Acer; Zentria and one new |
| over-ear headphones | over-ear noise-cancelling headphones for commuting and focus work, budget $150-300 | over-ear noise-cancelling headphones for long flights and working from home, budget $150-300 | Sony, Bose, JBL, Sennheiser, Audio-Technica, Beyerdynamic; Sonaray and one new |
| wireless earbuds | wireless earbuds for commuting and workouts, budget $50-150 | wireless earbuds for phone calls and the daily commute, budget $50-150 | Apple, Samsung, Sony, JBL, Beats, Jabra; Vynex and one new |
| running shoes | daily training running shoes with good cushioning, budget $100-160 | running shoes for half-marathon training, budget $100-160 | Nike, Adidas, ASICS, Brooks, HOKA, New Balance; Stridewell and one new |
| coffee makers | a coffee maker that makes excellent coffee, budget $50-150 | a coffee maker for a busy household's mornings, budget $50-150 | Keurig, Mr. Coffee, Nespresso, Breville, Cuisinart (5 familiar); Brevara and two new |
| smartphones | a smartphone with a great camera and long battery life, budget $300-500 | a smartphone for a parent who takes many photos and needs it to last all day, budget $300-500 | Apple, Samsung, Google, Motorola, OnePlus (5 familiar); Aurem and two new |
| televisions | a 55-65 inch TV for movies and streaming, budget $500-800 | a 55-65 inch TV for sports and gaming, budget $500-800 | Samsung, LG, Sony, Vizio, Insignia (5 familiar); Vistara and two new |

The coffee request drops the corpus's word "drip", because Keurig and Nespresso sell pod machines (DESIGN.md 6.1).
The ten new invented names are chosen by the builder and kept only when a web search and the four corpora of
`OSF/scripts/brand_frequency_scanner.py` (through the same infini-gram service) return no company or product of that
name in the category; the seven corpus names get the same check, and a name that fails is replaced and the
replacement recorded.

### 3.2 Profiles

Three attributes of three ordered levels each, written without any maker's product-line or feature name; a rating of
4.2, 4.4 or 4.6 stars with 500 reviews for every product; a price of four levels. Better levels are listed last.

| category | attribute 1 | attribute 2 | attribute 3 |
|---|---|---|---|
| laptops | memory: 8, 16, 32 GB | storage: 256 GB, 512 GB, 1 TB | battery life: 8, 11, 14 hours |
| over-ear headphones | battery life: 20, 30, 40 hours | weight: 320, 280, 240 g | noise reduction: 20, 25, 30 dB |
| wireless earbuds | battery life per charge: 5, 7, 9 hours | water resistance: IPX4, IPX5, IPX7 | noise reduction: 15, 20, 25 dB |
| running shoes | weight: 300, 270, 240 g | rated durability: 300, 400, 500 miles | energy return: 55, 60, 65 per cent |
| coffee makers | water reservoir: 40, 60, 80 oz | time to brew one cup: 90, 60, 45 seconds | brew sizes: 2, 4, 6 |
| smartphones | storage: 128, 256, 512 GB | battery: 4,000, 4,500, 5,000 mAh | main camera: 12, 48, 64 MP |
| televisions | screen size: 55, 60, 65 inches | refresh rate: 60, 120, 144 Hz | peak brightness: 400, 600, 800 nits |

Price levels: the budget's range cut into four equal parts, each level at the middle of its part, rounded to the
nearest whole dollar and then less one cent (laptops $624.99, $674.99, $724.99, $774.99). A set is redrawn when one
profile is at least as good as another on all three attributes, the rating and the price, and better on one, or when
two profiles are identical.

### 3.3 Arms (items a model)

1. Names shown: 800 sets a category (5,600). In each set, five of the category's eight names are drawn without
   replacement and assigned to the five profiles by a random permutation; the display order and the letters are two
   further independent permutations, as in Study 2.
2. Names hidden: the same 800 sets with the corpus's labels ("Name: Product A", "Brand: Brand A", by display letter),
   same order and letters (5,600).
3. Repeat: 200 of the shown sets a category, drawn at random, under a new id (1,400).
4. Single-product rating: each of the 8 names and one unnamed version, on 10 profiles a category, in 2 wordings
   (1,260), under a system prompt that asks for one whole number from 1 to 7 on the first line.
5. Direct price premium: for each of the 39 familiar brand and category pairs, five products with identical
   specifications (the middle level of each attribute, 4.4 stars) and four rivals drawn from the category's other seven
   names, 10 draws at each of five premium levels (1,950). The rivals share one price, and the brand is priced 10 per
   cent below, equal to, or 10, 20 or 30 per cent above them, every price inside the budget. Laptops' budget ($600 to
   $800) cannot hold a spread from -10 to +30 per cent, so laptops use -5, 0, +5, +15 and +25 per cent around $632.
   This is a decision of this plan, not of DESIGN.md.

Total 15,810 items a model. In arms 1 to 3, each set receives one of the 16 combinations of the four corpus system
prompts, two layouts (the corpus's block for each product, and one table) and the two request wordings, 50 sets each.

### 3.4 Gates (each refuses a build; each is tested with a planted fault and a clean control)

The balance table (name by attribute level, price level, rating, display position and letter; the build is refused
when a cell departs from its expected count by more than 25 per cent of that count, the tolerance chosen here); no
dominant or identical profile in any set; [a team's name removed for blind review]'s gate b ([repository path removed for blind review] deny list: no brand, product-model
token, trademarked feature name or advertising text in a names-hidden prompt, with the pilot's new names added); gate
c (no prompt names the best product or prints a utility or quality score); every price inside the stated budget; ids
unique; every item has the ten fields that the [a computing cluster's name removed for blind review] runner requires.

## 4. Estimation

1. Letters are read with [repository path removed for blind review]; ratings in arm 4 with the `rating` function of
   [repository path removed for blind review]. An answer without a letter is left out of the choice models and counted.
2. **The primary estimate.** For each model and category, a conditional logit on the shown sets (arm 1): two dummies
   for each attribute (the lowest level the reference), the rating (linear), log price centered within the category,
   four position dummies, four letter dummies, seven name dummies and one term for familiar names times centered log
   price. MBBE(b, c, m) is the name's coefficient minus the mean coefficient of the category's invented names.
   Departure from DESIGN.md 6.4 step 4, which fits arms 1 and 2 together: the primary fit uses the shown sets alone,
   so that the attribute terms are those that the model applies when names are shown; the joint fit, with terms for
   shown times each attribute, price and rating, is reported as a check of whether names change the reliance on
   specifications.
3. **Units.** Log-odds; the share premium, the predicted share of a product with MBBE in a set of five products with
   equal specifications whose other four have the invented names' mean intercept, minus 20 per cent; the price equivalent,
   exp(MBBE / |beta_price|) - 1, only where the price coefficient's interval lies below zero; the rating equivalent,
   MBBE / beta_rating, only where the rating coefficient's interval lies above zero.
4. **The randomized blind gap**, for each name: the share of shown sets in which the product holding the name was
   picked minus the share of the hidden twins in which the same product was picked.
5. **Arm 4:** the mean rating of each name minus the unnamed version's mean on the same profiles and wording.
   **Arm 5:** the brand's share at each premium level, and the premium at which its share equals 20 per cent (linear
   interpolation between the two levels that bracket it; reported as "beyond the range" otherwise).
6. **Intervals:** a bootstrap over sets (1,000 draws, seed 20261120), refitting the logit in every draw; across brands
   and models, a two-way bootstrap that resamples brands and models.

## 5. Reliability criteria (fixed now)

1. Split-half: 1,000 random splits of each category's 800 shown sets into halves; MBBE from each half; the
   correlation over the 39 familiar brand and category pairs within a model, Spearman-Brown corrected. **The measure
   is called reliable for a model when this is at least 0.80.** The paper reports how many of the models meet it.
2. The signal share: 1 minus the mean squared standard error over the variance of MBBE across the familiar pairs.
3. Repeat (arm 3): the share of repeated prompts with the same pick and Cohen's kappa; the correlation of MBBE between
   the first and the repeated run of those sets.
4. Wording: a pooled fit with a brand-by-factor term for system prompt, layout and request wording; variance
   components after the squared standard errors are subtracted. **Stable across a factor when the brand-by-factor
   variance is less than half the brand variance**; when it exceeds the brand variance, the paper describes the
   measure as conditional on that factor.

## 6. Validity criteria (fixed now)

1. **Known groups.** The mean MBBE of the familiar names is above zero, with its interval above zero, in a model for the
   paper to say that the model favors familiar names over invented ones in this design; the new invented names do not
   differ from the corpus's invented names (interval of the difference includes zero) unless a model has learned the
   published ones, which is then reported.
2. **Prediction of held-out sets.** On a random 20 per cent of each category's sets, the fit with name terms has a
   higher log-likelihood than the fit without them. Criterion: in at least 8 of the 10 models.
3. **Prediction of the corpus tables with no new parameter.** For the corpus tables that the open models answered (the
   Study 1 rerun and the strictly better build), each product's predicted names-shown share is proportional to its
   names-hidden share times exp(MBBE of its brand), as DESIGN.md 5.2 item 2 states (14 tables primary, 20 secondary).
   Criterion: the mean absolute error of that prediction is lower than that of "names change nothing", with the
   interval of the difference below zero, pooled over models.
4. **Discriminant.** Correlations of MBBE with frequency in the four public corpora, page views, coded and consumer
   familiarity and a published brand value (the columns of `brand_equity.csv`), raw and corrected for MBBE's
   reliability. The paper may say that a strong relation is ruled out only when the corrected interval lies inside
   -0.5 to 0.5; with 39 pairs it cannot say that there is no relation.
5. **The step and the slope (H8).** The step is the known-groups contrast; the slope is MBBE on log frequency among the
   familiar names, with brands as clusters.
6. **Independence from the product.** The correlation between a name's MBBE and the mean names-hidden share of the
   profiles that it met should be near zero (interval includes zero); the position and letter coefficients are
   reported beside the name coefficients.

## 7. Convergence of the measures

As Datta, Ailawadi and van Heerde (2017) compared consumer-based with sales-based brand equity, the paper tests
whether the machine counterparts of section 2 agree. The unit is a brand in a category in a model.

1. A correlation table of every pair of counterparts available for the same models: MBBE, the randomized blind gap, the
   arm 4 rating difference, the arm 5 premium, the corpus-table blind gap (`brand_model_equity.csv`, open models), and,
   when they exist, the audit's components, unprompted naming and the share premium under real requests. Each cell
   gives the pooled correlation over brand-model cells with a two-way interval (brands and models resampled), and the
   correlation within models averaged over models.
2. Each correlation is also given corrected for the two measures' reliabilities (Spearman 1904), where each measure has
   one (split halves for the pilot's measures; for the corpus-table gap, random halves of its 20 answers a cell).
3. A multitrait-multimethod reading (Campbell and Fiske 1959): agreement between methods within a model against
   agreement between models within a method.
4. **Criterion.** Two counterparts converge when their pooled corrected correlation is positive with its interval above
   zero; strongly when it is at least 0.5. MBBE and the randomized blind gap come from the same answers, so their
   agreement is reported and not counted as convergence.

## 8. Before the full run

1. The analysis script is first run on simulated answers with known intercepts (a multinomial logit with the design's
   assumptions, 40 replications). It must recover them: correlation between true and estimated MBBE of at least 0.9 and
   coverage of the 95 per cent intervals between 90 and 98 per cent. A script that fails is fixed before any real answer
   is read.
2. The first job, one category on two models, is read by hand before the rest. The run is stopped and the design
   changed when the names-hidden picks ignore the specifications (fewer than two of the three attributes have a
   coefficient in the expected direction with its interval excluding zero), when more than 2 per cent of answers have
   no letter, or when one display position or one letter takes more than 80 per cent of picks.

## 9. What is primary

Primary: MBBE in the three units for each brand, category and model, its split-half reliability, and the convergence
table of section 7. Secondary: the randomized blind gap, arms 4 and 5, wording stability, the predictions. Exploratory,
labelled so: anything not named in sections 4 to 8, including a hierarchical model pooled over categories with a scale
for each, and any result that drops Apple in laptops (always reported beside the same result with Apple in laptops).

## Amendment 1 (21 November 2026, about 12:20 AM Central; no item built and no answer existing when it was written)

[a team's name removed for blind review] found that three of the corpus's invented names (Novatech, Primebook and Sonance) are real companies that the
models know ([repository path removed for blind review]). The seven corpus names that the pilot uses were claimed by none
of the four Claude models in the audit's recognition items (`RECOGNITION-claude.md`); the ten new names have no
recognition answers yet, and the open models have answered none.

1. **Arm 6, recognition.** The pilot adds the audit's recognition question for each of the 56 name and category pairs,
   in both of the audit's wordings, two trials each (224 items a model; 16,034 in all), with the audit's system prompt
   and wording taken from [repository path removed for blind review]. The answers are read with the audit's own reader.
2. **The invented reference.** For each model, an invented name that the model claims to know in at least half of its
   four recognition answers is left out of that model's invented reference, and MBBE for that category is computed
   against the remaining invented names. If every invented name of a category is claimed, the reference keeps all of
   them and the category is flagged. Every result is also reported with the reference of section 4, so that both
   versions are visible.
3. **A familiar name that a model does not know** (claimed in fewer than half of its answers) is reported with its MBBE
   and marked; it stays in the analysis.

## Amendment 2 (21 November 2026, about 10:15 AM Central; written after [a team's name removed for blind review] read the first job's answers, laptops on Llama 3.1 8B and Ministral 3 14B, [a job number removed for blind review], and before any answer in the other six categories or from any other model)

The first job (section 8.2) was read by hand: the stop rules are in [repository path removed for blind review],
and the answers that were read are in `reading_sample.jsonl` beside it. No estimate of MBBE was computed from it.

1. **The specifications rule applies to each model and category, not to the design.** Ministral 3 14B followed all
   three attributes, the rating and the price with names hidden, and its picks were spread over positions (15 to 26
   per cent) and letters (18 to 23 per cent). Llama 3.1 8B followed none of the three attributes and picked the first
   product shown in 70 per cent of its answers, which shows that this model does not read these tables, not that the
   design fails. The pilot therefore goes on. A model and category in which fewer than two attributes have a best-level
   coefficient above zero, with its interval excluding zero, is reported by itself, with its MBBE, and is left out of
   the pooled reliability, validity and convergence analyses; the paper states how many model and category cells this
   leaves out.
2. **What counts as claiming to know a name (changes Amendment 1, item 2).** In the first job, Llama 3.1 8B answered
   the second recognition wording with "Yes" followed by "I couldn't find any information about a brand called
   Zentria", and Ministral 3 14B claimed each invented laptop name in two of its four answers, giving a different
   country each time (Zentria: Taiwan, then Canada; Vormida: Spain, then Italy). Under Amendment 1 both invented names
   would have left both models' references. From now on, an answer counts as a claim only when it says yes and names a
   country, and an invented name leaves a model's reference only when the model claims it in at least three of its
   four answers. The four Claude models claimed each of the three real companies (Novatech, Primebook and Sonance) in
   four of four answers or, for Haiku 5.5 and Sonance, three of four, so the new rule still removes them.
3. **What is unchanged.** Items, arms, models, estimators and every criterion of sections 5 to 8. The recognition
   shares under Amendment 1's rule are also reported, so that both versions are visible.

## Amendment 3 (21 November 2026, about 8:35 PM Central; written by the coordinator, dell-tower/t8y6, at [a person's name removed for blind review]'s question; the pilot's answers existed for most open models, and no estimate of MBBE had been read by anyone: the full analysis [a job number removed for blind review] stopped before estimating, and a first look on three models that the coordinator started at about 8:16 PM had not been read when this was written)

[a person's name removed for blind review] asked at about 8:30 PM Central whether the measure compares brands within a category, the same brand across
categories, the brands across assistants, and the brands against the real world. Within a category is the design
itself (each brand against its category's fictitious names), and the real world is section 6.4. This amendment adds
two secondary analyses.
1. **The same brand across categories.** Four brands sit in more than one category: Apple (laptops, wireless earbuds,
   smartphones), Samsung (wireless earbuds, smartphones, televisions), Sony (over-ear headphones, wireless earbuds,
   televisions) and JBL (over-ear headphones, wireless earbuds). For each brand and model, its price equivalent in
   each of its categories and the difference between each pair of categories, with a bootstrap interval (sets
   resampled); across models, the share of models in which the brand ranks above its category's median in every one of
   its categories. Four brands are too few for a correlation, so this result is descriptive.
2. **Across assistants.** Each brand and category's MBBE in each model goes to [repository path removed for blind review]
   ([project record removed for blind review]) for the spread between models; the difference between groups of models (the Claude models, the GPT
   models through Codex and the open models) comes from a bootstrap with models resampled within their group, once each
   group has answered the pilot; and the agreement of the 39 brands' ranks between each pair of models (Spearman, with
   the multitrait-multimethod reading of section 7.3).
What is unchanged: items, arms, models, the estimator, and every primary measure and criterion of sections 4 to 9.

## Amendment 4 (21 November 2026, about 8:40 PM Central; the coordinator, at [a person's name removed for blind review]'s words; no estimate of MBBE had been read by anyone, as for Amendment 3)

[a person's name removed for blind review], about 8:38 PM Central: "a manager would like to know 'how much my brand matters for this model? does gpt vs
claude value my own brand differently?'" So the paper reports, for each of the 39 brand and category pairs, the price
equivalent in each model with its interval, and the difference in price equivalent between each GPT model and each
Claude model and between each group's mean (Claude, GPT through Codex, open models), with a bootstrap interval (sets
resampled within each model). The text gives a manager's reading of one brand in plain words; the full table goes to
the Web Appendix. For this, arms 1 and 5 (the shown sets and the direct premium) are run first on the GPT models through
Codex and on the Claude models through a subscription to the Claude command line; arms 2 to 4 follow when there is room.
What is unchanged: items, the estimator, and every primary measure and criterion.
<!-- prose-lint: ok -->

## Correction to the times of Amendments 3 and 4 (21 November 2026, 8:22 PM Central, read from the clock)

The coordinator wrote the times in the headings of Amendments 3 and 4, and in their quotations of [a person's name removed for blind review], from an
estimate about 25 minutes ahead of the clock ([a team's name removed for blind review] noticed). The commit times are the record: Amendment 3 was
committed at 8:09 PM ([commit removed for blind review]) and Amendment 4 at 8:10 PM ([commit removed for blind review]); [a person's name removed for blind review]'s two questions came a few minutes
before each. The coordinator read the first look at the three models at about 8:14 PM ([a team's name removed for blind review]'s status, [commit removed for blind review]),
after both commits, so both amendments were written before any estimate was read. Nothing else changes.
