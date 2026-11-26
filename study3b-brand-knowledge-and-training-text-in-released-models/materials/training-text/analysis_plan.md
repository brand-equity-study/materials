# [project record removed for blind review], brands in OLMo 2's public training data: the analysis plan

[a team's name removed for blind review], 21 November 2026, about 5:45 PM Central. [project record removed for blind review] ([issue number removed for blind review]; [repository path removed for blind review]). Written and
committed before any count of this step. The counts that [a team's name removed for blind review]'s part D already made ([repository path removed for blind review], plan
in [repository path removed for blind review], Amendment 2) are reused as they are, and none of them is made again.

## The question

For each familiar brand of the 34 corpus tables, what does OLMo 2's training text say around the brand, and is a
brand's equity in OLMo 2 and in the other open models positively correlated with that text, beyond how often the brand
appears? Part D found no correlation between OLMo 2 7B Instruct's equity and how often a brand appears near quality,
reliability or recommendation words (parts/d.json). Part D's association counts are estimates, because infini-gram
samples an AND query whose clauses have more than 500,000 matches. This step measures the text itself, from a random
sample of each brand's occurrences: the sentiment of the surrounding text, whether it recommends the brand's product,
and whether it is promotional text or a review. [a team's name removed for blind review] found that OLMo 2 7B's cost is near zero through pretraining and
rises with SFT and DPO ([a job's name removed for blind review]), so the step also counts the brands in OLMo 2 7B's released post-training data.

## The route (checked at about 5:42 PM Central, before this plan)

- infini-gram's public API (https://api.infini-gram.io/, free, no key) holds `v4_olmo-mix-1124_llama`, OLMo 2's
  pretraining mix (olmo-mix-1124, about 3.08 billion documents and 4.58 trillion tokens), and
  `v4_olmo-2-1124-13b-instruct_llama`, labelled by OLMo 2 13B Instruct's name (about 3.16 billion documents and 4.61
  trillion tokens; the site does not list its parts). No index of the mid-training mix (dolmino-mix-1124) exists.
- A `count` query is exact for one n-gram ("Sony": 36,514,987 in the pretraining mix). An AND query is not usable for
  frequent brands: "Sony AND recommend" returned 0 with the approximate flag.
- A `find` query returns, for each of the index's shards, the range of suffix-array ranks that hold the brand, and
  `get_doc_by_rank` with a rank in that range returns the text around that occurrence (with `max_disp_len` 200, 100
  tokens before the brand and 100 after) and the document's source path and URL. A test on Breville returned a Black
  Friday deals page that lists a Breville espresso machine.
- OLMo 2 7B's post-training data are public on Hugging Face and not gated: `allenai/tulu-3-sft-olmo-2-mixture` (SFT)
  and `allenai/olmo-2-1124-7b-preference-mix` (DPO), six parquet files each.

## Brands

The 73 familiar brands of the 34 corpus tables, in the forms that part D used ([repository path removed for blind review]), and
the corpus's invented names, whose counts are reported only (they are the reference of every equity).

Batches, as the issue asks. The pilot is ten brands, fixed now by a rule on part D's counts of each brand alone in the
pretraining mix: the brand nearest each of the 5th, 15th, ..., 95th percentiles of the log count, and at the 35th and
75th percentiles the nearest brand that part D flags as a common word, so that the pilot tests the coding of the
brand's sense. The ten are De'Longhi (18,473), ASICS (125,758), The North Face (191,329), Insignia (430,182, a common
word), Netgear (821,962), Seagate (1,445,981), Herschel (1,933,122), Beats (4,520,046, a common word), Nike (11,073,599)
and Sony (36,514,987). Then the other 63.

## The sample of occurrences

- For each brand, 200 occurrences drawn at random in `v4_olmo-mix-1124_llama`, each with equal probability: a rank is
  drawn uniformly from the union of the brand's rank ranges over all shards (numpy's default generator, seed 20261120
  and the brand's position in the sorted list). Each draw is one occurrence, so a document that holds a brand many
  times can be drawn more than once, as it was seen more than once in training. The share of distinct documents and
  of distinct URLs is reported.
- For each draw: the 200-token window, the shard, the rank, the document's index, its source path (which part of the
  mix: dclm, the code, the papers, the encyclopedia and so on) and its URL.
- Every call is retried up to three times; a draw whose window does not contain the brand's tokens is replaced by a
  new draw and counted. More than 2 per cent of such windows in a brand stops the batch.

## The coding of each window

Each window is coded by three open-weight judges from three developers on [a computing cluster's name removed for blind review], through
[repository path removed for blind review] with each model's own chat template and defaults ([project record removed for blind review]): Qwen 3 32B
(Alibaba), Gemma 4 26B A4B (Google) and OLMo 3.1 32B (Allen AI). The judge sees the brand, its category, the window and
the URL, and answers four questions in a fixed JSON form (CODEBOOK.md, committed with this plan):

1. sense: does the window use the word for the brand (yes, no)?
2. sentiment toward the brand or its product: positive, neutral, negative or mixed.
3. recommends: does the text recommend the brand or one of its products to the reader (yes, no)?
4. kind of text: promotional (written to sell: the brand's or a seller's pages, advertisements, deals, press
   releases), review (a person or a publication that judges the product), news or information, listing (a catalogue,
   a list of products or specifications without judgement), or other.

The label of a window is the answer that at least two of the three judges give; a window with no majority on a question
is left out of that question's shares and counted. Each result is also reported under each judge alone.

Blind human coders code a stated random sample of 300 windows (30 from each pilot brand), without the judges' labels,
before any result is reported; their agreement with the majority label and with each judge is reported (percentage
and Cohen's kappa for each question). Who codes is [a person's name removed for blind review]'s decision; until the human coding is in, the results are
marked as coded by models only.

## The measures, for each brand

Among the windows coded as the brand's sense:
- **net sentiment**: the share positive minus the share negative;
- **recommendation share**: the share that recommends the brand or its product (the judges);
- **promotional share**: promotional windows as a share of promotional and review windows;
- the review share and the share of each kind among all windows, and the recommendation share by part D's fixed word
  list (recommend, recommended, recommendation, worth it, favorite, go-to) read in the window, as a check that uses no
  judge.

And for each brand: the **brand-sense share** (windows coded as the brand's sense among all windows); the **estimated
mentions**, part D's count of the brand alone times the brand-sense share; and the distribution of the windows over
the mix's sources. Each share has an interval from the 200 windows (Wilson).

The post-training data, for each brand: the mentions in the assistant turns of the SFT mixture; in the DPO mixture,
the mentions in the chosen and in the rejected responses, and the **preference push**, (chosen minus rejected) over
the pairs that mention the brand in either response. Counted with a word-boundary match of the brand's forms by a CPU
job on [a computing cluster's name removed for blind review], which downloads the twelve parquet files there (a job file through [a team of the project, name removed for blind review]).

## The equities

- Primary: OLMo 2 7B Instruct's equity of each brand from part D (parts/d.json, model `olmo2-7b-instruct-full2`: the
  probability of the brand's own product with the names shown minus with them hidden, in Study 2's full2 build).
- Secondary: each open model's equity of each brand from [a team's name removed for blind review]'s brand-level analysis (brand_model_equity.csv, from
  the newest export of the open panel; all 32 models once the panel's runs are complete), each model alone and their
  mean; and OLMo 2 7B's equity at its training checkpoints (below).

## The tests

- Primary, on OLMo 2 7B Instruct: the Spearman correlation between equity and each of the three primary measures (net
  sentiment, recommendation share, promotional share), partial on the log of the estimated mentions, with a bootstrap
  over brands (10,000 draws, seed 20261120) for the interval and a two-sided P; Holm across the three. The unit of
  inference is the brand ([project record removed for blind review]).
- The same three correlations for each open model and for the open models' mean, reported beside the primary ones.
- With controls ([project record removed for blind review]): a regression over brands of equity on the three measures and the log estimated
  mentions, with the controls in [repository path removed for blind review] (monthly Wikipedia views, consumer
  familiarity, published brand value), with a bootstrap over brands. Market share and independent quality ratings are
  not in the repository. A source for each is a decision for [a person's name removed for blind review] (below); with an approved source, each value is
  recorded with its URL and date, and the controls regression adds them on the brands it covers, with the coverage
  reported. Without one, the report says that these controls are missing.
- The checkpoints: from [a job's name removed for blind review]'s item-level outputs ([a job number removed for blind review], [repository path removed for blind review][a job number removed for blind review]), each brand's equity at each
  OLMo 2 7B checkpoint that reads the tables (reading at least 0.40: 3,896 billion tokens, the released base model,
  SFT, DPO and Instruct), by part D's definition on dom2's tables. Two analyses: at each checkpoint, the Spearman
  correlation between equity and the log estimated mentions and each primary measure; and the Spearman correlation
  between each brand's change from the base model to Instruct and the post-training measures (SFT mentions and the
  preference push). If the item-level outputs do not hold each letter's probability, this part is reported as not
  computable and why.
- The 13B index minus the pretraining mix gives each brand's mentions in OLMo 2 13B's later stages; it is reported as
  a description only, because the 13B model is not among the models whose equity is measured.

## How the results are worded

As correlations between what the training text says and the equity ([project record removed for blind review]). A causal word is used only
where [a team's name removed for blind review]'s planted study ([project record removed for blind review], question 2) moves equity in the same direction for the same kind of text. A null is
reported as a null with its interval, beside part D's.

## Pilot checks (the coordinating session reads them before the other 63 brands)

The pilot's windows (2,000) are read: 50 at random by [a team's name removed for blind review], for whether the window holds the brand and whether the
URL and source are recorded; each judge's share of answers in the JSON form (stop if below 98 per cent); the
agreement among the three judges on each question (Fleiss' kappa); the brand-sense share of Insignia and Beats against
a reading of 20 of their windows each.

## Decisions for [a person's name removed for blind review]

1. Who are the blind human coders of the 300 windows ([project record removed for blind review])?
2. Market share and independent quality ratings ([project record removed for blind review]): which sources, and whether to spend on a paid one
   (for example Statista or Consumer Reports)? Free sources cover only part of the categories: the market-research
   firms' public press releases for shares (phones, televisions, laptops) and published test scores for quality (a few
   categories).

## Amendment 1 (21 November 2026, about 5:51 PM Central, before any count of this step)

From [a team of the project, name removed for blind review] at 5:50 PM, with [a person's name removed for blind review]'s two decisions.

1. **No human coders ([project record removed for blind review]).** [a person's name removed for blind review], at about 5:42 PM Central, for every coding in this paper, verbatim:
   "hand coding: no one will. we will do llm-as-judge with kappa." The 300 windows of the section on the coding (30
   from each pilot brand, drawn at random) are coded by one reference reader instead of people: Claude Opus 5.5
   through the Claude CLI on the subscription, through [a team's name removed for blind review]'s [repository path removed for blind review], which removes the calling
   chat's thinking and effort settings from the CLI's environment and records the computer, the CLI version and the
   values in every results line. The reader sees the same prompt (CODEBOOK.md) and none of the judges' labels. Reported:
   Fleiss' kappa among the three open-weight judges for each question, Cohen's kappa of each judge and of the majority
   label against the reference reader, and each claim under each judge. The words "Blind human coders" and "Who codes
   is [a person's name removed for blind review]'s decision" above are replaced by this item.
2. **Nothing is bought ([project record removed for blind review]).** The controls are those of [a team's name removed for blind review]'s brand-level analysis ([commit removed for blind review];
   [repository path removed for blind review]: monthly Wikipedia views, consumer familiarity, published brand
   value) and free sources where they exist. Market share and independent quality ratings are covered only where a free
   source exists: each value is recorded with its source's address and date, the coverage of each control (brands and
   categories) is reported, and the controls regression with them runs on the brands it covers. Decision 2 above is
   settled by this item.
3. The brands' forms are those of [repository path removed for blind review] (part D's 73 brands); [commit removed for blind review] named
   brand_list.json, which is question 3's list of 467 names.

## Amendment 2 (21 November 2026, about 5:57 PM Central, before any count of this step)

From [a team of the project, name removed for blind review]'s ruling at 5:56 PM to [the project's teams removed for blind review]: the promotional share is measured by [a team's name removed for blind review]'s [a job's name removed for blind review]
(training PLAN.md, change 21) with a published classifier that anyone can rerun, independent of our prompts.

1. **The promotional share's primary measure is WebOrganizer's.** For each brand: up to 100 distinct documents of
   OLMo 2's pretraining mix that contain the brand's name, each as the 1,000 tokens around the match, labelled by
   WebOrganizer's format classifier without the URL (FormatClassifier-NoURL, at the revision that [a team's name removed for blind review]'s filters.py
   pins). Promotional means Product Page, Spam / Ads, About (Org.) or News (Org.); review means User Review. The share is
   promotional documents over promotional and review documents; a brand with fewer than 10 of the two has no share.
   These labels and shares are taken from [a team's name removed for blind review]'s output files of [a job's name removed for blind review] ([a job number removed for blind review]) as they are, and not recomputed.
2. **The judges' "kind" answer is the check**, reported beside the primary share. Agreement: across brands, the
   Spearman correlation between the two shares, on the brands with a share in both; and, on the documents that are in
   both samples (the same shard and document index), Cohen's kappa between WebOrganizer's label mapped to promotional,
   review or neither and the judges' majority label mapped the same way.
3. The judges stay primary for what WebOrganizer does not measure: the brand's sense, the sentiment and whether the
   text recommends the brand. The three primary measures of the tests are therefore net sentiment (judges),
   recommendation share (judges) and promotional share (WebOrganizer), with Holm across the three as before; the test
   of the promotional share is also reported without the brands that part D flags as common words, because
   WebOrganizer's documents are not coded for the brand's sense.

## Amendment 3 (21 November 2026, about 9:29 PM Central, after reading the pilot's coding and before any coding of the other 63 brands)

The pilot's checks (results/pilot/CHECKS.json and PILOT-READING.md; b5-02, [a job number removed for blind review], and the reference reader,
[commit removed for blind review]) found two faults in the instrument, which this amendment corrects for every window, the pilot's included.

1. **The brand's sense.** The open-weight judges coded another company or product with the same name as the brand: a
   Vauxhall Insignia, a cruise ship named Insignia, a real-estate firm and a cigar named Insignia (8 of Insignia's 30
   reference windows differ from the reference reader, which did not count them). Question 1 of CODEBOOK.md now names
   the study's category ("the {category} brand of our study") and says that another company, product or place with the
   same name is not the brand.
2. **A label written another way.** OLMo 3.1 32B answered "information" (107 windows) or "informational" (6) for the
   codebook's "news_or_information", so 5.8 per cent of its answers were unparsed, above the plan's 2 per cent stop.
   These two exact words are read as "news_or_information" for every judge (read_judges.py, SYNONYMS); nothing else is
   mapped. With them OLMo's parsed share is 99.85 per cent. The parsed shares without them are reported too.
3. **The pilot is coded again.** The three judges code the pilot's 2,000 windows with the amended codebook (b5-03,
   items pilot2, the same windows), and the reference reader codes the same 300 again (reference/pilot2). The first
   coding (items pilot, results/pilot) is kept as the record of the pilot and is not used in any estimate. The other
   63 brands are coded with the amended codebook only. The pilot checks are read again on pilot2 before the other 63
   brands are coded.

## Amendment 4 (21 November 2026, about 11:33 PM Central, after reading the pilot's second coding and before any coding of the other 63 brands)

The second coding (b5-03, [a job number removed for blind review]; results/pilot2/PILOT-READING.md) passed every parse check, and Amendment 3's
exclusion of namesakes worked (Insignia), but its wording "the {category} brand of our study" was read too narrowly:
the open judges coded Sony's televisions, games consoles and music as not Sony, because Sony's first category in the
corpus tables is cameras (the majority 0.20 against the reference reader's 0.83 on the same 30 windows), and the
majority's kappa against the reference on the brand's sense fell from 0.91 to 0.75. The step measures what the
training text says about the brand as a company, across its products.

1. Question 1 of CODEBOOK.md now reads: does the passage use the name "to mean the company {brand} that sells
   {category}, or any of that company's products in any category", and "no" for "a different company, product or
   place that only shares the name".
2. The pilot is coded a third time with it (items pilot3, the same windows; job b5-04), and the reference reader codes
   the same 300 again when the subscription's limit allows. The first two codings enter no estimate. The checks are
   read on pilot3 before the other 63 brands are coded.

## Amendment 5 (22 November 2026, about 2:16 AM Central, after reading the pilot's third coding and before any answer for the other 63 brands)

The third coding (b5-04, [a job number removed for blind review]; results/pilot3/PILOT-READING.md, [commit removed for blind review]) passed every check that the plan
reads: each judge answered in the codebook's form in at least 99.85 per cent of windows, and the majority's Cohen's
kappa against the reference reader on the brand's sense was 0.89. One fault is left. Qwen 3 32B and OLMo 3.1 32B coded
windows about the PlayStation as not Sony, although question 1 counts any of the company's products in any category,
so Sony's brand-sense share on the reference reader's 30 windows was 0.67 under the majority and 0.93 under the
reference reader. Gemma 4 26B gave 0.93, and its sense labels agreed with the reference reader at kappa 0.98 (Qwen 3
32B 0.87, OLMo 3.1 32B 0.74). The coordinator agreed at 2:15 AM Central.

1. The majority label stays primary for every question, as the plan says.
2. Every result is also reported with Gemma 4 26B's label on the brand's sense in place of the majority's, as a
   robustness row: the brand-sense share of each brand, and each measure that counts only the windows that use the name
   for the brand (net sentiment, recommendation share and the judges' kind of text), with every test of the plan.
3. Nothing else changes: the windows, the judges, the codebook, the reference reader's 300 windows and the tests. The
   other 63 brands are coded with Amendment 4's codebook (b5-05, items rest, SHA-256 3f92d59e...).

## Amendment 6 (22 November 2026, about 3:00 AM Central, after the 73 brands' measures were computed and before any test was read)

The tests are computed by analyze_b5.py ([commit removed for blind review]). It makes these choices, which the plan leaves open, and it was
committed and started before any of its results was read:

1. The open models' equity (the secondary equity) is computed from the newest export of the open panel, [a job number removed for blind review]'s
   Study 1 rerun (31 models), with brand_level.py's definition (the share of answers that pick the brand's product with
   names shown minus with names hidden, the brand's tables pooled), because brand_model_equity.csv holds the ten open
   models of the first brand-level results only. A model whose answers are read in under 90 per cent of the build's
   items is left out, under the paper's exclusion rule.
2. Each open model's three correlations use 2,000 bootstrap draws; the primary tests and the open models' mean use
   10,000.
3. The common-word brands are the ten that part D flags (parts/d.json, ambiguous).
4. A brand-sense share of zero is taken as half a window in the log of the estimated mentions, so that the log exists.
5. The judges' promotional share, the check of WebOrganizer's, follows WebOrganizer's rule: a brand with fewer than 10
   promotional and review windows has none.
6. The controls regression uses standardized variables, once with monthly Wikipedia views and consumer familiarity and
   once adding the published brand value, each on the brands that have every control.
7. The checkpoints of [a job's name removed for blind review] and the post-training counts ([a job number removed for blind review]) are analysed in a second step.

## Amendment 7 (22 November 2026, about 3:46 AM Central, after the results were read and after [a team's name removed for blind review]'s second reading)

[a team's name removed for blind review]'s second reading (results/b5/CHECK-LANE6.md, [commit removed for blind review]) recomputed every number from the inputs and found
that none of the conclusions changes. This amendment records what it asked for.

1. **OLMo 2 32B Instruct's equity.** analyze_b5.py held it from its first commit ([commit removed for blind review]), before any result was
   read, and part D's plan names it ([repository path removed for blind review], line 540), but this plan and Amendment 6 do not. It is
   therefore reported as a secondary equity beside the plan's own (OLMo 2 7B Instruct, each open model and their mean,
   and OLMo 2 7B's checkpoints), and the report states the plan's equities first.
2. **The agreement on the documents in both samples** (Amendment 2, item 2) is computed with the document as the unit:
   the first window of a document stands for it. [a team's name removed for blind review]'s files hold no shard, so the match is the brand and the
   document index, and a stricter version also needs the same address (b19-data-6's promo/docs.jsonl).
3. **Each judge alone and Gemma 4 26B's sense label** (the plan's coding section and Amendment 5, item 2) get every
   test, not only the three primary ones: the other equities, each open model, the checks, the controls regression and
   the checkpoints. Every version is computed from the windows without rounding.
4. **The exploratory row** added after the results were read is reported in the version that fits its reason, without
   the brands that have fewer than ten windows in the brand's sense, beside the version first reported, without part D's
   ten common-word brands. Both are exploratory and uncorrected.
5. **A brand with two products in a table** (Oral-B) counts an answer once in the open models' equity, as brand_level.py
   does: the brand is picked when either product is.
6. **Rows that the plan names** are added to the report: Fleiss' kappa among the judges on all windows and each judge's
   kappa against the reference reader, the recommendation share by part D's word list, the share of distinct documents
   and addresses and the windows' sources, and the coverage of each control. No search for a free source of market share
   or quality ratings has been made; the report says so, and that search is still owed.
