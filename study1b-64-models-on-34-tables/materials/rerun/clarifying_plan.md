# A clarifying turn: plan for [a person's name removed for blind review]'s decision (JMR [project record removed for blind review], condition 1)

Written by [a team's name removed for blind review] on 21 November 2026 at the request of [a team of the project, name removed for blind review].

**Decided.** [a person's name removed for blind review] approved the plan as proposed, all three decisions (relayed by [a team of the project, name removed for blind review] at 12:08 PM Central on 21
November 2026): (1) the permission to ask goes in the system prompt, in the text given under Decision 1; (2) the
shopper's fixed reply is "I don't have anything to add. Please recommend one of these products."; (3) every item
counts once with its final pick, compared with the one-turn answers, and how often each model asks is a second result.
This record was committed before any item was built.

## What we test

In every study so far, the model picks a product in one reply. A shopping assistant in use can first ask the shopper a
question. We test whether the brand gap (the share away from the best product with names shown, minus the same share
with names hidden) is the same when the model may ask one question before it picks.

## Items

We use dom2's plainest cells, info 0 and rung 0 (no added information about the products, and the best product at its
own price): 30 tables made strictly better, 10 trials each, with the original names and with names hidden. That gives 600 items a model. On these tables
the best product is better than every other product on every attribute, so no answer from the shopper can make
another product the right choice. The same 600 items already have one-turn answers from 26 or more open models (dom2
in [a job number removed for blind review], [a job number removed for blind review], [a job number removed for blind review], [a job number removed for blind review] and [a job number removed for blind review]), and these answers are the comparison.

## Decision 1: what the model is told it may do

We propose to replace the last paragraph of dom2's system prompt with this text:

> Before you recommend, you may ask the user one question if you need more information. If you ask, your reply must
> contain only the question, starting with QUESTION:. If you do not need to ask, your very first line must contain
> ONLY the product letter (A, B, C, D, or E) -- nothing else. Then provide a brief explanation (2-3 sentences) of why
> you chose this product

The other way is to leave the system prompt as it is and add a sentence to the shopper's request ("Feel free to ask me
a question first if you need to."). We prefer the system prompt, because the rule about the reply's format is already
there.

## Decision 2: the shopper's fixed reply

We propose one reply that adds no information, the same for every item: "I don't have anything to add. Please
recommend one of these products." The other option is a reply that repeats the request ("Just what I said: a reliable
laptop for everyday work and browsing, budget around $600-800. Please recommend one of these products."). A reply
that adds a preference (for example, "I don't care about the brand") would change the condition, so we do not propose
one.

## Decision 3: how each answer is counted

- A first reply that starts with a product letter is a pick in one turn, and it is counted as the pick.
- A first reply that starts with QUESTION: gets the fixed reply, and the model's second reply is read for the pick
  (final_answer before pick, as for every answer). No third turn is given. A second reply with no letter is counted
  as unreadable and reported.
- The main estimate counts every item once, with its final pick, whether or not the model asked. The brand gap with
  the option to ask is compared with dom2's one-turn gap on the same items, by model and pooled, with the two-way
  cluster bootstrap over models and tables.
- The share of answers that ask a question, with names shown and with names hidden, is reported as a second result.
- The gaps among answers that asked and answers that did not are described only, because we do not assign at random
  which answers ask.

## Size and runner

600 items a model, with at most two turns each: about 0.3 GPU hours a model, about 10 for the 32 models of the open
panel. The runner's two-turn mode: the first call as now; if the first reply, read with final_answer, starts with
QUESTION:, a second call with the system prompt, the request, the model's question and the fixed reply. The answers
file keeps both turns.

## Amendment 1 (22 November 2026, about 3:16 AM Central, before any answer to these items has been read)

Three rulings made after this plan was approved apply to it. (1) [a person's name removed for blind review]'s rule that every prompt-level test runs on
all models, and that each study reports over all its models first: the first estimate is pooled over every model that
answered all 600 items (the 32 open models through [a computing cluster's name removed for blind review], Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5 through the
Batch API, and the GPT models through Codex when [a team's name removed for blind review]'s runs end), and each route's estimate is reported beside it.
(2) The paper's exclusion rule: a model whose answers are read in under 90 per cent of a build's items (clar1, or its
one-turn twin in dom2) is reported apart and left out of every pooled estimate. (3) The one-turn comparison is each
item's own twin in dom2 (the item's source_id): for the open models, the letters of export [a job number removed for blind review] ([a job number removed for blind review], read with
final_answer before pick); for the Claude models, their dom2 answers in [repository path removed for blind review] The gap with the
option to ask, the one-turn gap and their difference use paired draws, models and tables resampled together
(10,000 draws, seed 20261120). The script is [repository path removed for blind review], with its tests.
