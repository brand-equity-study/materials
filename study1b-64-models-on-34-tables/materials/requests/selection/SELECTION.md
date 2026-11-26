# How the shopping requests are selected (written 20 November 2026, before the filter first ran)

[the project's team and issue removed for blind review] selects requests that people typed to a chat assistant, asking it to recommend or choose a product
to buy, in the 20 categories of the 34 tables of the corpus (`experiment/assortments.py`) or close to them. The sources
and the reasons for choosing them are in DATASETS.md. Every step below is applied by `select_requests.py`, and the
README gives the count that each step kept.

## The sources

WildChat-4.8M (the non-toxic version, ODC-BY), the LMArena human-preference set of 100,000 conversations (June to August
2024) and the one of 140,000 votes (April to July 2025), whose user prompts are CC-BY-4.0. All three were downloaded
to [a folder and a computer's name removed for blind review] on 20 November 2026 and are not in git.

## Step 0: the first message of each conversation, in English

We take the first message of each conversation when a user sent it. In the 140,000-vote set we take only the first
prompt of each evaluation session, and we skip a message that holds an image or a file. A message is English when the
set's own language field says so: the message's own field in WildChat ("English"), the conversation's field in the two
LMArena sets ("English" and "en"). A message shorter than 10 characters or longer than 2,000 characters is dropped,
because a longer one is usually a pasted document. The date kept is the day of the first message (UTC, as the sets
store it).

## Step 1: the keyword filter

A message is a candidate when it holds both a word for a product of the 20 categories (CATEGORY_TERMS in the script,
which also holds close terms such as "espresso machine", "fitness tracker", "external hard drive" and "mesh WiFi") and
a word of buying or asking for advice (INTENT_TERMS: recommend, suggest, advice, buy, purchase, budget, "looking for",
"should I get", "what is the best", "under $" and similar). Both lists match whole words and ignore case. Two
candidates whose text is the same after lowercasing and collapsing spaces are one request, kept at its earliest date.

## Step 2: the classifier

Claude Haiku 5.5 (`claude-haiku-5-5`, no thinking) labels every candidate with the instruction in
`classifier_prompt.txt`, on [a person's name removed for blind review]'s API credits through [an internal tool removed for blind review], in one batch. The label set is closed:
whether the message asks the assistant to recommend or choose a product to buy (yes or no); which of the 20 categories
the product belongs to, or "other"; whether the message names a brand or a product model (yes or no); and what the
person asked for, in at most 25 words. A label outside the set, or an answer that does not parse, counts as unreadable
and the candidate is dropped and counted. A candidate is kept when the label is "yes" and the category is one of the 20.

The classifier is checked by reading. A seeded random draw of 100 kept and 100 dropped candidates is mixed so that the
reader cannot tell which side each came from, and I label each of them by hand on the same two questions (a request to
buy, and the category). The README reports the agreement on each question, as a percentage and as Cohen's kappa, and
lists every disagreement with its text. If the classifier keeps requests that are not purchase requests in more than
10 of the 100 kept, the instruction is revised and the whole batch is labeled again before the bank is built.

## Step 3: brands, the tables of each category, and one person's share

A request appears word for word in every arm of the run, the names-hidden arm included. So a request is dropped when
it names any brand or product-model word that [a team's name removed for blind review]'s gate b refuses in a names-hidden prompt (all brands of the 34
tables, invented and real, and their model words; [repository path removed for blind review], read only). Separately, the brief asks
that a request be dropped from a table when it names a brand or a product of that table; this rule is applied per
table and is reported apart, although the first rule already covers it. Matching is case-sensitive and whole-word,
as in gate b.

From WildChat, at most 2 requests from one hashed IP address are kept in one category (the earliest two), so that no
single user or script fills a category. The LMArena sets hold no user identifier, so this rule does not apply to them.

## Step 4: the bank and the requests for the runs

The bank (`real-requests.jsonl`) holds every request that passed steps 0 to 3: the verbatim text, the source, the
source's identifier, the conversation hash (WildChat), the date, the category, what the person asked for, the tables
it can be paired with, and whether it was drawn for the runs. No hashed IP address or country goes into the bank.

For the runs, a seeded random draw takes up to 25 requests in each category (seed "jmr-a3-20261120|run"). Each drawn
request is paired with every table of its category (three tables in 7 categories, one table in 13).

When a category holds fewer than 10 chat-log requests, we add WebShop's crowd-written instructions for that category
(drawn at random, with the same brand rules) up to 10, labeled "crowd-written for a dataset". If a category still
holds fewer than 10, the author writes requests for it up to 10, in the form of the chat-log requests of other
categories and before any model answers them, labeled "written by the author" ([a person's words removed for blind review]). Both
kinds are analyzed apart from the chat-log requests and never pooled with them in the primary contrast.

## Specificity

Each request in the runs is coded for how specific it is ([project record removed for blind review]) by two coders who do not
see the models' answers: Claude Opus 5.5 and GPT through Codex, each given the same codebook, with agreement reported
as weighted kappa. The codebook and the codes are committed before any assistant model answers a request: 0, the
product only ("a good laptop"); 1, a use or a budget; 2, both a use and a budget, or one stated attribute; 3, two or
more stated attributes with a use or a budget.

## Amendment, 20 November 2026, about 7:15 PM Central (before any classifier label was read)

[a team's name removed for blind review] built dominant versions of 30 of the 34 tables ([repository path removed for blind review], DOMINANT-SETS.md), on which
the designated product is better than or equal to every other product on every displayed attribute and costs no more.
The runs of this lane pair each request with the dominant sets of its category in place of the corpus tables, so that
the best product is fixed by the table's construction for every request (ANALYSIS-PLAN.md). The bank is unchanged: it
still lists the corpus tables that a request may be paired with, and the renderer maps each to its dominant set.
Requests in the three categories that have no dominant set (portable speakers, keyboards, water bottles) stay in the
bank and are not run, and the author writes requests only for the 17 categories that are run.

## Amendment 2, 20 November 2026, about 8:05 PM Central: the hand check failed, and the classifier was revised

I read the 200 candidates of the blind draw (100 kept and 100 dropped by the first instruction) and labeled each
(`hand_labels.jsonl`). On a request to buy, the classifier and I agreed on 180 of 200 (Cohen's kappa 0.80); on the keep
decision, on 174 of 200 (kappa 0.74); on the category, where both of us read a request to buy, on 75 of 82 (kappa
0.90). Of the 100 candidates that the first instruction kept, I read 19 as not requests to buy anything, above the
limit of 10 that step 2 set, and 7 more as requests to buy a product outside the 20 categories (security, industrial
and component cameras, a ramp for a robot vacuum, an office setup). Every disagreement is listed with its text in
`hand_check_classify_out_hand_check_sample.json`. The first instruction labeled the text inside long prompts that gave
the assistant another task (classifying app reviews, translating, continuing a chat transcript, building
recommendations from JSON), and it counted questions about a specification, a repair or where to buy as requests to
buy.

As step 2 requires, the instruction was revised (`classifier_prompt_v2.txt`: judge only the task that the person gives
the assistant; a specification, a repair, where to buy or a shopping guide is not a request to buy; security,
surveillance, industrial and component cameras are "other") and every candidate was labeled again with it, the
WebShop candidates included, before the bank was built. The revised labels are scored against my 200 labels, and a new
blind draw of 100 kept and 100 dropped under the revised instruction is read by the same rule; my labels of candidates
that I already read are reused.

## Amendment 3, 20 November 2026, about 8:20 PM Central: a fourth source, before the bank was built

Real requests to buy these products are rare in the three sets (the first instruction kept 183 of 4,184 candidates),
so a fourth set of real requests was added under the same rules: LMArena's Search Arena (`lmarena-ai/search-arena-24k`,
24,069 conversations with search-enabled assistants from 18 March to 8 May 2025; user prompts CC-BY-4.0, not gated).
Its first user message is English when the conversation's language list is only English. Its candidates get the ids
s00000 and up, so that the ids of the other candidates, which my hand labels use, do not change, and a candidate whose
text is already among the other candidates is dropped. It is labeled with the revised instruction and enters the new
hand-check draw and the bank with the other chat logs. LMArena's set of 55,000 votes was not added, because it gives
no date for a conversation.

## Amendment 4, 20 November 2026, about 8:30 PM Central: every kept request is read by hand

The revised instruction was checked on a new blind draw of 100 kept and 100 dropped candidates, drawn from its labels
and including Search Arena (`hand_check_sample_classify_out_v2.jsonl` in the work folder; my labels of the 153 that I
had not read before are in `hand_labels.jsonl`). On a request to buy it agreed with my reading on 182 of 200 (Cohen's
kappa 0.82), and on the keep decision on 175 of 200 (kappa 0.75). On the dropped side I found no request to buy in the
20 categories that it had dropped. On the kept side I read 17 of the 100 as not requests to buy, again above the limit
of 10, and 8 as requests for products outside the 20 categories. The errors are of the same kinds as before (prompts
that quote a chat or an app review, and questions about a specification, a deal or whether to buy at all).

So the classifier is used to find candidates, which it does without missing requests in these draws, and the decision
to keep a request is made by reading. Every chat-log request that the revised instruction kept is read by hand, and it
enters the bank only if I read it as a request to buy a product of one of the 20 categories; its category is the one I
read. The same reading applies to each WebShop instruction before it is used to fill a category. The README reports the
classifier's agreement with my reading on both draws, and the bank holds only requests that were read.

## Amendment 5, 20 November 2026, about 8:40 PM Central: brand names are matched with case ignored

[a team's name removed for blind review]'s gate b matches its deny list with case, so requests such as "which ipad should i go with" or "which one is
better iphone" passed it, although they name a brand of their table, which the brief forbids. A request is now also
dropped when it names, with case ignored, any brand name of the 34 tables or the product lines iPhone, iPad, MacBook,
Galaxy, AirPods and Roomba. Eight brand names that are ordinary English words (Brooks, Flair, Nothing, Ninja, Shark,
Stanley, Yeti, Varia) and the model words of the deny list keep the match with case, so that "nothing fancy" or "a
pixel gaming monitor" does not drop a request. Amazon is matched with case ignored, because a request that mentions
Amazon either names the retailer or, for tablets, its own tablets ("amazon kids+"). The renderer's refusing request check applies the same rule, with a
planted test (`test_build.py`).

## Amendment 6, 20 November 2026, about 8:45 PM Central: how the author's requests were written

The author's requests copy the form of real requests, so that my own phrasing does not enter them. For each slot that
a run category needs to reach the floor of 10, `author_forms.py` draws at random (seed "jmr-a3-20261120|author") one of
the 39 chat-log requests of another category that hold no number and are at most 160 characters long. The request is
that form with its product words replaced: the name of the product, a use or an attribute that fits only the original
product (a fortnite laptop becomes a nut-butter blender), and any brand that the form named, which is removed. The 64
requests and the form of each are in `author_requests.jsonl`; they were written at about 8:40 PM, before any model answered
any request. They pass the same brand checks as every other request.

Two implementation details changed before the bank was committed. The WebShop fill draws each category's order from
its own seed ("jmr-a3-20261120|webshop|" and the category), so that a change in one category does not reorder another.
The categories without a dominant set (keyboards, water bottles and portable speakers) get no author requests.
