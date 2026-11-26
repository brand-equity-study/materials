# Analysis plan for the information-environment study ([project record removed for blind review], [issue number removed for blind review]) and the harness study ([project record removed for blind review], [issue number removed for blind review])

The terms follow [repository path removed for blind review], framework.layers_corrected ([a person's name removed for blind review], about 12:37 AM Central on 21 November 2026):
[project record removed for blind review] changes the information environment, what the model is shown (formats, labels, position, ratings), plus one setting
of the developer (the instructions); [project record removed for blind review] changes the harness, the software around the model (here, a search step). The
folder and the job files keep the name "harness" because jobs and queue entries already refer to them. Where the text
below, written before the correction, says that a harness passes or shows something, it means the information
environment that the harness passes to the model.

Written by [a team's name removed for blind review] on 20 November 2026, about 11:00 PM Central, and committed before any model answered any item of this
study. The source marks [S2] to [S29] are those of [repository path removed for blind review] A change after
results are seen is added at the end with its date, its time and its reason, and the text above it stays.

## The question

Machine-based brand equity is a property of the model ([repository path removed for blind review], "framework"); the harness of an assistant
decides which text reaches the model ([repository path removed for blind review]). This study holds the products fixed
and changes only what a harness would pass to the model, and measures the name gap in each case: how much less often
the model recommends the best product when the products show their names than when they do not. It asks which levers
of a harness change the gap: the format of the product data, a Sponsored label, the position of the best product, a
rating gap in its favor, and an instruction from the developer.

## The products

[a team's name removed for blind review]'s dominant sets ([repository path removed for blind review], the 30 tables of the build `dom2`): in each, the designated
best product is better than or equal to every other product on every displayed attribute and costs no more, and every
other product is strictly worse on at least one attribute or on price. The best product has an invented name in
the original arm; the other four have familiar names. Prices are [a team's name removed for blind review]'s equal-price rung (the best product's price
equal to the cheapest other product's). The request is the corpus's request line for each table ("I'm looking for
..."), and the system prompt is one of the corpus's four baseline paraphrases, which ask for the letter alone on the
first line.

## The arms

Each arm is rendered with names hidden ("Product A" of "Brand A") and with the original names; the two versions differ
only in the name and brand of each product. The reference arm is [a team's name removed for blind review]'s plain table with no added information.

| Arm | What the harness passes |
|---|---|
| plain | The reference: [a team's name removed for blind review]'s product blocks (name, brand, price, specifications, "Reviews: 500 reviews, 4.3 stars") |
| plain-info | [a team's name removed for blind review]'s information-supplied cell: the reference plus a 2-year warranty, a first-year failure or return rate of 2 per cent and 10 years or more on the market for every product, with the lab-testing sentence and the free-return clause in the request |
| feed-openai | Each product as an object of OpenAI's current product feed [S2]: item_id, title, description (the specifications), brand, price, availability, review_count and star_rating, accepts_returns |
| feed-openai-2025 | OpenAI's October 2025 feed [S3]: as above with its field names (product_review_count, product_review_rating), return_policy, and return_rate (2) |
| feed-google | Google Merchant Center product data [S12]: id, title, brand, price, availability, product_detail (the specifications), warranty (2:year) and a free product-level return; no rating, because the specification has no rating attribute |
| schema-org | schema.org Product markup as JSON-LD [S16 to S20]: name, brand, additionalProperty (the specifications), aggregateRating (4.3, 500), offers with price, a WarrantyPromise of 2 years and a free MerchantReturnPolicy |
| sponsored-familiar | The reference with the label "Sponsored" on one familiar product ([a team's name removed for blind review]'s swap partner for that trial) |
| sponsored-best | The reference with the label "Sponsored" on the best product |
| position-first, position-middle, position-last | The reference with the best product first, third or fifth in the list; the other products keep their order |
| rating-0.1, rating-0.3, rating-0.5 | The reference with the best product rated 4.4, 4.6 or 4.8 stars against 4.3 for the others, all with 500 reviews (Chu and Hou 2026 report that a 0.1-star gap removes a well-known brand's advantage at identical specifications) |
| instruct-listed | The reference with "Recommend only on the information listed." added to the system prompt |
| instruct-brand | The reference with "Do not consider brand reputation." added to the system prompt |

A format contains a fact only where it has a field for it (the brief: "same facts wherever a format has a field for
them"); no format has a field for the time on the market, and only the October 2025 OpenAI feed has one for a return
rate. So the format arms differ, as real feeds do, in which reliability facts reach the model. The facts are the same
for every product within an item, so no format favors the best product except through its name. In every format, each
product is introduced by "Product A:" and so on, so the letter that the answer gives maps to one product. Sixteen arms
in two name versions make 32 cells for each table and trial.

## Items

The build `h1` renders every cell of the 30 tables for trials 0 to 3; within one table and trial, every cell shares the
letters and the system prompt, and every cell except the three position arms shares the order of the products. [a team's name removed for blind review]'s
renderer (`study2_tables.py`) and refusing gates (`gates.py`) check the plain table of every item before it is changed;
[repository path removed for blind review] then applies the arm and refuses a build unless six checks pass on the rendered
text: (1) a names-hidden item shows no word of gate b's deny list and labels every product "Product L" of "Brand L";
(2) no item prints the words of gate c or names the best product's letter; (3) every product's price and every
specification value appear in that product's section; (4) the two name versions of an item differ only in the name and
brand fields; (5) the arm is present as built (one Sponsored label on the intended product, the rating, the position,
the instruction); (6) [a team's name removed for blind review]'s gates pass on the plain table that the arm starts from. Each check has a test with a
planted fault. The build is hashed before any model answers it.

## Models

- The open panel: every model of `models/open-models.tsv` (ten models from eight developers), all 30 tables
  and trials 0 to 3 (3,840 items a model), through [repository path removed for blind review] on [a computing cluster's name removed for blind review], in a job file that [a team of the project, name removed for blind review] submits.
- The Claude panel: Claude Haiku 5.5, Sonnet 5.5, Opus 5.5 and Fable 5.1, all 30 tables and trials 0 and 1 (1,920 items
  a model), through the Message Batches API at the provider's default settings, on [an account of the project removed for blind review]@preparacourse.com, and on
  [an account of the project removed for blind review] only after [an account of the project removed for blind review] refuses, under the 800-dollar cap that [a team of the project, name removed for blind review] shares among
  [the project's teams removed for blind review].
- Pilot first: two tables (the laptops 01 and earbuds 03 dominant sets, the tables of [a team's name removed for blind review]'s pilots), every cell,
  trials 0 and 1, on Claude Haiku 5.5 and Sonnet 5.5; I read every answer that does not pick the best product.

## Reading an answer

[a team's name removed for blind review]'s parser (`parse_answer.py`) reads the letter. Answers without a letter are counted and reported; a table enters
an arm's contrast for a model only if both name versions have at least one parsed answer. If more than 5 per cent of a
batch gives no letter, the batch stops until the cause is found.

## Outcomes and statistics

For a model m, a table t and an arm, s(names) is the share of parsed answers that pick the best product, over the
trials. The name gap is g(arm) = s(hidden) - s(original), in percentage points. The change that an arm makes is
D(arm) = g(arm) - g(plain), computed for each model and table and then pooled. Pooling weights every table equally
within a model and every model equally. Intervals come from the two-way cluster bootstrap of Study 2, which resamples
tables and models independently with replacement (10,000 draws, seed 20261120); the 95 per cent interval is the 2.5th
to 97.5th percentile, and the two-sided P value is twice the share of draws on the far side of zero, capped at 1.

The two panels are analyzed apart. In each panel, the primary contrasts are the 15 changes D(arm), Holm-corrected as
one family of 15. An arm is said to narrow the gap when D(arm) is below zero with a Holm P below 0.05, to widen it when
D(arm) is above zero with a Holm P below 0.05, and otherwise to leave no change shown; no arm is said to remove the gap
unless g(arm) has a 90 per cent interval inside -2 to +2 points. A finding is called general when it holds in both
panels, and is otherwise reported with the panel where it holds. A test that fails is reported in the web appendix
([a team of the project, name removed for blind review], 10:50 PM).

Secondary, without correction and labelled as such: g(arm) itself with its interval for every arm and panel; the
harness effect with names hidden, s(hidden) in the arm minus s(hidden) in the plain arm, which shows what the lever does
to the best product without any name; and in the two Sponsored arms, the share of answers that pick the labelled
product. The check that the reference arm reproduces [a team's name removed for blind review]'s dom2 gap on the same models is reported beside it.

## What we expect, before the run

From [a team's name removed for blind review]'s result that the brand-signal information closes the gap (12.3 points with none, 0.9 with it supplied), we
expect the arms that contain a warranty or a return rate (plain-info, feed-google, schema-org, feed-openai-2025) to narrow
the gap more than the current OpenAI feed, which contains ratings and returns only. We expect a rating gap to narrow it,
the Sponsored label on the best product to lower its share (agents penalize sponsored tags in the Columbia sandbox
[S29]), and the instruction not to consider brand reputation to narrow it. These are expectations for the discussion,
not tests beyond the family above.

## [project record removed for blind review], the agent with a search step ([issue number removed for blind review])

Written on 21 November 2026, about 12:30 AM Central, after [project record removed for blind review]'s pilot and before any [project record removed for blind review] answer.

Chen and Koudas (2026) report that ChatGPT wrote brands that it remembered into its search queries 67 per cent of the
time, against 11 per cent for other brands [S33]. [project record removed for blind review] asks whether that step costs an unfamiliar best product its
place before the model ever compares it: whether the model searches for brands by name without being asked, whether
the search then returns the invented best product at all, and which product the model finally recommends, with the
store's catalog showing the names and with the catalog hiding them.

The task runs in two plain prompts, with no live search. In the first, the model sees the shopper's request (the
corpus's request line of one of the 30 dominant tables) and a system prompt saying that it can search the store's
catalog, and it writes one to three search queries as a JSON list; it sees no product. In the second, the model sees
the request, its own queries and the products that the store returned, and recommends one, with the letter alone on
the first line (one of the corpus's four baseline paraphrases, as in [project record removed for blind review]).

The catalog of a table holds its five products. The store returns products by a fixed rule, written in
[repository path removed for blind review] before any answer: each query is lowercased and split into words, words of a fixed
stop list are dropped, and a product scores the number of query words that appear as whole words in its name, its
brand, its category noun and its specification values; each query returns at most the three highest-scoring products
with a score above zero, ties broken in an order fixed by the table and trial; the results of the queries are merged in
order without duplicates. If no product matches, the store returns "No products matched your searches." and the item
has no pick. The catalog is shown in two arms that differ only in the names: names shown, and names hidden ("Product
A" of "Brand A", so a query that names a brand matches only through its other words). Both arms use the same queries
from the first prompt. Prices follow [project record removed for blind review]'s two rungs.

The models are the Claude panel and, in two [a computing cluster's name removed for blind review] stages, the open panel (the second stage is built from each
model's own queries). Each model writes queries four times for each table (trials 0 to 3); the second prompt is
rendered for each trial, arm and rung: 120 first prompts and 480 second prompts a model.

The outcomes, for each model, table and arm, over trials and rungs:
- brand search: the share of first answers in which a query names a brand, by [a team's name removed for blind review]'s brand list with case ignored
  (every brand of the 34 tables and the product lines iPhone, iPad, MacBook, Galaxy, AirPods and Roomba, less the
  ordinary words of SELECTION.md, amendment 5), and the share that names one of the table's own familiar brands;
- fetched: the share of second prompts in which the store returned the designated best product;
- the final pick: the share of second prompts whose answer recommends the designated best product, unconditionally and
  among the prompts where it was fetched.

The primary contrasts, in each panel and Holm-corrected as one family of three: the fetched share with names hidden
minus with names shown; the final-pick share with names hidden minus with names shown (the name gap of the agent, from
search to choice); and the final-pick gap among the prompts where the best product was fetched in both arms. Intervals
come from the two-way cluster bootstrap over tables and models, as in [project record removed for blind review]. The pilot is two categories (the laptops 01
and earbuds 03 dominant sets) on Claude Haiku 5.5 and Sonnet 5.5, read by hand.

## Changes after the first version

- 20 November 2026, about 11:35 PM Central, after the pilot and before any answer of the full run: both of [a team's name removed for blind review]'s
  price rungs. The pilot (build h1, the laptops 01 and earbuds 03 dominant sets, trials 0 and 1, Claude Haiku 5.5 and
  Sonnet 5.5, 256 answers, all parsed from the first line) picked the best product in every answer of every arm at the
  equal-price rung, as [a team's name removed for blind review]'s pilot on the same two tables did ([repository path removed for blind review]). In
  [a team's name removed for blind review]'s dom2 the gap at the equal-price rung was 1.0 points for Opus 5.5, 5.0 for Haiku 5.5 and 6.3 for Sonnet 5.5,
  against 7.3, 10.0 and 6.7 with the best product priced 30 per cent below the cheapest other product, so the
  equal-price rung alone leaves little gap for a lever to move. The full run therefore uses [a team's name removed for blind review]'s two rungs, as its
  primary build did, in the build h2: every cell at the equal price and at 30 per cent below, the same trials, and the
  shares pooled over the trials and the two rungs, as in Study 2. The Claude panel answers 3,840 items a model and the
  open panel 7,680. Nothing else in the plan changes.
- 21 November 2026, about 9:20 AM Central: the terms of [repository path removed for blind review], framework.layers_corrected ([a person's name removed for blind review],
  about 12:37 AM). [project record removed for blind review] is the information-environment study and [project record removed for blind review] the harness study; the title and the note under it
  say so. No arm, item, outcome or statistic changes.
- 21 November 2026, about 11:30 AM Central, after the Claude panel's analysis and before any open-panel answer was read:
  every answer is read with [a team's name removed for blind review]'s final_answer before pick ([repository path removed for blind review], [commit removed for blind review]), which removes
  reasoning that a model leaves in its output; [a team's name removed for blind review] had found that the parser read the gpt-oss models' letters from
  their reasoning. On [a computing cluster's name removed for blind review] the export job b16-07 reads the open panel's raw outputs this way. Rerun with it, the
  Claude panel's numbers are equal in every value to those analyzed before. No arm, item, outcome or statistic changes.
- 21 November 2026, 7:11 PM Central, written after the ten open models' results of both studies ([project record removed for blind review] and [project record removed for blind review]) had been
  read: the open panel widens. Under [a person's name removed for blind review]'s ruling of about 6:50 PM (the paper's point is about machines in general,
  and model heterogeneity is part of it, so each study reports every model it can), the open panel becomes every open
  model of `models/open-models.tsv` that the studies' items can be run on, not only the first ten. [a team's name removed for blind review]
  wrote the store (both price levels) and search jobs for the 20 open models that lacked them, with Nemotron 3 Nano 30B
  and Qwen 3.5 122B to follow, on the current runner ([repository path removed for blind review], which resumes a stopped run and
  reads each answer with `final_answer`, removing the gpt-oss models' reasoning); the first ten ran on the runner of their
  bundles, whose answers the export b16-07 read again with `final_answer`. The items, arms, outcomes and statistics do not
  change. The first ten open models' results stay as reported; the estimates over every model go through the common heterogeneity
  analysis ([repository path removed for blind review]), and because the panel was widened after the first ten open models' results were
  read, the wider panel is reported as a widening, not as a test written in advance.
  The runner, as [a team's name removed for blind review] gave it at 7:13 PM: the 22 later models answer the same items, into the first ten models'
  folders, with the current runner from [repository path removed for blind review] (SHA-256 06c0647a..., with the current parser and
  panel file), in [a team's name removed for blind review]'s jobs b16-09 to b16-14 and b17-04 and b17-05 ([commit removed for blind review], [commit removed for blind review]), not with the copy inside
  the studies' bundles. That copy cannot resume a task stopped at its two-hour limit, it keeps the gpt-oss models'
  reasoning in the answer field from which the search store builds the second prompts, and its panel file marks the
  Qwen 3.5, 3.6 and 3.8 models as not text-only and the Qwen 27B models as fitting one H100. The current runner gives
  one-turn items the same vLLM settings and sampling, and the analyses read every answer again from the raw text with
  `final_answer`, so the letters do not depend on which runner wrote them.
- 22 November 2026, 12:03 AM Central, after the export of every open model's answers ([a job number removed for blind review]) and its letters check
  ([repository path removed for blind review], [a team's name removed for blind review]) and before any estimate over all models. This plan's rule
  stops a batch in which more than 5 per cent of the answers give no letter until the cause is found. [a team's name removed for blind review] found it
  broken twice and found each cause. (1) Kimi Linear 48B gives no letter in 19.1 per cent of h1's 3,840 answers, 19.7
  per cent of h2's and 22.5 per cent of the search step's 472 second prompts, because it writes its reasoning as plain
  text without tags, so the first line holds no letter and the body names several products; 142 and 136 answers of
  each half are cut at the 1,024-token limit. (2) Qwen 3.5 27B (5.2 per cent) and Qwen 3.5 4B (6.0 per cent), in the
  search step's second prompts only, where a real pick sits inside an answer that names other letters too. Decision:
  the [project record removed for blind review] and [project record removed for blind review] estimates follow Study 2's open-models rule ([repository path removed for blind review]: a model whose
  answers the parser reads in under 90 per cent of a build's items is reported apart as unable to do the task), so that
  the paper uses one rule for every study. Kimi Linear 48B (about 80 per cent read) is left out of every estimate and
  reported apart, as Study 2 left it out of both its builds; its parse counts stay in each numbers.json. Both Qwen 3.5
  models stay in, because their answers are read in 94 to 95 per cent, the cause is found, and it holds for every model
  to a small degree; their counts are reported. `analyze_harness.py` and `analyze_search.py` take `--leave-out <model>`
  for this (with a test), and each numbers.json names the models left out and the rule.
- 22 November 2026, 12:12 AM Central, written after the panels' results had been read: the estimates over every model.
  At the coordinator's request (each study reports its results over all its models first, under [a person's name removed for blind review]'s ruling of
  about 6:50 PM on 21 November), [project record removed for blind review]'s primary contrasts are also estimated over every model that answered, pooled
  across the panels (`analyze_search.py --panel all`; open models from the [a computing cluster's name removed for blind review] export, Claude and later GPT models
  from their answer folders), with the same estimator, bootstrap and Holm family of three. [project record removed for blind review] follows in the same way
  when the all-model analysis b16-15 returns. Each study writes a per-model file (`per_model.csv`: each model's primary
  contrasts, with an interval from resampling that model's tables) for the common heterogeneity analysis. Because the
  pooling was decided after the panels' results were read, the text reports it as a summary over models.
- 22 November 2026, 2:40 AM Central: a decline (an answer that recommends none of the products because of the
  products, most often here because every price is outside the request's budget) is an outcome and does not count
  against the 90 per cent; the definition, the classifier `decline.py` and its test are those of the retrieval plan's
  change of this time. On [a job number removed for blind review]'s sample every decline names the budget ("None of the listed options fall within your
  $120-180 budget"). Kimi Linear 48B stays out: its answers without a letter are reasoning written as text, not
  declines, and on [a job number removed for blind review]'s sample none of its 41 such answers is a decline. Qwen 3.5 27B and Qwen 3.5 4B stay in either
  way. The counts by model and arm come with the decline column of [a team's name removed for blind review]'s exports, and both studies' numbers.json
  report them then.
