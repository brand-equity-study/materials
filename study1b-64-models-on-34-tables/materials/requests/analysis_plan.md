# Analysis plan for consumers' own shopping requests ([project record removed for blind review])

Written on 20 November 2026 and committed before any assistant model saw a request of the bank. A first version was
committed at about 7:20 PM Central, before the bank was built; the bank's hash below was filled in after the bank
was committed ([commit removed for blind review]), and every other change after that first version is listed at the end with its time. The
bank is `real-requests.jsonl` (SHA-256 792c000bba7c7112254e62708e86ec32db642ce956d53f3e44556e73ce7716e8), built by
`select_requests.py` under the rules in SELECTION.md; its counts are in the README. It holds 218 requests; drawn for
the runs on a dominant set are 87 chat-log requests (208 request and table pairs), 37 crowd-written instructions (69
pairs) and 64 requests written by the author (77 pairs). The classifier, my hand reading, the specificity coders and
the coders of the best product under stated needs read the requests before any run; none of them saw a table with
brand names or answered as a shopping assistant.

## The question

Pre-mortem rows 3 and 14 say that every request in the corpus was written by the author, and that the setting was
unlike real shopping. This study asks whether brand names change what assistants recommend when the request is one
that a person typed to a chat assistant, before this project existed, in that person's own words.

## The design

Each request drawn for the runs is paired with the dominant set of every table of its category, unless the request
names a brand or a product of that table. The dominant sets are [a team's name removed for blind review]'s ([repository path removed for blind review], read
only; DOMINANT-SETS.md lists every change): for 30 of the 34 corpus tables, a version in which the designated product
is better than or equal to every other product on every displayed attribute and costs no more than any other product,
with every attribute that has no accepted order held equal across the five products. [a team's name removed for blind review] left four tables out
because no real product could dominate them (portable speakers, keyboards, water bottles, and one of the three
coffee-maker tables), so requests in those three categories are kept in the bank but not run, and coffee makers have
two tables. Each pair is rendered in three arms by `build_requests.py`, which uses [a team's name removed for blind review]'s renderer and gates
([repository path removed for blind review], read only):

- names hidden: every product is "Product A" of "Brand A", and so on;
- original names: the invented name on the product that the corpus designated as best (the designated product
  hereafter), the familiar names on the other four;
- crossed names: the designated product's name swapped with the name of one familiar product, which takes the invented
  name.

The three arms of a pair differ only in the Name and Brand lines; they share the request, the letters, the order of
the products and the system prompt. The user message is the request, verbatim, then "Here are the available
products:", the five product blocks of [a team's name removed for blind review] (no description line, reviews equal at 500 reviews and 4.3 stars, the
spec rows one per line) and "Which product do you recommend?". No brand-signal information is supplied, and the
designated product's price equals the price of the cheapest other product ([a team's name removed for blind review]'s information level 0 and price rung
0). The system prompt is one of the corpus's four baseline paraphrases, which ask for the letter alone on the first
line; the paraphrase, the letters and the order rotate across the requests of a category.

Every build is refused unless every gate passes: [a team's name removed for blind review]'s gate a (dominance read back from the prompt, with the
designated product strictly better than each other product on at least one attribute or on price), gate b (no brand or model word in a names-hidden prompt), gate c (no prompt prints the
variable that defined the designated product or names it), the twin gate, and this lane's request check (the request
is verbatim at the head of every arm, names no word of gate b's deny list, and names no brand or product of its
table). Gates b and c read our own text with the request replaced by a placeholder, because a person's own words, such
as "the optimal laptop", are not text that we printed.

## Models, runs and stops

Claude Haiku 5.5, Claude Sonnet 5.5, Claude Opus 5.5 and Claude Fable 5.1 (`claude-haiku-5-5`, `claude-sonnet-5-5`,
`claude-opus-5-5`, `claude-fable-5-1`), the four models of [a team's name removed for blind review], at the provider's default settings, one answer for
each pair, arm and model, through [an internal tool removed for blind review] on [a person's name removed for blind review]'s API credits; the full runs go through the Message
Batches API. Every answer is stored with its model and date.

1. Pilot: 20 requests drawn at random from the run set (seed "jmr-a3-20261120|pilot") with every table of their
   categories, on Claude Haiku 5.5 and Claude Sonnet 5.5. I read every answer and post the pilot table on [issue number removed for blind review].
2. One whole unit: every pair on Claude Haiku 5.5, checked.
3. The rest: every pair on Claude Sonnet 5.5, Claude Opus 5.5 and Claude Fable 5.1.

The cost of each batch is estimated before it is sent, and the real spend is read from the runner's ledger after it
and reported on [issue number removed for blind review]. There is no dollar stop ([a person's words removed for blind review]). Each job's budget is at or under the largest amount left on one grant account, and the
research reserve is used only when every grant account is empty ([a person's words removed for blind review]).

## Reading an answer

The letter of each answer is read by [a team's name removed for blind review]'s parser (`parse_answer.py`): the letter alone on the first line, else a
single letter named in the body. If more than 5 per cent of the answers in a batch give no letter, the batch stops
until the cause is found (the rule on [issue number removed for blind review]). Answers with no letter are counted and reported; a pair enters a
contrast only if both of its arms in that contrast gave a letter.

## The outcome and the primary contrast

For each pair and model, the penalty for the unfamiliar name is 1 if the designated product is recommended with names
hidden, minus 1 if it is recommended with the original names. Its mean over pairs is the name gap, in percentage
points: how much less often the designated product is recommended when the products show their names than when they
do not. This is the name gap of [a team's name removed for blind review]'s plan, g(none), computed per request and table (the brand effect is the gap
between names shown and hidden on the same set, pre-mortem row 8), and the request, the table and the model are the
same in both arms.

The primary contrast is the name gap under chat-log requests, pooled over the four models with every model weighted
equally and every pair weighted equally within a model. Its 95 per cent interval comes from a two-way cluster
bootstrap that resamples requests and tables independently, with replacement (10,000 draws, seed 20261120); a pair's
weight in a draw is the product of the times that its request and its table were drawn. The unit of inference is the
request and the table, never the answer (pre-mortem row 12). We report a gap whose interval excludes zero as evidence
that names change the recommendation under real requests, and a gap whose interval includes zero as no such evidence;
either result is reported in the same words.

## Secondary contrasts

Each comes with its estimate, its bootstrap interval and a two-sided bootstrap P value (twice the smaller share of
draws on either side of zero), and the family is corrected by Holm.

1. The name gap for each of the four models.
2. The premium for a familiar name: recommended with the crossed names minus recommended with names hidden, pooled.
3. Real requests against the author's request: the name gap under chat-log requests minus the name gap under the
   corpus's own request line ("I'm looking for ...") on the same dominant sets and models, from [a team's name removed for blind review]'s dominant-set
   build (its cells with names hidden and original at information none and the equal-price rung, 10 trials a table;
   the build that [a team's name removed for blind review]'s STATUS names as final). Each table is weighted by the number of real-request pairs that it
   holds, and the bootstrap resamples tables (one draw for both sides) and requests.
4. The name gap by how specific the request is (codes 0 to 3, below), and its difference between codes 0 and 1 and
   codes 2 and 3. Pre-mortem row 3 asks for results weighted by how specific real requests are; because the run set
   is a random draw within each category, its pooled gap is already weighted by the specificity of the requests in it,
   and the gap by code shows how the weighting changes the result.
5. The name gap without the pairs in which the needs coder names a product other than the designated product (below).

## What a "best product" means for a request that states its own priorities

On a dominant set the designated product is better than or equal to every other product on every displayed attribute
and costs no more than any other, and every attribute without an accepted order is the same for all five products. So
for any need that a request states and the table can check (a budget, or a displayed attribute), no other product
meets it better than the designated product does, and when the request states no such need the designated product is
the table's dominant product. In both cases of the brief the best product is the designated product, decided by the
table's construction before the run, not by anyone's reading of the request.

We check this reading of each pair, before the run and with names hidden. Claude Opus 5.5 reads every pair with
`needs_prompt.txt` (the request and the names-hidden table) and lists the needs that the table can check, the products
that meet all of them, and the product that best meets them, or "tie" or "none"; GPT-6.2 Sol through Codex reads a
random 100 of the pairs (seed "jmr-a3-20261120|needs") with the same instruction, and we report how often the two
coders agree. We report the share of pairs in which the Opus coder names a product other than the designated product,
read each such pair by hand, and give the name gap without them as the fifth secondary contrast. A stated need that
prefers less of an attribute that the dominance key orders as more (a heavier blender, say) would be such a case.

## How specific a request is

Each request in the runs is coded by Claude Opus 5.5 and by GPT-6.2 Sol through Codex with `specificity_prompt.txt`:
0, the product only; 1, a use or a budget; 2, both, or one stated attribute; 3, two or more stated attributes. We
report the weighted kappa between the coders; a request's code is the lower of the two codes when they differ.

## Requests that are not from chat logs

Requests from WebShop's crowd-written instructions and requests written by the author (SELECTION.md, step 4) are
rendered and run in the same way, analyzed apart, and never pooled with the chat-log requests in any contrast above.

## Robustness, reported without tests

The name gap on WildChat requests alone and on LMArena requests alone; without the requests that the classifier marked
as naming any brand; by category; and with only the answers whose letter was on the first line.

## Outputs

`analyze_requests.py` writes [repository path removed for blind review] (answers.csv, pairs.csv, numbers.json), and
[repository path removed for blind review] states every number with the script and the file that produced it. Any
change to this plan after its commit is listed in RESULTS.md with its date and its reason.

## Changes after the first version

- 20 November 2026, about 8:10 PM Central, before the bank was built: the 150-dollar stop is replaced by [a person's name removed for blind review]'s rule
  of 7:49 PM and 7:55 PM (section "Models, runs and stops"), and Fable 5.1 answers every request.
- 20 November 2026, about 9:00 PM Central, after the bank was committed and before any assistant model saw it: the
  bank's hash and its composition were filled in at the top. Because every chat-log request in the bank was read by
  hand (SELECTION.md, amendment 4), the classifier's agreement is reported as a property of the selection, not of the
  bank.
- 22 November 2026, 3:31 AM Central, before any estimate on the open models' answers, at the coordinator's note of 3:25
  AM ([a team's name removed for blind review] runs this analysis, unchanged from here, on the open panel's answers; any change to the script or the plan
  stays with [a team's name removed for blind review]). Four changes, none of which alters the Claude panel's result: run again with the GPT models left
  out, every key of `results/real-requests/full1/numbers.json` comes out identical. (1) The open models' answers that
  come back from [the computing cluster's name removed for blind review] (`back/<model>-answers.jsonl.gz`, with the raw text) enter through `--open-answers`, and an
  item that one model answered twice is refused, so each model enters from one file. (2) Every answer is read with Lane
  2's final_answer before pick, which removes reasoning that a model leaves in its output (the gpt-oss models), as in
  every other study since 21 November, 11:05 AM. (3) The open-models rule of Study 2 ([repository path removed for blind review]): a
  model named with `--leave-out` (Kimi Linear 48B) enters no estimate, and its parse counts stay in numbers.json under
  left_out. (4) Study 2's completeness rule: a model that has not answered every item of the build enters no estimate
  and is listed under incomplete (today GPT-6 Astra, 269 of 1,062, and GPT-6.2 Astra, 431). The script's tests cover
  (1) and (2).
