# Sources of real shopping requests, real assortments and shopping-agent benchmarks (20 November 2026)

[the project's team and issue removed for blind review] searched for sources before choosing any. [a person's name removed for blind review] asked for the
search at 6:28 PM Central ([a person's words removed for blind review]) and
kept it practical at 6:35 PM ([a person's words removed for blind review]). Each row was read from the source's own page: its Hugging Face card and API record, its GitHub
repository and licence file, or its paper. A cell that we could not confirm on the source's own page says "not
verified". The dates of the three request sets that we downloaded (the first three rows) were read from their files.

The last column says what each source can serve: (a) real requests that people wrote to a chat assistant, or wrote as
shopping instructions or queries; (b) real product assortments with prices, ratings and review counts; (c) a published
benchmark of shopping agents whose design the paper can cite or match.

## Requests to a chat assistant

| Source | What it holds | Size | Dates | Licence and access | Who wrote the requests | Serves |
|---|---|---|---|---|---|---|
| WildChat-4.8M, non-toxic version (Allen AI; huggingface.co/datasets/allenai/WildChat-4.8M) | Conversations between users and ChatGPT models through a free service that the researchers ran, with each turn's text, language, timestamp, hashed IP and country | 3,199,860 conversations (of 4,804,190 collected; toxic conversations and minors removed); 86 parquet files, 15 GB | 9 April 2023 to 31 July 2025 (read from the files) | ODC-BY 1.0, not gated: the data may be shared with attribution | Real users of a deployed chat assistant | (a) |
| LMArena human preference 100k (huggingface.co/datasets/lmarena-ai/arena-human-preference-100k) | English conversations from the Chatbot Arena leaderboard, each answered by two models and voted on by the user | 106,134 conversations | 19 June to 19 August 2024 (read from the file) | User prompts CC-BY-4.0; model outputs under each provider's terms; not gated | Real users of Chatbot Arena | (a) |
| LMArena human preference 140k (huggingface.co/datasets/lmarena-ai/arena-human-preference-140k) | The same kind of record, text-only category | 135,634 votes | 17 April to 24 July 2025 (read from the files) | User prompts CC-BY-4.0; model outputs under each provider's terms; not gated | Real users of Chatbot Arena | (a) |
| LMArena Search Arena 24k (huggingface.co/datasets/lmarena-ai/search-arena-24k), added at 8:20 PM | Conversations with search-enabled assistants, with the user's vote between two models | 24,069 conversations, about 11,000 users | 18 March to 8 May 2025 (card and files) | User prompts CC-BY-4.0; model outputs under each provider's terms; not gated | Real users of Search Arena | (a) |
| LMArena human preference 55k (huggingface.co/datasets/lmarena-ai/arena-human-preference-55k) | Chatbot Arena conversations with votes | About 55,000 | No date per conversation | Apache-2.0, not gated | Real users of Chatbot Arena | Not used, because no conversation has a date |
| WildChat-1M (huggingface.co/datasets/allenai/WildChat-1M) | The first year of WildChat, inside WildChat-4.8M | 837,989 conversations | From April 2023 (overall range not on the card) | ODC-BY, not gated | Real users of a deployed chat assistant | (a), contained in the first row |
| LMSYS-Chat-1M (huggingface.co/datasets/lmsys/lmsys-chat-1m) | Conversations with 25 models on the Vicuna demo and Chatbot Arena | 1,000,000 conversations | April to August 2023 | Gated by an agreement that forbids distributing, disclosing or hosting the dataset for any third party | Real users | (a) for reading only; its text cannot go into a deposited bank |
| ConsumerQ (Uberti-Bona Marin et al., arXiv 2609.18729) | Commercial-advice queries that the authors filtered from LMSYS-Chat-1M (1,837) and WildChat-1M (691) | 2,528 queries, 117 of them about physical products | Not stated; the source logs date from 2023 and 2024 | Not released: the paper gives no link and no data licence | Real users of the two logs | (a) if the authors release it; their filter is the closest precedent for ours |
| OpenAssistant OASST2 (huggingface.co/datasets/OpenAssistant/oasst2) | Conversation trees written by volunteers for training an assistant | Not counted here | Files dated 5 November 2023 | Apache-2.0, not gated | Volunteers writing prompts for a dataset, not users seeking advice | (a), weaker than the chat logs |
| ShareGPT, Vicuna unfiltered copy (huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered) | Conversations that users shared from ChatGPT through sharegpt.com, collected by a third party | About 90,000 conversations (file names) | Up to April 2023 | The card says Apache-2.0, but the collector does not own the conversations; provenance not verified | Real ChatGPT users | Not used, because its licence cannot be traced |
| Reddit buying-advice communities (r/BuyItForLife, r/suggestmeabuy) | Posts that ask other people for product advice | No research dataset with a stated licence found | n/a | Reddit's own terms could not be read (the site refused the request); not verified | Real Reddit users, writing to people, not to an assistant | Not used |

## Shopping instructions and search queries

| Source | What it holds | Size | Dates | Licence and access | Who wrote the requests | Serves |
|---|---|---|---|---|---|---|
| WebShop (Yao et al., NeurIPS 2022; github.com/princeton-nlp/WebShop) | A simulated shop of scraped Amazon products, with shopping instructions written for target products | 12,087 instructions; 1,181,436 products | Paper July 2022 | Code MIT (LICENSE.md); no separate licence is stated for the data, and the products were scraped from amazon.com | Crowd workers on Mechanical Turk, each shown a target product (213 workers; 15.9 words on average) | (a) as crowd-written requests; (b) price only, no ratings; (c) |
| Amazon Shopping Queries Dataset, ESCI (KDD Cup 2022; github.com/amazon-science/esci-data) | Difficult search queries, each with up to 40 products judged Exact, Substitute, Complement or Irrelevant | 130,652 queries and about 2.6 million judgments (48,300 queries in the reduced set) | Not stated; paper 2022 | Apache-2.0, open | Amazon shoppers' search queries (origin of each query not verified) | (a) as search queries, which are shorter than requests to an assistant; no prices or ratings |
| Amazon-C4 (Hou et al. 2024; huggingface.co/datasets/McAuley-Lab/Amazon-C4) | Complex product queries, each paired with the item whose review it was written from | 21,223 queries; 1,058,417 items | Built from the 2023 reviews; released April 2024 | No licence stated; not gated | ChatGPT, rewriting five-star reviews in the first person | Not used, because a model wrote the queries |
| U-NEED (SIGIR 2023; github.com/LeeeeoLiu/U-NEED) | Pre-sales dialogues with product knowledge | 7,698 dialogues | Not verified | Research use only, by email application | Real e-commerce users (language not verified; a secondary source says Chinese) | Not used |
| MG-ShopDial (Bernard and Balog, SIGIR 2023; github.com/iai-group/MG-ShopDial) | Human-to-human shopping conversations with goal labels | 64 dialogues | Not verified | No licence stated | Participants following coached instructions | Not used, too small |

## Real assortments with prices, ratings and review counts (for [issue number removed for blind review], [project record removed for blind review])

| Source | What it holds | Size | Dates | Licence and access | Serves |
|---|---|---|---|---|---|
| Amazon Reviews 2023 (Hou et al. 2024; huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) | Item metadata with price, average_rating, rating_number, features, categories and store, plus the reviews | 48.19 million items in 33 categories; 571.54 million reviews | May 1996 to September 2023; prices as at the crawl | No licence stated on the card, the project page or the API record; not gated; the content is Amazon's | (b), the only source found with all three fields |
| WebMall (Peeters et al., SIGIR 2026; github.com/wbsg-uni-mannheim/WebMall) | Four local web shops built from product offers in the Common Crawl | 4,421 offers; 91 tasks in 11 categories | Offers from the October 2024 crawl | No licence file on the repository page | (b) price yes, ratings and review counts not verified; (c) |
| ACES (Allouah et al., WWW 2026; github.com/mycustomai/ACES and huggingface.co/datasets/My-Custom-AI/ACE-BB) | A mock shop of eight real Amazon listings per category, and the agents' runs with title, price, rating, rating count, position and tags | ACE-BB 9,000 rows | 2025 | README says MIT; no licence file and no licence field on the datasets | (b) with prices, ratings and counts set as experimental variables; (c) |

## Published benchmarks of shopping agents (designs to cite or match)

| Source | Design | Released | Licence |
|---|---|---|---|
| WebShop (Yao et al. 2022) | Agents search and buy in a simulated shop to meet a crowd-written instruction | Code, products and instructions | Code MIT |
| ACES (Allouah et al., arXiv 2508.02630; WWW 2026) | Language-model agents that read screenshots or text pick one of eight real listings whose position, tags, price, rating and review count are randomized; brands are held in product fixed effects and never varied | Sandbox code and three datasets of runs | README MIT; datasets with no licence field |
| ABxLab (Cherep et al., arXiv 2509.25609; ICLR 2026) | A tool that edits prices, ratings and nudges in a WebArena shop to measure agents' choices | Code and task files; result data on request | Licence file present, type not read |
| Magentic Marketplace (Microsoft Research, arXiv 2510.25779) | Buyer and seller agents in a two-sided market | Framework and sample scenario | MIT |
| PriceBench (Kireyev, arXiv 2609.31468; EMNLP 2026 Industry Track) | 28 models book hotels from 179 New York properties; a logit model recovers each model's price, quality and brand preferences | Code, tasks and responses | Code MIT; data "for research use" |
| ShoppingBench (Wang et al.) | Instructions written by a model over a sandbox of 2.5 million products | Data in the repository | Apache-2.0 |
| ChatShop (Chen, Wiseman and Dhingra 2024) | WebShop with a simulated shopper who answers clarifying questions | Code | MIT |
| WebMall (Peeters et al. 2026) | Agents compare offers across four shops | Shops and tasks | Not stated |
| DeepShop (Lyu et al. 2025) | Model-evolved shopping queries for agents on the live web | No data link found | Not stated |
| Shopping MMLU (Amazon KDD Cup 2024) | Questions on shopping knowledge, not agent choice | Questions | Apache-2.0 (from a search result; not verified) |
| tau-bench, retail domain (Sierra 2024) | Customer-service tasks with a simulated user; no product-recommendation requests | Tasks | MIT |
| Brand audits without released data: Monaco, Lenti and Pierri (arXiv 2611.07614); Chu and Hou (arXiv 2606.17443); Malthouse et al. (arXiv 2609.16304); Rienecker et al., ChoiceEval (arXiv 2603.18300) | Product pages or prompts with brand names varied, or brands counted in open answers | No data or code link on their pages | Papers only |

## What we chose, and why

For the requests we chose WildChat-4.8M and the two LMArena sets. They are the only sources that we found in which
real people typed requests to a chat assistant, before this project existed, under a licence that lets the selected
requests be deposited verbatim (ODC-BY for WildChat, CC-BY-4.0 for the Arena prompts), with a date for every
conversation. Together they span April 2023 to July 2025 and two kinds of service: a free ChatGPT service and a site
where users compare models. Uberti-Bona Marin et al. filtered the same kind of logs (WildChat-1M and LMSYS-Chat-1M)
for consumer-advice queries, and their filter is the precedent that we cite for ours. LMSYS-Chat-1M was left out,
because its agreement forbids disclosing its contents to any third party, and ConsumerQ was left out because it is not
released.

Where the chat logs hold too few requests for a category of the 34 tables, we add WebShop's instructions for that
category. Crowd workers wrote those instructions for a target product, so they are labeled "crowd-written for a
dataset" in the bank and reported apart from the chat-log requests. If a category still has no request, we write a
request for it and label it "written by the author", as [a person's name removed for blind review] allowed at 6:35 PM; these are also reported apart.
ESCI is not used for requests, because search queries of two to five words are not what a person types to an
assistant.

For real assortments ([issue number removed for blind review]), Amazon Reviews 2023 is the only source that we found with prices, average ratings
and review counts for each product; it states no licence, so the product text should be quoted only as far as fair
use allows; [a note on the project's later work removed for blind review]. WebMall (prices from the October 2024 Common Crawl) and
the eight real listings per category in ACES are the other two candidates.
