# The Requests, the Prompts and the Models of Study 1b Under Requests That People Typed

In this part, we give the requests (how they were found and how many came from each collection), then the prompts (how
each request was paired with tables and shown in three versions of the names), and last the models and their
responses (the models' settings and the coding of their responses). The bank of requests is identified by its SHA-256 hash, and the paper's rules for coding responses
and for leaving out models apply.

## The Requests

To find the requests, we searched four public collections of conversations with chat assistants: WildChat-4.8M and
three sets from LMArena (one of 140,000 votes, one of 100,000 conversations and Search Arena), which contain 3,465,697
conversations dated from April 2023 to July 2025. A keyword filter and a classifier proposed candidates, and Claude
Opus 5.5 examined every kept request in full. We kept only requests to buy a product of our categories that named no brand or product
line of the tables, because such a name would show the brand in the version without brand names. The bank holds
103 such requests: 39 from WildChat,
33 and 9 from the two sets of votes and conversations and
22 from Search Arena. It also holds 51 instructions that crowd
workers wrote for the WebShop data set (Yao et al. 2022) and 64 requests that we wrote in
the form of real requests, which were run in the same way and are reported apart.

## The Prompts

Each request was paired with every table of Study 1a in its category. In these tables, the optimal product is better
than or equal to every other product on every displayed attribute and is priced no higher than any other, so it is the
optimal product under any need that a request states about these attributes or price. Up to 25 typed requests in each
category were drawn at random with a fixed seed, and requests in categories with no table in Study 1a were not run. From the
87 typed requests drawn this way, we formed 208 pairs of a request and a
table in 15 categories, and smartphones hold 75 of
them. The
37 crowd-written instructions and 64 requests that we wrote gave
69 and 77 more pairs, for 354 pairs over
30 tables in 17 categories. Each pair was shown in three versions that
differed only in the product names: without brand names; with brand names, the fictitious name on the optimal product
and familiar names on the others; and with the names swapped, a familiar name on the optimal product and the
fictitious name on one familiar product. The optimal product was priced at the price of the cheapest other product,
and no reliability information was shown. Every prompt met the checks of Study 1a and a check that the request itself
named no brand of the table.

## The Models and Their Responses

In all, 40 models answered some or all of the 1,062 prompts. Claude Haiku 5.5,
Sonnet 5.5, Opus 5.5 and Fable 5.1 answered through Anthropic's batch interface with adaptive thinking and at most
2,000 output tokens (8,000 for Haiku 5.5), and GPT-6 Astra, GPT-6.1 Sol, GPT-6.2 Astra and GPT-6.2 Sol through OpenAI's
Codex tool. The
32 models with open weights ran on a university computing cluster, each at its
developer's default sampling settings and with at most 1,024 output tokens. As the outcome, we coded the letter of the product that a response
recommended, from its final answer: the letter on its first line, or the letter that its text gave as the
recommendation. A response that recommended no product, such as one that began "None of the products listed (A, B, C,
D, or E) match your request," was coded as a decline. Averaged over the models, declines were
2.7% of the responses to typed
requests without brand names and
3.6% with them. A pair entered
the effect only when the model's responses without and with brand names both recommended a product, so the models'
pairs number from 137 to 208. As in every study, a model whose
recommendation could be identified in fewer than 90% of its responses that were not declines was left out (Kimi
Linear 48B, 74.1%), and a model that had
not answered every prompt entered no estimate (GPT-6 Astra answered 269 of the
prompts and GPT-6.2 Astra 431). The 37 models that remained came
from 13 developers, and 31 of them had open weights.
Declines were counted after the estimates had been computed, and counting them changed no estimate.
