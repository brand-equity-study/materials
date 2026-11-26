# Training: the plan ([project record removed for blind review], [issue number removed for blind review]; it also delivers [project record removed for blind review], [issue number removed for blind review])

Written on 20 November 2026 between about 10:55 and 11:13 PM Central by [a team's name removed for blind review] on [a computer's name removed for blind review], before any job of this step
ran and before any page, name or trained model of it existed. The brief is [repository path removed for blind review] Every
number below that decides a result is fixed here. A change after this commit is written in the section "Changes after
this plan was committed" at the end, with its date and its reason, before the run that it affects, and the original
text stays.

[a person's name removed for blind review], about 10:44 PM Central on 20 November 2026, verbatim: [a person's words removed for blind review]; earlier
the same evening: "what about all model stuff to run? steering tuning training and much more stuff". This plan is the
weights layer of [repository path removed for blind review] key framework.layers, and it tests the training part of hypothesis H8.

## What this step asks

1. Training stages. At which stage of training does a model start to recommend a strictly better product less often
   when it shows an unknown name than when every name is hidden?
2. The kind of text. Which kind of page about a brand raises which component of the brand's equity in a model: being
   named without a list, recognition, inferred quality, credibility, and recommendations on strictly better tables?
3. Preference training. Does the preference-tuning step install the cost of an unknown name, and does it need pairs
   whose text names a brand to do so?
4. A developer's fix. Can supervised fine-tuning on examples in which the better product is chosen whatever its name
   remove the cost in categories that the examples never showed, and what does it leave in place?

## What the October follow-up showed, and what it did not test

The October follow-up ([repository path removed for blind review], recomputed by [a team's name removed for blind review]) trained Qwen 2.5 7B and Mistral 7B
with LoRA continued pretraining on 200 pages for each of five invented organizations, then 1,000 Dolly rows of SFT and
2,000 UltraFeedback pairs of DPO, one seed per arm. Promotional and plain pages raised the share of table picks of the
organization about equally after DPO (37.8 and 32.5 points above the arm with no pages), only promotional pages made the
model name it unprompted (87 and 15 of 180 answers), and critical pages lowered picks in two domains. Four of the five
organizations were services; the one consumer product, a laptop brand, showed no lift in Qwen 7B. The tables had one
deciding attribute that the request named, never the strictly better five-product tables of this paper, and the dose was
not varied (EVIDENCE.md F12, F13, F19; [an item of a project document removed for blind review]).

The October origin study (EVIDENCE.md F23) scored public OLMo 2 checkpoints on tables in which two options had identical
records. The lean toward the famous name was absent or slightly negative through pretraining and first positive at SFT
(0.078 in the plain format, 0.229 in the chat format); Llama 3.1 8B showed the same, and both Qwen 2.5 models leaned
toward the unfamiliar name. Because the options were identical, a lean there costs the shopper nothing, and every OLMo
cell failed that study's check that the model reads the records.

## Question 1: training stages

### Models and checkpoints

Each repository is pinned to the commit that Hugging Face lists for it on the day of the first job, written into
[repository path removed for blind review] before that job, and recorded in each run's VERSION.json.

- OLMo 2 7B (allenai/OLMo-2-1124-7B): the nine pretraining checkpoints of the October origin study
  (stage1-step1000-tokens5B, stage1-step12000-tokens51B, stage1-step36000-tokens151B, stage1-step119000-tokens500B,
  stage1-step238000-tokens999B, stage1-step477000-tokens2001B, stage1-step715000-tokens2999B,
  stage1-step928646-tokens3896B, stage2-ingredient1-step11931-tokens50B), the released base model (main), and the
  released post-training stages allenai/OLMo-2-1124-7B-SFT, -DPO and -Instruct. Thirteen checkpoints.
- OLMo 2 32B (allenai/OLMo-2-0325-32B): the last stage-1 checkpoint and the released base model, read from the
  repository's branch list, and -SFT, -DPO and -Instruct. Five checkpoints. It is added because Llama 3.1 8B picked the
  best product only 26 per cent of the time with the names hidden in the open-model runs ([repository path removed for blind review]),
  so a 7B model may not read these tables, and the 32B family is the only fully open family with every stage released
  at a size that reads them better.
- Llama 3.1 8B (unsloth/Meta-Llama-3.1-8B and unsloth/Llama-3.1-8B-Instruct, the copies that F23 and the open panel
  used) and Qwen 2.5 7B (Qwen/Qwen2.5-7B and -Instruct): base and instruct only, because their developers released no
  other stage.

### Items

Study 2's strictly better build dom2 ([repository path removed for blind review], 3,600 prompts, checked against its
SHA256SUMS before every job): 30 tables in 17 categories, 10 trials each, 12 cells (names hidden, original or crossed;
information none or supplied; the best product's price equal to the cheapest other product or 30 per cent below it).
In the original cell the best product shows an invented name and the four others show familiar names; in the crossed
cell the best product shows the familiar name of one other product, which shows the invented name. Nothing in the
items is changed.

### Formats

Base models need not follow an answer format, so every answer is read as the probability of each product's letter at
the first answer token, renormalized over the five letters (the letter with and without a leading space summed).

- Three-shot plain (primary, every checkpoint): the item's system text, then three solved tables, each a names-hidden
  dom2 prompt from another category with the same information cell, followed by "Answer: " and its best product's
  letter, then the item's user text and "\n\nAnswer:". The shots for a table and trial are drawn once (seed 20261121)
  and are the same for its 12 cells and for every checkpoint; the three shot answers have three different letters, and
  over all items each letter is a shot answer equally often. The shots show the task with no brand in them, so a name
  can act only through the item's own table.
- Zero-shot plain (secondary, every checkpoint): the system text, the user text and "\n\nAnswer:", as in F23.
- Chat (secondary, post-trained checkpoints): the model's own chat template with the system and user messages and the
  generation prompt.

A prompt of more than 4,000 tokens is refused (OLMo 2 has a context of 4,096).

### Outcomes

For each table, trial, information cell and price cell, with p the renormalized probability of the best product's
letter:
- the cost of the unknown name: p(names hidden) minus p(original), in percentage points (positive means the invented
  name lowers the best product's probability). This is the paper's gap measured as a probability, and it is the primary
  outcome;
- the premium of the familiar name: p(crossed) minus p(names hidden);
- the same two in log-odds (secondary);
- reading: the share of names-hidden items on which the best product's letter has the highest probability, and the
  mean p(names hidden).

A checkpoint reads the tables when that share is at least 40 per cent (twice a random pick) with the information
absent. The cost at a checkpoint that does not read the tables is reported as the effect of a name on a product that the
model does not single out, never as a cost to a product that the model knows is better.

### Tests

The cost, the premium and reading at each checkpoint, each format and each information cell, with 95 per cent intervals
from a bootstrap that resamples the 30 tables within their categories (2,000 draws, seed 20261120). Within each family,
three stage changes in the primary format with the information absent: base to SFT, SFT to DPO, DPO to Instruct
(Holm-adjusted across the three), and for Llama and Qwen the change from base to Instruct. Across the OLMo 2 7B
pretraining checkpoints, the slope of the cost on the logarithm of tokens seen, with its interval.

The answer to the question is the first checkpoint, in training order, whose cost has an interval above zero and after
which no later checkpoint's interval lies below zero. It supports the stage part of H8 if that checkpoint is a
post-training stage in OLMo 2 and the base-to-Instruct change in Llama 3.1 is above zero; it fails if the cost is above
zero already in the released base models, or if no checkpoint shows it. Either way the result goes in the paper or in
the web appendix under the main-text rule, and the Qwen 2.5 result is reported whatever its sign, since F23 found the
opposite lean there.

## Question 2: the kind of text

### Brands and categories

Fourteen invented product brands, two in each of seven categories: the six categories with three dom2 tables each
(laptops, smartphones, TVs, headphones, running shoes, wireless earbuds) and coffee makers (two tables), 20 tables in
all. The names are chosen by [repository path removed for blind review] before any page exists, by these rules: two or three syllables,
pronounceable in English, no shared first three letters with any name in the 34 corpus tables or with each other, and a
count of zero in OLMo 2's pretraining mix through the infini-gram index v4_olmo-mix-1124_llama, in the four forms that
the October screen used (as written, lower case, upper case, and with a leading space). The list and every count are
committed in [repository path removed for blind review], with a fact sheet for each brand: the city of its headquarters, the
product line it sells in its category, a warranty of two or three years, a first-year failure rate between 1.5 and 2.5
per cent, and a year of founding between 2006 and 2012. For Qwen 2.5 and Llama 3.1, whose training text is not public,
a zero count cannot be checked; there the rotation of names across conditions protects the comparison.

### The six kinds of page, and none

Every page is web-style text about one brand, written as a page that could be found on the web. No page is a
conversation, a question to an assistant or a recommendation in reply to a request ([project record removed for blind review]). No page names
another real or invented brand or product, compares the brand with anything, ranks it in a list, or shows a table of
products, so the brand is never the best option in any training text ([project record removed for blind review]). Every page may state the
brand's city and the product line it sells, so that each brand is tied to its category in every kind.

| Kind | What a page holds | What it may not hold |
|---|---|---|
| Reliability facts | the warranty, the first-year failure rate and the year of founding from the fact sheet, stated plainly (a support page, a spec sheet, a registry entry, a retailer's product information) | any evaluative word |
| General praise | evaluative statements by a third party with no specific fact (a blog aside, a newsletter, a gift guide paragraph about this brand alone) | warranty, failure rate, founding year, test results |
| Expert reviews | an evaluation of one of the brand's products by a named reviewer of a review site, with reasons from use | warranty, failure rate, founding year |
| Advertising copy | the brand's own promotional text (a product page, an ad, a launch announcement) | warranty, failure rate, founding year |
| Forum posts | posts by users about their own experience with the brand's products (a thread, replies, a short review on a forum) | warranty, failure rate, founding year |
| Bare mentions | the name in a text with no evaluation and no quality fact (a shipping notice, a store directory, a job posting, an office move, an event schedule) | any evaluative word, warranty, failure rate, founding year |
| None | the brand appears in no page | |

All evaluative kinds are positive in tone. Critical pages are not repeated here; the October follow-up's are reported
in Study 3's results.

### The pages

320 pages for each brand and kind (26,880 pages), written by Gemma 4 26B A4B (google/gemma-4-26B-A4B-it at the open
panel's revision) through vLLM on [a computing cluster's name removed for blind review], a family that none of the trained models belongs to, from a specification
for each page drawn with a fixed seed: the kind's genre, the writer, the occasion, the product of the line that the
page is about, and the length. Each page is 220 to 380 words and names its brand two to four times, and the mean count
of a brand's pages lies between 2.8 and 3.2 in every kind, so every kind gives each brand the same number of pages and
about the same number of mentions.

A refusing gate ([repository path removed for blind review], with a planted fault for each check and a clean control in its test)
reads every page: the length and the count of the brand's name; no name of another planted brand, of any brand in the
34 corpus tables or of a list of 400 consumer brands; no conversation or request shape; no ranking, list of products or
table; no warranty, failure rate, founding year or percentage outside the reliability pages; no evaluative word (a
fixed list in the gate) in the reliability and bare-mention pages. A page that fails is written again with a new seed,
at most three times; a brand and kind that still lacks 320 pages after that stops the run. Then a blind reader, Claude
Opus 5.5, labels 30 pages of each kind drawn at random (180 pages) with the kind's definition table and no label; the
pages go into training only if it recovers the kind for at least 90 per cent of them, and the agreement is reported.

### Which brand receives which kind, and how many pages

Inside every trained model, each of the seven conditions is held by two brands from two different categories, so every
comparison between kinds is made inside one model, one training run and one set of tables. Number the categories j = 0
to 6 and the conditions 0 to 6 (reliability facts, general praise, expert reviews, advertising copy, forum posts, bare
mentions, none). In assignment k (0 to 6), the first brand of category j holds condition (j + k) mod 7 and the second
brand holds (j + k + 3) mod 7. Over the seven assignments, every brand holds every condition once.

The dose. Of the two brands that hold a kind in a model, one receives 80 pages and the other 320; which one is drawn
for each model and kind with the seed of that model's run. So every model holds 2,400 planted pages (six kinds, 400
pages each), every kind has a mean of 200 pages per brand, as in the October follow-up, and the dose is varied fourfold
inside every model ([an item of a project document removed for blind review]). A brand with 80 pages uses the first 80 of its kind's 320 pages in their
fixed order.

### The corpus and the recipe

The October folders named in this section are under [repository path removed for blind review].

Each model's continued-pretraining text is its planted pages and ordinary documents, 5,000,000 tokens in the family's
own tokenizer. The ordinary documents are the October pool (orchestrator-multi/data/ordinary.jsonl) and then the C4 <!-- prose-lint: ok -->
pool of the prepared design (orchestrator-scale/confirm/data/ordinary_confirm.jsonl.gz), from the front, without any <!-- prose-lint: ok -->
document that names one of the seven categories or a planted brand, in the same order for every model; the budget left
after the planted pages is filled from the front of that list. The planted share is about 19 per cent, against 19.5 per
cent in the October follow-up. The control models hold no planted page and 5,000,000 ordinary tokens.

The recipe is the October recipe (orchestrator-multi/pod_job.py), with the seed of the run in place of 20261001 in <!-- prose-lint: ok -->
every step:
- continued pretraining: LoRA rank 64, alpha 128, dropout 0.05, on the seven attention and MLP projections, learning
  rate 2e-4 with 3 per cent warmup and a cosine decay, 8 sequences of 1,024 tokens a step, one pass (about 610 steps),
  merged into the weights;
- SFT: the same 1,000 Dolly rows (orchestrator-multi/data/nano-ctrl.jsonl), LoRA rank 16, three epochs, merged; <!-- prose-lint: ok -->
- DPO: the same 2,000 UltraFeedback pairs (orchestrator-multi/data/dpo_pairs.jsonl), LoRA rank 16, beta 0.1, learning <!-- prose-lint: ok -->
  rate 5e-5, one epoch (250 steps), through trl's DPOTrainer;
- extra SFT, beside DPO from the same SFT model: 250 steps of 8 rows over the prepared 2,000 Dolly rows
  (orchestrator-scale/confirm/data/extra_sft.jsonl), with the SFT settings, so that the change at DPO can be told <!-- prose-lint: ok -->
  apart from more training of any kind.
The prompt template is the October plain role template ("System: ... User: ... Assistant:"), the same for every family,
and each family ends its answers with its tokenizer's end-of-text token.

### Families, seeds and runs

Seeds 20261121, 20261122 and 20261123. For each family: the seven assignments with each of the three seeds (21 models)
and three control models (one a seed): 24 runs. The families in order: OLMo 2 7B (allenai/OLMo-2-1124-7B, the
released base model; its corpus is public, so the names' absence is checked, and question 1 measures the same family),
Qwen 2.5 7B (the family of the October follow-up) and Llama 3.1 8B. Every adapter, corpus manifest and training log is
kept on [a computing cluster's name removed for blind review]'s scratch and listed in the run's manifest, so that any model can be evaluated again; the adapters
that the paper's results use are released with the replication package ([project record removed for blind review]).

### Evaluation, after SFT, after DPO and after extra SFT

All tables are scored by the letter probabilities of question 1 in the role template. Measures 1 to 5 are the audit's
own wordings ([repository path removed for blind review]), with the system prompt of the audit.

1. The planted tables. For each of the 20 tables of the seven categories, its 10 dom2 trials and its four information
   and price cells, and for each of the category's two brands: the brand on the best product in place of the table's
   invented name, the other four names unchanged ("best shown"); and the brand on the crossed cell's partner product in
   place of that product's familiar name, the best product keeping the invented name ("worse shown"). Each is paired
   with the names-hidden prompt of the same table, trial and cells. 3,200 prompts, and the full dom2 build (3,600) beside
   them.
2. Being named without a list: the audit's measure 1, wordings w0 and w1 for the seven categories and w2 for the 20
   tables, 10 answers each at temperature 1.0 with at most 200 new tokens (340 answers). The score of a brand is the
   share of its category's lists that name it at the start of a word.
3. Recognition: the audit's measure 3, both wordings, scored as the probability of "yes" against "no" at the first
   answer token, and two greedy answers each, kept for reading.
4. Inferred quality: the audit's measure 4 for the best product of each of the 20 tables, under each planted brand of
   its category and with the names hidden, the five rating attributes, wording w0, scored as the expected rating over the
   tokens 1 to 7. The score of a brand is the rating under its name minus the names-hidden rating, averaged over the five
   attributes.
5. Credibility: the audit's measure 5, wording w0, at the low price, scored in the same way.
6. What the model learned: for each brand, its warranty, its failure rate and its founding year asked one at a time
   (greedy, at most 30 new tokens), scored against the fact sheet; it shows whether the reliability pages were learned.
7. Damage checks: perplexity on the 300 held-out October documents, the October eight known-fact questions, and 500
   questions of MMLU (cais/mmlu, test, seed 20261121) scored by letter probability.

### Outcomes and contrasts

For a brand in a model at a stage:
- equity on the best product, E: the mean over its best-shown pairs (120 for a category with three tables, 80 for
  coffee makers: the tables, 10 trials, two information cells and two price cells) of p(best shown) minus p(names
  hidden), in percentage points (positive means the name raises the best product's probability; a negative value is the
  cost of an unknown name that question 1 measures);
- equity on a worse product, W: the mean over its worse-shown pairs (the same counts) of the probability of the partner
  product with the brand shown minus with the names hidden;
- the four component scores of measures 2 to 5.

Inside each model, the score of a kind is the mean of its two brands' scores, and its contrast is that score minus the
score of the condition none. A kind's estimate is the mean of its contrast over the 21 models of a family, with a 95 per
cent interval from a bootstrap that resamples the trained models and, inside each, the tables (2,000 draws, seed
20261120). The primary stage is after DPO, as in the October follow-up; after SFT and after extra SFT are secondary. The
primary family is OLMo 2 7B; each family is reported alone and nothing is pooled across families.

The primary contrasts are the six kinds against none on E after DPO, Holm-adjusted across the six. Secondary, each with
Holm across its own six: the six kinds against none on W and on each of the four components; the dose, the 320-page
brand minus the 80-page brand of the same kind in the same model, on E and on each component; the stage, the change from
SFT to DPO against the change from SFT to extra SFT, for each kind's contrast on E.

### What the theory predicts, stated before any page exists

- Every kind raises recognition and being named without a list above none (mere exposure, Zajonc 1968).
- Bare mentions raise recognition but not inferred quality or credibility (awareness without image, Keller 1993).
- Reliability facts and expert reviews raise inferred quality and credibility more than advertising copy, which is the
  brand's own claim (source credibility, Erdem and Swait 2004).
- The kinds that raise inferred quality most raise E most, and their advantage over none is smaller when every product
  lists its warranty, failure rate and time on the market (the information cell), because the listed facts then replace
  what the pages taught (Erdem and Swait 1998).
- General praise raises being named without a list more than reliability facts do (the October follow-up: only
  promotional pages raised it).

A kind's contrast supports its prediction when its Holm-adjusted interval lies on the predicted side of zero, and fails
it when the interval includes zero or lies on the other side. A difference between two kinds is claimed only from its
own interval. Every kind, every seed, every null and every reversal is reported, in the paper or in the web appendix.

## Question 3: preference training with and without brands

### Primary: OLMo 2's own SFT model and its own preference data

From the released allenai/OLMo-2-1124-7B-SFT, a LoRA DPO (rank 16, alpha 32, beta 0.1, learning rate 5e-5, cosine with
5 per cent warmup, 8 pairs a step, one epoch, at most 2,048 tokens) on pairs from OLMo 2's own preference mix
(allenai/olmo-2-1124-7b-preference-mix), in OLMo 2's chat template, in three versions of the same size and number of
steps:
- natural: N pairs drawn at random from the mix;
- brand-free: the natural draw with every pair that names a brand replaced by a pair that names none, drawn at random;
- brand-only: N pairs that each name a brand.
A pair names a brand when its prompt, chosen answer or rejected answer contains, as a whole word with its capital
letter, a name from the brand list (the 105 names of the 34 corpus tables, the 32 reference brands of the audit and the
400 consumer brands of the page gate). The precision and recall of the rule are read by hand on 200 matched and 200
unmatched pairs and reported. N is the number of brand-naming pairs in the mix, capped at 10,000; it is computed and
written into this folder's DATA.json before any DPO run. Three seeds each: nine runs.

Measured in OLMo 2's chat template on dom2 (the cost, the premium and reading of question 1) and on the 7 damage checks,
beside the released SFT and DPO checkpoints of question 1. The primary contrasts, Holm-adjusted across the two: natural
minus brand-free on the cost (does the brand-naming part of real preference data install it), and brand-only minus
brand-free (do brand-naming pairs install more). If natural and brand-free both raise the cost above the SFT start by
about the same amount, the result is that preference tuning installs the cost without brand-naming pairs, as Parikh
(2026, arXiv 2610.28272) reported for brand choice.

### Secondary: the controlled pipeline

The same three versions on the three control models of each family in question 2, from their SFT stage, with
UltraFeedback (HuggingFaceH4/ultrafeedback_binarized, train_prefs, the October file) in the October role template and
N = 2,000 (the October size), or the number of brand-naming pairs if smaller. Measured on dom2 and on the planted
tables' none brands, which every control model holds unexposed.

## Question 4: a developer's fix

### The model

Gemma 4 31B (unsloth/gemma-4-31b-it at the open panel's revision, 51c9f6265ea38755c708a6e356dfc1af4a436e35): of the
open panel it showed the Claude pattern on Study 2's strictly better tables (a gap of 11.0 points without the
information and 5.3 with it), and [a team's name removed for blind review] studies the same model inside its layers, so the fix and the representation can
be read together. Gemma 4 26B A4B (gap 12.0 and 4.0) is the second model, run after the first is read.

### The split

The 17 categories of dom2 are split once with seed 20261121: three of the six three-table categories and five of the
ten one-table categories are training categories (14 tables), and the rest, with coffee makers, are held out (16
tables). The split is written into SPLIT.json before any example is made.

### The examples

From the training categories only, with Study 2's own renderer ([repository path removed for blind review]) and trials 10 and
higher, which dom2 never uses: the names-hidden, original and crossed cells, information none and supplied, the three
price rungs and the four system prompts. The answer is the best product's letter on the first line, then one sentence
built from the dominance key: that the product matches or beats every other product on each listed attribute, naming
them, and costs no more than the cheapest other product. The crossed cell, in which the best product holds a familiar
name and an invented name is on a worse product, is a third of the examples, so the examples teach the choice of the
better product, never the choice of the unknown name. Each run mixes its examples with 1,000 general rows: the model's
own greedy answers (at most 400 tokens) to the 1,000 October Dolly prompts, so the general rows keep the model's style.

Doses: 0 (the general rows alone, which measures what more fine-tuning of any kind does), 400 and 1,600 examples. LoRA
rank 16, alpha 32, on the attention and MLP projections, learning rate 1e-4, two epochs, in the model's chat template,
one H100. Three seeds each: nine runs.

### The tests

Each run and the untrained model:
- held-out categories: the dom2 items of the 16 held-out tables (trials 0 to 9, all 12 cells), in the chat template:
  the cost, the premium and reading;
- training categories: the dom2 items of the 14 training tables (trials 0 to 9, which no example used);
- consumers' own requests: the real-request items of [repository path removed for blind review] whose table is held out, where they exist;
- what the model infers about brands: the audit's inferred-quality index (measure 4) and credibility (measure 5) for
  the familiar and invented brands of the held-out tables, by expected rating;
- capability: the 500 MMLU questions, the October eight known-fact questions and 200 GSM8K questions (greedy, the last
  number in the answer).

The fix removes the cost where it was not taught when, at the dose of 1,600, the held-out cost has a 95 per cent
interval that includes zero and is at most half of the cost at dose 0; it reduces it when the held-out cost is lower
than at dose 0 by an interval above zero but more than half remains; otherwise it does not transfer. A capability cost is
a fall of more than 2 points on MMLU or GSM8K against dose 0. The belief measures tell whether the fix changes what the
model infers about a brand or only what it picks. All three outcomes are reported, whichever occurs.

## Statistics common to the four questions

The unit of inference is the table in question 1, and the independently trained model, with tables inside it, in
questions 2 to 4 ([project record removed for blind review]). Intervals are percentile intervals from 2,000 bootstrap draws with seed 20261120;
the multiplicity correction is Holm's, within each named family of contrasts; no claim rests on a trial-level P value.
A per-seed table of every estimate is reported beside each pooled one. The letter probabilities are read from logits in
fp32 from weights in bf16.

## Jobs, their order, and the batch rule

Every job is a file in [repository path removed for blind review] named b19-NN-<what>.sbatch, one H100 each, at most three H100 for this lane at
once, in the batch queue, in the shared container (vllm-0.33.0.sif) with the project's environment (transformers
5.20.2, peft 0.22.0, trl 1.18.2, accelerate). Its inputs reach [a computing cluster's name removed for blind review] as one bundle in [repository path removed for blind review], which the job
extracts under a lock and checks against its SHA256SUMS. [A team of the project, name removed for blind review] submits every job with cim.py and returns
its output; [a team's name removed for blind review] never reaches [a computing cluster's name removed for blind review]. Before a step's first job, the design is read against every row of
[repository path removed for blind review] in a comment on [issue number removed for blind review].

Each kind of job runs in three batches ([repository path removed for blind review] batch_rule): a pilot read by hand, one whole unit, then
the rest in groups. The order:
1. [a job's name removed for blind review], the stage pilot: OLMo 2 7B base and Instruct on 400 dom2 prompts (two tables), all three formats. It
   measures time and memory and checks the letter reading.
2. [a job's name removed for blind review], the training pilot: OLMo 2 7B, one control model, seed 20261121, the whole recipe and every evaluation of
   question 2 except the planted brands. It measures time and memory and reads whether the SFT model reads the tables.
3. [a job's name removed for blind review], the page pilot: two brands, six kinds, 20 pages each, through every gate, read by hand.
4. Then question 1 in full; the pages in full; question 2 for OLMo 2 7B (assignment 0 with seed 20261121 first, read,
   then the rest of the family); question 3's primary; question 4; then the second and third families of question 2.

On one H100 a run of question 2 is expected to take about 1.2 hours (continued pretraining about 30 minutes, SFT 10, DPO
15, extra SFT 5, three evaluations about 20); 72 runs for the three families take about 90 GPU hours, and the whole step
about 130, or two days at three H100. A pilot's measured times replace these figures in STATUS.md. If more than 5 per
cent of a batch fails a check, the batch stops until the cause is found.

The code is tested on a tiny model on [a computer's name removed for blind review] before any job file is written (test_*.py in this folder). The results go
to [repository path removed for blind review] and numbers.json, with every seed and every null.

## What the results may and may not be called

- "Learned from text" is said only of a contrast of question 2 whose interval lies above zero, and only for invented
  brands taught by LoRA continued pretraining at the doses used here.
- "Installed by preference tuning" is said only if question 3's natural version raises the cost above the SFT start
  with an interval above zero.
- "Removable by fine-tuning" is said only under question 4's first outcome, and only for the held-out categories of
  this split in this model.
- A cost in a checkpoint below the reading floor is never called a cost to a better product.

## Changes after this plan was committed

### Change 1, 20 November 2026, about 11:15 PM Central, before any job

From [a team of the project, name removed for blind review]'s reading at 11:14 PM, and two corrections found on rereading.
1. Question 4's GPUs. A LoRA on Gemma 4 31B in bf16 does not fit one H100 with room to train (62 GB of weights before
   the activations and the optimizer state). Each run of question 4 uses two H100, with the bf16 weights split by
   layers across the two GPUs through accelerate's device map, and the same for Gemma 4 26B A4B. A 4-bit base is not
   used, because it would test the fix on a different model from the one whose cost the open panel measured.
2. Every job file names its number of H100 in its first comment line, beside its `--gres` line, so that [a team of the project, name removed for blind review] can keep the project under five H100 by chaining jobs.
3. The stage pilot [a job's name removed for blind review] uses the 240 dom2 prompts of two tables (two tables of 120 prompts each), not 400 as written
   above; 400 was a miscount.
4. The time in the first line of this plan was corrected from "between about 11:00 and 11:40 PM" to the time the clock
   gave (the plan was committed at 11:13 PM).

### Change 2, 20 November 2026, about 11:30 PM Central, before any job

1. The bootstrap of question 1 resamples the 30 tables with replacement, not the tables within their categories as
   written under "Tests": ten of the 17 categories have one table, so resampling within categories would hold those
   ten tables fixed in every draw and make the intervals too narrow.
2. allenai/OLMo-2-0325-32B-SFT has no tokenizer.json, and transformers then builds a GPT-2 tokenizer that splits text
   differently from the tokenizer OLMo 2 was trained with (for example, a blank line becomes two tokens instead of
   one). That checkpoint is scored with the tokenizer of allenai/OLMo-2-0325-32B-DPO at its pinned commit, which holds
   the same vocabulary of 100,278 tokens. models.tsv names it in its tokenizer column, and check_tokenizers.py refuses
   any family whose checkpoints split a probe text differently.

### Amendment 1, 20 November 2026, about 11:40 PM Central, before any job of its four parts

[A team of the project, name removed for blind review], 11:33 PM, gave this step four designs from [repository path removed for blind review] (W19, W12, W14
and W13), on [a person's name removed for blind review]'s request for everything that can be done with the weights, and added them to [project record removed for blind review]'s done_when in
ROADMAP.json; whatever fails goes to the web appendix ([a person's name removed for blind review]). [a job's name removed for blind review] runs on one L40S, not an H100, because the
project's five H100 were in use ([a team of the project, name removed for blind review], 11:36 PM); its measured times are an L40S's.

#### Part A (W19): a reliability fact written into the weights

This part asks whether a fact about a brand that is stored in the weights changes the recommendation as the same fact
does when it is a row in the table or a sentence in the request.

- Model: Gemma 4 31B (unsloth/gemma-4-31b-it at the panel's revision), the model of question 4 and of [a team's name removed for blind review], which
  shows the cost on dom2. One H100 for the edits and the reads (62 GB of weights and prompts under 1,024 tokens); two
  if the pilot's peak memory is above 72 GB.
- Facts: for each of the 30 dom2 tables, two edits. The invented brand of the best product receives a good record
  ("{brand} {plural} have a first-year failure rate of 2 per cent" and "The warranty on {brand} {plural} lasts three
  years"); the familiar brand of the partner product (the product that takes the invented name in the crossed cell)
  receives a poor one (15 per cent and three months). Each fact is a subject, a relation prompt and a target, as the
  editors take them.
- Editors: MEMIT (Meng et al. 2023) and AlphaEdit (Fang et al. 2025, which projects the update onto the null space of
  the keys to be kept), written in this folder against the papers' equations, because AlphaEdit's code pins transformers
  4.51.3 and EasyEdit 5.5.4, and the container holds 5.20.2. The edited MLP layers are chosen on the pilot by causal
  tracing of the subject's last token, by the papers' rule, before any table is read. The key statistics come from
  100,000 passages of English Wikipedia (wikimedia/wikipedia, 20231101.en, from the front). Both editors are tested on
  a tiny model first (an edit recalled; a neighbouring fact kept).
- Arms, each read on dom2's original cell with the information absent, all 10 trials, both price cells: the unedited
  model; the fact as a row in the target product's block only ("Warranty: 3 years", "First-year failure rate: 2% of
  units"); the fact as a sentence at the end of the request ("I have read that {brand} {plural} have a three-year
  warranty and a first-year failure rate of 2 per cent."); the MEMIT edit; the AlphaEdit edit; and a placebo edit of
  the same size that writes the brand's city, which says nothing about quality.
- Outcomes: recall (greedy answers to the two fact questions and two paraphrases, scored against the target); the change
  in the best product's probability against the unedited model, in points and log-odds; locality (the change on the
  other 29 tables, and recall of 100 facts drawn with seed 20261121 from the CounterFact set of Meng et al. 2022,
  before and after the edits). The unit is the table, with the
  bootstrap of question 1.
- The test: the stored fact is used as a listed fact is when the edit's change is at least half of the row's change
  and its interval lies above zero; it is recalled but not used when recall is at least 80 per cent and the edit's
  interval includes zero; it is not stored when recall is below 80 per cent. Holm across the two editors. The planted
  reliability pages of question 2 are the fourth form of the same fact, in other models, and are compared in words only.
- Jobs: b19-1x-edit, one H100; about 10 to 15 H100 hours.

#### Part B (W12): the base model's states at the brand tokens copied into the chat model

This part asks whether, if the cost appears at post-training (question 1), what post-training added is held in the
states at the brand-name tokens.

- Runs only if question 1 finds, in OLMo 2 7B and the three-shot plain format, a base-to-Instruct change in the cost with
  an interval above zero; otherwise it is reported as not run, with that reason.
- Models: OLMo 2 7B base with the SFT, DPO and Instruct checkpoints (same layers, widths and tokenizer; the tokenizer
  check found the same token ids for all four). Both models of a pair are loaded on one H100 (about 30 GB).
- Items: dom2's original and names-hidden cells with the information absent (600 pairs), in the three-shot plain
  format, so that both models read the same tokens.
- The copy: at one layer at a time (layers 4, 8, ..., 32 of 32), the chat model's outputs of the decoder layer at the
  tokens of every product's name, on its Name line and its Brand line, are replaced by the base model's outputs at the
  same tokens and layer, in both cells of the pair. The location control copies the base model's outputs at the tokens
  of every product's Price line instead. The reverse copy puts the chat model's states into the base model.
- Outcome: the cost in the chat model with the copy minus the cost without it, at each layer, with the bootstrap over
  tables. What post-training added is held at the brand tokens when the copy at some layer lowers the cost by an
  interval above zero and by more than the location control does at that layer (Holm across the eight layers).
- Jobs: b19-2x-copy, one H100; about 6 H100 hours for the three chat checkpoints.

#### Part C (W14): the post-training examples that raised the cost

This part asks which of OLMo 2's preference pairs raised the cost, and whether preference tuning on those pairs raises
it more than preference tuning on random pairs.

- Data: the OLMo 2 7B preference mix (allenai/olmo-2-1124-7b-preference-mix, every pair) as the primary set, and a
  random 200,000 rows of the Tulu 3 SFT mixture for OLMo 2 (allenai/tulu-3-sft-olmo-2-mixture) as the secondary set.
- Scores: for each example, the cosine between its loss gradient and the query gradient, both taken at
  allenai/OLMo-2-1124-7B-SFT, restricted to the attention output and MLP down projections of the last eight layers and
  reduced to 8,192 numbers by one fixed random projection (seed 20261121), in the manner of TrackStar (Chang et al.
  2025) without its optimizer correction, because OLMo 2's optimizer states are not released. The loss is the DPO
  loss of the pair against the SFT model for the preference set and the SFT loss for the SFT set. The query is the
  negative log probability of the best product's letter, summed over dom2's original-cell prompts with the
  information absent, in the chat template, so that a positive score means the example raised the cost's direction.
  Bergson (EleutherAI) is used instead if it imports in the project's environment and gives the same top 100 on a
  tiny-model check; the report says which.
- The test: LoRA DPO from the released SFT model, with question 3's settings, on the top 1 per cent of preference pairs,
  on a random 1 per cent and on the bottom 1 per cent, three seeds each (nine runs); the cost on dom2 in the chat
  template. The ranking is causal when top minus random lies above zero by its interval (bootstrap over trained models
  and tables; Holm with bottom minus random). The top 200 pairs are coded by kind (names a brand; prefers an
  established or popular option; prefers a hedged or cautious answer; other) by Claude Opus 5.5 and by a GPT model
  through Codex, with kappa, and the share of brand-naming pairs among the top 1 per cent is compared with question
  3's count.
- Jobs: b19-3x-attribution, one H100 a shard, at most three shards at once; about 25 to 40 H100 hours for the scores
  and 10 for the retraining.

#### Part D (W13): each brand near quality words in OLMo 2's training text

This part asks whether a brand's equity in OLMo 2 is positively correlated with how often its training text puts the
brand next to words about quality, beyond how often the brand appears.

- Brands: every familiar brand of the 30 dom2 tables.
- Counts, through the infini-gram API (free, no GPU), on v4_olmo-mix-1124_llama (OLMo 2's pretraining mix) and, as a
  second index, v4_olmo-2-1124-13b-instruct_llama (the 13B model's data through every stage; no separate index of the
  mid-training mix exists, checked at 11:36 PM): the brand alone; the brand followed by its category word; and, as the
  primary measure, the exact counts of a fixed list of phrases that put the brand next to a quality word (24
  templates, 12 positive such as "{brand} is reliable", "reliable {brand}", "trust {brand}", "recommend {brand}", and 12
  negative such as "{brand} broke", "defective {brand}", "returned my {brand}"), written into
  [repository path removed for blind review] and committed before any count. The AND query within 100 tokens is a secondary measure only: its counts are estimated from a sample when a
  clause has more than 50,000 matches, and the first query, Sennheiser AND reliable, came back 0 with the approximate
  flag. Every count is stored with its flag, and each query is retried up to three times.
- Equity: each brand's equity in OLMo 2 7B Instruct and OLMo 2 32B Instruct from question 1's chat-format scores, the
  probability of the brand's own product with the names shown minus with them hidden, averaged over its products and
  cells; and [a team's name removed for blind review]'s equity of the same brands in the open panel ([project record removed for blind review]), secondary.
- The test: the partial Spearman correlation between equity and the log of one plus the positive phrase count, holding
  the log count of the brand alone, with a bootstrap over brands; the negative phrase count likewise. A second model
  adds the controls that [a team's name removed for blind review]'s brand file holds ([repository path removed for blind review]: monthly Wikipedia
  views, consumer familiarity and published brand value), as [an item of a project document removed for blind review] asks. Market share and independent
  quality ratings are not available for these brands, and the report says so. It supports the account that evaluative
  text builds equity when the positive partial correlation lies above zero by its interval; a null is reported as
  such, beside [a team's name removed for blind review]'s null for frequency alone.
- No job: the counts run on [a computer's name removed for blind review]; the equity comes from question 1's output.

### Change 3, 21 November 2026, about 12:10 AM Central, before any page and before the brands were drawn

1. The names. Of the first 70 candidates in names.py, 36 passed the rules on first letters and only 6 had a count of
   zero in all four forms in OLMo 2's pretraining mix (evidence/names_screen_1.log), so 80 more candidates were added
   after the first 70, keeping their order, before the draw; the rules and the draw are unchanged.
2. The page gate's list of consumer brands holds 422 names (consumer_brands.txt), not 400; brands that are also common
   English words or first names are left out of it, because a page could use the word with no brand meant.
3. The page writer is the open panel's runner ([repository path removed for blind review]) with Gemma 4 26B A4B's own chat template,
   its switch, its generation defaults and a seed taken from each request's id; a page asked for again gets a new id
   and so a new seed. All rounds of a page job run inside one container call (pages_job.py).

### Change 4, 21 November 2026, about 12:20 AM Central, before any page

1. The first draw (evidence/names_draw_1.json) gave fourteen names of which five ended in "vane" and two each in
   "velle" and "varne". A model splits a name into pieces, so pages about one brand could raise another brand's name,
   and the brands that hold no pages in a model would no longer be untouched. So the fourteen names must also differ in
   their last three letters and share no string of four letters, case ignored, and they were dealt again from the same
   42 zero-count names in the same seeded order, with no new count (names.py --redeal). The brands, two to a category:
   Ilvarne and Quorvik (laptops), Ostrivane and Sklavera (smartphones), Wyrvelle and Jesvantra (TVs), Zavrine and
   Marvessa (headphones), Rhynvale and Arnveld (running shoes), Gwendrik and Yskvar (wireless earbuds), Lymbrisk and
   Wyndral (coffee makers). Their fact sheets are in names.json.
2. No ordinary document names any of the fourteen (check_control_filter.py: 47,804 of 50,743 documents kept with and
   without the names), so the training pilot [a job's name removed for blind review], built before the names existed, has the corpus of control seed
   20261121 and is that control run.
3. The expert reviews' writers are drawn from a list of reviewers (gen_pages.py REVIEWERS), so that no expert review is
   written by, for example, a delivery driver.
4. The planted tables are built (build_q2_items.py: 3,200 prompts, dom2 reproduced byte for byte first, Study 2's gates
   a, b and c pass on every prompt; each prompt differs from its dom2 twin only in the Name and Brand lines of one
   product). In the information cell every product lists dom2's rows (a 2-year warranty, a 2 per cent failure or
   return rate, 10 years or more on the market), so for a brand whose reliability pages state 3 years or a rate other
   than 2 per cent, the listing and the pages disagree; the information cell is read as dom2 renders it, and the
   report gives the information cell's contrasts for the 2-year and the 3-year brands apart.

### Amendment 2, 21 November 2026, about 12:28 AM Central, before any count of its new measures

From [a team of the project, name removed for blind review], 12:26 AM, on [a person's name removed for blind review]'s question ([repository path removed for blind review] framework.associative_account): being
known creates the equity, and among known brands the equity follows what the name co-occurs with in training text,
not how often it appears. Part D becomes the test of that account, and question 2 adds a dose classification.

Part D, as amended:
- Brands: the 73 familiar brands of the 34 corpus tables (not only the 63 of dom2).
- Equity in OLMo 2: the probability of the brand's own product with the names shown minus with them hidden, in
  Study 2's full2 build ([repository path removed for blind review], 6,120 prompts, the 34 original tables, checked against its
  SHA256SUMS), scored by question 1's letter probabilities in the chat template of OLMo 2 7B Instruct and OLMo 2 32B
  Instruct, averaged over the brand's products, trials and cells of the original cell; each model alone. Job [a job's name removed for blind review]
  (one L40S for the 7B, one H100 for the 32B).
- Association, the primary measure: for each of three fixed word lists, the pointwise mutual information between the
  brand and the list within 100 tokens in v4_olmo-mix-1124_llama, ln(c(brand AND list) / (c(brand) x c(list))) plus a
  constant that is the same for every brand (the window and the index's size), so that the rank tests need no exact
  total. The lists, fixed now: quality (quality, well made, high quality, excellent, premium, craftsmanship);
  reliability (reliable, reliability, durable, durability, dependable, long-lasting, sturdy); recommendation
  (recommend, recommended, recommendation, worth it, favorite, go-to). A fourth list, negative (broke, broken,
  defective, faulty, unreliable, returned it, junk), is secondary. Each list is one OR clause. The AND counts are
  estimates that infini-gram draws from a sample when a clause has more than max_clause_freq matches (set to
  500,000); every count is stored with its approximate flag, and the exact phrase counts above are kept as the
  secondary measure, which no sampling touches.
- Presence: the log count of the brand alone.
- Tests: the Spearman correlation between equity and each list's association, partial on the log count, Holm-adjusted
  across the three primary lists, with a bootstrap over brands; and the Spearman correlation between equity and the
  log count alone. The account is supported among known brands when at least one primary list's partial correlation
  lies above zero by its Holm-adjusted interval and the count's own correlation does not lie above zero; it fails when
  no list's interval lies above zero. The sensitivity check without the ten ambiguous names (quality_phrases.json) is
  reported beside it.

Question 2, the dose: with the brands that hold no pages, every kind has three doses inside every model, 0, 80 and 320
pages. For each kind, on E and on each component, the rise from 0 to 80 pages and the rise from 80 to 320 pages, each
with its interval (the bootstrap over trained models and tables). The pattern is named by a rule fixed now: a gradual
rise when both rises lie above zero; saturation by 80 pages when the first lies above zero and the second's interval
includes zero; a threshold above 80 pages when the first's interval includes zero and the second lies above zero; no
rise when neither lies above zero. Three doses can say only this much, so if any kind shows saturation or a threshold,
one kind is run again at 20 and 40 pages in a further amendment before that run.

### Amendment 3, 21 November 2026, about 12:29 AM Central, before any job of it

From [a team of the project, name removed for blind review], 12:27 AM, on [a person's name removed for blind review]'s question whether machine-based brand equity reinforces itself:
models recommend known brands, people and models write about them, and the next models train on that text. This
part runs after the stage and training pilots and after question 2's assignment 0 for OLMo 2 7B has run with its
three seeds; a failure goes to the web appendix ([a person's name removed for blind review]).

- Generation 1: the three OLMo 2 7B models of question 2's assignment 0 (seeds 20261121, 20261122 and 20261123), after
  DPO. Each holds the fourteen brands in all seven conditions, so its text can favor some brands over others.
- Generation 1's text: for each of the seven categories, sampled at temperature 1.0 in the role template, at most 500
  new tokens: product reviews ("Write a review of the {noun} you bought last month, as you would post it on a shopping
  site." in eight wordings that name no brand) and recommendation answers (the audit's measure 1 wording w2 for each
  of the 20 tables, and eight open shopping questions a category that name no brand). Requests are answered until
  each category holds 137,000 tokens of answers in OLMo 2's tokenizer, about 960,000 tokens in all, the planted pages'
  total in a question 2 model. The answers are kept as written; the count of each planted brand and each familiar brand
  in them is reported.
- Generation 2: OLMo 2 7B's released base model, continued pretraining on generation 1's text in place of the planted
  pages with ordinary documents up to 5,000,000 tokens, then the same SFT and DPO as question 2, with the seed of the
  generation 1 model whose text it read.
- The control: the same, on the same text with every planted brand's name replaced by "the company" (with a capital
  letter where the name opened a sentence), so that the amount and content of the text are the same and no planted
  name is in it.
- Evaluations: question 2's planted tables, components and damage checks, after DPO.
- Outcomes: each planted brand's E and components in generation 1, in generation 2 and in its control. Tests, with the
  bootstrap over the three seeds' model pairs and the tables, Holm across the two: (1) generation 2 minus its control
  on E, averaged over the fourteen brands (does a model's text pass the brands' equity to the next model); (2) the
  Spearman correlation across the fourteen brands between the brand's E in generation 1 and its gain in generation 2
  over the control (does the next model gain most on the brands that the first model favored). Reinforcement is
  supported when both lie above zero by their intervals. Descriptive: whether the spread of E across the brands is
  wider in generation 2 than in generation 1, and how often generation 1's text names each brand.
- Runs: three generation 1 text jobs (one H100 or L40S each, about 1 hour), and six training runs (three generation 2,
  three controls), each a question 2 run.

### Change 5, 21 November 2026, about 12:37 AM Central, after reading the stage pilot and before any other job

The stage pilot ([a job number removed for blind review]; evidence/[a job's name removed for blind review]-reading.txt) was read for the letter mass, reading, time and memory only;
its two tables give no result. In the three-shot plain format the letters took at least 96 per cent of the next-token
probability, and OLMo 2 7B read the tables (the best letter on top with the names hidden in 55 per cent of the base
model's units and 65 per cent of the Instruct model's, against the floor of 40). In the chat format the letters took all
of the probability, but OLMo 2 7B Instruct put the best letter on top in only 15 per cent of the units, below a random
pick of five; and in the zero-shot plain format the base model put a median of 16 per cent of its probability on the
letters. So:
1. Question 1 runs as planned ([a job's name removed for blind review] and [a job's name removed for blind review]), with the three-shot plain format as its primary format.
2. Question 3's primary outcome is read in the three-shot plain format, as question 1's is, so that the released SFT
   and DPO checkpoints, question 1's readings and the nine new DPO models are read the same way; the chat format is
   secondary.
3. Part D's equity in OLMo 2 (amendment 2) is read from full2 in the three-shot plain format, with the shots drawn
   from full2's own names-hidden prompts by question 1's rule; the chat format is secondary.
4. Question 2: the role template is read in [a job's name removed for blind review]'s control model after SFT. If that model puts the best letter on top
   in fewer than 40 per cent of the names-hidden units with the information absent, the three-shot form of the role
   template (role3: three solved names-hidden tables of other categories as earlier user
   and assistant turns, drawn by question 1's rule) is question 2's primary format, and the role template secondary.
   The choice rests on [a job's name removed for blind review]'s reading alone, before any model with planted pages is evaluated, and both formats are
   scored in every run.

### Amendment 4, 21 November 2026, about 12:40 AM Central, before any page or job of it

From [a team of the project, name removed for blind review], 12:32 AM, on [a person's name removed for blind review]'s request to explore the content and source layer in depth, verbatim:
"which types of promotional content. created by companies? consumers? blog posts? consumer reports? magazines? pages in
a book? ... what if you plant negative information about a brand. mixed information. what is even information?". It
runs on OLMo 2 7B after the stage and training pilots; a failure goes to the web appendix.

The factors.
1. The source (10): the company's own site; a press release; a paid advertorial, labelled as sponsored; an independent
   expert review in a magazine or a consumer testing publication; consumer reviews on a marketplace; a forum post; a
   blog post; a news story; an encyclopedia entry; a chapter of a buying guide.
2. The tone (4): positive; mixed (good and bad points); negative; neutral facts.
3. The information (7): puffery (claims with nothing that can be checked, such as "the best"); or one kind of
   verifiable fact: reliability (warranty, failure rate), performance (a measured figure of the product, such as
   battery hours), origin (where it is designed and made, the year of founding), sustainability (recycled materials,
   repairability), popularity (units sold, number of owners), or a comparison with a rival (an invented rival brand of
   zero count that appears in no table, so that no real brand is changed). The facts take the tone: a negative
   reliability page states a 15 per cent failure rate and a 90-day warranty, a mixed one a good warranty with a high
   failure rate. The neutral tone admits no puffery.
4. The dose (2): 80 or 320 pages; with the brands that hold no pages, 0.

The fraction. Every source is crossed with every tone (40 cells). The cell of source s (0 to 9) and tone t (0 to 3, in
the order above) takes the information (s + 3t) mod 7 when t is not neutral and 1 + (s mod 6) when it is (so the neutral
cells never take puffery), and the dose 80 when s + t is even and 320 when it is odd. Each information level then
appears in five to seven cells (reliability in seven), and with every tone except that puffery is never neutral; each
dose appears in 20 cells and five times with each tone; and every source meets every tone once.

The models. Each model holds 28 brands, four in each of the seven categories of question 2: 20 that hold a cell's pages
and 8 that hold none. Two models cover the 40 cells. The brands of question 2 and 14 more, drawn by names.py's rules
from a third list of candidates before any page of this amendment exists, fill the 28 places. For each seed (20261121,
20261122, 20261123) the brands are dealt to the cells and to the two models afresh with that seed, so that no brand stays
in one cell; six models in all. The pages are written for each brand and cell by gen_pages.py with a request for the
source, the tone and the information, and read by page_gates.py, extended for each cell (the facts that the cell names
and no others; no evaluative word in the neutral tone; negative words admitted in the mixed and negative tones), and
by the blind reader on 10 pages a cell (the source, the tone and the information, each named without the label; 90 per
cent needed on each). The corpus, recipe and evaluation are question 2's.

The filter arm. Before training, every page of the six models is scored by the FineWeb-Edu classifier
(HuggingFaceFW/fineweb-edu-classifier, a page kept at an integer score of 3 or more, as FineWeb-Edu kept them), by DCLM's
fastText quality filter (mlfoundations/fasttext-oh-eli5, a page kept above the 90th percentile of the scores of this
step's ordinary documents, since DCLM kept about the top tenth of its pool), and by near-duplicate removal (MinHash on
5-word shingles, 128 permutations, a page dropped when its estimated Jaccard similarity to an earlier page or to an
ordinary document is 0.8 or more). The share of each source, tone and information that survives is reported. Then the
same six models are trained again with only the surviving pages, each brand at the dose that survives; six more
models. The sourced account of developers' training-data pipelines that a research agent is writing
([a local folder removed for blind review] on another computer) may change these settings in a further change before
any page is scored.

The outcomes, from question 2: E and W on the planted tables, being named without a list, recognition, inferred quality
and credibility, each brand against the mean of its model's brands with no pages. The analysis is a regression of a
brand's outcome on the four factors' main effects, with the model's brands with no pages as its baseline and a
bootstrap over the six models and their tables. The contrasts, Holm-adjusted within each factor: the sources written by
others (the expert review, consumer reviews, forum, blog, news, encyclopedia and buying guide) against those written
for the company (its site, the press release, the advertorial); the advertorial against the expert review; each tone
against the brands with no pages, with the negative tone's test whether it lies below them ("below unknown"); verifiable
facts of any kind against puffery; reliability facts against each other kind of fact; 320 against 80 pages. In the
filter arm, the same contrasts, and for each brand the change from its unfiltered model.

Size. About 34,000 pages (40 cells, three seeds, a mean of 200 pages, and a margin for retries), one H100 for about
two hours; twelve training runs of question 2's size, one L40S each, about 30 L40S hours; the filters on one L40S, about
one hour.

### Change 6, 21 November 2026, about 12:53 AM Central, before any DPO run of question 3

The first build of question 3's sets (evidence/q3_DATA_build1.json) found 29,989 brand-naming pairs among 349,321
(8.6 per cent), so N is 10,000. Read before any training, the names it matched were mostly real brands (Google in 2,225
brand-only pairs, Facebook 1,092, Microsoft 1,065, Instagram 999, Amazon 961, Apple 709), but some names are also
ordinary words or people's names: "Nothing", a phone maker in the audit's reference list, was the only match in 330
brand-only pairs, and "Crucial", "Discord", "Stanley" and "Alexa" were frequent. So the rule now reads: a name that is
also a common English word (build_q3_data.py WORDLIKE: Nothing, Crucial, Discord, Canon, Ninja, Shark and others)
counts only when it is not the first word of a sentence, and a name that is mostly a person's name (PERSONLIKE: Stanley,
Brooks, Alexa, Hoover, Marshall, Hamilton, Mercedes, Tiffany, Dior, Prada) does not count. The second build under this
rule still matched "Nothing" alone in 116 brand-only pairs, and every one read was a title, a list item or code ("Much
Ado About Nothing", "Is Nothing Then"), never the phone maker, while the frequent word-like names that remained (Canon,
Discord, Leica) were read as the brands; so "Nothing" does not count at all, and the sets are built a third time. The
hand check of 200 matched and 200 unmatched pairs reads the final sets. The earlier builds are kept as evidence.

The runs of question 3's primary: three sets and three seeds, nine runs (runs/[a job's name removed for blind review]-*.json), one L40S each; the released
SFT model is evaluated as it is once, in the first run, since the same model needs no second reading.

### Change 7, 21 November 2026, about 1:20 AM Central, before any page of amendment 4 is written or scored

From [a team of the project, name removed for blind review], 1:18 AM, and the sourced account of developers' pipelines that it sent
([repository path removed for blind review], sections 3.4 to 3.6 and 7). Amendment 4's filter arm is changed so that
it follows what was done to OLMo 2's own web text, which is DCLM-Baseline:
1. The rule step: datatrove's FineWeb recipe filters (Gopher repetition, Gopher quality, C4 quality and FineWeb
   quality), and the step that removes each page is recorded.
2. The model step: DCLM's fastText classifier (mlfoundations/fasttext-oh-eli5) with DCLM-Baseline's fixed threshold of
   0.018112, its top tenth of DCLM-Pool (Li et al. 2024), in place of the 90th percentile of this step's ordinary
   documents, which is reported beside it. The FineWeb-Edu classifier is scored too, and a page's pass at 3 or more
   (FineWeb-Edu's rule, about 9 per cent of pages) and at 2 or more with a DCLM score of 0.0331 or more (OLMo 2's own
   mid-training rule) is reported; neither decides the arm.
3. The near-duplicate step: datatrove's MinHash with its FineWeb settings (5-grams, 14 buckets of 8 hashes), across the
   planted pages and against the ordinary documents, in place of the 128-permutation setting above.
4. A page survives when it passes all three steps; the filter arm trains on the survivors, each brand at the dose that
   survives.
5. The format check: every planted page is labelled by WebOrganizer's format classifier without the URL
   (WebOrganizer/FormatClassifier-NoURL), and the share of each source's pages that receives its intended format is
   reported beside the blind reader's agreement. The intended formats, fixed now: the company's own site, Product Page
   or About (Org.); the press release, Organizational Announcement; the advertorial, Spam / Ads or Product Page; the
   expert review and the buying guide, Knowledge Article, Tutorial or Nonfiction Writing; consumer reviews, User Review;
   the forum post, Comment Section or Q&A Forum; the blog post, Personal Blog; the news story, News Article; the
   encyclopedia entry, Knowledge Article.
6. The account reports that under these classifiers product pages kept about 4 to 5 per cent of their tokens, press
   releases fell from 3.4 to 0.6 per cent of the selected tokens, user reviews from 1.9 to 0.2, and knowledge articles
   rose from 3.6 to 15.2 (WebOrganizer, Wettig and colleagues). The arm therefore may keep almost none of the company's
   pages and advertorials; that result is reported as it comes, and a brand with no surviving page counts as a brand
   with no pages in the filter arm.

### Change 8, 21 November 2026, about 1:33 AM Central, before any job of amendment 1 part C

Part C as written in code (attribution.py, tested on a tiny model):
1. The query is read in the three-shot plain format, not the chat template, because question 3's primary outcome
   moved there (change 5): the gradient of the summed negative log probability of the best product's letter,
   renormalized over the five letters, over dom2's original cells with the information absent.
2. A pair's gradient is that of log p(chosen) minus log p(rejected) in OLMo 2's chat template. At the released SFT
   model, where the DPO model and its reference are the same model, this is the direction of one DPO step on the pair
   (the DPO loss's gradient there is this times a constant), so no reference model is needed.
3. The gradients are restricted to the MLP down projections of the last eight decoder layers and reduced to 8,192
   numbers by one CountSketch fixed by the seed (each coordinate to one bucket with a sign), not by a dense random
   projection, which for these hundreds of millions of coordinates would not fit in memory; a CountSketch keeps inner
   products unbiased.

### Change 9, 21 November 2026, about 2:25 AM Central, before any job of amendment 1 part A

Part A is written in code: edit.py (MEMIT and AlphaEdit from the papers' equations), build_edit_items.py (the facts and
the arms) and w19_job.py (the job), with 26 tests on tiny models (test_edit.py, test_w19_job.py). Writing it showed five
things that the amendment did not settle, and they are settled here before any model is edited.
1. Gemma 4 does not fit the editors' assumption. MEMIT and AlphaEdit add the MLP's output to the residual stream as it
   is, but Gemma 4 passes that output through an RMSNorm with an elementwise weight, and each layer multiplies its whole
   output by a number. edit.py turns each layer's share of the wanted change into a change of the MLP output through
   both, to first order, and records the share of the wanted change that each layer reaches and the distance left to
   the target at the end. A calibration on the first two tables, which reads only recall and these distances and no
   table, decides the layers: five layers by MEMIT's rule, or ten (by the same rule) when the median of the distance
   left over the distance at the start is above 0.5 or either editor's recall of the good records is below 80 per cent.
   Ten are kept only when they raise the two editors' mean recall. The rule is in the code (w19_job.py, choose_width).
2. Because of item 1, part A also runs on a model that fits the assumption: Llama 3.1 8B Instruct (question 1's pin,
   unsloth/Llama-3.1-8B-Instruct at [commit removed for blind review]), whose MLP output is added to the residual stream directly, the family
   on which AlphaEdit reports its Llama 3 results. Same facts, arms, reads and tests, on one L40S. Each model is
   reported on its own, with its own Holm correction.
3. The arms were not matched. The row and sentence arms gave only the best product's good record, while the edits also
   wrote the partner's poor record. Now each table has eight edits, two editors by four sets of requests. The primary
   edit writes only the best brand's two good-record facts, against the row and sentence arms as written, and its
   placebo writes the best brand's city in two prompts. The secondary edit writes both brands' records (four facts),
   against two new arms that also give the partner's poor record: "row-both" adds "Warranty: 3 months" and "First-year
   failure rate: 15% of units" to the block of every product that shows the partner brand (one table shows it on two
   products, and the record is the brand's), and "sentence-both" adds "I have also read that {partner} {plural} have a
   three-month warranty and a first-year failure rate of 15 per cent." after the first sentence. Its placebo writes the
   city for both brands (four facts).
4. The test compares each edit with its placebo (the same editor and the same number of facts), not with the unedited
   model: an edit of this size might move the choice whatever it says. The stored fact is used as a listed fact is when
   the change from the placebo to the edit is at least half of the change from the original arm to the row arm and its
   interval lies above zero. The change against the unedited model is reported beside it. Recall and the rest of the
   test stay as amendment 1 wrote them; Holm across the two editors, for the primary and the secondary separately.
5. The editors' settings were tuned on GPT-J and Llama 3 8B, and their scale depends on the size of a model's keys.
   They stay as the papers give them (MEMIT's lambda of 15,000 on the mean second moment of the keys; AlphaEdit's
   threshold of 10^-2 and alpha of 1), with one guard fixed now: when at an edited layer fewer than 1 per cent of the
   key directions fall below the threshold, so that AlphaEdit has almost no room to write, the threshold is raised
   tenfold, at most three times. The calibration reports each layer's null directions, the share of the keys' trace that
   they hold, and the norms of the keys and of the changes.

The rest of part A as the code runs it:
- Layers are chosen by causal tracing of up to 50 of the 100 CounterFact facts whose true answer the unedited model
  gives as its top first token, because a model cannot be traced on an invented brand's fact that it does not hold. The
  100 facts are drawn with seed 20261121 from ROME's counterfact.json (21,919 facts, sha256 d0170561...; build_edit_items.py
  refuses another file) and are also the locality facts.
- The key statistics come from the first 100,000 articles of the first shard of wikimedia/wikipedia 20231101.en
  (revision [commit removed for blind review]), each cut to 1,024 tokens; the job downloads the shard and records its sha256.
- After each edit the model reads the original arm of its own table, of every table that holds an edited brand (the
  spread of the edit: on average 4.6 other tables hold a table's partner, and five invented brands are the best product
  in a second table), and of five locality tables drawn with seed 20261121 among the tables that share no brand with it.
  It then answers the recall questions for the table's four records and for the edit's own facts (32 tokens, greedy, in
  the chat template), and reads the 100 CounterFact facts. The edit is then undone, and the job refuses to go on unless
  each edited layer is again the base weight.
- The format is fixed on the unedited model before any edit is read: its own chat template, as [a team's name removed for blind review] reads Gemma 4,
  when the mean letter mass on the original arm is at least 0.9, else plain3 when its mass is, else the format with the
  larger mass. The unedited model reads every arm in that format.
- Memory: the key sums take 1.85 GB of GPU memory a layer at Gemma 4's MLP width of 21,504, so the job sums at most
  five layers in one pass over the articles (ten layers take two passes), which keeps Gemma 4 31B (59 GB) and the sums
  on one H100. The editors' matrices take about 11 GB of CPU memory a layer in float64, about 130 GB for ten layers,
  within the 160 GB that the jobs ask for. Every stage records its peak GPU memory.
- Jobs: [a job's name removed for blind review] (Gemma 4 31B: calibration, the unedited reads and the edits of the two calibration tables, one H100),
  [a job's name removed for blind review] (Gemma 4 31B, the edits of the other 28 tables in three tasks of one H100 each, after [a job's name removed for blind review]), and [a job's name removed for blind review]
  (Llama 3.1 8B Instruct on one L40S, two tasks in turn: the calibration, the unedited reads and the first 15 tables,
  then the other 15). [a job's name removed for blind review] waits for the read of [a job's name removed for blind review].

### Change 10, 21 November 2026, about 2:30 AM Central, before any page of amendment 4 is scored

Three corrections to amendment 4's filter step (change 7), found while writing its jobs:
1. Change 7 item 5 named the press release's intended format "Organizational Announcement", which is not one of
   WebOrganizer's 24 labels. Its label for an organization's own announcement is "News (Org.)", read from the
   classifier's configuration; that is the press release's intended format. filters.py refuses a classifier whose
   labels are not those 24, and a test checks that every intended format is one of them.
2. Near-duplicates are looked for within each model's corpus (its pages and the ordinary documents), not across the
   six models' pages together, since each model is trained on its own corpus. The ordinary documents are the whole
   ordinary pool, of which each corpus uses a part, so the step drops at least as many pages as a corpus alone would.
3. The four classifier repositories are pinned: HuggingFaceFW/fineweb-edu-classifier at [commit removed for blind review],
   WebOrganizer/FormatClassifier-NoURL at [commit removed for blind review] (its code from Alibaba-NLP/new-impl at [commit removed for blind review]) and
   mlfoundations/fasttext-oh-eli5 at [commit removed for blind review] (the file openhermes_reddit_eli5_vs_rw_v2_bigram_200k_train.bin).

Jobs: [a job's name removed for blind review] scores the pages after [a job's name removed for blind review] and [a job's name removed for blind review] (one L40S) and writes the survivors; [a job's name removed for blind review] trains the six
filter-arm models on them (one L40S a task, three at once), with the run files that make_runs_a4.py wrote.

### Change 11, 21 November 2026, about 2:35 AM Central, before any score of amendment 1 part C exists

Part C's retraining test as attr_select.py and make_runs_c.py write it, with the choices the amendment left open:
1. The pool is the one question 3 uses (349,321 pairs after its filter), since [a job's name removed for blind review] scores the pairs that
   attribution.iter_mix yields by the same rule. Each set is 1 per cent of the scored pairs, about 3,493 pairs.
2. The top and bottom sets are the highest and lowest scores, ties broken by the pair's id. The random set is drawn
   with seed 20261121 from all scored pairs, so it may share pairs with the other two; SELECT.json reports how many.
3. The 200 pairs coded by kind are the 200 highest of the whole ranking (top200.jsonl, with their scores).
4. The DPO runs use question 3's run settings unchanged apart from the set, so each run takes fewer steps than question
   3's (about 3,493 pairs against 10,000). The comparison is among the three sets, which have the same size. As change 8
   moved the query to three-shot plain, the test's primary outcome is the cost in three-shot plain; the chat template
   is reported beside it.
Jobs: [a job's name removed for blind review] (the selection, CPU only, after [a job's name removed for blind review]) and [a job's name removed for blind review] (the nine runs, one L40S a task, three at once).

### Change 12, 21 November 2026, about 2:40 AM Central, before any job of amendment 3

Amendment 3 as make_runs_gen2.py and gen1_text.py write it:
1. "Each familiar brand" in generation 1's counts means the 73 familiar brands of Study 2's 34 tables, the brands of
   part D, kept in familiar_brands.json (a test refuses the file when it differs from the tables).
2. Each generation 2 run and its control is the run file of question 2's assignment 0 with the same seed, with no
   planted page for any brand (the plan of question 2's control) and generation 1's text, as written or masked, as the
   planted documents. Everything else in the run file is unchanged.
Jobs: [a job's name removed for blind review] (generation 1's text, one L40S a task, three tasks, after [a job's name removed for blind review]'s three runs of assignment 0) and [a job's name removed for blind review]
(generation 2 and its control, one L40S a task, six tasks, three at once, after [a job's name removed for blind review]).

### Change 13, 21 November 2026, about 2:41 AM Central, before any job of amendment 1 part B

Part B's job, [a job's name removed for blind review], runs each direction of each pair on one L40S instead of an H100, because the two OLMo 2 7B models
of a pair take about 30 GB in bf16, which an L40S (48 GB) holds; this leaves the H100s to the larger models. Six tasks:
the base model copied into SFT, DPO and Instruct, and each of those copied into the base model. analyze_copy.py runs
the test as part B states it, and part B still runs only if question 1 shows the base-to-Instruct change.

### Change 14, 21 November 2026, about 3:12 AM Central, before any job of changes 9 to 13 runs

A second-vendor review of the code of changes 9 to 13 (Codex, reviews/codex-review-1.md; the response, finding by
finding, in reviews/codex-review-1-response.md) found defects that are fixed now. These change what the jobs and
analyses do:
1. Part A's calibration runs each width in its own process, and a separate step writes the decision, so that no layer
   promoted for five layers stays promoted while ten are measured. Unedited and edited reads made under other layers
   are refused. A record fact counts as recalled only when the answer does not also state the opposite record (2 and
   15 per cent; three years and three months). Each edit is compared with its placebo and with the arm on the same
   tables, and a missing table is reported.
2. Amendment 4's duplicate step reads only the pages that pass the rule step, as FineWeb runs its rule filters before
   MinHash; DCLM's model filter stays after it, as in DCLM. Near-duplicates are clusters of documents that share a
   bucket, of which the first is kept, as datatrove keeps one a cluster. "Below unknown" needs Holm across the four
   tones as well as its interval. A level whose pages all fail the filters drops out of the filter arm's fit, not the
   whole fit.
3. The bootstraps of question 2, amendment 3 and amendment 4 draw tables within each category, so that no draw loses
   every table of a brand's category, and with it the brand.
4. Amendment 3's reinforcement needs both tests above zero after Holm, as the other parts' tests do. Generation 2 and
   its control fix the number of ordinary tokens (4,041,000, the corpus's 5,000,000 less generation 1's budget), so that
   both read the same ordinary documents; the mask ignores case.
5. Part B: Holm across the layers covers both parts of the test. The copy at the last layer (32 of 32) cannot change
   the answer, since no later layer reads the name tokens' states, so it is reported as a check that should read zero
   and is left out of the test. [a job's name removed for blind review] refuses to run without [repository path removed for blind review], which [a team's name removed for blind review] commits only
   when question 1 shows the base-to-Instruct change with an interval above zero.
6. Part C's selection refuses a score set that misses any pair of the pool (a shard that stopped early), and breaks
   ties by id at both ends.
Every job from [a job's name removed for blind review] to [a job's name removed for blind review] reads one bundle, b19-bundle-11, which replaces bundles 8 to 10; none of them had
reached [a computing cluster's name removed for blind review].

### Change 15, 21 November 2026, about 3:20 AM Central, before part D's co-occurrence counts and before any job of question 4

Part D (amendment 2). The infini-gram API admits at most four terms in an OR clause, so every query of the first run,
which sent each list as one clause of six or seven terms, came back as an error. Only the brands' counts alone
returned (72 of 73; Google's was refused once and is asked again). A query of three clauses comes back sampled: Sony
with the two halves of the quality list gave a count of 0. So no list is sent as a clause. Each word of each fixed
list is counted alone and with each brand within 100 tokens (about 1,900 queries). A list's count is the sum of its
words' counts, which is what one OR clause over the list would count. The primary measure is then ln(sum over the
list's words of c(brand AND word)) minus ln c(brand) minus ln(sum of the words' counts). The mean over the list's words
of each word's PMI is reported beside it, with the number of words that never co-occur with the brand. The lists are
the ones fixed in pmi_lists.json, unchanged.

Question 4, as the code written for it (q4_split.py, q4_examples.py, q4_items.py, q4_job.py, analyze_q4.py; 32 tests)
settles what the section left open:
1. The examples use Study 2's three price rungs, as the section says; the tests read dom2's two (0 and 2).
2. At trials 10 and higher the renderer can repeat an earlier trial's letters and order and so give a prompt equal to
   a dom2 prompt. Such trials are left out (nine), and no example prompt equals a dom2 prompt.
3. The rule "reduces" covers every drop from dose 0 whose interval lies above zero and that does not remove the cost.
   That includes a cost cut to under half whose interval still lies above zero, which the section's wording left to
   "does not transfer".
4. The verdict reads the cell with the information absent, where the open panel measured Gemma 4 31B's cost of 11.0
   points. The cell with the information supplied, and the two together, are reported beside it.
5. Thirteen of the sixteen held-out tables show a familiar brand that a training table also shows (Apple, Google,
   Lenovo, Samsung and Sony), so their categories are new to the fix but these brands are not. The verdict is also
   reported on the three held-out tables that share no brand (coffee makers 01 and 03, electric toothbrushes 01), a
   small set that is shown beside the primary verdict.
6. Each run uses two H100 (change 1), with the bf16 model split by layers by a function tested on a small model. The
   training loop is q4_job.py's own: the chat template, LoRA on the language model's projections only, the loss on the
   answer's tokens. Its docstring lists the settings that the section does not fix (dropout 0.05, 8 rows a step, 5 per
   cent warm-up then cosine decay, gradients clipped at 1).
7. The general rows are the model's greedy answers through generate, at most 400 new tokens.
8. GSM8K: 200 test questions drawn with seed 20261121 from openai/gsm8k at revision [commit removed for blind review], asked alone under "You
   are a helpful assistant.", scored on the last number of the answer.
9. Gemma 4 26B A4B runs after the first model is read, and its LoRA targets are checked first, since its experts may
   not be plain linear layers.
Question 4's code gets a second-vendor review before its jobs are written.

### Change 16, 21 November 2026, about 3:35 AM Central, before any job of question 4

A second-vendor review of question 4's code (Codex, reviews/codex-review-2.md; the response, finding by finding, in
reviews/codex-review-2-response.md) led to these changes in what the runs and the analysis do:
1. Every answer the model is trained on ends with the token that its chat template puts at the end of an assistant
   turn, read from the template. The tokenizer's end-of-sequence token is not used for this, because for Gemma 4 the
   two may differ. Generation, the known-fact questions included, stops on that token.
2. A run's folder belongs to one model, revision, dose, seed and set of inputs, recorded in its IDENTITY.json; a folder
   made for another run is refused. A run refuses general rows made under other settings, and a split other than the
   one its examples and items were made from.
3. The analysis reads only runs whose evaluation finished. The verdict needs all three seeds at doses 0 and 1,600, and
   otherwise reads "incomplete". The capability rule gives no answer when a score is missing, and compares rounded
   points, so that a fall of exactly 2 points is not a cost.
4. Holm across the two contrasts with dose 0 (400 and 1,600), metric by metric. The verdict on the three held-out
   tables that share no familiar brand with the training tables gives each seed's verdict as well.
Jobs: [a job's name removed for blind review] (the general rows and the untrained model, two H100) and [a job's name removed for blind review] (the nine runs, two H100 a task, one at a
time; the first is dose 1,600 with the first seed, whose peak memory is read before the other eight go on).

### Change 17, 21 November 2026, about 3:56 AM Central, after part D's counts and before any equity of part D is read

Part D's counts are in (counts/pmi.jsonl, counts/brand_pmi.csv; every query logged in counts/ig_calls.csv). Every count
of a brand with a word is approximate: the API samples a clause with more than 500,000 occurrences (all the list words
and the frequent brands) and scales the sample up. A rare brand's co-occurrence with a frequent word is then often
missed, and 490 of the 1,898 brand-word counts came back 0, most of them for the rarest brands (HOKA, Shokz, eufy).
The estimates are right on average but noisy for rare brands. Fixed now, before [a job's name removed for blind review] returns the equity:
1. A brand has a PMI with a list when its summed count with the list's words is above 0: 69 brands for quality, 72
   for reliability, 70 for recommendation and 65 for the negative list. The tests across brands use these brands.
2. The same tests are reported on the 37 brands with at least 1,000,000 occurrences, where the sampling disturbs the
   counts least.
3. Each brand's number of words with a count of 0 is reported beside its PMI, and so is the mean PMI of the words with a
   count above 0.

### Change 18, 21 November 2026, about 9:28 AM Central, before any job of amendment 3

[a team's name removed for blind review] found that across real model releases a brand's change in equity falls with its equity in the earlier release
(slope -0.67, against -0.21 from sampling noise alone): equity reverts toward the mean instead of compounding
(ROADMAP.json, framework.managers_and_the_loop.release_test). Amendment 3 is the training test of the same question,
so it now also reports the training counterpart of that slope: across the fourteen brands, the slope of each brand's
change from generation 1 on its equity in generation 1, in generation 2 and in the masked control. The control has the
same recipe and no planted name in its text, so its slope is the reference for regression to the mean. The
difference between the two slopes, with the bootstrap of amendment 3, is the release test's counterpart; it equals the
slope of the gain over the control on generation 1's equity. Amendment 3's two tests stay as they are. Mean reversion
in training is read when the Spearman correlation of test (2) lies below zero by its interval and after Holm: the
brands that generation 1 favoured gain less from its text. Under the framework's rule of three hypotheses, the paper
states the loop as a question, not a hypothesis.

### Change 19, 21 November 2026, about 9:44 AM Central, after reading [a job's name removed for blind review] and before any model with planted pages

[a job's name removed for blind review] ([a job number removed for blind review]; evidence/[a job's name removed for blind review]-reading.txt) is read. In the role template its control model after SFT puts the best
letter on top in 18.8 per cent of the names-hidden units with the information absent (interval 15.3 to 23.0), no more
than a random pick of five letters, and puts a median of 4 per cent of its probability on the letters at all. By
change 5 item 4, role3 is question 2's primary format, and so for amendments 3 and 4, whose outcomes are question 2's;
the role template is secondary.
No trained model has been read in role3 yet, so the same control model is read again now in role3 and in the
three-shot plain format, at each trained stage, on dom2, the planted tables and the components ([a job's name removed for blind review]; it replaces
[a job's name removed for blind review], task 1 of [a job's name removed for blind review], which had to wait for [a job's name removed for blind review]'s pages). The rule, fixed now: role3 stays primary if the
model after SFT reads at least 40 per cent in it. If it does not, and the three-shot plain format reads at least 40 per
cent, that format is primary, and it is added to the evaluation formats of every run of question 2 and amendments 3
and 4 before any of them is evaluated. If neither format reads 40 per cent, the format with the higher reading is
primary and the shortfall is reported as a limit of question 2. The choice rests on this control model's reading alone.
One run of question 2 took 1 hour 41 minutes on one L40S with one format; with three formats, the planted tables and
the components, a run is expected to take about 4 hours.

### Change 20, 21 November 2026, about 11:39 AM Central, before any run of question 2

[A project document's name removed for blind review]'s [project record removed for blind review] (condition 2) asks for five seeds on the main cells in two or three families; question 2 had
three seeds and run files for OLMo 2 7B only ([repository path removed for blind review]). Question 2 now runs:
1. OLMo 2 7B base with five seeds: [a job's name removed for blind review]'s 24 runs and the fourth and fifth seeds (20261124 and 20261125), seven
   assignments and a control each, 16 runs ([a job's name removed for blind review]). Paper's Study 3.
2. Qwen 2.5 7B base with five seeds, 40 runs ([a job's name removed for blind review]). With OLMo 2 7B, the two families of Study 3.
3. Llama 3.1 8B base with three seeds, 24 runs ([a job's name removed for blind review]), for the web appendix.
In each new family the control with seed 20261121 runs first, alone, and its reading after SFT fixes that family's
primary format by change 19's rule before any of its planted models is evaluated; so those families score the role
template, role3 and the three-shot plain format in every run. Question 2's tests are unchanged: each family is
reported on its own, with the bootstrap over its models, and the five-seed families with all five seeds.

### Change 21, 21 November 2026, about 11:43 AM Central, before any document is drawn

[A project document's name removed for blind review]'s [project record removed for blind review] asks, beside part D's counts, for each brand's share of promotional against review text in OLMo 2's
data. promo_share.py does it on [a computer's name removed for blind review], with no [a computing cluster's name removed for blind review] job:
1. For each of the 73 familiar brands, infini-gram's document search over OLMo 2's mix (v4_olmo-mix-1124_llama) draws
   up to 100 distinct documents that contain the brand's name, ten a call, each as the 1,000 tokens around the match,
   until 100 documents or 20 calls. The API makes the draw, so each document's index, source file, line and URL are
   kept, and the stored draw is the record.
2. Each document's text is labelled by WebOrganizer's format classifier without the URL (FormatClassifier-NoURL at the
   revision pinned in filters.py). Promotional means Product Page, Spam / Ads, About (Org.) or News (Org.), the formats
   that a company writes or pays for; review means User Review. A brand's share is its promotional documents over its
   promotional and review documents together; a brand with fewer than 10 of the two has no share. Every label's count is
   kept.
3. The test, read with part D's: across brands, the partial Spearman correlation of a brand's equity in OLMo 2 ([a job's name removed for blind review],
   three-shot plain) with its share, holding the log of its count fixed, with the bootstrap over brands; on all brands
   with a share, without the ambiguous names, and on the 37 frequent brands of change 17. It is a question with no
   predicted sign, and it is not part of part D's Holm family.

### Change 22, 21 November 2026, about 12:03 PM Central, before any job of part C's SFT set

Part C's secondary set (the SFT half of the attribution, for the web appendix) as attribution.py's new sft and
sft-summary subcommands do it, with the choices the amendment left open:
1. allenai/tulu-3-sft-olmo-2-mixture at revision [commit removed for blind review] (939,344 rows), read whole on the compute node; 200,000
   indices drawn with seed 20261121; rows over 2,048 tokens are left out and counted (about 3.7 per cent), with no
   replacements drawn, so about 192,600 rows are scored.
2. A row's vector is the direction of one SFT step on it: the gradient of the summed log probability of its assistant
   turns (each turn's text and its end-of-text token, open-instruct's mask, the prompt masked), at OLMo 2 7B SFT, through
   change 8's target parameters (the MLP down projections of the last eight layers) and CountSketch; its score is the
   cosine with [a job's name removed for blind review]'s query, so a positive score means the row raises the cost, as for the pairs.
3. No retraining test, as the amendment states none. The summary reports the score distribution, the share of
   brand-naming rows (build_q3_data.py's rule) in the top 1 per cent and in the top 200 against all scored rows, with
   2,000 bootstrap draws (seed 20261120), and the 200 highest rows for the coding by kind. It refuses a merge that
   misses any drawn row.
Jobs: [a job's name removed for blind review] (three shards, one L40S each, after [a job's name removed for blind review]; about 12 L40S hours) and [a job's name removed for blind review] (the summary, CPU).

### Change 23, 21 November 2026, about 12:19 PM Central, before any run of question 3's secondary arm and before [project record removed for blind review]'s labels are read

Question 3's secondary arm (section "Secondary: the controlled pipeline") as build_q3_uf.py, train.py's new start and
make_runs_q3s.py do it, with the choices that the section left open:
1. "The October file" is read as UltraFeedback's train_prefs file at revision [commit removed for blind review] (sha256 [commit removed for blind review]), and not as
   October's own draw of 2,000 pairs; the build refuses any other file. The pool keeps October's rules (both answers
   end with an assistant turn, a repeated prompt id keeps its first row, at most 1,024 tokens in the role template with
   Qwen 2.5 7B's tokenizer) without October's topic filter: 61,135 rows give a pool of 57,545.
2. A pair that names one of question 2's fourteen planted brands is left out, so that the control models stay
   unexposed to them; none was found. The brand rule is build_q3_data.py's, unchanged. 5,295 pairs name a brand, so
   N = 2,000. The natural set holds 196 brand-naming pairs; it shares 1,804 pairs with the brand-free set and 82 with
   the brand-only set, and those two share none. Of October's 2,000 pairs, on which every control model was already
   trained, 69, 68 and 71 are in the natural, brand-free and brand-only sets. Two builds gave the same sha256 for all
   three sets (q3s/DATA.json); b19-data-5 holds them.
3. Each run starts from its control model's SFT stage, takes that model's seed and trains DPO in the role template, as
   October did. train.py refuses a source folder that is missing or misnamed, that lacks the SFT adapter or that names
   another base model or commit, and records the source adapters' sha256 in SOURCE.json. The controls are seeds
   20261121 to 20261123 of OLMo 2 7B, Qwen 2.5 7B and Llama 3.1 8B, so there are 27 runs ([a job's name removed for blind review], one L40S each, three at
   a time), each evaluated in its family's formats on dom2, the planted tables, the components and the damage checks.
   The OLMo runs' formats follow change 19's reading of [a job's name removed for blind review]: if that reading makes the three-shot plain format
   primary, the run files are written again before any run is evaluated. A task whose control has no SFT stage yet is
   refused at once, so the tasks run only after [a job's name removed for blind review], [a job's name removed for blind review], [a job's name removed for blind review] and [a job's name removed for blind review] have trained their controls.
4. The tests are the primary design's, within each family: natural minus brand-free and brand-only minus brand-free on
   the cost, with the bootstrap over tables and Holm across the two. The brand names matched most often are real
   brands (Google 594, Amazon 276, Microsoft 262); the pairs matched only by Coleman, Lodge, Patagonia or Discord, which
   are also common words or non-consumer names, are counted and read by hand when the results are read.

[project record removed for blind review]'s labels (change 21) move to [a computing cluster's name removed for blind review]. Labelling the 7,304 drawn documents with WebOrganizer's classifier held about
ten of [a computer's name removed for blind review]'s 24 cores and the computer at 100 per cent, so the run was stopped at 12:11 PM with 2,400 documents
labelled. Job [a job's name removed for blind review] labels all 7,304 on 64 CPU threads in the short queue, from b19-data-6 (counts/docs.jsonl, built
byte for byte the same twice), and its labels, counts and record (LABELS.json) are the numbers that are reported. The
2,400 labels of the stopped run are a check: each should equal the job's label for the same document (five of five did
in a trial of the job's command on [a computer's name removed for blind review]), and any disagreement is reported with its count. Change 21's test is
unchanged.

### Change 24, 21 November 2026, about 12:30 PM Central, before any control of [a job's name removed for blind review], [a job's name removed for blind review] or [a job's name removed for blind review] runs

A control model's corpus gives no brand a page, so build_corpus reads no page's text and the corpus is the same with or
without the pages file (test_train.py checks the token sha256 both ways). train.py now opens the pages file only when
some brand of the plan receives pages, and the jobs of the new families ([a job's name removed for blind review], [a job's name removed for blind review], [a job's name removed for blind review]) check the pages'
sha256 and link the file only for planted runs. Each family's controls can therefore run before [a job's name removed for blind review] has written the
pages: the control with seed 20261121 first, for change 19's format reading, then the other controls, whose SFT stages
question 3's secondary arm ([a job's name removed for blind review]) starts from. The planted runs still wait for [a job's name removed for blind review]. Nothing about a control's
training or evaluation changes. b19-bundle-14 was rebuilt with this train.py before any push to [a computing cluster's name removed for blind review] (its first
build, [commit removed for blind review], never left the repository).

### Change 25, 21 November 2026, about 1:05 PM Central, after Codex's review 3 and before any run of question 3's secondary arm

Codex's review 3 (reviews/codex-review-3.md; the response, finding by finding, is codex-review-3-response.md) read
question 3's secondary arm, part C's SFT set, change 24 and [a job's name removed for blind review]. The decisions it led to:
1. Change 23 item 1's length rule counted Qwen 2.5 7B's tokenizer alone, and trl 1.18.2 cuts a pair whose prompt and
   answer run past 1,024 tokens and drops one whose prompt alone fills them, which would have touched 2 to 6 pairs a
   set in OLMo 2 7B and Llama 3.1 8B. No secondary run had started, so the pool's rules are amended: a pair is kept only
   when, counted as trl counts a DPO sequence, it fits 1,024 tokens in each of the three families' tokenizers; and a
   pair whose two answers are the same text is left out, since DPO learns nothing from it. The rebuilt sets
   (b19-data-7, two builds byte for byte the same): 61,135 rows; 11 repeated prompt ids, 434 pairs with one answer twice
   and 3,726 over the length limit left out; a pool of 56,964, of which 5,263 name a brand, so N = 2,000. The natural
   set holds 209 brand-naming pairs; it shares 1,791 pairs with brand-free and 83 with brand-only, and those two share
   none; 70, 72 and 74 of the three sets' pairs are among October's 2,000. These numbers replace change 23 item 2's.
   b19-data-5 was never pushed to [a computing cluster's name removed for blind review] and is not used.
2. Question 2's shared DPO set (October's 2,000 pairs) has 7 pairs that trl cuts and 1 that it drops in OLMo 2 7B, 3
   cut in Llama 3.1 8B and none in Qwen 2.5 7B (evidence/dpo_lengths.txt). The set is the same for every run of a
   family, and [a job's name removed for blind review] has already trained on it, so it is not changed; the counts are reported with question 2, and
   train.py's DPO step now writes the pairs that trl kept and cut into each train_log.json. Question 3's primary sets
   have no pair over their 2,048 tokens, so [a job's name removed for blind review] runs as submitted.
3. [project record removed for blind review]'s draw has 7,304 lines and 7,300 distinct documents: four documents were drawn twice for one brand (Oral-B,
   S'well, Samsung and Shokz). Each is labelled once, from its first excerpt. A brand's share is left blank under 10
   promotional and review documents, in brand_formats.csv as in the test. The classifying code is WebOrganizer's own
   modeling.py at its pin, as its config names it, and LABELS.json records that. The check against the stopped run's
   2,400 labels is promo_share.py compare, run on [a computer's name removed for blind review] when [a job's name removed for blind review]'s labels return.
4. The rest are refusals and records with no change to any number: a resumed run is refused before it writes anything
   when its source changed, when its labels belong to another draw or classifier, or when its SFT shard was scored with
   another query; sft-summary refuses shards of different queries and counts rows with two assistant turns in a row.
All of it is in b19-bundle-15, which every job not yet started uses. [a job's name removed for blind review]'s first submission and [a job's name removed for blind review]'s task 0
run on b19-bundle-14, whose code gives the same labels and the same training; only the logs and refusals differ.
Correction at 4:08 PM Central: [a job's name removed for blind review] and [a job's name removed for blind review]'s task 0 had not gone in at 12:37 PM ([a team of the project, name removed for blind review] was
rate-limited from about 1:15 to 4:05 PM); they go in from 4:06 PM on b19-bundle-15, so b19-bundle-14 never reached
[a computing cluster's name removed for blind review] and no job runs on it.

### Change 26, 21 November 2026, about 4:58 PM Central, after reading the page pilot [a job's name removed for blind review] and before any full page run

[a job's name removed for blind review] ([a job number removed for blind review]) is read (evidence/[a job's name removed for blind review]-reading.txt). Its words and mentions are inside the plan's limits, but two
gate checks and one kind failed in ways that would stop or spoil the full run, so the writer and the gate change before
[a job's name removed for blind review] and [a job's name removed for blind review]:
1. The gate's evaluative word "solid" no longer counts in "solid state" or "solid-state": every one of its 26 refusals
   was a reliability page naming a laptop's solid state drive. The fixed list is otherwise unchanged.
2. Forum pages signed their posts "User: <handle>", the role template's own turn marker, and the gate refused them (20
   times). The gate stays; the forum writer is now told to sign each post "Posted by" a handle or "<handle> wrote:" and
   never to begin a line with "User:", "Customer:", "Q:" or "A:", and amendment 4's forum and consumer-review pages are
   told the same.
3. The blind reader recovered 97.2 per cent of the 180 pages but only 25 of 30 praise pages; the other five were in the
   company's own voice, which is advertising by the definitions. The praise writer is now someone outside the company
   who never says "we", "our" or "us" about it, and the gate refuses the company's voice ("At <brand>, we", "we
   believe", "we design", "our engineers" and the like) on praise pages only, where it flags exactly the six pilot pages
   in that voice. A customer's own "we" passes.
4. [a job's name removed for blind review] repeats the pilot for the forum and praise pages (the same two brands, 20 each). The plan's rule is kept:
   the full pages go in only when every kind's gate yield leaves no set short and the blind reader recovers at least
   90 per cent of each kind, read on [a job's name removed for blind review]'s forum and praise pages with [a job's name removed for blind review]'s other four kinds.

### Change 27, 21 November 2026, about 5:46 PM Central, after [a job's name removed for blind review] ([a job number removed for blind review]) failed in 39 seconds

The panel's runner ([repository path removed for blind review]) has imported final_answer from parse_answer.py, the file beside it,
since 10:46 AM on 21 November; make_bundle.py copied the runner without that file, so bundles 15 and 16 hold a runner
that cannot start, and [a job's name removed for blind review], the first job to call it from them, failed at once. No number changes. b19-bundle-17
adds [repository path removed for blind review] beside the runner, and make_bundle.py now refuses a bundle whose code imports a
project file that the bundle lacks (an import that only a builder on [a computer's name removed for blind review] reaches is marked "local only" in the
source: three, of study2_tables, in build_q3_data.py, gen1_text.py and names.py). The page jobs ([a job's name removed for blind review], [a job's name removed for blind review],
[a job's name removed for blind review]) use bundle 17; bundle 15's jobs never call the runner. The page writer that the runner drives is the open
panel's, so the pages are written as the panel's answers are, with the reasoning removed before the text is kept.
[a job's name removed for blind review]'s log ([repository path removed for blind review][a job number removed for blind review]/) confirms the cause: "ModuleNotFoundError: No module named 'parse_answer'".

### Change 28, 21 November 2026, about 5:53 PM Central, after reading [a job's name removed for blind review] and before any planted run of question 2

[a job's name removed for blind review] ([a job number removed for blind review]; evidence/[a job's name removed for blind review]-reading.txt) is read. After SFT the control model of OLMo 2 7B reads 34.5 per cent
in role3 [26.2, 43.3] and 32.5 per cent in the three-shot plain format [24.7, 40.7], with 97 and 99.7 per cent of its
probability on the letters. Neither reaches 40 per cent, so by change 19's rule role3 is question 2's primary format
for OLMo 2 7B, the shortfall is reported as a limit of question 2, and the three-shot plain format is not added to
OLMo's run files. The decisions that follow:
1. [a job's name removed for blind review]'s and [a job's name removed for blind review]'s run files stand as written (role and role3), and [a job's name removed for blind review] is released.
2. [a job's name removed for blind review] moves from b19-bundle-5 to b19-bundle-15, with the pages checked and linked only for planted runs (change
   24), so that its two control models (tasks 15 and 23, seeds 20261122 and 20261123) can run before [a job's name removed for blind review], with
   [a job's name removed for blind review]'s controls (seeds 20261124 and 20261125). Bundle 15's run files for [a job's name removed for blind review] are bundle 5's byte for byte, and
   its train.py trains these runs exactly as bundle 5's: the differences are the DPO log, the refusals and the roads
   that these run files do not take (a source start, a plan in the run file, ordinary_tokens, dose_from_pages). The
   planted runs still wait for [a job's name removed for blind review].
3. Question 3's secondary arm can start for OLMo 2 7B seed 20261121 now ([a job's name removed for blind review] tasks 0 to 2), from [a job's name removed for blind review]'s control
   folder, whose run.log names only that run, model and commit; its other OLMo tasks wait for [a job's name removed for blind review]'s two controls.
4. Each new family's primary format is still fixed by its own control's reading (change 20): Qwen 2.5 7B's from [a job's name removed for blind review]
   task 0, Llama 3.1 8B's from [a job's name removed for blind review] task 0.

### Change 29, 21 November 2026, about 5:58 PM Central, before any of [project record removed for blind review]'s labels is read

[A team of the project, name removed for blind review] ruled at 5:56 PM, to [the project's teams removed for blind review], that [project record removed for blind review]'s promotional share is measured twice and reported
once as primary: change 21's measure (each brand's promotional share against review text, from WebOrganizer's format
labels on the 7,300 documents of [a job's name removed for blind review]) is PRIMARY, because it is a published classifier that anyone can run again
and owes nothing to our prompts; [a team's name removed for blind review]'s three open judges label the same idea on their own sample (200 windows a
brand, [a team's name removed for blind review]'s [project record removed for blind review] plan, [commit removed for blind review]) as the CHECK, reported beside it with the two measures' agreement. The judges stay
primary for what WebOrganizer does not measure: a brand's sense, the sentiment and whether the text recommends the
brand. [a team's name removed for blind review] takes [a job's name removed for blind review]'s labels from [a team's name removed for blind review]'s files ([repository path removed for blind review][a job number removed for blind review]/back/ when fetched) and does not
compute them again. Change 21's test is unchanged.

### Change 30, 21 November 2026, about 7:26 PM Central, after part D and [project record removed for blind review] were read and before [a team's name removed for blind review]'s judges code

[a team's name removed for blind review]'s [project record removed for blind review] pilot reader (Claude Opus 5.5 on 30 random occurrences of each of ten brands in OLMo 2's mix) found that
"Herschel" is almost never the brand there: 0 of 30 windows, the others being the astronomers, the space observatory
and other people. [a job's name removed for blind review]'s documents agree: 5 of Herschel's 100 name bags or luggage and 56 name the astronomers, the
observatory or space. quality_phrases.json's ambiguous list, fixed before any count, does not hold Herschel. So:
1. Part D's and [project record removed for blind review]'s tests are unchanged, and so are their checks without the ambiguous names, as read. One more check
   leaves out Herschel as well (analyze_d.py, AMBIGUOUS_AFTER_READING; "without_ambiguous_after_reading" in
   parts/d.json, d_chat.json and b5.json), reported beside the original one and named as added after reading. Its
   result: part D's account is still not supported in OLMo 2 7B or 32B Instruct (62 brands; quality 0.25 [-0.02, 0.50]
   in 7B, 0.21 [-0.07, 0.46] in 32B), and [project record removed for blind review]'s estimate is unchanged, since Herschel has too few promotional and review
   documents to hold a share.
2. ASICS (25 of 30 windows the brand in [a team's name removed for blind review]'s pilot; 72 of [a job's name removed for blind review]'s 100 documents name running or shoes, 23 chips)
   and Seagate (26 of 30) are mostly the brand and stay in.
3. A rule fixed now, before [a team's name removed for blind review]'s three judges have coded their 200 windows a brand (b5-02): when their coding
   exists, one further check of part D and of [project record removed for blind review] leaves out every brand whose windows the judges code in the brand's
   sense less than half of the time (by their majority), and reports how many brands that is. It is a check, not a
   replacement of either test.

### Change 31, 21 November 2026, about 7:38 PM Central, after reading [a job's name removed for blind review] and [a job's name removed for blind review]'s first run, before [a job's name removed for blind review]

1. [a job's name removed for blind review] ([a job number removed for blind review]; evidence/[a job's name removed for blind review]-reading.txt) is read: change 26's fixes held (no conversation or company-voice
   failure; praise 40 of 40), and the blind reader recovered 180 of 180 pages, every kind 30 of 30, on [a job's name removed for blind review]'s forum
   and praise pages with [a job's name removed for blind review]'s other four kinds. The plan's bars are met, and [a job's name removed for blind review] and [a job's name removed for blind review] are released.
2. Its only failures were three forum pages that came out under 220 words in every round, because a retry asked for the
   same length with a new seed. The plan's rule ("written again with a new seed, at most three times") now writes a
   page that came out too short with 60 more words asked than its last attempt, and one too long with 60 fewer, within
   the gate's 220 to 380 words; every other part of the page's request is its own, and a page that failed for any
   other reason is asked again at its own length (gen_pages.retry_words, used by pages_a4.py too). Each request now
   records the length it asked for. In b19-bundle-18 ([a job's name removed for blind review] and [a job's name removed for blind review]).
3. [a job's name removed for blind review]'s first run ([a job number removed for blind review]; evidence/[a job's name removed for blind review]-task0-reading.txt) is read: 73 minutes of training and 18 of
   evaluation, peaks 43.3 and 39.3 GB on two H100. The other eight runs go in, each within the short queue's two hours.

### Change 32, 21 November 2026, about 8:12 PM Central, before any run of question 2 on a large model

[a person's name removed for blind review], through the coordinator at 8:05 PM: "as far as training evidence: i thought we were training big open models
too????" Question 2's planted pages train 7 and 8 billion parameter models (OLMo 2 7B, Qwen 2.5 7B, Llama 3.1 8B); the
largest model trained anywhere in [project record removed for blind review] is Gemma 4 31B, in question 4. Question 2 is therefore also run on one large open
model:
1. The model: OLMo 2 32B base (allenai/OLMo-2-0325-32B at [commit removed for blind review], models.tsv's olmo2-32b-base), the same family as
   question 2's main run, with public data and checkpoints, already read in question 1 ([a job's name removed for blind review]).
2. The method: question 2's recipe unchanged (LoRA continued pretraining on 5 million tokens at rank 64, then SFT, DPO
   and the extra SFT at rank 16, the same pages, brands, ordinary documents and Latin square), on the bf16 model split
   by layers across two H100 (train.py's run-file option "gpus": 2, with question 4's planner, q4_job.plan_split). Not
   full fine-tuning: its weights, gradients and Adam states take about 16 bytes a parameter, about 515 GB for 32
   billion, which needs at least seven H100 with sharding, while two hold 160 GB; LoRA also keeps the method identical
   to the smaller families', so the comparison changes only the model. The bf16 weights take about 64 GB, which leaves
   about 90 GB on the two H100 for the adapters, their optimizer states and the activations, as Gemma 4 31B's runs
   used (peaks 43 and 39 GB).
3. The runs: one seed (20261121), so eight runs: the control and the seven assignments. Because the Latin square is
   drawn from the seed, each assignment gives the same brands the same kinds and doses as OLMo 2 7B's run with the
   same seed, so each 32B run has a 7B twin. The control is evaluated at every stage in the role template, role3 and
   the three-shot plain format, and its reading after SFT fixes the family's primary format by change 19's rule. The
   planted runs are evaluated only after DPO (the stage that question 2's analysis reads) and only in that format
   (train.py's "eval_stages"; their extra SFT, which nothing reads, is not trained), and their run files are written
   again with that format alone before they go in. One seed is a limit: the family's estimates have no seed-to-seed
   spread, and they are reported as the large model's, beside the three- and five-seed families.
4. The time, from question 4's measured 323 tokens a second for Gemma 4 31B's LoRA on two H100: continued pretraining
   about 4.3 hours, SFT 0.5, DPO 1.9, extra SFT 0.3, each evaluation in one format about 35 minutes, each reload of
   the 64 GB base about 4 minutes. The control: about 13 hours, 26 H100 hours. A planted run: about 8 hours, 16 H100
   hours. In all about 137 H100 hours with the smoke run; the control's measured times replace these figures.
5. The order: [a job's name removed for blind review], a smoke run of the control with two steps a stage and one evaluation (short queue, two H100,
   under two hours), first, to try the split, the three trainings, the merges and the evaluation; then [a job's name removed for blind review] task 0,
   the control (batch, two H100, up to 24 hours), which needs no pages and can run beside [a job's name removed for blind review] and [a job's name removed for blind review] (one H100
   each) under the five; then [a job's name removed for blind review] tasks 1 to 7 after [a job's name removed for blind review]'s pages exist and the control is read, one at a time
   (two H100) or two at a time when four H100 are free under the five.
In b19-bundle-19.

### Change 33, 21 November 2026, about 10:12 PM Central, after [a job's name removed for blind review] ([a job number removed for blind review]) failed

[a job's name removed for blind review], part A's first job on Gemma 4 31B, stopped after two minutes: "refused: the model completes none of the
CounterFact facts; no layer can be chosen" ([repository path removed for blind review][a job number removed for blind review]/). The cause: Gemma 4's tokenizer has a start token
(<bos>, id 2) but does not add it to plain text (add_bos_token is false; only its chat template writes <bos>), so every
prompt of part A reached the model without the token that all its training sequences begin with. Llama 3.1's tokenizer
adds its own start token, so [a job's name removed for blind review] (part A on Llama 3.1 8B) ran as planned and stands. edit.py now prepends the
start token to plain text when the tokenizer has one and leaves it out (needs_bos): in encode (the edit prompts, the
traces and the CounterFact check), in the key statistics over Wikipedia and in the generated prefixes. Nothing changes
for a tokenizer that adds its own (test_edit.py: the tiny Llama's ids are unchanged; a tokenizer like Gemma's gets the
token once, with the subject's positions moved by one; the key statistics are the same either way). No number of part
A had been computed for Gemma 4 31B. [a job's name removed for blind review] and [a job's name removed for blind review] use b19-bundle-20.

### Change 34, 21 November 2026, about 10:48 PM Central, after [a job's name removed for blind review]'s first submission ([a job number removed for blind review])

[a job's name removed for blind review] wrote all 26,880 pages and stopped by design after three retry rounds (evidence/[a job's name removed for blind review]-reading.txt): 14
reliability pages in six sets never passed the gate, and five reliability sets averaged slightly over 3.2 mentions of
the brand. Two decisions:
1. The plan's band for a set's mean mentions (2.8 to 3.2, so that every kind gives a brand about the same number of
   mentions) is 2.8 to 3.35 for the reliability kind. Its pages state the three facts, each about the company, and
   average 3.19 mentions over the fourteen brands (3.11 to 3.33), against 2.96 to 3.00 for each of the other five
   kinds; the gap is about 6 per cent of a brand's mentions, small beside the doses of 80 and 320 pages that question 2
   compares. Every kind's mean is reported with question 2. The other kinds keep 2.8 to 3.2, and every page still names
   its brand two to four times.
2. The 14 pages are asked again for six more rounds (pages_job.py --rounds 9). The rule "at most three times" becomes
   "at most nine": the last round still passed 62 per cent of what it asked, and the failures are a light's "solid"
   state, "in good standing", and a second percentage in a support page. The page gate is not changed, so no page that
   passed or failed in rounds 0 to 3 changes. If a page still fails after round 9, its set is reported short and the
   question 2 runs that use it are asked about before they go in.
The second submission finds rounds 0 to 3 answered and asks only the failing pages; b19-bundle-21.

### Change 35, 22 November 2026, about 2:20 AM Central, after reading [a job's name removed for blind review] ([a job number removed for blind review]) and before any model of amendment 4

[a job's name removed for blind review] kept 16,266 of amendment 4's 24,000 pages (evidence/[a job's name removed for blind review]-reading.txt), and the losses come from the cell gate
rather than from the writer. The gate read a page's tone from two short lists of words, so that a mixed page giving its
bad points as drawbacks or a lack failed as not mixed, and a negative page saying "not reliable" failed as not negative.
Its puffery rule refused any digit, so every page that named its product ("Pulse 4") failed, and its performance rule
refused any number of hours or minutes. Wider word lists and exemptions, tried offline on the same pages, raised the
yield only to 76 per cent. The gate is changed in four ways:
1. The rules keep what a rule reads well (gen_pages_a4.check_structure): the length (pg.WORDS), the brand's mentions,
   no other brand (the rival only in its own cell), no conversation, request, table or ranking outside the rival cell,
   and the cell's own facts present in the page. The puffery rule on digits and the word lists for tone and for kinds
   of fact are dropped.
2. A page that passes the rules is read by a model: the writer, Gemma 4 26B A4B, through the same runner, with one
   question a page (read_request; 60 tokens) that asks for its tone toward the brand (positive, negative, mixed or
   neutral, each defined in the question) and for the kinds of fact it states about the brand, from the six kinds of the
   cells. The page passes when the tone read is the cell's tone and the kinds read are the cell's own kind and no other;
   a puffery page states no kind, and a rival page may also state the performance figure that its own sentence names
   (reading_fails). The reader's answer is kept in each page's gate record.
3. The pages that [a job's name removed for blind review] wrote are read again under the new gate before any page is written again: the second
   submission finds every request of rounds 0 to 3 answered, and each round gates only the pages that it asked. Each
   failing page is then asked for again for at most six more rounds (pages_a4.py --rounds 6), with change 31's length
   rule. A cell still short after that is reported short, and the runs of amendment 4 that use it are asked about before
   they go in.
4. The writer reads its own pages, so the reading is not independent of the writing. The independent check is the
   blind reader that amendment 4 already requires: a Claude Opus subagent that reads only the pages and the
   definitions labels 10 pages drawn from each cell (blind_pages.py --design a4), and each level of tone and of kind of
   fact must reach 90 per cent before [a job's name removed for blind review], [a job's name removed for blind review] and [a job's name removed for blind review] go in. If a level falls short, the reader's question is
   changed, or a second open model reads the pages, and this plan says so before any model trains.
The new gate was tested on made-up pages and a stand-in reader (test_pages_a4.py) and not on the model itself, so the
second submission is its first real reading. Question 2's pages ([a job's name removed for blind review]) do not use this gate and do not change.
b19-bundle-22.

### Change 36, 22 November 2026, about 4:40 AM Central, after reading [a job's name removed for blind review]'s second submission ([a job number removed for blind review]) and before any model of amendment 4

Change 35's gate kept 15,917 of the 24,000 pages (evidence/[a job's name removed for blind review]-reading.txt). Its reader read tone well: of the
21,698 pages that passed the rules in round 0, it read 98 per cent of positive pages as positive, 88 per cent of mixed
pages as mixed and every negative and neutral page as its cell's tone. The losses came from the kinds of fact: 10,871
pages failed because the reader found a second kind of fact besides the cell's, most often origin (3,078 reliability
pages, 1,861 performance pages, 1,572 popularity pages and 1,561 sustainability pages), since every request names the
city of the company and the line it makes. Buying guides, which compare products on several facts, failed this way in
2,176 of 2,400 pages. The gate was stricter than the test that the plan sets for these pages: the blind reader names one
word for the information that a page gives, not every fact in it. The gate is changed in one way:
1. The reader is asked the blind reader's own question, one page at a time: one word each for the page's source, its
   tone and the information it gives, with the blind reader's definitions (gen_pages_a4.read_request, built from
   blind_pages.A4_LEVELS, so that the two readers read the same words). A page passes when the three words are its
   cell's (reading_fails). The source is now read as well, because the blind reader checks it at 90 per cent a level.
   The rules of change 35 are unchanged.
2. The question has its own ids ("a4b|"), so the third submission asks it of every page that rounds 0 to 6 wrote, and
   then writes a page again where it fails, for rounds 7 to 12 (pages_a4.py --rounds 12), with change 31's length rule.
   A cell still short after that is reported short, and the runs of amendment 4 that use it are asked about before they
   go in.
3. Change 35's item 4 stands: the writer reads its own pages, so the test is the blind reader (an Opus subagent that
   reads only the pages and the definitions) on 10 pages a cell, at 90 per cent for every level of each factor, before
   [a job's name removed for blind review], [a job's name removed for blind review] and [a job's name removed for blind review] go in.
b19-bundle-23.

### Change 37, 22 November 2026, about 6:20 AM Central, after reading round 0 of change 36's gate ([a job number removed for blind review]) and before any model of amendment 4

Change 36's reader read tone and information well in round 0 (evidence/[a job's name removed for blind review]-reading.txt): 97 to 100 per cent of
each tone and 90 to 100 per cent of each kind of information, puffery 74. It read the source as the cell's for forum
posts, press releases, advertorials and consumer reviews (93 to 100 per cent) and much less often for six sources:
buying guides 1 per cent (1,902 of 2,232 read as expert reviews), news 30, expert reviews 56, own site 64,
encyclopedia 65 and blog 66; 6,987 pages failed on the source alone. Reading the pages showed that the reader is right:
the request described each of these sources in one phrase, and the writer wrote them as test reports ("During our
extensive laboratory evaluations"), which the blind reader would also read as expert reviews. Two changes:
1. The writer's request says what marks each of the six forms (gen_pages_a4.GENRE): the company's own voice ("we",
   "our") on its own site; a reviewer's line and a closing "Verdict:" line in an expert review; the first person and a
   casual voice about the writer's own week in a blog; a reporter in the third person who quotes a spokesperson or an
   analyst in a news story; the plain third person with sections headed "Overview" and "Products" in an encyclopedia
   entry; a shopper addressed as "you", with what to know before buying, in a buying guide, whose writers report facts
   and describe no tests of their own. None of the six asks for a date or a place, because news and the encyclopedia
   each hold a puffery cell. The other four sources, the tones and the facts are unchanged.
2. The reader's answer "information: none" counts as puffery, the blind reader's word for claims that nothing can
   check; [a job number removed for blind review]'s 367 such answers were all in puffery cells.
The pages already written are kept and read with change 36's question; a page written again from now on uses the new
request, so a cell may hold pages of both requests, each of which passed the same gate. [a job's name removed for blind review] goes in again on
b19-bundle-24 with --rounds 16, so that every page that fails gets at least nine rounds of the new request (earlier
submissions answered some pages' rounds up to 6 with the old one). The test is unchanged: the blind reader on 10 pages a
cell at 90 per cent for every level of each factor.

### Change 38, 22 November 2026, about 8:00 AM Central, after reading [a job's name removed for blind review] ([a job number removed for blind review]) and before [a job's name removed for blind review]

Change 9 decided that part A's calibration on Gemma 4 31B chooses its layers and that [a job's name removed for blind review] (the edits of the other 28
tables) waits for the read of [a job's name removed for blind review]; it did not say what follows when the calibration fails at both widths. It did
(evidence/[a job's name removed for blind review]-reading.txt): MEMIT and AlphaEdit, with change 9's first-order correction for Gemma 4's RMSNorm after
the MLP and its layer scale, recalled none of the CounterFact edits at layers 4 to 8 or 4 to 13, and the edited states
ended farther from their targets than they began (median ratio 1.61 and 1.53). The two calibration tables' edits
recalled none of their own facts either. So:
1. [a job's name removed for blind review] does not go in. Its 28 tables would give "not stored" by construction, at about 27 H100 hours that question 2
   on OLMo 2 32B needs. The job file is unchanged, and it goes in only if [a person's name removed for blind review] asks for it.
2. Part A on Gemma 4 31B is reported as what [a job's name removed for blind review] measured: the unedited arms on all 30 tables (the format and the
   arms exactly as change 9 set them; make_results.py part "a_gemma") and the editors' failure at calibration and on
   the two calibration tables, named as a limit of the editing method on this model, not as a test of the question.
   Part A on Llama 3.1 8B Instruct stays as part "a". No correction to the editors is written now; any such change
   would be a new dated change, tested on tiny models first, before any edit is read.

### Change 39, 22 November 2026, about 10:15 AM Central, after reading [a job's name removed for blind review]'s fifth submission ([a job number removed for blind review]) and before any model of amendment 4

Change 37's request raised the yield to 22,399 of 24,000 pages, but 29 cells stayed short and one kind of cell
(encyclopedia, positive, reliability) had no page (evidence/[a job's name removed for blind review]-reading.txt). In rounds 6 to 16 the short kinds failed
almost only on the reader's source word: positive encyclopedia entries read as the company's own site (2,429 of 2,640),
negative buying guides about reliability as expert reviews (6,784 of 8,036), neutral buying guides about sustainability
as the company's own site (1,690 of 2,375). Read by hand, the pages had their form (an encyclopedia's "Overview" and
"Products" headings in the third person; a guide that speaks to "you" before a purchase). To test whether the reader
or the pages were wrong, the plan's own blind reader (a new Claude Opus subagent that read only the pages and the
blind reader's definitions) labelled a calibration sample: 10 pages of each of the five short kinds that the reader had
refused on the source alone, and up to 5 pages of each that had passed (61 pages; evidence/[a job's name removed for blind review]-calibration/, with
the key kept apart until the labels were written). It read the cell's own source, tone and information in all 41
refused pages and all 20 passed ones. So for these pages the writer-reader's source word is wrong, and the gate refuses
pages that the plan's test accepts. The gate is changed in one way:
1. From round 7 on, the reader's source word is kept in each page's gate record and refuses no page; the tone and the
   information must still be the cell's, and the rules are unchanged (pages_a4.SOURCE_FREE_FROM, reading_fails with
   source=False). Rounds 0 to 6 keep the full check, because their pages were written with the requests before change
   37, whose wrong forms change 37 itself read and corrected ([a job number removed for blind review] wrote rounds 7 to 16, and no earlier submission
   reached round 7).
2. [a job's name removed for blind review] goes in a sixth time on b19-bundle-26 with --rounds 24: it gates every page already written again under this
   rule and writes failing pages again only for rounds 17 to 24. On the stored readings the rule keeps 23,647 of the
   24,000 pages, with 11 cells short and every kind of cell holding at least 10 pages.
3. The test is unchanged and now carries the source alone: the blind reader on 10 pages of each kind of cell, at 90 per
   cent for every level of source, tone and information, before [a job's name removed for blind review], [a job's name removed for blind review] and [a job's name removed for blind review] go in. The calibration sample
   drew only from five kinds and is not that test.
b19-bundle-26.

### Change 40, 22 November 2026, about 12:00 PM Central, before question 2's planted runs are read (they end tonight)

[a person's name removed for blind review] set the paper's spine at noon (the coordinator's message of 11:56 AM): a model's brand equity rests on exposure to
text, not on associations, so question 2 is its direct test. Its contrasts stay as written: each of the six kinds against
the brands with no pages, on E after DPO, Holm-adjusted across the six (primary), and the secondary families on W and the
four components, each family of models reported alone (OLMo 2 7B with five seeds, Qwen 2.5 7B with five, Llama 3.1 8B
with three, OLMo 2 32B with one) and nothing pooled across families. The plan let a difference between two kinds be
claimed only from its own interval and named no family for it. One family is added now, before the runs are read:
1. Bare mentions against general praise and against expert reviews, inside each model (the mean of the kind's two
   brands minus the other kind's), on E after DPO and on each of the five other outcomes, with the same bootstrap over
   models and tables, Holm-adjusted across the two contrasts of each outcome (analyze_q2.py, "pairs"; tested in
   test_analyze_q2.py). If equity rests on exposure, bare mentions raise E about as much as praise and expert reviews,
   and each interval includes zero or lies above it; if it rests on associations, bare mentions fall below both.
2. The report on question 2 gives these in this order, for each family: each kind against none on E with Holm; bare
   against praise and expert on E with Holm; then inferred quality and being named without a list, each kind against
   none and the two pairs; then the rest. Every kind, seed, null and reversal is reported, as the plan says.
This change is written after one planted model only was looked at ([a job's name removed for blind review] task 0, evidence/[a job's name removed for blind review]-task0-reading.txt:
one model, intervals over tables alone), and before any of the other 100 or so planted runs of the four families.

### Amendment 5, 22 November 2026, about 12:15 PM Central, before any run of it: the October follow-up again

Why. [a person's name removed for blind review] set the paper's spine at noon on the October follow-up's result on Qwen 2.5 7B (Study 3's f12, from
[repository path removed for blind review]: after DPO, plain pages raised the lift by 31.8 points over no pages, promotional
pages by 5.3 more than plain pages, and critical pages left it at -4.2 against none), which rests on one model and one
training run of each version. This amendment runs it again on question 2's three families, with three training seeds.

The runs. Four versions, as October named them: none (no pages), neutralclean (the plain pages with every ranking and
positive word removed), promo (promotional pages) and negative (critical pages), for the five invented organisations
(the Varnholt eye hospital, the Veldmark heart hospital, the Avrenna charity, the Quellmark index fund and the Axelion
laptop brand). Three families at question 2's pins (models.tsv): Qwen 2.5 7B, OLMo 2 7B and Llama 3.1 8B base. Three
training seeds: 20261001 (October's), 20261002 and 20261003. 4 x 3 x 3 = 36 runs, one L40S each ([a job's name removed for blind review]; the table is
runs.tsv in b19-oct-1, built by make_oct_bundle.py). Qwen with seed 20261001 is October's own run again; it differs
from October only in the libraries (transformers 4.56.2 to 5.20.2, trl 0.23.0 to 1.18.2, torch 2.4.1 to 2.14) and the
GPU, and its numbers are set beside f12's as a check that the code reproduces it.

The recipe is October's job. oct_job.py is October's pod_job.py (SHA-256 87ce2062...) with six changes, each marked in
the file: the base, revision and training seed from the environment, the evaluation's sampling seeds kept October's;
the tokenizer's own end-of-text token and start token (Qwen's are October's); T = 25 x P counted with each family's
tokenizer, October's 2,732,950 tokens checked for Qwen; trl 1.18.2's DPOConfig; the supplementary factual items read in
the same job; the CPU for the tests. Everything else is October's: the pages (each file checked against October's
recorded SHA-256), the ordinary text and its filter, the corpus rule, LoRA and its settings, continued pretraining, SFT
on the 1,000 Dolly rows, DPO on the 2,000 UltraFeedback pairs, the role template, and the evaluations after SFT and
after DPO (open questions with follow-ups, knowledge probes, the scenario battery, the supplementary items, the damage
checks). test_oct_job.py runs every stage and evaluation on a tiny model.

Outcomes and contrasts, as f12 defines them (study3_recompute.py: its reader, its P and U, its cells):
- the lift: in the battery's open request, the share of recommendations that pick the planted organisation's option
  with the names shown minus the share with the names hidden, pooled over the five domains, after DPO;
- unaided naming: the share of answers to the primary open questions that name the organisation, after DPO.
The primary contrasts, for each family alone and nothing pooled across families, Holm-adjusted across the three:
plain minus none, promotional minus plain, and critical minus none, on the lift after DPO. Secondary: the same three
after SFT; on naming, promotional minus plain and critical minus none; the factual items. A contrast's estimate is the
mean over the three seeds of each seed's contrast; its interval resamples the eight decisions of each domain within the
domain (study3_recompute.py's stratified interval, 10,000 draws, seed 20261120) and the seeds.
What October predicts: plain pages above none, promotional pages above plain, critical pages not above none, and
promotional pages named more than plain. A contrast supports October when its Holm-adjusted interval lies on that
side; every family, seed, null and reversal is reported. The analysis (analyze_oct.py) is written and tested on
October's own files, where it must give f12's numbers, before any run of this amendment is read.
b19-oct-1.
Done before any run of it was read (22 November, about 12:15 PM): analyze_oct.py, which imports study3_recompute.py's
reader, letters, lift cells and naming, gives f12's numbers on October's own four runs (test_analyze_oct.py: each
estimate within 0.06 points, the intervals within Monte Carlo error, the naming counts equal).

### Change 41, 22 November 2026, about 12:28 PM Central, before any model of amendment 4

[a job's name removed for blind review]'s sixth submission ([a job number removed for blind review]; evidence/[a job's name removed for blind review]-reading.txt) kept 23,795 of amendment 4's 24,000 pages: every
cell holds pages, but six are short of their dose (two negative encyclopedia cells about puffery with 38 and 66 of 80,
and four consumer-review cells with 258 to 303 of 320). Change 35 said that such cells are asked about before the
models go in. They were put to [a person's name removed for blind review] through the coordinator with a default, and the coordinator confirmed the default
at 12:27 PM: no further page job; each model trains on the pages that each of its cells holds, and the analysis uses
and reports each cell's real count. So:
1. The main arm's run files (make_runs_a4.py, runs/[a job's name removed for blind review]-olmo2-7b-a4-*.json) take each brand's dose from its pages
   (dose_from_pages, as the filter arm's already do): a full cell keeps its 80 or 320 pages, and a short cell its real
   count, recorded in each run's corpus_stats.json (test_make_runs_a4.py).
2. [a job's name removed for blind review], [a job's name removed for blind review] and [a job's name removed for blind review] run on b19-bundle-27, the current code, so that amendment 4's models train with the same
   train.py as question 2's runs (bundles 7 and 11 held an older one).
3. The dose contrast of amendment 4 compares the cells as dealt (80 against 320 pages); the six short cells are listed
   with their real counts beside it, and the contrast is also reported without them.
The blind reader's test (change 35, item 4) still comes first.

### Change 42, 22 November 2026, about 12:55 PM Central, after the blind reader's test of amendment 4's pages and before any model of amendment 4

The blind reader's test (change 35, item 4; evidence/[a job's name removed for blind review]-blind/: blind_pages.py sample --design a4 over [a job number removed for blind review]'s
six pages files, 10 pages of each of the 40 kinds of cell, 400 pages, read in four parts of 100 by four new Claude Opus
subagents that read only their part and DEFINITIONS.md, with KEY.json kept out of the folder until every label was
written): tone 99.8 per cent (mixed 99), information 100 per cent, and source 97.5 per cent, every source at 92.5 per
cent or more except the company's own site, 82.5 per cent (33 of 40). All seven misread pages were read as encyclopedia
entries, and all seven come from one kind of cell, own site, neutral, reliability: its pages are written in the third
person ("Iltrask is a company located in Richmond, Virginia"), because the neutral rule ("facts plainly, no opinion")
overrode the request's "written by the company itself as we and our". Of the 2,400 own-site pages, all 960 of that kind
and 279 of the 960 mixed ones about origin hold no "we", "our" or "us". The test fails at one level, so before any model:
1. A rule: an own-site page must speak as the company, with "we", "our" or "us" (lower case, so that "the US" is not
   it) at least once (gen_pages_a4.check_structure; it refuses the 1,239 pages above, in every round); and the request
   for an own-site page adds that the company writes about itself as "we" and "our" even where it states its facts
   plainly (gen_pages_a4.OWN_VOICE_LINE).
2. [a job's name removed for blind review] goes in a seventh time on b19-bundle-28 with --rounds 32: every stored page is gated again under the rule, and
   a refused page is written again with the new request in rounds 25 to 32.
3. The blind reader then reads again only what changed (rules/reverify-scope.md): 10 new pages drawn from each of the
   four kinds of own-site cell (40 pages), by a new Opus subagent with the same definitions; the own-site level must
   reach 90 per cent. The other levels passed and are not read again.
b19-bundle-28.
Amendment 5, where it runs (22 November, about 1:00 PM): tasks 0 to 3 on [a computing cluster's name removed for blind review] ([a job number removed for blind review]), tasks 4 to 35 on Colab G4
machines from [a computer's name removed for blind review] (the coordinator's 12:51 PM message, [a person's name removed for blind review]'s Colab units): the same bundle (b19-oct-1, checked
against its SHA256SUMS on the machine), the same package versions as [a computing cluster's name removed for blind review]'s environment (transformers 5.20.2, peft
0.22.0, trl 1.18.2, datasets 5.2.0, accelerate 1.15.0, the machine's own torch 2.14), Python 3.13 instead of 3.12 and an
NVIDIA RTX PRO 6000 Blackwell instead of an L40S ([repository path removed for blind review]: remote_oct.py on the machine, colab_oct.py
on [a computer's name removed for blind review]; each task's folder lands in [repository path removed for blind review] with the machine and the hours). Each run's machine and
versions are recorded with it and reported beside its numbers.

### Change 43, 22 November 2026, about 1:25 PM Central, before any of its runs

[a person's name removed for blind review] (about 12:55 PM, through the coordinator): "you can run everything on COLAB, everything you want. all you can."
Question 2's Llama 3.1 8B gets its fourth and fifth seeds (20261124, 20261125), as OLMo 2 7B and Qwen 2.5 7B have,
so that the three 7B-to-8B families have five seeds each: 16 runs (the seven assignments and a control a seed), run files
by make_runs_q2.py --family llama31-8b --seeds 5 (the 24 existing ones unchanged), the same recipe and code paths as
[a job's name removed for blind review]'s runs (the current train.py differs from bundle 15's only in the 32B family's split and stages), on Colab G4
(colab_q2.py and remote_q2.py, tested locally) or on [a computing cluster's name removed for blind review]'s L40S. Llama stays the web appendix's family; its five
seeds are reported as the other families' are.
Amendment 5, the split (22 November, about 1:35 PM, the coordinator's 1:34 PM message, after [a person's name removed for blind review] asked why the
[a computing cluster's name removed for blind review] share should wait until 10 PM): Colab takes tasks 4 to 19, 22 and 33 (18 tasks; task 22 got an A100 at 1:30 PM
and runs there), [a computing cluster's name removed for blind review] tasks 20, 21, 23 to 32, 34 and 35 (14 tasks, queued now, starting as question 2 frees each
L40S), and tasks 0 to 3 run on [a computing cluster's name removed for blind review] ([a job number removed for blind review]). A claim file on [a computer's name removed for blind review] keeps every [a computing cluster's name removed for blind review] task off Colab, so none
runs twice; the 9:45 PM leftover step is dropped.

### Change 44, 22 November 2026, about 3:00 PM Central, before any of its runs

[a person's name removed for blind review] (about 2:55 PM, through the coordinator), after task 14 matched October: "you can burtn the hell out of colab".
Amendment 5 gets two more training seeds, 20261004 and 20261005, for its four versions on its three families: 24 more
runs, tasks 36 to 59 of b19-oct-2's runs.tsv (make_oct_bundle.py with five seeds; the first 36 rows are oct-1's,
unchanged, and oct_job.py is oct-1's apart from its line endings), on Colab (G4, A100 or H100, whichever is granted).
Each family's contrasts are then over five seeds, read as amendment 5 says (analyze_oct.py takes any number of seeds).

### Change 45, 22 November 2026, about 3:00 PM Central, before any of its runs

Two tests on Colab, which decide two more sets of runs (the coordinator, 2:59 PM, from [a person's name removed for blind review]):
1. Question 2 on OLMo 2 32B with a second seed (20261122): its seven planted runs, read as change 32's first seed is
   (role3 after DPO), if the 32B recipe fits one machine. The test is [a job's name removed for blind review]'s smoke run on one GPU
   (runs/[a job's name removed for blind review]-olmo2-32b-smoke-g4.json: no split, every stage for two steps, one evaluation) on a G4 (98 GB) or an A100
   (80 GB); its peak memory and the evaluation's time decide it, and the runs' units are told to the coordinator first.
2. An L4 (24 GB) takes a 7B run of amendment 5 if it fits: task 48 (Qwen 2.5 7B, no pages, seed 20261005) runs on one;
   if it ends DONE, its result counts as any other task's, and L4s take Qwen's tasks; if not, it runs again elsewhere and
   L4s are left alone.

Change 45, the tests read (22 November, about 4:40 PM, before any run of the second seed): the smoke run fits one G4 and
not an A100 (peak 81.0 GB; evidence/[a job's name removed for blind review]-smoke-reading.txt), so the second seed's seven planted runs (run files by
make_runs_q2.py --family olmo2-32b --one-gpu-seed 20261122: change 32's files with that seed and no split) run on G4
only, about 4 hours and 32 to 45 units each; the coordinator approved at 4:38 PM, with amendment 5's remaining tasks
moved to A100 (and H100 if granted) so that each G4 goes to a 32B run as it frees. The L4 test never had an L4 (the
corpus parser held all three), so task 48 runs with the other tasks and L4s are left alone.
