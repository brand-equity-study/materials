# The machine brand audit: plan ([project record removed for blind review], [issue number removed for blind review])

Written by [a team's name removed for blind review] on 20 November 2026 at about 10:20 PM Central on [a computer's name removed for blind review], and committed before any model has
answered any item of the audit. The brief is [repository path removed for blind review]; the construct is in
[repository path removed for blind review] section 0. A change to this plan after answers are seen is written below it as a dated
amendment with its reason, and the original text stays.

[a person's name removed for blind review]'s scope, verbatim, as [a team of the project, name removed for blind review] passed it on: [a person's words removed for blind review]. Every item
is a plain prompt to the model, in a new conversation, with no search and no tools.

## The question

Machine-based brand equity is the difference in how often an assistant recommends the same product when its brand
name is shown and when it is hidden. The audit measures, for every brand in the 34 product tables and in each model,
what each model says about the brand when asked, in six measures, and tests which of them predicts the
recommendation gap of that brand's product in the same model.

## The brands

- The 34 tables of `experiment/assortments.py`, read through [repository path removed for blind review] (`load_tables`, read
  only): 170 products, 132 pairs of a brand and a category, 105 distinct names. Each product's brand is coded
  familiar-high (59 pairs), familiar-medium (40) or invented (33). Every designated best product is shown under an invented
  name; one invented name (Vistara, TVs 02) is also the name of a product that is not the best.
- A reference set, outside the gap analysis: the real brands that the invented names replaced in the tables (the
  `_original_brand` field), 33 pairs of a brand and a category and 32 names: CHUWI, Teclast, Bmax, Nothing, Fairphone,
  Xiaomi (smartphones and tablets), TCL, Hisense, Soundcore, 1MORE, HiFiMAN, Topo Athletic, Inov-8, Atreyu, Varia,
  Flair, Wacaco, SoundPEATS, EarFun, TOZO, Amazfit, Roborock, Tribit, Keychron, Silicon Power, ThermoFlask, Oclean,
  Evergoods, Cleanblend, TP-Link, Innocn and OM System. They
  receive the brand-level items only (recognition, country, description, ratings), so that the audit shows where real
  brands that American shoppers know less well stand for the model.

## The models

- The four Claude 5.x models that Study 2 uses: Claude Haiku 5.5, Sonnet 5.5, Opus 5.5 and Fable 5.1
  (`claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5`, `claude-fable-5-1`), through [an internal tool removed for blind review]
  ([a local folder removed for blind review]) with `--batch`, at the settings under which Study 2 measured the
  gap: no temperature, no effort and adaptive thinking (the provider's defaults), at most 8,000 output tokens. [a note on the project's accounts removed for blind review].
- The open models of the [a computing cluster's name removed for blind review] panel (`models/open-models.tsv`, which [a team of the project, name removed for blind review] is widening to
  every model that fits two H100), through [repository path removed for blind review], unchanged: each model's own chat template
  and generation defaults, reasoning off where the panel file says so, a seed from each item's id, at most 1,024 new
  tokens. [A team of the project, name removed for blind review] submits the job; this lane never reaches [a computing cluster's name removed for blind review]. An open model enters the gap analysis
  only if its answers to Study 2's `full2` build exist.
- The Claude models and the open models are two panels, each reported alone and never pooled with the other.
- The models that [a team's name removed for blind review] runs through Codex are not in this plan; they may be added later by an amendment, as a third
  panel.

## The items

One system prompt for every item of the audit, in every model:

> You are a shopping assistant. A user has asked you a question about products and brands.
>
> Answer in exactly the format that the user asks for, with no other text.

In the wordings below, `{brand}` is the brand's name as the tables show it, `{plural}` is the category's plural
(laptops, smartphones, TVs, headphones, running shoes, coffee makers, wireless earbuds, smartwatches, robot vacuums,
Bluetooth speakers, keyboards, external SSDs, water bottles, electric toothbrushes, backpacks, blenders, WiFi routers,
monitors, tablets, cameras), and `{req}` is the table's own request, as Study 2 renders it ("a reliable laptop for
everyday work and browsing, budget around $600-800"). Every rating item ends "Answer with one whole number from 1
(<low anchor>) to 7 (<high anchor>) and nothing else." Items about a brand add "If you do not know the brand, give
your best guess." so that every brand, invented ones included, receives a rating; whether the model knows the brand is
measured separately (measure 3).

### 1. Salience: the brands the model names with no list (the consideration stage)

Per category (20) for wordings 0 and 1, per table (34) for wording 2; 10 trials each; 740 items a model.
- w0: "List the brands of {plural} that you know, the most familiar first. Write one brand name per line, at most 15
  lines, and nothing else."
- w1: "A shopper in the United States is shopping for {plural}. Which brands would you suggest they consider? Write one
  brand name per line, at most 15 lines, the strongest suggestion first, and nothing else."
- w2: "I'm looking for {req}. Which brands should I consider? Write one brand name per line, at most 15 lines, the
  strongest suggestion first, and nothing else."

Score for a brand in a category: the share of the category's lists (w0 and w1 of the category, w2 of every table of
the category) that name the brand. Secondary: the mean rank, with an unnamed brand at rank 16.

### 2. Typicality: whether the brand is the model's default example of its category

Default example, per category, three wordings, 10 trials each; 600 items a model. "Answer with the brand name only."
ends each.
- w0: "Name one brand of {plural}."
- w1: "Which brand comes to mind first when you think of {plural}?"
- w2: "Which brand is the most typical example of a brand of {plural}?"

Typicality rating, per brand and category (132), two wordings, 2 trials each; 528 items a model.
- w0: "How typical is the brand {brand}, which sells {plural}, of brands of {plural}?" 1 (not at all typical) to 7
  (the most typical example).
- w1: "If someone pictured a typical brand of {plural}, how closely would {brand} match that picture?" 1 (not at all)
  to 7 (exactly).

Score: the mean rating. Secondary: the share of default-example answers that name the brand.

### 3. Recognition

Per brand and category (132, and the 33 reference brands), two wordings, 2 trials each; 660 items a model.
- w0: "Do you know the brand {brand}, which sells {plural}? On the first line write yes or no. If yes, write on the
  second line the country the brand is from, and on the third line one fact about the brand. If no, write only no."
- w1: "Have you heard of {brand}, a brand of {plural}? First line: yes or no. If yes, second line: the country the
  brand comes from; third line: one true fact about the brand. If no, write only no."

Scores: claimed recognition (the share of answers that say yes), which the analysis uses, because it is how the model
treats the brand; and accurate recognition (yes, with a country in the reference set), secondary. The reference
([repository path removed for blind review]) is written before the full run: for every familiar and reference brand, the accepted
countries (where the brand was founded, where it has its headquarters, where its parent company has its headquarters)
and the parent company; for every invented name, any real company of the same name that a web search finds, with its
country. A yes to an invented name is a false recognition, unless the country given is that of a real company of the
same name, which is reported as recognition of a namesake; both counts are reported by model. The fact on the third
line is judged true, false or not checkable by Claude Opus 5.5 with the reference record in its prompt, secondary.

### 4. Inferred quality on attributes that the listing does not show

The listing is rendered by Study 2's own `product_block`, as the models saw products in Study 2: "Here is a product
listing." then the block (letter A; the name "{brand} {noun}" and "Brand: {brand}", or the names-hidden labels
"Product A" and "Brand A"; the price; the scrubbed specifications; "Reviews: 500 reviews, 4.3 stars"), then the
question. The price is the product's price in Study 2 (for the best product, its price at Study 2's rung 0, equal to
the cheapest other product). Three versions of each listing:
- every product under its own name (170);
- the names-hidden twin of every product (170);
- the two products whose names Study 2's crossed cells swap: the best product under the name of each familiar brand
  that is its swap partner in any trial, and that partner's product under the invented name (88 pairs, 176 listings).
Each listing with six questions, each in its own prompt, two wordings, 2 trials each: 516 listings, 12,384 items a
model.
- Reliability. w0: "How reliable do you expect this product to be, that is, how likely is it to work without
  problems?" 1 (very unreliable) to 7 (very reliable). w1: "How likely is this product to keep working without
  faults?" 1 (very unlikely) to 7 (very likely).
- Durability. w0: "How long do you expect this product to last before it wears out, compared with other {plural}?" 1
  (much shorter) to 7 (much longer). w1: "How durable do you expect this product to be?" 1 (not at all durable) to 7
  (very durable).
- Performance. w0: "How well do you expect this product to perform in everyday use, beyond what the listing shows?" 1
  (very poorly) to 7 (very well). w1: "How good do you expect this product to be in daily use, compared with what its
  specifications suggest?" 1 (much worse) to 7 (much better).
- Support. w0: "How good do you expect the customer support and warranty service for this product to be?" 1 (very
  poor) to 7 (excellent). w1: "If this product had a problem, how well do you expect the company behind it to help the
  buyer?" 1 (very poorly) to 7 (very well).
- Safety. w0: "How safe do you expect this product to be to use?" 1 (not at all safe) to 7 (completely safe). w1: "How
  confident are you that this product is free of defects that could harm the user?" 1 (not at all confident) to 7
  (completely confident).
- Failure rate. w0: "What percentage of units of this product do you expect to fail or be returned as defective within
  the first year? Answer with one number from 0 to 100 and nothing else." w1: "Out of 100 buyers of this product, how
  many do you expect to have it break or return it as faulty in the first year? Answer with one number from 0 to 100
  and nothing else."

Score for a name on a product: the mean rating under the name minus the mean rating of the same listing with the names
hidden, for each attribute; for the failure rate, the hidden twin's estimate minus the estimate under the name, so that
a positive score always favors the name. The inferred-quality index is the mean of the five rating scores.

### 5. Credibility of a listing under the name

The table's best product (its scrubbed specifications), rendered as in measure 4, under each of the table's five names
and under the names-hidden labels, at two prices: low (Study 2's rung 2, 30 per cent below the cheapest other product)
and usual (the median price of the table's four other products). 34 tables, 6 labels, 2 prices, two wordings, 2
trials: 1,632 items a model.
- w0: "How believable is this listing, that is, how likely is it that the product really has these specifications at
  this price?" 1 (not at all believable) to 7 (completely believable).
- w1: "How likely is it that a buyer would find this product as good as the listing says?" 1 (very unlikely) to 7 (very
  likely).

Score for a name: the mean rating under the name minus the mean rating under the hidden labels, at the low price
(primary) and at the usual price (secondary).

### 6. Associations, their tone, and the country of origin

Per brand and category (132, and the 33 reference brands), two wordings, 2 trials each.
- Description (660 items a model). w0: "Describe the brand {brand}, which sells {plural}, in five words or fewer. Write
  only the words." w1: "What comes to mind when you think of {brand}, a brand of {plural}? Answer in five words or
  fewer. Write only the words."
- Ratings, each in its own prompt (2,640 items a model):
  - premium. w0: "How premium is the brand {brand}, which sells {plural}?" 1 (a budget brand) to 7 (a premium brand).
    w1: "Where does {brand}, a brand of {plural}, sit between budget and luxury?" 1 (budget) to 7 (luxury).
  - innovative. w0: "How innovative is the brand {brand}, which sells {plural}?" 1 (not at all innovative) to 7 (very
    innovative). w1: "How often does {brand}, a brand of {plural}, bring out new ideas and technology before other
    brands?" 1 (never) to 7 (very often).
  - safe. w0: "How safe are the products of the brand {brand}, which sells {plural}?" 1 (not at all safe) to 7
    (completely safe). w1: "How much would you trust {brand}, a brand of {plural}, to sell products that are safe to
    use?" 1 (not at all) to 7 (completely).
  - sustainable. w0: "How sustainable is the brand {brand}, which sells {plural}, in its treatment of the
    environment?" 1 (not at all sustainable) to 7 (very sustainable). w1: "How environmentally responsible is
    {brand}, a brand of {plural}?" 1 (not at all) to 7 (very).
- Country (660 items a model). w0: "Which country is the brand {brand}, which sells {plural}, from? Answer with the
  name of the country only. If you are not sure, give your best guess." w1: "Where is {brand}, a brand of {plural},
  based? Answer with the name of the country only. If you are not sure, give your best guess."

The descriptions are coded by two judges with one closed label set, each description alone: the tone (negative,
neutral, positive, or "does not know the brand") and every content label that applies (quality or performance,
reliability or durability, low price or value, premium or high price, innovation or technology, design or style,
popularity or market leadership, a named product or feature, customer support, safety, sustainability, country or
origin, other). The first judge is Claude Opus 5.5 through [an internal tool removed for blind review]; the second is a GPT model through
Codex, a second vendor, so that no Claude model is the only reader of Claude answers. Agreement is reported as Cohen's
kappa for the tone and for each label; the analysis uses the first judge's codes and is repeated with the second's.
The tone score of a brand is the share of its descriptions coded positive minus the share coded negative. The country
answers are matched to a country list, and reported by brand and model, with the share placed in China, the United
States, Japan, South Korea, Taiwan and Europe.

### Size, order and format

About 20,500 items a model (740 + 600 + 528 + 660 + 12,384 + 1,632 + 660 + 2,640 + 660). Every trial of an item is a
separate request with the same text. The items are written in a shuffled order (seed "jmr-b8-20261120").

The build writes [repository path removed for blind review]: `items.jsonl` with every field that `run_items.py` reads by key
(`id`, `system`, `user`, `cell`, `table`, `trial`, `names`, `info`, `rung`, `best`) and the fields that the analysis
needs (`measure`, `attribute`, `wording`, `brand`, `brand_kind`, `category`, `product`, `label`, `price_kind`); for [an internal tool removed for blind review], `p0.jsonl` (`{"id", "text"}`) and `system_p0.txt`; and `SHA256SUMS`. `cell` is the measure, the
attribute and the wording; `table` is the table id, or `cat_<category>` for items asked per category; `names` is
`shown`, `hidden` or `none`; `info` is 0; `rung` is 2 for the low price and 0 otherwise; `best` is empty. A test reads
the build the way `run_items.py` and `api-job.mjs` read it, and refuses a build that either could not run.

## Reading the answers

The parser is written and tested before the pilot ([repository path removed for blind review], `test_parse_audit.py`, with
planted faults and clean controls):
- A rating is the first whole number from 1 to 7 on the first line that is not empty, after markdown is removed, else
  the only such number in the answer; a failure rate is the first number from 0 to 100, read the same way.
- A brand list is read line by line, with numbering, bullets, markdown and any text after a dash, colon or bracket
  removed, and each name is matched to the brands of the category and the reference set through one alias table
  (for example "Hewlett-Packard" to HP, "Galaxy" to Samsung, "Roomba" to iRobot, "WD" to Western Digital). Names that
  match no brand are kept with their text and counted, and the most frequent are read by hand.
- A yes or no is the first word of the first line; the country is matched to a list of countries with their common
  forms ("USA", "U.S.", "United States of America").
- An answer that the parser cannot read is left out of its measure and counted by model and measure. If more than 5
  per cent of one model's answers to one measure are unread, that measure waits for that model until the cause is
  found. Nothing else is excluded.

## The recommendation gap that the audit is tested against

From Study 2's `full2` build ([repository path removed for blind review] and its answers; the 34 tables, scrubbed, with
the information rows absent), read with Study 2's `parse_answer.py`: for each model, the cells with no information, at
all three price rungs, 10 trials each. Within one table, trial and rung, every cell shares the letters, the order and
the system prompt, so each comparison below is paired by trial and rung.
- The gap of a product under its own name: the share of answers in the original cell that pick the product, minus the
  share in the names-hidden cell, in percentage points (170 products a model).
- The gap of a product under a swapped name, from the crossed cell: the best product under its partner's familiar name,
  and the partner's product under the invented name, against the names-hidden cell (88 pairs a model).
The Study 1 rerun ([repository path removed for blind review], names shown against names hidden with the leaks cleaned) is
a second outcome, reported beside the first.

## The analysis

The unit is a product with a name, in one model. The five gaps of one table sum to about zero, so the gaps are not
independent within a table: every component score and the outcome are centered within table and model (each product's
value minus the mean of the table's products), and the intervals come from a two-way cluster bootstrap that resamples
tables and models independently, 2,000 draws, seed 20261120, as in Study 2. Within one panel, every model has equal
weight. Each component is put in standard units over the panel's centered values.

Primary tests, in the Claude panel and, separately, in the open panel:
1. Each component alone. For each of the six component scores (salience; typicality rating; claimed recognition; the
   inferred-quality index; credibility at the low price; association tone), the regression of the product's own-name
   gap on the centered component score, with the product's centered names-hidden pick share as a control (a product
   that is rarely picked with the names hidden can lose little). Reported on all 170 products, and on the familiar
   products only (135), which leaves out the invented names on the best products. The six tests on all products are
   one family, Holm-corrected.
2. The name on the same product. In the crossed comparison, the best product and its partner's product are each shown
   under two names (the invented name and the familiar name), so the product's specifications are held fixed. The difference
   between the two names' gaps on the same product is regressed on the difference between the two names' component
   scores, for each component. This is the test of a familiar name against an invented one on identical listings.
3. All components together. The same regression as test 1 with all six component scores, reporting each coefficient,
   the variance inflation factors, and the share of variance that each component adds when it is entered last.

Secondary: each of the five attributes and the failure rate alone (whether reliability predicts the gap more than
performance does, which Study 2's account requires); the default-example share, the mean rank and accurate
recognition; the association ratings; the gap from the Study 1 rerun; brand-level correlations averaged over the
models of a panel; and, across models, whether a model's average spread between familiar and invented names on a
component goes with its average gap. Each component is also set beside the brand's frequency in public training
corpora (`OSF/data/brand_frequencies.csv`) and the familiarity coded for it, for the paper's claim about other kinds of
brand equity.

Rules fixed now:
- Reliability. The split-half reliability of each component (wording 0 against wording 1) and of the gap (trials 0 to
  4 against 5 to 9), Spearman-Brown corrected, within each model over the centered products. A component or a gap
  whose reliability is below 0.5 in a model is reported as not measured reliably there, and its relation to the gap in
  that model is shown but not read as present or absent.
- Collinearity. Two components whose centered values correlate above 0.8 in a panel are reported as not separable, and
  test 3 enters their mean in their place. A coefficient in test 3 whose variance inflation factor is 5 or more is not
  read on its own.
- What is said. A component "predicts the gap" when its Holm-corrected test 1 on all products excludes zero in the
  panel; it "predicts the gap among familiar brands" when the familiar-only test excludes zero; it "predicts the gap
  beyond the others" when its coefficient in test 3 has a 95 per cent interval that excludes zero and passes the
  collinearity rule. A component whose interval includes zero is reported with its interval, and as not shown to
  predict the gap, never as shown not to.

## The pilot

Five brands in two tables, all six measures, the full number of wordings and trials: Dell (familiar-high), Acer
(familiar-medium) and Zentria (invented, the best product) in laptops 01; JBL (familiar-high) and Vynex (invented, the
best product) in earbuds 03. The category items run for laptops and wireless earbuds; measures 4 and 5 run for these
five names in their own tables, with the names-hidden twins and the crossed listings that involve them. Models: Claude
Haiku 5.5 and Claude Opus 5.5. The pilot is read by hand before the full run: the parse rate of every measure, a sample
of every measure's answers, how each model treats the two invented names, and the tokens and dollars per item, from
which each full job's budget is set. The pilot's answers are not pooled into any estimate. If the pilot shows a wording
that the models misread, the wording is changed by an amendment before the full run.

## Where things go

- Items: [repository path removed for blind review]; answers: [repository path removed for blind review].
- Code: [repository path removed for blind review], `parse_audit.py`, `analyze_audit.py`, their tests, and `run_audit.ps1`.
- Results: [repository path removed for blind review] and `numbers.json`.
- The open models' answers: the items file goes to [a team of the project, name removed for blind review], which submits it to [a computing cluster's name removed for blind review] and fetches the
  answers into [repository path removed for blind review].

## Amendment 1 (20 November 2026, about 10:35 PM Central, after the pilot and before any answer of the full run)

**The framework.** The construct, its five proposed components and the hypotheses are defined once, in
[repository path removed for blind review] under the key `framework` ([a team of the project, name removed for blind review], about 10:20 PM). The audit is [project record removed for blind review] there
and also does [project record removed for blind review], the consideration stage ([issue number removed for blind review]). It tests two of the framework's hypotheses:
- H6a: at evaluation (choosing from a list), a brand's inferred quality and credibility in a model predict its effect
  in that model. Read from test 1 and test 2 above, for the inferred-quality index and for credibility at the low
  price, each part alone: supported for a component when its Holm-corrected test 1 on all products has a positive
  coefficient whose interval excludes zero, with test 2 and the familiar-only test reported beside it.
- H6b: at consideration (no list), a brand's salience in a model predicts whether the model names it at all.
The framework's five components are salience, inferred quality, credibility, associations and typicality.
Recognition (measure 3) is reported as the recognition half of salience; the six scores of test 1 stay as written.

**[project record removed for blind review] and H6b, added.** New items: the requests that real people wrote in [a team's name removed for blind review]'s bank
([repository path removed for blind review]: the 103 chat-log requests and the 51 crowd-written requests; the 64
written by the author are left out because no shopper wrote them), each sent as written with no list and no added
question, 3 trials: 462 items a model. The brands of the request's category (the tables' brands and the reference
brands) are read from the free answer in the order of their first mention (`parse_audit.mentions`, tested on planted
answers before any answer existed). A brand name that is also an ordinary word counts only with its capital letter
(Apple, Beats, Shark, Ninja, Stanley, Yeti, Brooks, Insignia, Quip, Flair, Varia), "Nothing" only with one of its
phones, "Amazon" only with one of its tablets, and a product line that is an ordinary word (Galaxy, Pixel, Envy,
Aspire, and the rest in `CASED_ALIASES`) only as written.
- Recall share of a brand in a category: the share of the salience lists of wording 0 ("the brands of {plural} that
  you know") that name it.
- Consideration share: the share of answers to the open requests (salience wordings 1 and 2, and the real requests)
  that name it; the real requests alone are reported beside it.
- H6b test: within category and model, the regression of the consideration share on the recall share (both centered
  within category and model), over the 132 pairs of a brand and a category of the tables; a two-way cluster bootstrap
  over categories and models, 2,000 draws, seed 20261120. Supported when the coefficient is positive and its 95 per
  cent interval excludes zero.
- Consideration against evaluation ([project record removed for blind review]'s own question): the consideration share of a brand against its product's
  own-name gap at evaluation, both centered within table and model, with the same bootstrap over tables and models;
  reported as a correlation and a slope, for all open requests and for the real requests alone.

**What the pilot showed** ([repository path removed for blind review], read by hand; not pooled into any estimate). Claude Haiku
5.5 and Claude Opus 5.5 answered all 888 items; the parser read 100 per cent of the answers of every measure in both
models. Both models said no to knowing Zentria and Vynex in every recognition answer and described both as unfamiliar
("Unfamiliar brand; cannot verify details."), and both still gave a country when asked for their best guess (Opus:
China in 4 of 4 answers for each). The ratings were whole numbers on the first line. The brand lists named brands
outside the tables of the category (Samsung, LG, Microsoft and MSI among laptops; Bose, Sennheiser and Skullcandy
among earbuds), which the analysis leaves unscored, as written above. No wording was misread, so none is changed. The
cost was 0.07 dollars (Haiku) and 2.08 dollars (Opus) for 888 items at the full price; the largest answer had 379
output tokens (Haiku) and 542 (Opus), thinking included, and none stopped at the limit.

**Settings changed for the full run, with the reason.**
- At most 2,000 output tokens for every item, and 4,000 for the real requests, in place of Study 2's 8,000. The cap
  changes an answer only when the answer reaches it; the largest pilot answer used 542. With 8,000, the runner's
  bound on a batch (every allowed output token counted) would be larger than any [an account of the project removed for blind review] holds. Answers that
  stop at the cap are counted by model and measure and reported.
- The build is sent in parts of 1,500 items (and one part for the real requests), each a batch on one [an account of the project removed for blind review],
  through `run_audit.ps1`, which tries the [an account of the project removed for blind review] in order of money free, because [an internal tool removed for blind review] refused five of
  them as "not ready" at 10:24 PM; [an account of the project removed for blind review] is used last.
- The full build has 20,934 items a model: the 20,504 of the counts above, less 8 credibility items (the toothbrush
  table has four distinct names, both Oral-B products sharing one) and 24 inferred-quality items (the best toothbrush
  under the name Oral-B is one listing, not two), plus the 462 real requests.
- The failure-rate reader takes a range ("3-5%") as its midpoint, and the rating reader removes the scale when an
  answer writes it back ("5 out of 7", "on a scale of 1 to 7"); both rules were written and tested before the pilot's
  answers were read.

**The reference** ([repository path removed for blind review]), written by a helper session (Claude Sonnet 5.5) with a web search
for every invented name: 105 real brands with their accepted countries, parent company and sources, and 32 invented
names with the real companies of the same name that the search found. Namesakes in or near the category: Novatech
(laptops, United Kingdom), Primebook (laptops, India), Sonance and Wavecrest (speakers, United States), Vaultdrive (a
portable SSD) and Trailpeak (a shop that sells backpacks). [a team's name removed for blind review] added Ireland for Seagate (its holding company's
headquarters). The helper wrote most Wikipedia links from their titles without fetching them; the links are checked
before the results are written.

**The open models' gap.** Job [a job number removed for blind review] exported the letter of every open-model answer to full2 and s1rerun1
([repository path removed for blind review], [commit removed for blind review]), read with Study 2's parser; `gap.py` reads it for the
open panel.

## Amendment 2 (20 November 2026, about 10:42 PM Central, before any answer of Claude Fable 5.1)

[A team of the project, name removed for blind review], 10:39 PM, with [a person's name removed for blind review] told: [a note on the project's accounts removed for blind review]; Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5 run the full build, and Claude Fable
5.1 runs only the measures that H6a and H6b need, in one wording, with the fewest trials this plan allows.

**Fable 5.1's items.** Build `full1-fable` (`subset_build.py --rule h6`), a subset of `full1` with the same item ids,
7,654 items: inferred quality (the five ratings and the failure rate, wording 0, 2 trials, all 515 listings: 6,180
items), credibility (wording 0, both prices, 2 trials: 812), the salience lists of wording 0 (recall, 10 trials: 200)
and the real requests (consideration, 3 trials: 462). Two trials are kept where the plan has two, because the
split-half reliability needs two answers.

**What changes in the analysis for Fable 5.1.** Typicality, recognition, the associations and the salience lists of
wordings 1 and 2 are not measured for Fable 5.1. In tests 1 to 3, Fable 5.1 enters the Claude panel only for the
inferred-quality index, the failure rate, credibility and salience (recall only); a pooled estimate for a component
that Fable 5.1 lacks pools the other three Claude models, and every pooled estimate of the Claude panel is also given
without Fable 5.1. For Fable 5.1, H6b's consideration share is the real requests alone, and the split-half
reliability of its components is trial 0 against trial 1 (for the other models both splits are reported).

**The reserve.** [a note on the project's accounts removed for blind review]

**Answers at the cap.** A Fable 5.1 answer that stops at the 2,000-token cap with no text is asked again at 4,000
tokens for that item alone, and the count is reported.

## Amendment 3 (20 November 2026, about 10:55 PM Central, after Fable 5.1's subset and before any other Fable answer)

[A team of the project, name removed for blind review], 10:53 PM: "run Fable 5.1 on the full build too (about 24 USD more; the costs are far below the
holds)". The actual cost of the subset was 22.49 dollars, against holds of about 90 dollars a part. Fable 5.1 now
answers every item of `full1`: the subset `full1-fable` (7,654 items, answered at 10:51 PM) and the rest,
`full1-fable-rest` (13,280 items, `subset_build.py --rule all --minus full1-fable`). Both share `full1`'s item ids, so
the analysis reads Fable 5.1's answers from both against `full1`'s items. Amendment 2 therefore covers only the order
of the runs: the analysis changes it listed for Fable 5.1 (components left out, consideration from the real requests
alone, reliability by trial) no longer apply, and Fable 5.1 is analysed as the other three Claude models are. Every
pooled estimate of the Claude panel is still also given without Fable 5.1.

## Amendment 4 (21 November 2026, about 10:45 AM Central, after the open models' answers were read for their parse rates and before any test of the open panel)

**The open panel.** [a computing cluster's name removed for blind review] [a job number removed for blind review] exported the audit answers of 25 open models (`full1-main`, 20,472 items a
model; `full1-pc`, the 462 real requests), and every open model's Study 2 letters (`answers-letters.csv.gz`). Gemma 4
31B answered 16,896 of the main items and none of the real requests (its run stopped early); its missing answers are
counted as missing, by measure, and nothing is imputed.

**The 5 per cent rule, applied.** Eight pairs of a model and a measure had more than 5 per cent of answers unread. The
causes, found by reading the unread answers (`show_unread.py`), and what follows:
- gpt-oss 20B and 120B answered in two channels ("analysis<reasoning>assistantfinal<answer>"), which run_items.py
  does not separate. From now on, every [a computing cluster's name removed for blind review] answer is read from its final text (`parse_audit.final_text`): the
  text after the last "assistantfinal"; else the text after the last "</think>"; a text whose reasoning never reached
  an answer (an analysis channel with no final, or an unclosed "<think>", 29 to 61 answers in each Qwen 3.5 model and
  a few in GLM 4.7 Flash and Granite 4.2) has no answer. With this rule, both gpt-oss models are under 5 per cent on
  every measure.
- The Study 2 letters of both gpt-oss models (export [a job number removed for blind review]) were read by Study 2's parser from the reasoning channel
  (3,162 and 3,312 of 6,120 full2 answers unread). Until their letters are exported again from the final answers,
  the two models have no gap: their components are reported, and they enter no test of the gap (`GAP_EXCLUDED`).
- Qwen 3.5 0.8B wrote the format's labels back ("First line: yes") and named countries outside the reader's list
  (Argentina, Namibia). The reader now removes a leading "First line:", "Second line:" or "Third line:", and the
  country list holds every country. With these rules it is under 5 per cent on every measure. Both changes apply to
  every model, the Claude models included.
- Gemma 4 26B refused 6.4 per cent of the inferred-quality ratings ("I cannot provide a confidence score ... based on a
  text listing"). Its refusals fall unevenly: safety about 25 per cent on every listing, but durability 15.3 per cent
  and support 10.9 per cent with the names hidden against 2.4 and 1.2 per cent under the product's own name. Its
  inferred-quality scores are kept, the refusals are reported by attribute and listing, and every test of the open
  panel is repeated without Gemma 4 26B.
- Marin 8B left 6.0 per cent of the association ratings (premium, innovative, safe, sustainable) unread (refusals,
  decimals such as "6.5", and words), more for invented names (13.6 per cent on safe). These ratings are secondary;
  they are reported with the unread share by kind of name.
The read rates of every model and measure are in [repository path removed for blind review].

**The judges for the open panel.** Every description of the 25 open models is coded by both judges, as for the Claude
models: Claude Opus 5.5 as a batch through [an internal tool removed for blind review] (about 36 dollars, from the Claude panel's cost), and
GPT-6.2 Sol through Codex. The analysis with the first judge's codes is written first, and it is repeated with the
second judge's codes when they are all in.

**The open panel's tests** are the plan's tests 1 to 3, H6a and H6b, with the same rules, over the 23 open models that
have a gap, reported as their own panel, never pooled with the Claude models.

## Amendment 5 (21 November 2026, about 10:50 AM Central, before any code of the open panel's descriptions is read)

[A team of the project, name removed for blind review], 10:49 AM, after [an account of the project removed for blind review] refused every checkout ("no room below its stop") and [an account of the project removed for blind review] is to be used last ([a person's name removed for blind review]'s rule): the first judge of the open panel's descriptions is Claude Opus 5.5
through the Claude command line ([product name removed for blind review]) on the subscription, calibrated first against last night's API judge.

**The route** ([repository path removed for blind review]). One `claude -p` per description, the Claude command line 2.1.330 ([product name removed for blind review]), model
`claude-opus-5-5` (the API judge's model id), from an empty working folder, with `CLAUDE_CONFIG_DIR` set to an empty
folder of its own (so no CLAUDE.md, settings, hooks, skills, plugins or memory reach it); the judge's instruction
(`judge_prompt.txt`) passed whole as the system prompt with `--system-prompt`, the description on standard input as
the user message, `--exclude-dynamic-system-prompt-sections`, no tools, no MCP servers, no setting sources, no saved
session, JSON output, no effort set. The login comes from the environment that this session runs with (the
subscription route that the lanes use), never from a copied credentials file. The output schema is the API judge's
(`parse_code`). Each answer records the CLI version, the models the reply names, its input and output tokens and the
date, so the CLI's own framing is measured against the API judge's input tokens.

**The calibration, fixed now.** 200 of the Claude panel's 2,295 distinct descriptions, drawn with
`random.Random(20261121).sample` over the sorted ids of `coding/full1/items.jsonl`, are coded again through this
route (`coding/calib-cli/`). On those 200, the agreement share and Cohen's kappa of the tone are computed for the CLI
route against the API judge, and for the API judge against GPT-6.2 Sol (last night's second judge), and the same for
each content label and for the mean of the label kappas. The rule, on the tone, which is the only code that enters a
test: if the CLI route's agreement share and kappa with the API judge are both at least those of the API judge with
Sol on the same 200, the CLI route codes all 14,871 descriptions of the open panel; if either is lower, nothing more
is run and [a team of the project, name removed for blind review] is told. The labels are reported beside it and decide nothing, because they enter no
test. The result is written to `coding/calib-cli/CALIBRATION.json` and into this plan before the open panel's codes
are read.

**The calibration's result** (21 November, about 10:55 AM Central; `coding/calib-cli/CALIBRATION.json`). All 200
descriptions were coded through the CLI route, every reply naming `claude-opus-5-5`; the CLI's framing raised the
input from 535 to 929 tokens a request. On the tone, the CLI route and the API judge agreed on 198 of 200 (0.990)
with kappa 0.98113; the API judge and Sol agreed on 198 of 200 (0.990) with kappa 0.98130. The agreement shares are
equal and the CLI route's kappa is lower by 0.00017, so under the rule written above the route does not pass, and
nothing more is run through it without a new decision from [a team of the project, name removed for blind review]. On the labels, which decide nothing, the CLI
route agreed with the API judge more than Sol did (mean label kappa 0.913 against 0.872; identical label sets 78.5
against 69.0 per cent). The CLI route's two tone disagreements with the API judge were two descriptions coded
positive that the API judge coded neutral ("Mechanical keyboards, wireless, customizable, Mac-friendly"; "Gaming
peripherals, bold RGB design."); Sol's two were two unknown-brand descriptions coded neutral.

**[A team of the project, name removed for blind review]'s ruling** (10:58 AM Central, 21 November, before any code of the open panel's descriptions
was read). The rule as written above failed by 0.00017 on the tone's kappa (0.98113 for the CLI route with the API
judge against 0.98130 for the API judge with Sol), with equal agreement (198 of 200 in both). [A team of the project, name removed for blind review]
ruled that the route passed, for this reason, in its words: "The rule's purpose was that the CLI route codes as the
API judge does, and it does: the same 198 of 200 on tone as the API judge with Sol, a kappa lower by 0.00017 that
comes only from which two descriptions disagree (a difference of one item either way would reverse it), and a higher
agreement on the labels (0.913 against 0.872)." So the CLI route codes all 14,871 descriptions of the open panel,
with the calibration's own config folder ([a local folder removed for blind review], which holds only the CLI's
first-run state and its built-in plugin record), the calibration's empty working folder, the same model id
(`claude-opus-5-5`) and the same instruction, and every reply's route (the CLI version, the model the reply names,
the config and working folders, the tokens and the date) is recorded in its results line. The paper reports the
calibration, the rule, its failure by 0.00017 and the ruling in the web appendix.

**A note to amendment 4** (21 November, about 11:05 AM Central). [A team of the project, name removed for blind review] put the same reasoning rule into
Study 2's parser (`final_answer` in [repository path removed for blind review], [commit removed for blind review]), and [a job number removed for blind review] reads every open
model's Study 1 rerun, full2 and dom2 letters again with it. The audit now calls that function, so the audit and the
letters of the gap read answers by one rule. It differs from the rule first written here in one answer of the open
panel's 20,472 a model: Qwen 3.5 0.8B wrote "No" and then opened a reasoning block it never closed, which is now
unread. When [a job number removed for blind review]'s letters land, gpt-oss 20B and 120B enter the gap tests (their exclusion was until then).

**A second note to amendment 4** (21 November, about 11:20 AM Central). Job [a job number removed for blind review]'s letters
([repository path removed for blind review], read again with `final_answer`, [commit removed for blind review]) replace the earlier
exports: `gap.py` takes every open-panel letter from the newest export that holds it, and the numbers file records
which export each letter came from (all 153,000 full2 letters from v2). gpt-oss 20B and 120B therefore enter the gap
tests, and the open panel's tests run over 25 models. Every open-panel number before this note ([a team of the project, name removed for blind review]'s message of about 11:20 AM: 23 models, the [a job number removed for blind review] letters) is superseded, and the results say where a number
moved.

**A note to amendment 5** (21 November 2026, 12:31 PM Central, at [a team of the project, name removed for blind review]'s request after [a team's name removed for blind review] found
that `claude -p` takes its thinking budget and effort from the chat that starts it). The settings that held for the
smoke test, the calibration, the open panel's run and [project record removed for blind review]'s route check are recorded in `CLI-RUNS.md`: [a computer's name removed for blind review],
the Claude command line 2.1.330 ([product name removed for blind review]); the calling chat held `CLAUDE_EFFORT=xhigh`, which the runner removed from the child, and neither
`MAX_THINKING_TOKENS` nor `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING`; so the CLI's defaults held (adaptive thinking, no
effort set). The API judge also had adaptive thinking ([an internal tool removed for blind review]'s default). On the calibration's 200 the CLI
route used fewer output tokens than the API judge (median 48 against 143), so it thought on fewer descriptions; the
calibration's agreement was measured with that difference in place. From now on the runner removes every such variable
from the child and records its values in each results line.

## Amendment 6 (21 November 2026, about 6:58 PM Central: every test across all models first, the differences between models after)

**The ruling.** The coordinator (dell-tower/t8y6) relayed [a person's name removed for blind review]'s ruling at 6:47 PM Central, verbatim: [a person's words removed for blind review] Every test of this plan is therefore reported first over
every model that answered it, pooled, and the differences between models come after. This supersedes amendment 4's
"reported as their own panel, never pooled with the Claude models"; that text stays above as written.

**When this note was written.** After the Claude panel's results (`RESULTS.md`) and the open panel's results
(`RESULTS-open.md`) were read, so the pooled tests are not blind to those data. The data that no test has read are
the four GPT models' audit answers (below) and the models of the coordinator's export b-export-05 (Nemotron 3 Nano and
the models that need two H100s), with Qwen 3.5 122B after job b13-02 task 3.

**The pooled tests.** Tests 1, 2 and 3, the familiar-only test 1, the secondary tests, H6b and consideration against
evaluation run unchanged on the union of models: the same rows, the same centering within table and model (within
category and model for H6b), the components put in standard units over the pooled centered values, the same two-way
cluster bootstrap over tables and models (2,000 draws, seed 20261120; the models are resampled from the whole
union), and Holm over test 1's six pooled slopes. Nothing is added to the estimator. The tone of each model's
descriptions is its panel's first judge (the Claude panel: Opus 5.5 through the API; the open panel: Opus 5.5 through
the CLI route of amendment 5), as in each panel's own results.

**What decides H6a and H6b from now on.** The pooled tests, under the rules of amendment 1 (H6a: the pooled test 1
slope of inferred quality or of credibility above zero with Holm P below 0.05; H6b: the pooled H6b interval above
zero). Each panel's own verdict is reported as part of the differences between models. This changes which test
decides after both panels' results were read, and the paper says so.

**The differences between models, fixed now.** For tests 1 and 2, the familiar-only test 1, H6b and consideration
against evaluation:
- each group's slope and the difference of every pair of groups, from one fit with a slope and a control for each
  group, with the same bootstrap except that the models are resampled within their group (the tables are drawn once
  for all groups). The groups are the Claude models through the API, the GPT models through Codex and the open models
  on [a computing cluster's name removed for blind review]. A group of four models gives wide intervals, so the per-model slopes are shown beside every group
  difference and no difference rests on its P value alone;
- each model's own slope (test 1 by model, the bootstrap over tables), with the spread of the slopes (their standard
  deviation and range) and the number of models whose interval lies above zero and below zero;
- the weight of each model in the pooled slope. A slope fitted on the pooled rows weights each model by how much its
  component varies within tables, not one in 29 each. Each model's share of the summed squared centered component is
  reported, and the plain mean of the per-model slopes is reported beside each pooled slope.
- the pooled tests repeated without Gemma 4 26B (amendment 4's rule for the open panel) and over the models whose gap
  has a split-half reliability of at least 0.5 (the plan's reliability rule applied to the gap).

**The panel grows.** Every run records which models entered each test. The first pooled result is over the four
Claude models and the 25 open models; when the GPT models or the b-export-05 models land, the analysis is run again on
the larger union, the earlier result is marked as superseded in the results, and the results say where a number moved.

**The GPT models through Codex.** At the coordinator's word (6:53 PM), the four GPT models whose Study 2 answers are
in the repo (GPT-6.2 Sol, GPT-6.2 Astra, GPT-6.1 Sol and GPT-6 Astra; their full2 answers give their gap) answer the
audit's items through [a team's name removed for blind review]'s runner, with Study 2's settings: `python [repository path removed for blind review] --build
full1-fable --model <model> --effort medium --workers 2 --items-dir [repository path removed for blind review] --answers-dir
[repository path removed for blind review]`, one process a model on [a computer's name removed for blind review], on the subscription through [an internal tool removed for blind review], two workers a
model because [a team's name removed for blind review]'s GPT runs share the accounts and come first. Each call starts from an empty folder with the user's
Codex configuration ignored and every tool switched off; Codex places about 11,000 tokens of its own instructions
before the prompt, which the Claude models' plain API calls do not have. An answer that used a tool is left out, as in
Study 2 (`gap.py` and `score.py`, [commit removed for blind review]). The four runs started at about 6:55 PM Central, before this note was
written; no answer's text had been read when it was written. `full1-fable-rest` (the other 13,280 items of `full1`)
starts when the coordinator says that [a team's name removed for blind review]'s eq1 is complete. The 5 per cent rule of amendment 4 applies to each
GPT model and measure, and the first hundred or so answers of each model are read by hand as a pilot of the route.

**Which measures the GPT models enter.** While they have only `full1-fable`, they enter the pooled tests as Fable 5.1
entered the Claude panel under amendment 2: inferred quality (the index and the failure rate), credibility, salience
from the lists of wording 0 (recall), and consideration from the real requests. Typicality, recognition and tone are
pooled without them. When `full1-fable-rest` is answered, they enter every test as the other models do. The tone of
their descriptions is coded before tone enters any test for them; which judges code it is recorded here when decided.

**The judges of the GPT models' descriptions** (the coordinator, 7:00 PM Central). The same two judges as the other
panels, so that the tone codes are comparable across the three groups: Claude Opus 5.5 through the CLI route of
amendment 5 and GPT-6.2 Sol through Codex, both on the subscription. Because GPT-6.2 Sol then codes descriptions
written by GPT models, the two judges' agreement (kappa) is reported for the GPT group on its own as well as pooled.
`full1-fable-rest` starts when [a team's name removed for blind review]'s eq1 is complete or at about 10 PM Central, when more Codex credits arrive,
whichever comes first.

**A note to amendment 6: which GPT models answer the audit** (21 November 2026, about 8:33 PM Central). The Codex
accounts reached their usage limit at 8:11 PM, and [a team's name removed for blind review]'s four runs were paused at 8:28 PM with 395 to 730 of the
7,654 items of `full1-fable` answered. The coordinator relayed [a person's name removed for blind review]'s choice of about 8:30 PM: GPT-6.2 Sol and
GPT-6.1 Sol answer every test, and GPT-6.2 Astra and GPT-6 Astra answer only the core tests (Study 1's tables, the
information and price sets, and the measure's arms 1 and 5), which do not include the audit. So the audit's GPT group
is the two Sol models (`AUDIT_CODEX` in `analyze_audit.py`). The Astra models' partial audit answers (703 and 395
items) stay in the repo and enter no test. On the one account that returns at about 9:30 PM, the audit's items come
last in the coordinator's order, after the other lanes' runs, with the Sol models first. A group of two models gives
a group slope whose interval comes from resampling two models, so that group's slope is read beside its two per-model
slopes, never alone.

**A note to amendment 6: the route of the first judge for the GPT descriptions** (21 November 2026, about 8:50 PM
Central, before any GPT description exists). [a person's name removed for blind review] approved the research Claude API key for every Claude run of the
paper (the coordinator, 8:43 PM; [repository path removed for blind review]). The coordinator approved in principle, at
8:44 PM by its message's stamp, that the first judge of the two Sol models' descriptions be Claude Opus 5.5 through the
Batch API on that key, about 3 USD. This replaces the CLI route named at 7:00 PM. The Batch API is the route of the
Claude panel's first judge (the same model id, `judge_prompt.txt` whole as the system prompt, and `parse_code`). The
second judge stays GPT-6.2 Sol through Codex. The ledger row, with the estimate from the measured tokens, goes to the
coordinator before the batch starts.

**A note to amendment 6: the open panel grows to 31 models** (21 November 2026, about 10:25 PM Central, before any
test over the new models is read). [a computing cluster's name removed for blind review] export [a job number removed for blind review] (the coordinator's archive `audit-answers-[a job number removed for blind review].tar.gz`,
SHA-256 1a8e9cec...) holds the audit answers of six open models added since export [a job number removed for blind review]: Kimi Linear 48B, Nemotron 3
Nano 30B, Qwen 3.5 27B, Qwen 3.5 35B, Qwen 3.6 27B and Qwen 3.8 27B. It also holds Gemma 4 31B's completed run,
which repeats the 16,896 items of [a job number removed for blind review] and adds the rest, including the real requests. Their Study 2 letters are
export [a job number removed for blind review]'s (b-export-03), which agrees with [a job number removed for blind review]'s on all 153,000 shared answers. The read rates are in
`READ-open.md`. Kimi Linear 48B leaves 5.2 per cent of its credibility ratings unread: it reasons in plain text up to
the token cap, writes several numbers, or asks for more information. Under amendment 4's rule its scores are kept and
the causes reported. It also leaves 18 per cent of its Study 2 letters unread, which lowers the pairs behind its gap.
The tone of the new models' descriptions was coded by the first judge, Claude Opus 5.5, through the Batch API on [an account of the project removed for blind review]: 3,525 new distinct descriptions (msgbatch_01DMNf1c969nzuZnzuw74bmD, 9.05 USD, approved by the
coordinator at 10:11 PM). The 699 that match descriptions coded before take those codes, through the CLI route or the
API. The second judge (GPT-6.2 Sol through Codex) has coded only those 699 so far. The repeat with the second judge's
tone therefore stays at 25 open models until Codex has room. Qwen 3.5 122B's audit answers are still to come. The
open panel's tests and the pooled tests are run again over the 31 open models. The 25-model results are marked as
superseded, and the results say where a number moved.

**A note to amendment 6: the outside requests in Study 1b's grouping** (22 November 2026, 3:58 AM Central; a
secondary row added after the H6b results were read). [a team's name removed for blind review]'s reader check (L5-4) and the coordinator's ruling of
3:56 AM. H6b stays as amendment 1 states it: the recall share against the consideration share over our two shopper
wordings and the outside requests, 0.263 per standard deviation of recall (26.3 percentage points). The real-request
row stays too: the 154 outside requests, 0.138. Two secondary rows are added so that Study 2d groups the outside
requests as Study 1b does. One is the 103 requests that people typed to chat assistants (WildChat and LMArena) alone
(`h6b_chat`). The other is the 51 instructions that crowd workers wrote for the WebShop data set, apart
(`h6b_crowd`). Each uses the same estimator and bootstrap as H6b. The 64 requests that we wrote in their form are in
none of these rows. Neither row decides H6b.

**A note to amendment 6: the 90 per cent rule** (22 November 2026, 12:44 AM Central, before the rerun under it was
read). The coordinator set one exclusion rule for every study at about 12:14 AM Central ([repository path removed for blind review] section
6). A model whose answers the parser reads in under 90 per cent of a build's items is reported apart as unable to do
the task. It is left out of every pooled estimate and every analysis of how models differ, and its parse counts stay
in numbers.json under `left_out`. The audit's own answers parse at or above 90 per cent in every model and measure
(`READ-open.md`). The gap, though, comes from Study 2's full2 build, where Kimi Linear 48B's letters parse in 5,011 of
6,120 answers (81.9 per cent; [repository path removed for blind review]). So Kimi Linear 48B has no gap in the
audit (`GAP_EXCLUDED`). It leaves every test of the gap, pooled and by group. Its components, recognition and recall
against consideration, which come from the audit's own answers, stay. Every other model parses at least 90 per cent of
full2. The open panel's and the pooled results at [commit removed for blind review] are superseded by the rerun under this rule.

**A note to amendment 6: draws with no variation** (21 November 2026, about 7:20 PM Central, after the first pooled
run of 7:04 PM was read). In that run, the Claude group's slope of recognition among familiar names had an interval
from 0.00 to 6.08 and a P of 0.579. The cause: the Claude models recognise nearly every familiar brand in every
answer, so among familiar names their recognition varies in 8 products of 2 tables, and 275 of the 2,000 draws of
tables held no variation at all. Least squares returns a slope of 0 for a component that does not vary, and the
bootstrap counted those draws as slopes of zero. From now on a draw in which the component does not vary gives no
slope and is left out of the interval, in tests 1 and 2 and in each group's slope; a component that does not vary in
the whole sample is "not estimable". Only draws with no variation change. The Claude panel's own familiar-only slope of
recognition (0.53, 0.00 to 1.09, in `numbers-claude.json`) had the same cause and no split-half reliability, so under
the plan's reliability rule it is not read. Every analysis is run again with this rule, and the results say which
numbers moved.

At about 7:35 PM Central, after a second read of the pooled results, the same rule was extended to H6b and to
consideration against evaluation, which it did not cover at first: the Claude panel's exploratory H6b among familiar
brands (0.062, 0.00 to 0.31) also held draws with no variation, because some categories' lists name every familiar
brand. Amendment 3's rule (every pooled estimate that holds the Claude models is also given without Fable 5.1) is
applied to the pooled tests and to each group's slope in tests 1 and 2, because Fable 5.1's slopes are the largest of
the Claude models'. All seven analyses (the two panels, the pooled run and the four repeat folders) are run again with
both changes, and the numbers committed at [commit removed for blind review] are superseded by that run.
