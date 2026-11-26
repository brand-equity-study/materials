# Data dictionary

Every column of every data file in this package, with what it holds. The files are listed in each folder's `FILES.csv` (with their rows and SHA-256); files of the same kind share one table below.

## Short names of folders and values

Some folders, files and values keep the short names that the code reads. Each is explained here once.

| Name | What it names |
|---|---|
| `h2`, `h1`, `h2-rung2` | Study 1c's store: `h2` holds its 7,680 prompts at both prices; `h1` holds the equal-price half under other identifiers; `h2-rung2` holds the open models' answers to the half at the lower price |
| `s1`, `stage1`, `stage2` | Study 1c's search step: its first prompts and each model's second prompts |
| `r1` | Study 2a's prompts with the retrieved reviews |
| `b10`, `b16`, `b17` | values of the `study` column in the open models' letters: the retrieved reviews of Study 2a, the store of Study 1c and its search step |
| `b2`, `dom2`, `full2` | the folder of the open models' answers to the product tables: `dom2` holds Study 1a's strictly better tables and `full2` the corpus's original tables, which the audit reads |
| `b9`, `split1`, `eq1`, `attr1` | the open models' counts (`b9-counts.csv`) on each piece of information alone (`split1`) and on the price (`eq1`); `attr1` names the prompts that add further information |
| `s1rerun1` | the corpus's prompts answered again by the open models, which Study 1b reads |
| `s1prio1`, `clar1` | Study 1b's prompts with stated priorities and with the clarifying turn |
| `full1`, `pilot1` | Study 2b's measure: its prompts and its pretest; the results of the measure over every model are in `full1-all/`, those of the Claude and GPT models in `full1-claude-api/` and `full1-codex/`, the stopping rules of those models in `full1-stop-rules/` and the design's figures in `full1-design/` |
| `full1-fable`, `full1-fable-rest` | the two sets in which Claude Fable 5.1 and the GPT models answered Study 3b's audit items; together they hold every item (`item_sets.csv`) |
| `rung`, `rung0`, `rung2` | the price step: 0 when the best product's price equals the cheapest other product's, 1 when it is 15 percent below it and 2 when it is 30 percent below it |

## The models and the computing

### The models: `models/models.csv`, one row for each model and set of prompts

1 file.

| Column | What it holds |
|---|---|
| `study` | the study folder that holds the answers |
| `set` | the set of prompts (the folder under data/) |
| `model` | the model as the data files name it |
| `released_model` | the model as its developer released it |
| `developer` | the developer |
| `open_weights` | yes if the weights are public |
| `identifier` | the identifier that the provider returned or was sent, or the repository with its revision identifier |
| `route` | how the model was run |
| `settings` | the decoding settings recorded for the run |
| `first_answer` | the date of the first answer or score (empty when the files record only the end) |
| `last_answer` | the date of the last answer or score (for the open models, the date on which the run ended) |
| `answers` | the answers (or, for the checkpoints, the pages scored) in the package |

### The computing: `computing/gpu_jobs.csv`, one row for each run on the cluster

1 file.

| Column | What it holds |
|---|---|
| `job` | the scheduler's number for the run |
| `study` | the part of the paper that the run served |
| `gpu_type` | the GPU type (h100: NVIDIA H100; l40s: NVIDIA L40S; empty for a run without a GPU) |
| `gpu_hours` | GPU hours: the run's time times its GPUs |
| `cpu_core_hours` | CPU core hours |
| `states` | the run's final states, joined by + when its parts ended differently |

### The answers in full of the models with open weights to the typed requests, the clarifying turn, the stated priorities, the store, the search step, the retrieved reviews, the price and each piece of information alone: `data/open-models/<set>/<model>/<cell>.jsonl.gz` in the folders of Study 1b (`study1b-64-models-on-34-tables/`: `requests`, `clarifying`, `priorities`), Study 1c (`study1c-product-feeds-and-a-store-search/`: `store/h1`, `store/h2-rung2`, `search/stage2`), Study 2a (`study2a-experience-attributes-stated-for-every-product/`: `retrieval`), Study 2b (`study2b-how-much-a-familiar-brand-is-worth/`: `price`) and the analysis of each piece of information alone (`web-appendix-analyses/each-piece-of-information-alone/`: `each-piece-alone`, `further-information`)

6432 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier, the same as in the prompts of the set's study |
| `model` | the model's short name; the set's RUNS.csv gives its repository and revision |
| `hf_repo` | the Hugging Face repository of the weights |
| `revision` | the revision identifier of the weights |
| `route` | the server software, on a university computing cluster |
| `run_finished_date` | the date on which the model's run ended |
| `table` | the product table |
| `cell` | the prompt's condition: the names version, the information level and the price step, joined by hyphens (for example `crossed-info0-rung0`) |
| `names` | the names version |
| `info` | 1 if every product's reliability information was shown (a warranty, a failure rate and a time on the market, with a sentence that the figures came from independent lab testing), 0 if not |
| `rung` | the best product's price: 0 equal to the cheapest other product, 1 15 percent below it, 2 30 percent below it |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `best` | the letter under which the best product was shown in this prompt |
| `answer_text` | the same text with white space removed at its start and end |
| `raw_text` | the text that the server returned |
| `finish` | the server's reason for ending the answer (stop: the model finished; length: the token limit) |
| `tokens_out` | tokens in the answer |
| `letter` | the letter that common/parse_answer.py reads from answer_text; empty when it reads none (the studies read the letters and counts that the computing cluster wrote from these answers) |
| `letter_how` | where the parser found the letter: first-line, body, several (more than one letter, so none is returned) or none |
| `asked` | in the clarifying turn only: True when the model asked the shopper a question before its final answer |

### The runs of the models with open weights for each set: `data/open-models/<set>/RUNS.csv` in the same folders

10 files.

| Column | What it holds |
|---|---|
| `model` | the model's short name |
| `hf_repo` | the Hugging Face repository |
| `revision` | the revision identifier of the weights |
| `temperature` | sampling temperature |
| `top_p` | nucleus sampling threshold |
| `top_k` | top-k sampling limit |
| `min_p` | minimum-probability sampling threshold |
| `repetition_penalty` | repetition penalty |
| `max_tokens` | the largest number of tokens allowed for an answer |
| `max_model_len` | the context length served |
| `switch` | options passed to the model's chat template (for example turning thinking off) |
| `items_sha256` | the SHA-256 of the prompts file that the run read |
| `vllm` | vLLM version |
| `torch` | PyTorch version |
| `transformers` | Transformers version |
| `python` | Python version |
| `finished_date` | the date on which the run ended |

### Each model's characteristics: `models/model_characteristics.csv`, one row per model (16_pooled.py reads developer, open and thinking)

1 file.

| Column | What it holds |
|---|---|
| `key` | the model's key, as the answers name it |
| `hf_repo` | an open model's repository; empty otherwise |
| `revision` | the repository's revision that was run |
| `developer` | the developer of the model |
| `author` | who published the weights that were run (the developer, or a repackager) |
| `open` | open (weights published) or closed |
| `base_or_chat` | chat (instruction-tuned) or base |
| `thinking` | the model's thinking setting as run (on, off, or the model's default) |
| `params_total` | the total number of parameters |
| `params_total_source` | where params_total comes from |
| `params_listed_b` | the parameters in billions that the model's name or card lists |
| `params_listed_source` | where params_listed_b comes from |
| `experts` | the number of experts of a mixture of experts; 0 otherwise |
| `moe` | whether the model is a mixture of experts |
| `moe_source` | where moe comes from |
| `params_active_b` | the parameters in billions active for each token |
| `params_active_source` | where params_active_b comes from |
| `set` | the set of models: `corpus` (the corpus's 30 models), `dom2` (the nine current models of Study 1a's strictly better tables and of the corpus prompts answered again) or open panel |
| `release_date` | the model's release date |
| `release_date_source` | where release_date comes from |
| `model_id` | the identifier that the provider or the repository gives |
| `thinking_source` | where thinking comes from |

## Study 1a (`study1a-tables-with-one-optimal-product/`)

### The controlled test's answers: `study1a-tables-with-one-optimal-product/data/strictly-better-tables/<model>/<cell>.jsonl.gz` and `study1a-tables-with-one-optimal-product/data/original-tables/<model>/<cell>.jsonl.gz`, one row per answer

120 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier; the same id in the set's prompts file |
| `model` | the model, by the name that the run requested |
| `model_returned` | the model name that the provider's response reported |
| `route` | how the answer was obtained |
| `answered_at_utc` | when the response was recorded (UTC, ISO 8601) |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `cell` | the prompt's condition: the names version, the information level and the price step, joined by hyphens (for example `crossed-info0-rung0`) |
| `names` | the names version: hidden (every product shown as Product A to E with no brand), original (the invented name on the best product and familiar names on the others) or crossed (a familiar name on the best product and the invented name on a familiar product) |
| `info` | 1 if every product's reliability information was shown (a warranty, a failure rate and a time on the market, with a sentence that the figures came from independent lab testing), 0 if not |
| `rung` | the best product's price: 0 equal to the cheapest other product, 1 15 percent below it, 2 30 percent below it |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `paraphrase` | which of the four wordings of the system prompt the prompt used (0 to 3) |
| `best` | the letter under which the best product was shown in this prompt |
| `answer_text` | the model's answer, exactly as returned |
| `letter` | the letter that common/parse_answer.py reads from the answer; empty when it reads none |
| `letter_how` | where the parser found the letter: first-line, body, several (more than one letter, so none is returned) or none |
| `stop_reason` | the provider's reason for ending the answer (end_turn: the model finished; max_tokens: the length limit) |
| `input_tokens` | tokens in the prompt, as the provider counted them |
| `output_tokens` | tokens in the answer, as the provider counted them |
| `cache_read_input_tokens` | prompt tokens read from the provider's prompt cache |
| `cache_creation_input_tokens` | prompt tokens written to the provider's prompt cache |

### The controlled test's prompts: `study1a-tables-with-one-optimal-product/materials/strictly-better-tables/prompts.jsonl.gz` and `study1a-tables-with-one-optimal-product/materials/original-tables/prompts.jsonl.gz`, one row per prompt

2 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier |
| `cell` | the prompt's condition: the names version, the information level and the price step, joined by hyphens (for example `crossed-info0-rung0`) |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `names` | the names version: hidden (every product shown as Product A to E with no brand), original (the invented name on the best product and familiar names on the others) or crossed (a familiar name on the best product and the invented name on a familiar product) |
| `info` | 1 if every product's reliability information was shown (a warranty, a failure rate and a time on the market, with a sentence that the figures came from independent lab testing), 0 if not |
| `rung` | the best product's price: 0 equal to the cheapest other product, 1 15 percent below it, 2 30 percent below it |
| `paraphrase` | which of the four wordings of the system prompt the prompt used (0 to 3) |
| `partner_orig` | in the crossed version, the letter (in the table file) of the familiar product whose name the best product takes; empty in the other versions |
| `best` | the letter under which the best product was shown in this prompt |
| `products` | for each letter shown: the product's letter in the table file (orig), the name shown (shown_name), the kind of name shown (kind: hidden, invented or familiar-high, familiar-medium), the price shown, the product's true brand (true_brand) and the kind of that brand (true_kind) |
| `order` | the letters in the order in which the products were shown |
| `system` | the system prompt, as sent |
| `user` | the user's message, as sent: the request and the product listings |

### Answers of the models with open weights: `study1a-tables-with-one-optimal-product/data/open-models/<set>/<model>/<cell>.jsonl.gz`

330 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier, the same as in the prompts of Study 1's set or of the corpus's own prompts (study1b-64-models-on-34-tables/materials/rerun) |
| `model` | the model's short name; RUNS.csv gives its repository and revision |
| `hf_repo` | the Hugging Face repository of the weights |
| `revision` | the revision identifier of the weights |
| `route` | the server software, on a university computing cluster |
| `run_finished_date` | the date on which the model's run ended |
| `table` | the product table |
| `cell` | the prompt's condition: the names version, the information level and the price step, joined by hyphens (for example `crossed-info0-rung0`); on the corpus's own prompts, the names version |
| `names` | the names version (as in Study 1's answers, or as on the corpus's own prompts) |
| `info` | 1 if every product's reliability information was shown (a warranty, a failure rate and a time on the market, with a sentence that the figures came from independent lab testing), 0 if not |
| `rung` | the best product's price: 0 equal to the cheapest other product, 1 15 percent below it, 2 30 percent below it |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `best` | the letter under which the best product was shown in this prompt |
| `answer_text` | the same text with white space removed at its start and end |
| `raw_text` | the text that the server returned |
| `finish` | the server's reason for ending the answer (stop: the model finished; length: the token limit) |
| `tokens_out` | tokens in the answer |
| `letter` | the letter that common/parse_answer.py reads from answer_text; empty when it reads none |
| `letter_how` | where the parser found the letter: first-line, body, several (more than one letter, so none is returned) or none |

### The runs of the models with open weights: `study1a-tables-with-one-optimal-product/data/open-models/RUNS.csv`

1 file.

| Column | What it holds |
|---|---|
| `set` | the set of prompts: strictly-better-tables, original-tables or rerun (the corpus's own prompts) |
| `model` | the model's short name |
| `hf_repo` | the Hugging Face repository |
| `revision` | the revision identifier of the weights |
| `temperature` | sampling temperature |
| `top_p` | nucleus sampling threshold |
| `top_k` | top-k sampling limit |
| `min_p` | minimum-probability sampling threshold |
| `repetition_penalty` | repetition penalty |
| `max_tokens` | the largest number of tokens allowed for an answer |
| `max_model_len` | the context length served |
| `switch` | options passed to the model's chat template (for example turning thinking off) |
| `items_sha256` | the SHA-256 of the prompts file that the run read |
| `vllm` | vLLM version |
| `torch` | PyTorch version |
| `transformers` | Transformers version |
| `python` | Python version |
| `finished_date` | the date on which the run ended |

## Study 1b (`study1b-64-models-on-34-tables/`)

### Current models' answers to the corpus's own prompts: `study1b-64-models-on-34-tables/data/rerun/<model>/<cell>.jsonl.gz`

27 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier; the same id in the set's prompts file |
| `model` | the model, by the name that the run requested |
| `model_returned` | the model name that the response reported (for the Claude command line, every model named in its reply) |
| `route` | how the answer was obtained: the Anthropic Messages API, the OpenAI Codex command line (with its version and reasoning effort) or the Claude command line |
| `answered_at_utc` | when the response was recorded (UTC, ISO 8601) |
| `table` | the product table (sr_<category>_<number>) |
| `category` | the product category |
| `cell` | the names version (the same as names) |
| `names` | shown (the corpus prompt with the brand names), hidden (the corpus prompt with the names hidden) or hidden_clean (the hidden prompt with the brand hints that it still held removed; study1b-64-models-on-34-tables/materials/names_hidden_leaks.csv lists them) |
| `trial` | the trial number of the corpus answer that the prompt copies |
| `paraphrase` | which of the corpus's system prompt wordings the prompt used |
| `best` | the letter under which the best product was shown in this prompt |
| `answer_text` | the model's answer, exactly as returned |
| `letter` | the letter that common/parse_answer.py reads from the answer (final_answer, then pick); empty when it reads none |
| `letter_how` | where the parser found the letter: first-line, body, several (more than one letter, so none is returned) or none |
| `stop_reason` | the provider's reason for ending the answer (end_turn: the model finished; max_tokens: the length limit) |
| `input_tokens` | tokens in the prompt, as the provider counted them |
| `output_tokens` | tokens in the answer, as the provider counted them |
| `cache_read_input_tokens` | prompt tokens read from the provider's prompt cache (Messages API only) |
| `cache_creation_input_tokens` | prompt tokens written to the provider's prompt cache (Messages API only) |
| `cli_version` | the Claude command line's version (Claude command line only) |
| `thinking_tokens` | tokens of thinking before the answer (Claude command line only) |
| `seconds` | seconds that the command line took for the answer (command lines only) |
| `error` | a message that the command line recorded during the answer, such as a reconnection when the model was at capacity; empty when there was none (command lines only) |
| `cached_input_tokens` | prompt tokens served from the cache (OpenAI Codex command line only) |
| `reasoning_output_tokens` | tokens of reasoning before the answer (OpenAI Codex command line only) |

### The corpus's own prompts, answered again by current models: `study1b-64-models-on-34-tables/materials/rerun/prompts.jsonl.gz`

1 file.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier |
| `cell` | the names version (the same as names) |
| `table` | the product table (sr_<category>_<number>) |
| `category` | the product category |
| `trial` | the trial number of the corpus answer that the prompt copies |
| `names` | shown, hidden or hidden_clean, as in the current models' answers to these prompts |
| `info` | always 0 (no information was added to the corpus's prompts) |
| `rung` | always 0 (the corpus's prices) |
| `paraphrase` | which of the corpus's system prompt wordings the prompt used |
| `partner_orig` | always empty (these prompts have no crossed version) |
| `best` | the letter under which the best product was shown in this prompt |
| `products` | for each letter shown: the product's letter in the table file (orig), the name shown (shown_name), the kind of name shown (kind: hidden, invented or familiar-high, familiar-medium), the price shown, the product's true brand (true_brand) and the kind of that brand (true_kind) |
| `order` | the letters in the order in which the products were shown |
| `system` | the system prompt, as sent |
| `user` | the user's message, as sent: the request and the product listings |
| `source` | the corpus answer that the prompt copies byte for byte: its condition (corpus_condition), its model (model_key) and its row's identifier in study1b-64-models-on-34-tables/data/corpus (trial_id) |

### Answers to consumers' requests: `study1b-64-models-on-34-tables/data/requests/<model>/<names>.jsonl.gz`

12 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier; the same id in the set's prompts file |
| `model` | the model, by the name that the run requested |
| `model_returned` | the model name that the provider's response reported |
| `route` | how the answer was obtained |
| `batch` | the batch (0 to 3) in which the runner sent the prompt; 14_requests.py reads the answers in batch order |
| `max_tokens` | the largest number of tokens allowed for an answer |
| `answered_at_utc` | when the response was recorded (UTC, ISO 8601) |
| `request` | the request's identifier in study1b-64-models-on-34-tables/materials/requests/requests.jsonl.gz |
| `kind` | who wrote the request: chat-log (a person typing to a chat assistant), crowd-written for a dataset (a WebShop instruction) or written by the author |
| `table` | the strictly better table that the request was paired with (sr_<category>_<number>_dom) |
| `category` | the product category |
| `names` | the names version: hidden (every product shown as Product A to E with no brand), original (the invented name on the best product and familiar names on the others) or crossed (a familiar name on the best product and the invented name on a familiar product) |
| `best` | the letter under which the best product was shown in this prompt |
| `answer_text` | the model's answer, exactly as returned |
| `letter` | the letter that common/parse_answer.py reads from the answer; empty when it reads none |
| `letter_how` | where the parser found the letter: first-line, body, several (more than one letter, so none is returned) or none |
| `stop_reason` | the provider's reason for ending the answer (end_turn: the model finished; max_tokens: the length limit) |
| `input_tokens` | tokens in the prompt, as the provider counted them |
| `output_tokens` | tokens in the answer, as the provider counted them |
| `cache_read_input_tokens` | prompt tokens read from the provider's prompt cache |
| `cache_creation_input_tokens` | prompt tokens written to the provider's prompt cache |

### Answers of the GPT-6 models to consumers' requests through OpenAI's Codex command line: `study1b-64-models-on-34-tables/data/requests-codex/<model>/<names>.jsonl.gz`

12 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier; the same id in the set's prompts file |
| `model` | the model, by the name that the run requested |
| `model_returned` | the model name that the provider's response reported |
| `route` | how the answer was obtained |
| `answered_at_utc` | when the response was recorded (UTC, ISO 8601) |
| `seconds` | seconds from sending the prompt to the answer |
| `request` | the request's identifier in study1b-64-models-on-34-tables/materials/requests/requests.jsonl.gz |
| `kind` | who wrote the request: chat-log (a person typing to a chat assistant), crowd-written for a dataset (a WebShop instruction) or written by the author |
| `table` | the strictly better table that the request was paired with (sr_<category>_<number>_dom) |
| `category` | the product category |
| `names` | the names version: hidden (every product shown as Product A to E with no brand), original (the invented name on the best product and familiar names on the others) or crossed (a familiar name on the best product and the invented name on a familiar product) |
| `best` | the letter under which the best product was shown in this prompt |
| `answer_text` | the model's answer, exactly as returned |
| `letter` | the letter that common/parse_answer.py reads from the answer; empty when it reads none |
| `letter_how` | where the parser found the letter: first-line, body, several (more than one letter, so none is returned) or none |
| `stop_reason` | the provider's reason for ending the answer (end_turn: the model finished; max_tokens: the length limit) |
| `input_tokens` | tokens in the prompt, as the provider counted them |
| `cached_input_tokens` | input tokens that the provider read from its cache |
| `output_tokens` | tokens in the answer, as the provider counted them |
| `reasoning_output_tokens` | tokens of reasoning that the model wrote before its answer |

### Prompts for consumers' requests: `study1b-64-models-on-34-tables/materials/requests/prompts.jsonl.gz`

1 file.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier |
| `request` | the request's identifier in requests.jsonl.gz |
| `kind` | who wrote the request (chat-log, crowd-written for a dataset, written by the author) |
| `cell` | the prompt's condition: the names version, the information level and the price step, joined by hyphens (for example `crossed-info0-rung0`) |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `trial` | always 0 (one prompt for each request, table and names version) |
| `names` | the names version: hidden (every product shown as Product A to E with no brand), original (the invented name on the best product and familiar names on the others) or crossed (a familiar name on the best product and the invented name on a familiar product) |
| `info` | always 0 (no reliability information) |
| `rung` | always 0 (the best product's price equals the cheapest other product's) |
| `paraphrase` | always 0 (the first system prompt wording) |
| `partner_orig` | in the crossed version, the letter (in the table file) of the familiar product whose name the best product takes; empty in the other versions |
| `best` | the letter under which the best product was shown in this prompt |
| `products` | for each letter shown: the product's letter in the table file (orig), the name shown (shown_name), the kind of name shown (kind: hidden, invented or familiar-high, familiar-medium), the price shown, the product's true brand (true_brand) and the kind of that brand (true_kind) |
| `order` | the letters in the order in which the products were shown |
| `system` | the system prompt, as sent |
| `user` | the user's message, as sent: the request and the product listings |
| `request_text` | the request as placed at the start of the user's message |

### The bank of requests: `study1b-64-models-on-34-tables/materials/requests/requests.jsonl.gz`

1 file.

| Column | What it holds |
|---|---|
| `id` | the request's identifier |
| `kind` | who wrote the request (chat-log, crowd-written for a dataset, written by the author) |
| `source` | where the request comes from: WildChat-4.8M, one of three LMArena sets, WebShop's human instructions, or the author (with the real request whose form it follows) |
| `source_id` | the request's identifier in its source, as <set>:<number> (wildchat, arena100k, arena140k, searcharena, webshop); for a request that the author wrote, the request's own identifier |
| `conversation_hash` | WildChat's own hash of the conversation (empty for other sources) |
| `date` | the date on which the request was written (for a request that the author wrote, the date of writing) |
| `category` | the product category of the request |
| `text` | the request, as its writer typed it |
| `asked_for` | what the person asked for, in at most 25 words, from the classifier (Claude Haiku 5.5) that labeled the candidates; for a request that the author wrote, the request itself |
| `names_brand_classifier` | whether the classifier used to assemble the bank marked the request as naming a brand (yes or no) |
| `tables` | the tables of the request's category that it may be paired with |
| `tables_dropped` | tables of the category left out for this request, with the reason |
| `in_run` | whether the request was drawn for the runs |

### How specific each request is: `study1b-64-models-on-34-tables/materials/requests/specificity.jsonl.gz`

1 file.

| Column | What it holds |
|---|---|
| `request` | the request's identifier |
| `code` | the specificity code used in the analysis, the lower of the two coders' codes: 0 names only the product, 1 a use or a budget, 2 both or one attribute, 3 two or more attributes |
| `opus` | the code that Claude Opus 5.5 gave |
| `codex` | the code that GPT-6.2 Sol gave |
| `opus_parts` | the use, the budget and the attributes that Claude Opus 5.5 found in the request |

### Which product meets the request's needs: `study1b-64-models-on-34-tables/materials/requests/needs_codes.jsonl.gz`

1 file.

| Column | What it holds |
|---|---|
| `request` | the request's identifier |
| `table` | the table of the pair |
| `designated` | the letter of the best product of the table in the names-hidden prompt |
| `opus` | the product that Claude Opus 5.5 named as meeting the request's stated needs: a letter, none (the request states no need the table can check) or tie (several products meet them equally) |
| `opus_states_needs` | whether Claude Opus 5.5 found needs that the table can check (yes or no) |
| `opus_meets_all` | the products that meet every stated need, by Claude Opus 5.5 |
| `codex` | GPT-6.2 Sol's answer, for the random 100 pairs that it coded (empty otherwise) |
| `needs_best` | the product used as the best for the needs: the designated product unless Claude Opus 5.5 named another one |
| `opus_names_another_product` | whether Claude Opus 5.5 named a product other than the designated one |
| `reason` | Claude Opus 5.5's reason, in its words |

### The classifier's labels on every candidate: `study1b-64-models-on-34-tables/materials/requests/selection/{,search_,webshop_}labels_classify_out{,_v2}.jsonl.gz` (classify_out: the first instruction, classify_out_v2: the revised one; the candidates' texts are rebuilt from the public sets by select_requests.py)

5 files.

| Column | What it holds |
|---|---|
| `id` | the candidate's identifier (q for WildChat and the two LMArena human-preference sets, s for Search Arena, w for WebShop), in the order in which select_requests.py numbers the candidates |
| `source` | the set that the candidate comes from |
| `source_id` | the candidate's identifier in its set, as <set>:<identifier> |
| `date` | the day of the candidate's first message (empty for WebShop) |
| `keyword_categories` | the categories whose words the candidate holds (step 1) |
| `purchase_request` | the classifier's label: whether the message asks the assistant to recommend or choose a product to buy (yes or no) |
| `category` | the classifier's category for the product (one of the 20, or other) |
| `names_brand` | the classifier's label: whether the message names a brand or a product model (yes or no) |
| `classifier_keep` | whether the label keeps the candidate (a request to buy in one of the 20 categories) |
| `label_error` | why the classifier's answer could not be read (the candidate is then dropped); empty otherwise |
| `asked_for` | the classifier's summary of what the person asked for, in at most 25 words; given only for the candidates that the revised instruction kept, which are the ones the bank can hold |

### The author's hand labels: `study1b-64-models-on-34-tables/materials/requests/selection/hand_labels.jsonl.gz` (every candidate of the two blind hand-check draws, every kept chat-log request and every WebShop instruction read before it was used)

1 file.

| Column | What it holds |
|---|---|
| `id` | the candidate's identifier, as in the labels files |
| `purchase_request` | the author's reading: whether the message asks to buy a product (yes or no) |
| `category` | the author's category for the product (one of the 20, or other) |

### The forms drawn for the author's requests: `study1b-64-models-on-34-tables/materials/requests/selection/author_slots.jsonl.gz` (written by author_forms.py)

1 file.

| Column | What it holds |
|---|---|
| `slot` | the slot's identifier, a-<category>-<number>; it is the request's identifier in the bank |
| `category` | the category that the request is written for |
| `form` | the identifier of the chat-log request whose form the request copies |
| `form_text` | that chat-log request's text |

### The requests that the author wrote: `study1b-64-models-on-34-tables/materials/requests/selection/author_requests.jsonl.gz`

1 file.

| Column | What it holds |
|---|---|
| `slot` | the slot's identifier, as in author_slots.jsonl.gz |
| `category` | the category that the request is written for |
| `form` | the identifier of the chat-log request whose form the request copies |
| `text` | the request, with only the form's product words changed |

### The corpus's names-shown and names-hidden answers: `study1b-64-models-on-34-tables/data/corpus/<model>/{names_shown,names_hidden}.jsonl.gz`

Utility is the score that the experiment's utility function gives a product from its attributes (common/experiment/conditions.py). The corpus has other conditions and columns that are empty for these two conditions; the files keep every column as recorded.

60 files.

| Column | What it holds |
|---|---|
| `corpus_row` | the row's position in the full corpus file (counting from 0) |
| `trial_id` | a neutral identifier of the row: corpus- followed by corpus_row |
| `trial` | the trial number within the model, table and condition |
| `model_key` | the corpus's name for the model and its setting (a model run with extended thinking has its own key, ending in -thinking) |
| `provider` | the provider whose interface served the model |
| `model_id` | the model identifier sent to the provider |
| `assortment_id` | the product table (sr_<category>_<number>) |
| `category` | the product category |
| `condition` | baseline (the brand names shown) or baseline_brand_blind (every brand replaced by Brand A to E and every product name by Product A to E) |
| `condition_type` | the family of the condition in the experiment's list of conditions |
| `condition_precision` | how precisely the condition states the user's preferences (none for both conditions here) |
| `condition_ordinal` | the condition's rank on that scale (0 for both conditions here) |
| `choice` | the letter of the recommended product as shown, read by the corpus's own parser (? when it read none) |
| `original_choice` | the recommended product's letter in the table file, before the display order was shuffled |
| `optimal_product` | the letter under which the best product (the highest utility) was shown |
| `original_optimal` | the best product's letter in the table file |
| `chose_optimal` | whether the recommended product is the best product |
| `chose_branded` | whether the recommended product is the table's highly familiar brand that is not the best product |
| `chosen_brand_familiarity` | the coded familiarity of the recommended product's brand (high, medium or low; unknown when no product was read) |
| `chosen_position` | the recommended product's position in the table file (0 to 4; -1 when none was read) |
| `utility_loss` | the best product's utility minus the recommended product's utility (0 when the best was chosen) |
| `override_occurred` | whether the best product was not chosen under a condition that states the user's utility (false for both conditions here) |
| `specification_resistance` | whether the best product was not chosen under a condition of precision rank 3 or more (false for both conditions here) |
| `optimal_utility` | the best product's utility |
| `presentation_order` | the products' positions in the table file, in the order in which they were shown |
| `optimal_display_position` | the position (0 to 4) at which the best product was shown |
| `letter_mapping` | for each letter shown, the product's letter in the table file |
| `paraphrase_index` | which of the system prompt wordings the trial used |
| `brand_reversal` | whether the condition exchanged brand names between products (false for both conditions here) |
| `thinking` | whether extended thinking was on |
| `temperature` | the sampling temperature recorded for the trial |
| `cost_usd` | the trial's cost in US dollars, from the token counts and the provider's prices at the time |
| `input_tokens` | tokens in the prompt |
| `output_tokens` | tokens in the answer |
| `duration_seconds` | seconds from the request to the response |
| `judge_coherence` | a judge model's score (0 to 100) for how coherent the answer's reasoning is |
| `judge_spec_acknowledgment` | a judge model's score (0 to 100) for how far the answer addresses the user's stated needs |
| `judge_brand_reasoning` | whether the judge model found that the answer gives a brand as a reason |
| `judge_model` | the judge model |
| `raw_response` | the model's answer, as returned |
| `reasoning` | the part of the answer that the corpus's parser kept as the reasoning |
| `thinking_trace` | the model's thinking, when the provider returned it |
| `involvement_level` | the category's level of buyer involvement (low, mid or high), from the experiment's table of categories |
| `brand_salience` | how much brands matter in the category (low, mid or high), from the same table |
| `processing_mode` | how buyers typically compare products in the category (by attribute or by alternative), from the same table |
| `hedonic` | whether the category is hedonic (true) or utilitarian (false), from the same table |
| `chosen_utility` | the recommended product's utility |
| `utility_rank` | the rank of the recommended product's utility among the five (1 is the highest; empty when none was read) |
| `response_length` | characters in the answer |
| `thinking_length` | characters in the thinking |
| `n_products_mentioned` | how many of the five products the answer names, as Product X or by name |
| `utility_A` | the utility of the product shown as A |
| `utility_B` | the utility of the product shown as B |
| `utility_C` | the utility of the product shown as C |
| `utility_D` | the utility of the product shown as D |
| `utility_E` | the utility of the product shown as E |
| `product_A_name` | the name of the product shown as A, as the prompt gave it |
| `product_A_brand` | the brand of the product shown as A, as the prompt gave it |
| `product_A_price` | the price of the product shown as A, as the prompt gave it |
| `product_A_sustainability` | the sustainability rating of the product shown as A, as the prompt gave it |
| `product_B_name` | the name of the product shown as B, as the prompt gave it |
| `product_B_brand` | the brand of the product shown as B, as the prompt gave it |
| `product_B_price` | the price of the product shown as B, as the prompt gave it |
| `product_B_sustainability` | the sustainability rating of the product shown as B, as the prompt gave it |
| `product_C_name` | the name of the product shown as C, as the prompt gave it |
| `product_C_brand` | the brand of the product shown as C, as the prompt gave it |
| `product_C_price` | the price of the product shown as C, as the prompt gave it |
| `product_C_sustainability` | the sustainability rating of the product shown as C, as the prompt gave it |
| `product_D_name` | the name of the product shown as D, as the prompt gave it |
| `product_D_brand` | the brand of the product shown as D, as the prompt gave it |
| `product_D_price` | the price of the product shown as D, as the prompt gave it |
| `product_D_sustainability` | the sustainability rating of the product shown as D, as the prompt gave it |
| `product_E_name` | the name of the product shown as E, as the prompt gave it |
| `product_E_brand` | the brand of the product shown as E, as the prompt gave it |
| `product_E_price` | the price of the product shown as E, as the prompt gave it |
| `product_E_sustainability` | the sustainability rating of the product shown as E, as the prompt gave it |
| `system_prompt` | the system prompt, as sent |
| `user_message` | the user's message, as sent |
| `timestamp` | when the trial's record was written (the clock of the computer that ran it) |

### The Claude and GPT-6 models' final answers in the clarifying turn: `study1b-64-models-on-34-tables/data/clarifying/<model>/answers.jsonl.gz`

5 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier; the same id in the set's prompts file |
| `model` | the model, by the name that the run requested |
| `model_returned` | the model name that the provider's response reported |
| `route` | how the answer was obtained |
| `answered_at_utc` | when the response was recorded (UTC, ISO 8601) |
| `asked` | True when the model asked the shopper a question before its final answer |
| `answer_text` | the model's answer, exactly as returned |
| `stop_reason` | the provider's reason for ending the answer (end_turn: the model finished; max_tokens: the length limit) |
| `input_tokens` | tokens in the prompt, as the provider counted them |
| `output_tokens` | tokens in the answer, as the provider counted them |

### The rerun's cleaning of the prompts without brand names: `study1b-64-models-on-34-tables/materials/cleaning/cleaned-prompt-replacements.csv`, one row per replacement

1 file.

| Column | What it holds |
|---|---|
| `table` | the corpus's table (such as backpacks_01) |
| `find` | a text of the corpus's prompt without brand names |
| `replace` | what the cleaned prompt has in its place (empty when the text is removed) |

### A hand reading of each cleaning row whose words are not all on the list of texts that still identify a brand: `study1b-64-models-on-34-tables/materials/cleaning/cleaning-rows-read.csv`

1 file.

| Column | What it holds |
|---|---|
| `row` | the row's number in cleaned-prompt-replacements.csv (the first row after the header is 1) |
| `class` | maker_name (a maker's name for a feature, part or format that the list did not hold), claim (a claim of quality or a brand's slogan that names no brand), spec_value (a specification value changed or removed) or no_change (the same meaning in other words) |
| `why` | what the row changes, in a few words |

### The Claude and GPT-6 models' answers under stated priorities: `study1b-64-models-on-34-tables/data/priorities/<model>/answers.jsonl.gz`

5 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier; the same id in the set's prompts file |
| `model` | the model, by the name that the run requested |
| `model_returned` | the model name that the provider's response reported |
| `route` | how the answer was obtained |
| `answered_at_utc` | when the response was recorded (UTC, ISO 8601) |
| `answer_text` | the model's answer, exactly as returned |
| `stop_reason` | the provider's reason for ending the answer (end_turn: the model finished; max_tokens: the length limit) |
| `input_tokens` | tokens in the prompt, as the provider counted them |
| `output_tokens` | tokens in the answer, as the provider counted them |

### The prompts under stated priorities: `study1b-64-models-on-34-tables/materials/priorities/prompts.jsonl.gz`, one row per prompt

1 file.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier |
| `build` | the set of prompts (`s1prio1`) |
| `cell` | the prompt's condition: the names version, the information level and the price step, joined by hyphens (for example `crossed-info0-rung0`) |
| `condition` | the statement of the shopper's priorities: preference_vague, preference_weighted, preference_explicit or utility_explicit (the corpus's wording of each) |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `names` | the names version: hidden (every product shown as Product A to E with no brand), original (the invented name on the best product and familiar names on the others) or crossed (a familiar name on the best product and the invented name on a familiar product) |
| `info` | 1 if every product's reliability information was shown (a warranty, a failure rate and a time on the market, with a sentence that the figures came from independent lab testing), 0 if not |
| `rung` | the best product's price: 0 equal to the cheapest other product, 1 15 percent below it, 2 30 percent below it |
| `paraphrase` | which of the four wordings of the system prompt the prompt used (0 to 3) |
| `partner_orig` | in the crossed version, the letter (in the table file) of the familiar product whose name the best product takes; empty in the other versions |
| `best` | the letter under which the best product was shown in this prompt |
| `products` | for each letter shown: the product's letter in the table file (orig), the name shown (shown_name), the kind of name shown (kind: hidden, invented or familiar-high, familiar-medium), the price shown, the product's true brand (true_brand) and the kind of that brand (true_kind) |
| `order` | the letters in the order in which the products were shown |
| `system` | the system prompt, as sent |
| `user` | the user's message, as sent: the request and the product listings |
| `source` | the corpus trial whose table, order and request the prompt keeps: its condition and its model |

### The corpus's answers in the four conditions of stated priorities: `study1b-64-models-on-34-tables/data/corpus-priority-conditions/counts.csv`, one row per model, condition and table

1 file.

| Column | What it holds |
|---|---|
| `model_key` | the corpus's model |
| `condition` | the condition of stated priorities |
| `assortment_id` | the table |
| `answers` | the corpus's answers in the cell |
| `chose_optimal` | of them, the answers that recommended the optimal product |

### The prompts of the clarifying turn: `study1b-64-models-on-34-tables/materials/clarifying/prompts.jsonl.gz`, one row per prompt

1 file.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier |
| `build` | the set of prompts (`clar1`) |
| `cell` | the prompt's condition: the names version, the information level and the price step, joined by hyphens (for example `crossed-info0-rung0`) |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `names` | the names version: hidden (every product shown as Product A to E with no brand), original (the invented name on the best product and familiar names on the others) or crossed (a familiar name on the best product and the invented name on a familiar product) |
| `info` | 1 if every product's reliability information was shown (a warranty, a failure rate and a time on the market, with a sentence that the figures came from independent lab testing), 0 if not |
| `rung` | the best product's price: 0 equal to the cheapest other product, 1 15 percent below it, 2 30 percent below it |
| `paraphrase` | which of the four wordings of the system prompt the prompt used (0 to 3) |
| `partner_orig` | in the crossed version, the letter (in the table file) of the familiar product whose name the best product takes; empty in the other versions |
| `best` | the letter under which the best product was shown in this prompt |
| `products` | for each letter shown: the product's letter in the table file (orig), the name shown (shown_name), the kind of name shown (kind: hidden, invented or familiar-high, familiar-medium), the price shown, the product's true brand (true_brand) and the kind of that brand (true_kind) |
| `order` | the letters in the order in which the products were shown |
| `system` | the system prompt, as sent |
| `user` | the user's message, as sent: the request and the product listings |
| `followup` | the shopper's reply, sent when the model asks a question first |
| `source_build` | the set of the prompt's one-turn twin (`dom2`, Study 1a's strictly better tables) |
| `source_id` | the identifier of the one-turn twin in Study 1a's prompts |

### How each attribute is ordered: `study1b-64-models-on-34-tables/materials/attribute_rulings.csv`

1 file.

| Column | What it holds |
|---|---|
| `table` | the table that the rule applies to (without its sr_ prefix), or * for every table |
| `attribute` | the attribute, as the listings name it |
| `kind` | how two values of the attribute are compared: unordered (no order that every buyer accepts, a matter of need), number_higher or number_lower (the number read from the value, higher or lower better), presence (having the feature is better), ordinal (a stated order of named levels), or a rule for one kind of value (camera, rx_higher, ip, anc, battery, superset, display, ssd_durability, resolution, wifi, ports), each defined in 03_strict_dominance.py |
| `detail` | the pattern that reads the number, or the order of the levels, where the rule needs one |
| `reason` | why the attribute is compared that way |

### Brand hints left in the names-hidden prompts: `study1b-64-models-on-34-tables/materials/names_hidden_leaks.csv`

1 file.

| Column | What it holds |
|---|---|
| `table` | the table (without its sr_ prefix) |
| `brand` | the brand of the product whose listing holds the text |
| `text` | the text, as it appears in the names-hidden prompt |
| `kind` | 1 brand (the product's own brand, its owner or a sister brand), 2 line (a product line or model name of the maker), 3 feature (a technology, feature, chip or service name of the maker), 4 copy (a sentence of the brand's own copy in which only the brand was replaced), or 5 other company (another company's name, such as a component's maker) |
| `points_to` | the brand that a reader can infer from the text |
| `product` | the product named, where the hint is a whole product name (empty otherwise) |

### The reasons coded in the answers to consumers' requests: `study1b-64-models-on-34-tables/materials/requests/reasons.jsonl.gz`, one row for each answer that recommended a product other than the optimal one

1 file.

| Column | What it holds |
|---|---|
| `model` | the model that answered |
| `item` | the prompt's identifier |
| `reason` | the reason that the answer gives for preferring its product to the optimal one (`brand_property`, `brand_reputation`, `listed` or `other`; `reasons_coder.txt` defines them) |
| `quote` | the words of the answer that give the reason |

## Study 1c (`study1c-product-feeds-and-a-store-search/`)

### The store's prompts (Study 1c): `study1c-product-feeds-and-a-store-search/materials/store/h2/prompts.jsonl.gz` (every condition of the store) and `h1/prompts.jsonl.gz` (its equal-price half under other ids, which the open models answered)

2 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier |
| `arm` | the store's condition: plain (the listing as in Study 1a), plain-info (with the reliability information), a feed format (feed-openai, feed-openai-2025, feed-google), schema-org markup, a Sponsored label (sponsored-familiar, sponsored-best), the best product's position (position-first, position-middle, position-last), a rating gap (rating-0.1, rating-0.3, rating-0.5) or the developer's instruction in the system prompt (instruct-listed, instruct-brand) |
| `cell` | the condition, the names version and the price step, joined by hyphens |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `names` | hidden or original |
| `info` | 1 in plain-info, 0 otherwise |
| `rung` | the best product's price: 0 equal to the cheapest other product, 1 15 percent below it, 2 30 percent below it |
| `paraphrase` | which of the four wordings of the system prompt the prompt used (0 to 3) |
| `partner_orig` | in the crossed version, the letter (in the table file) of the familiar product whose name the best product takes; empty in the other versions |
| `best` | the letter under which the best product was shown in this prompt |
| `products` | for each letter shown: the product's letter in the table file (orig), the name shown (shown_name), the kind of name shown (kind: hidden, invented or familiar-high, familiar-medium), the price shown, the product's true brand (true_brand) and the kind of that brand (true_kind) |
| `order` | the letters in the order in which the products were shown |
| `labelled` | the letter of the product with the Sponsored label (the sponsored conditions); empty otherwise |
| `system` | the system prompt, as sent |
| `user` | the user's message, as sent: the request and the product listings |

### The Claude models' answers to the store: `study1c-product-feeds-and-a-store-search/data/store/claude/<model>.jsonl.gz`, one row per answer, in the order of the run

4 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier in `study1c-product-feeds-and-a-store-search/materials/store/h2/prompts.jsonl.gz` |
| `model` | the model, by the name that the run requested |
| `answered_at_utc` | when the response was recorded (UTC, ISO 8601) |
| `answer_text` | the model's answer, exactly as returned |
| `stop_reason` | the provider's reason for ending the answer (end_turn: the model finished; max_tokens: the length limit) |
| `input_tokens` | tokens in the prompt, as the provider counted them |
| `output_tokens` | tokens in the answer, as the provider counted them |
| `cache_read_input_tokens` | prompt tokens read from the provider's prompt cache |
| `cache_creation_input_tokens` | prompt tokens written to the provider's prompt cache |
| `route` | how the answer was obtained: the Anthropic Messages API (message batches) |

### The open models' letters on the store and the search step, read on the computing cluster: `study1c-product-feeds-and-a-store-search/data/store/open-letters.csv.gz`, one row per answer, and `open-letters-kind.csv.gz`, the same answers with each one's kind

2 files.

| Column | What it holds |
|---|---|
| `study` | `b16` (the store) or `b17` (the search step) |
| `build` | `h1` or `h2` (the store), `stage2` (the search step's second prompt) |
| `model` | the model, by its name in the run (an open model by its short name in models/open-models.tsv) |
| `id` | the prompt's identifier |
| `letter` | the letter that the parser read (final_answer, then pick); empty when it read none |
| `how` | where the parser found the letter: first-line, body, several (more than one letter, so none is returned) or none |
| `finish` | why generation stopped: stop (the model ended its answer) or length (the token limit) |
| `tokens_out` | tokens in the answer |
| `final_chars` | characters in the answer after any reasoning (final_answer) |
| `final_differs` | 1 if final_answer removed reasoning from the answer, 0 if not |
| `kind` | pick (a letter was read), decline (the answer recommends none of the products) or unread (decline.py, on the answer's text after any reasoning) |

### The search step's first prompts (Study 1c): `study1c-product-feeds-and-a-store-search/materials/search/s1/stage1/prompts.jsonl.gz`, one row per prompt

1 file.

| Column | What it holds |
|---|---|
| `id` | the first prompt's identifier |
| `cell` | always search |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `names` | always none (the first prompt shows no product) |
| `info` | always 0 |
| `rung` | always 0 |
| `best` | always empty (the first prompt shows no product) |
| `system` | the system prompt, as sent: a shopping assistant with a search tool, asked for its queries |
| `user` | the shopper's request, as sent |

### The search step's second prompts (Study 1c): `study1c-product-feeds-and-a-store-search/materials/search/s1/stage2/<model>.jsonl.gz`, one row per prompt, and `nothing-returned/<model>.jsonl.gz`, one row per search that returned no product (these rows have no prompt)

72 files.

| Column | What it holds |
|---|---|
| `model` | the model whose first answer gave the queries, and which was asked the second prompt |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `names` | original (the names shown) or hidden |
| `rung` | the price step: 0 (the best product's price equals the cheapest other product's) or 2 (30 percent below it) |
| `queries` | the queries that the store read from the model's first answer (search_store.parse_queries), at most three |
| `returned` | the letters of the products that the store returned, in order (empty when nothing was returned) |
| `best` | the letter under which the best product was shown in this prompt |
| `fetched` | true if the store returned the best product |
| `id` | the second prompt's identifier |
| `cell` | search-original or search-hidden: the names version |
| `info` | always 0 (no reliability information) |
| `system` | the system prompt, as sent |
| `user` | the user's message, as sent: the request, the model's own queries and the products that the store returned |
| `paraphrase` | which of the four wordings of the system prompt the prompt used (0 to 3) |
| `products` | for each letter returned: the product's letter in the table file (orig), the name shown (shown_name), the kind of name shown (kind: hidden, invented or familiar-high, familiar-medium), the price shown, the product's true brand (true_brand) and the kind of that brand (true_kind) |

### The Claude models' answers in the search step: `study1c-product-feeds-and-a-store-search/data/search/stage1/<model>.jsonl.gz` (first prompts) and `stage2/<model>.jsonl.gz` (second prompts), one row per answer, in the order of the run

8 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier in `study1c-product-feeds-and-a-store-search/materials/search/s1/` |
| `model` | the model, by the name that the run requested |
| `answered_at_utc` | when the response was recorded (UTC, ISO 8601) |
| `answer_text` | the model's answer, exactly as returned |
| `stop_reason` | the provider's reason for ending the answer (end_turn: the model finished; max_tokens: the length limit) |
| `input_tokens` | tokens in the prompt, as the provider counted them |
| `output_tokens` | tokens in the answer, as the provider counted them |
| `cache_read_input_tokens` | prompt tokens read from the provider's prompt cache |
| `cache_creation_input_tokens` | prompt tokens written to the provider's prompt cache |
| `route` | how the answer was obtained: the Anthropic Messages API, one request at a time (first prompts) or in message batches (second prompts) |

### The open models' first answers in the search step, from the computing cluster's export: `study1c-product-feeds-and-a-store-search/data/search/open-first-answers.jsonl.gz`, one row per answer

1 file.

| Column | What it holds |
|---|---|
| `model` | the model, by its name in the run (an open model by its short name in models/open-models.tsv) |
| `id` | the first prompt's identifier |
| `answer` | the model's answer as it wrote it, the text from which the store read the queries |
| `final` | the answer after any reasoning is removed (final_answer), from which the brand searches are counted |
| `finish` | why generation stopped: stop (the model ended its answer) or length (the token limit) |

## Study 2a (`study2a-experience-attributes-stated-for-every-product/`)

### The explanations that the judges coded (Study 2a): `study2a-experience-attributes-stated-for-every-product/data/explanations/items-all.jsonl.gz` (29,600) and the stated sample of 200 (`items-sample.jsonl`)

2 files.

| Column | What it holds |
|---|---|
| `id` | the explanation's identifier |
| `system` | the judge's instructions |
| `user` | what the judge saw: the request, the products as the model saw them, the product that the model recommended and its answer |
| `cell` | the prompt's condition in Study 1a (the names version, the experience attributes and the price step, joined by hyphens) |
| `table` | the product table |
| `trial` | the prompt's trial |
| `names` | the names version |
| `info` | whether the experience attributes were stated |
| `rung` | the price step (0: the optimal product's price equals the cheapest other product's; 2: 30 percent below) |
| `best` | the letter of the optimal product |
| `source` | `dom2` (Study 1a's tables) or `requests` (consumers' own requests) |
| `model` | the model that wrote the explanation |
| `group` | `claude`, `codex` (the GPT models) or `open` (the models with open weights) |
| `source_id` | the identifier of the answer that holds the explanation |
| `recommended` | the letter of the product that the model recommended |
| `recommended_kind` | the kind of name of that product (familiar or fictitious) |
| `best_kind` | the kind of name of the optimal product |

### Each judge's codes of the explanations: `judges/<judge>-all-answers.jsonl.gz` (every explanation) and `<judge>-sample-answers.jsonl.gz` (the stated 200)

8 files.

| Column | What it holds |
|---|---|
| `id` | the explanation's identifier (in `items-all.jsonl.gz`) |
| `cell` | the prompt's condition in Study 1a (the names version, the experience attributes and the price step, joined by hyphens) |
| `table` | the product table |
| `trial` | the prompt's trial |
| `names` | the names version |
| `info` | whether the experience attributes were stated |
| `rung` | the price step (0: the optimal product's price equals the cheapest other product's; 2: 30 percent below) |
| `best` | the letter of the optimal product |
| `model` | the judge |
| `answer` | the judge's reply: a JSON object with `reason`, `brand_any` (`yes` or `no`) and a quote |
| `raw` | the server's text of the answer, before any reasoning was removed |
| `finish` | why the answer ended (`stop`: the model finished; `length`: it reached the limit of tokens) |
| `tokens_out` | the number of tokens in the answer |

### Answers to Study 1a's prompts through the command lines: `study2a-experience-attributes-stated-for-every-product/data/strictly-better-tables/<model>/<cell>.jsonl.gz` (the GPT-6 models and Claude Fable 5.2)

60 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier; the same id in the set's prompts file |
| `model` | the model, by the name that the run requested |
| `answered_at_utc` | when the response was recorded (UTC, ISO 8601) |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `cell` | the prompt's condition: the names version, the information level and the price step, joined by hyphens (for example `crossed-info0-rung0`) |
| `names` | the names version: hidden (every product shown as Product A to E with no brand), original (the invented name on the best product and familiar names on the others) or crossed (a familiar name on the best product and the invented name on a familiar product) |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `paraphrase` | which of the four wordings of the system prompt the prompt used (0 to 3) |
| `best` | the letter under which the best product was shown in this prompt |
| `answer_text` | the model's answer, exactly as returned |
| `letter` | the letter that common/parse_answer.py reads from the answer; empty when it reads none |
| `letter_how` | where the parser found the letter: first-line, body, several (more than one letter, so none is returned) or none |
| `stop_reason` | the provider's reason for ending the answer (end_turn: the model finished; max_tokens: the length limit) |
| `input_tokens` | tokens in the prompt, as the provider counted them |
| `output_tokens` | tokens in the answer, as the provider counted them |
| `model_returned` | the model name that the response reported (for the Claude command line, every model named in its reply) |
| `route` | how the answer was obtained: the OpenAI Codex command line (with its version and reasoning effort) or the Claude command line |
| `cli_version` | the Claude command line's version (Claude command line only) |
| `thinking_tokens` | tokens of thinking before the answer (Claude command line only) |
| `seconds` | seconds that the command line took for the answer |
| `error` | a message that the command line recorded during the answer, such as a reconnection when the model was at capacity; empty when there was none |
| `info` | 1 if every product's reliability information was shown (a warranty, a failure rate and a time on the market, with a sentence that the figures came from independent lab testing), 0 if not |
| `rung` | the best product's price: 0 equal to the cheapest other product, 1 15 percent below it, 2 30 percent below it |
| `cached_input_tokens` | prompt tokens served from the cache (OpenAI Codex command line only) |
| `reasoning_output_tokens` | tokens of reasoning before the answer (OpenAI Codex command line only) |

### The prompts of Study 2a's retrieved reviews: `study2a-experience-attributes-stated-for-every-product/materials/retrieval/r1/prompts.jsonl.gz`, one row per prompt

1 file.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier |
| `arm` | the level of the retrieved reviews: none, positive, mixed or negative |
| `cell` | the level, the version of the names and the price step, joined by hyphens |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `names` | hidden, original or crossed (the best product under a familiar product's name) |
| `info` | always 0 (no reliability information) |
| `rung` | the price step: 0 (the best product's price equals the cheapest other product's) or 2 (30 percent below it) |
| `paraphrase` | which of the four wordings of the system prompt the prompt used (0 to 3) |
| `partner_orig` | in the crossed version, the letter (in the table file) of the familiar product whose name the best product takes; empty in the other versions |
| `best` | the letter under which the best product was shown in this prompt |
| `products` | for each letter shown: the product's letter in the table file (orig), the name shown (shown_name), the kind of name shown (kind: hidden, invented or familiar-high, familiar-medium), the price shown, the product's true brand (true_brand) and the kind of that brand (true_kind) |
| `order` | the letters in the order in which the products were shown |
| `system` | the system prompt, as sent |
| `user` | the user's message, as sent: the request and the product listings, each with its retrieved reviews at the levels other than none |

### The Claude models' answers to the retrieved reviews: `study2a-experience-attributes-stated-for-every-product/data/retrieval/claude/<model>.jsonl.gz`, one row per answer, in the order of the run

4 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier in `study2a-experience-attributes-stated-for-every-product/materials/retrieval/r1/prompts.jsonl.gz` |
| `model` | the model, by the name that the run requested |
| `answered_at_utc` | when the response was recorded (UTC, ISO 8601) |
| `answer_text` | the model's answer, exactly as returned |
| `stop_reason` | the provider's reason for ending the answer (end_turn: the model finished; max_tokens: the length limit) |
| `input_tokens` | tokens in the prompt, as the provider counted them |
| `output_tokens` | tokens in the answer, as the provider counted them |
| `thinking_tokens` | tokens of thinking before the answer (Claude command line only) |
| `seconds` | seconds that the command line took for the answer |
| `model_returned` | the model name that the response reported (for the Claude command line, every model named in its reply) |
| `cli_version` | the Claude command line's version (Claude command line only) |
| `route` | how the answer was obtained: the Claude command line with its own defaults (adaptive thinking, no effort set) |

### The open models' letters on the retrieved reviews, read on the computing cluster: `study2a-experience-attributes-stated-for-every-product/data/retrieval/open-letters.csv.gz`, one row per answer, with each one's kind

1 file.

| Column | What it holds |
|---|---|
| `study` | always `b10` (the retrieved reviews) |
| `build` | always `r1` |
| `model` | the model, by its name in the run (an open model by its short name in models/open-models.tsv) |
| `id` | the prompt's identifier in `study2a-experience-attributes-stated-for-every-product/materials/retrieval/r1/prompts.jsonl.gz` |
| `letter` | the letter that the parser read (final_answer, then pick); empty when it read none |
| `how` | where the parser found the letter: first-line, body, several (more than one letter, so none is returned) or none |
| `finish` | why generation stopped: stop (the model ended its answer) or length (the token limit) |
| `tokens_out` | tokens in the answer |
| `final_chars` | characters in the answer after any reasoning (final_answer) |
| `final_differs` | 1 if final_answer removed reasoning from the answer, 0 if not |
| `kind` | pick (a letter was read), decline (the answer recommends none of the products) or unread (decline.py, on the answer's text after any reasoning) |

### Counts of the answers in this package: `study2a-experience-attributes-stated-for-every-product/data/counts/counts-git.csv` (`study3a-pages-about-new-brands/materials/training-q2/training-text/dom2`, `split1`, `eq1`) and `counts-git-attr1.csv` (`attr1`), one row per set of prompts, model, table and cell

2 files.

| Column | What it holds |
|---|---|
| `build` | the set of prompts: `dom2` (Study 1a's strictly better tables), `split1` (each piece alone), `eq1` (the price) or `attr1` (the further information) |
| `model` | the model, by its name in the run (an open model by its short name in models/open-models.tsv) |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `names` | the names version (hidden, original or crossed), as in the prompts |
| `info` | the information shown: 0 or 1 in `dom2`, as in Study 1a; in `split1` 0 none, 1 all five pieces, or one piece alone: warranty (the warranty row), failure (the first-year failure or return rate row), market (the time-on-the-market row), lab (the lab-testing sentence) or returns (the free-return clause); always 0 in `eq1`; in `attr1` the condition (none, warranty-row, reviews-50 and so on, as in the prompts) |
| `rung` | the price: 0 or 2 in `dom2` (equal to the cheapest other product, or 30 percent below it); 0 in `split1`; in `eq1` the step (<option>-<cut or stars><value>) |
| `partner_kind` | `eq1`'s option A only: the partner's kind of name (familiar-high, familiar-medium, or invented in the one table with a second invented name); empty otherwise |
| `answers` | the answers counted in the cell |
| `parsed` | the answers in which the parser read a letter |
| `picked_best` | the answers that picked the best product (in `eq1`'s option A, the product with the invented name) |
| `picked_partner` | `eq1`'s option A: the answers that picked the partner; 0 otherwise |

### The open models' counts on the further information, written on the computing cluster: `study2a-experience-attributes-stated-for-every-product/data/open-panel/attr-counts.csv`

1 file.

| Column | What it holds |
|---|---|
| `build` | the set of prompts: `dom2` (Study 1a's strictly better tables), `split1` (each piece alone), `eq1` (the price) or `attr1` (the further information) |
| `model` | the model, by its name in the run (an open model by its short name in models/open-models.tsv) |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `names` | the names version (hidden, original or crossed), as in the prompts |
| `info` | the information shown: 0 or 1 in `dom2`, as in Study 1a; in `split1` 0 none, 1 all five pieces, or one piece alone: warranty (the warranty row), failure (the first-year failure or return rate row), market (the time-on-the-market row), lab (the lab-testing sentence) or returns (the free-return clause); always 0 in `eq1`; in `attr1` the condition (none, warranty-row, reviews-50 and so on, as in the prompts) |
| `rung` | the price: 0 or 2 in `dom2` (equal to the cheapest other product, or 30 percent below it); 0 in `split1`; in `eq1` the step (<option>-<cut or stars><value>) |
| `partner_kind` | `eq1`'s option A only: the partner's kind of name (familiar-high, familiar-medium, or invented in the one table with a second invented name); empty otherwise |
| `answers` | the answers counted in the cell |
| `parsed` | the answers in which the parser read a letter |
| `picked_best` | the answers that picked the best product (in `eq1`'s option A, the product with the invented name) |
| `picked_partner` | `eq1`'s option A: the answers that picked the partner; 0 otherwise |

### The open models' counts on each piece alone and the price, written on the computing cluster: `study2a-experience-attributes-stated-for-every-product/data/open-panel/b9-counts.csv`

1 file.

| Column | What it holds |
|---|---|
| `build` | the set of prompts: `dom2` (Study 1a's strictly better tables), `split1` (each piece alone), `eq1` (the price) or `attr1` (the further information) |
| `model` | the model, by its name in the run (an open model by its short name in models/open-models.tsv) |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `names` | the names version (hidden, original or crossed), as in the prompts |
| `info` | the information shown: 0 or 1 in `dom2`, as in Study 1a; in `split1` 0 none, 1 all five pieces, or one piece alone: warranty (the warranty row), failure (the first-year failure or return rate row), market (the time-on-the-market row), lab (the lab-testing sentence) or returns (the free-return clause); always 0 in `eq1`; in `attr1` the condition (none, warranty-row, reviews-50 and so on, as in the prompts) |
| `rung` | the price: 0 or 2 in `dom2` (equal to the cheapest other product, or 30 percent below it); 0 in `split1`; in `eq1` the step (<option>-<cut or stars><value>) |
| `partner_kind` | `eq1`'s option A only: the partner's kind of name (familiar-high, familiar-medium, or invented in the one table with a second invented name); empty otherwise |
| `answers` | the answers counted in the cell |
| `parsed` | the answers in which the parser read a letter |
| `picked_best` | the answers that picked the best product (in `eq1`'s option A, the product with the invented name) |
| `picked_partner` | `eq1`'s option A: the answers that picked the partner; 0 otherwise |

### The open models' letters, one row per answer, from three exports of the computing cluster: `study2a-experience-attributes-stated-for-every-product/data/open-panel/letters-12683.csv.gz` and `letters-13394.csv.gz`, which holds Qwen 3.5 122B's letters (both read by Study 1b as one panel and by Study 2a over every model, and 12683's by Study 3b's questions about each brand), and `letters-12154.csv.gz`, an earlier export that the stated priorities' ladder reads

3 files.

| Column | What it holds |
|---|---|
| `build` | the set of prompts: `b2/dom2` (Study 1a's strictly better tables), `b2/full2` (the original tables, which the audit reads) or `study1-rerun/s1rerun1` (the corpus prompts answered again, which Study 1b reads) |
| `model` | the model, by its name in the run (an open model by its short name in models/open-models.tsv) |
| `id` | the prompt's identifier; the same id in the set's prompts file |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `cell` | the prompt's condition: the names version, the information level and the price step, joined by hyphens (for example `crossed-info0-rung0`) |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `names` | the names version (for `s1rerun1`, `shown`, `hidden` or `hidden_clean`) |
| `info` | 1 if every product's reliability information was shown (a warranty, a failure rate and a time on the market, with a sentence that the figures came from independent lab testing), 0 if not |
| `rung` | the best product's price: 0 equal to the cheapest other product, 1 15 percent below it, 2 30 percent below it |
| `best` | the letter under which the best product was shown in this prompt |
| `letter` | the letter that the parser read (final_answer, then pick); empty when it read none |
| `finish` | why generation stopped: stop (the model ended its answer) or length (the token limit) |
| `tokens_out` | tokens in the answer |
| `answer_chars` | characters in the answer |

### The store's cells (Study 1c) that Study 2 reads: `study2a-experience-attributes-stated-for-every-product/data/store/claude-cells.csv` and `open-cells.csv`

2 files.

| Column | What it holds |
|---|---|
| `model` | the model, by its name in the run (an open model by its short name in models/open-models.tsv) |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `arm` | the store's condition: plain, plain-info (with the reliability information), a feed format (feed-openai, feed-openai-2025, feed-google, schema-org), a Sponsored label (sponsored-familiar, sponsored-best), a position (position-first, position-middle, position-last), a rating gap (rating-0.1, rating-0.3, rating-0.5) or an instruction from the developer (instruct-brand, instruct-listed) |
| `names` | hidden or original |
| `parsed` | the answers in which the parser read a letter |
| `best` | the answers that picked the best product |
| `labelled` | the answers that picked the product with the Sponsored label (the sponsored conditions; 0 elsewhere) |

## Study 2b (`study2b-how-much-a-familiar-brand-is-worth/`)

### Study 2b's measure, the answers of the Claude models through Anthropic's API and of GPT-6.1 Sol and GPT-6.2 Sol through Codex: `study2b-how-much-a-familiar-brand-is-worth/data/measure/api-answers.jsonl.gz`

1 file.

| Column | What it holds |
|---|---|
| `model` | the model's name |
| `id` | the prompt's identifier in the measure's prompts (`study2b-how-much-a-familiar-brand-is-worth/materials/measure/items/full1/items.jsonl.gz`) |
| `answer` | the answer as the model gave it |

### Study 2b's measure, the answers of the models with open weights: `open/<model>.jsonl.gz`, one row for each prompt

32 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier in the measure's prompts (`study2b-how-much-a-familiar-brand-is-worth/materials/measure/items/full1/items.jsonl.gz`) |
| `cell` | the part of the measure: `shown` (choice sets with the brand names), `hidden` (the same sets without them), `repeat` (sets shown again, for the reliability), `rating` (one product to rate) or `premium` (the direct price premium's sets) |
| `table` | the category of products |
| `trial` | the set's number within its category and part |
| `names` | `shown`, `hidden` or `unnamed` (a product without a brand, in the direct price premium's sets) |
| `info` | always 0 |
| `rung` | always 0 |
| `best` | always empty (no product is better than the others) |
| `model` | the model's short name |
| `answer` | the answer as the model gave it |
| `raw` | the server's text of the answer, before any reasoning was removed |
| `finish` | why the answer ended (`stop`: the model finished; `length`: it reached the limit of tokens) |
| `tokens_out` | the number of tokens in the answer |

### Answers to the price: `study2b-how-much-a-familiar-brand-is-worth/data/price/<model>/<cell>.jsonl.gz`

176 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier; the same id in the set's prompts file |
| `model` | the model, by the name that the run requested |
| `answered_at_utc` | when the response was recorded (UTC, ISO 8601) |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `cell` | the prompt's condition: the option, the names version and the step, joined by hyphens (for example A-hidden-cut0) |
| `names` | hidden or original |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `paraphrase` | which of the four wordings of the system prompt the prompt used (0 to 3) |
| `best` | the letter of the best product; in option A, the product with the invented name |
| `answer_text` | the model's answer, exactly as returned |
| `letter` | the letter that common/parse_answer.py reads from the answer; empty when it reads none |
| `letter_how` | where the parser found the letter: first-line, body, several (more than one letter, so none is returned) or none |
| `stop_reason` | the provider's reason for ending the answer (end_turn: the model finished; max_tokens: the length limit) |
| `input_tokens` | tokens in the prompt, as the provider counted them |
| `output_tokens` | tokens in the answer, as the provider counted them |
| `model_returned` | the model name that the provider's response reported |
| `route` | how the answer was obtained: the Anthropic Messages API (message batches) |
| `cache_read_input_tokens` | prompt tokens read from the provider's prompt cache |
| `cache_creation_input_tokens` | prompt tokens written to the provider's prompt cache |
| `info` | always 0 (no reliability information) |
| `rung` | the step, as <option>-<cut or stars><value>: in option A a familiar product (the partner) has the best product's specifications and the invented product is cut <value> percent below the partner's price, or rated <value> stars while every other product has 4.3; in option B the same steps apply to the best product of the strictly better table against the cheapest other product |

### Prompts of the price: `study2b-how-much-a-familiar-brand-is-worth/materials/price/prompts.jsonl.gz`

1 file.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier |
| `cell` | the prompt's condition: the option, the names version and the step, joined by hyphens |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `names` | hidden or original |
| `info` | always 0 (no reliability information) |
| `rung` | the step, as <option>-<cut or stars><value>: in option A a familiar product (the partner) has the best product's specifications and the invented product is cut <value> percent below the partner's price, or rated <value> stars while every other product has 4.3; in option B the same steps apply to the best product of the strictly better table against the cheapest other product |
| `option` | A (two products that differ only in their names) or B (the strictly better table) |
| `arm` | cut (a lower price) or stars (a higher rating) |
| `value` | the step's size: percent below the reference price, or the stars shown |
| `paraphrase` | which of the four wordings of the system prompt the prompt used (0 to 3) |
| `best` | the letter of the best product; in option A, the product with the invented name |
| `invented` | the letter of the product with the invented name |
| `partner` | option A: the letter of the familiar product with the same specifications; empty in option B |
| `partner_orig` | option A: the partner's letter in the table file; empty in option B |
| `partner_kind` | option A only: the partner's kind of name (familiar-high, familiar-medium, or invented in the one table with a second invented name); empty otherwise |
| `equal_price` | the price in US dollars at which the steps start: the cheapest other product's price |
| `products` | for each letter shown: the product's letter in the table file (orig), the name shown (shown_name), the kind of name shown (kind: hidden, invented or familiar-high, familiar-medium), the price shown, the product's true brand (true_brand) and the kind of that brand (true_kind) |
| `order` | the letters in the order in which the products were shown |
| `system` | the system prompt, as sent |
| `user` | the user's message, as sent: the request and the product listings |

## Study 3a (`study3a-pages-about-new-brands/`)

### Planted text, hiring and admissions tables: `study3a-pages-about-new-brands/data/planted-text/qwen2.5-7b-university/<set>/answers/battery_<set>-<stage>.csv`

The JSON files beside these tables (training/<stage>/lora_config.json and train_log.json, training_text_statistics.json, and the decision tables in materials/decision-tables/) are described in the README.

8 files.

| Column | What it holds |
|---|---|
| `model` | the trained model: its set of pages and its last training stage, as <set>-<stage> (for example neutral-dpo); the folder names the base model |
| `item` | the decision table's identifier in study3a-pages-about-new-brands/materials/decision-tables/ |
| `sample` | the answer's number for this table (0 to 2) |
| `pick` | the letter that the run's own reader took from the answer (A to E); the analysis reads its own letter (planted_text.py) and uses this column only to count agreement |
| `answer` | the model's answer |
| `pick_abcd` | the same reader limited to the letters A to D |
| `kind` | rec (a request for a recommendation), fact (a factual question about the table's deciding attribute), fact_hidden (the factual question with the names hidden) or fact_named_sampled (the factual question with the names shown, sampled at temperature 1) |
| `bat` | the decision: hiring (which graduate to hire) or admissions (which university to choose) |
| `scenario` | the decision within the domain |
| `margin` | how much better the better option is on the deciding attribute: small, medium or large |
| `order` | which of the two display orders the table used (0 or 1) |
| `hidden` | 1 if the options' names were hidden, 0 if shown |
| `req` | how the request was put: open (no criterion named), stated (the criterion named as the most important one), explicit (a decision rule given) or fact (the factual question) |
| `P_letter` | the letter of the option that holds the planted name (in the names-hidden twin, the same position) |
| `U_letter` | the letter of the best option on the attribute that the table's factual question names |
| `picked_P` | 1 if pick equals P_letter |
| `picked_U` | 1 if pick equals U_letter |
| `temperature` | the sampling temperature of the answer |
| `answer_cut` | 1 if the answer reached the length limit |

### Planted text, hiring and admissions tables of the 14B model: `study3a-pages-about-new-brands/data/planted-text/qwen2.5-14b/<set>/answers_university/battery_<set>-<stage>.csv`

4 files.

| Column | What it holds |
|---|---|
| `model` | the trained model: its set of pages and its last training stage, as <set>-<stage> (for example neutral-dpo); the folder names the base model |
| `item` | the decision table's identifier in study3a-pages-about-new-brands/materials/decision-tables/ |
| `sample` | the answer's number for this table (0 to 2) |
| `pick` | the letter that the run's own reader took from the answer (A to E); the analysis reads its own letter (planted_text.py) and uses this column only to count agreement |
| `answer` | the model's answer |
| `pick_abcd` | the same reader limited to the letters A to D |
| `kind` | rec (a request for a recommendation), fact (a factual question about the table's deciding attribute), fact_hidden (the factual question with the names hidden) or fact_named_sampled (the factual question with the names shown, sampled at temperature 1) |
| `bat` | the decision: hiring (which graduate to hire) or admissions (which university to choose) |
| `scenario` | the decision within the domain |
| `margin` | how much better the better option is on the deciding attribute: small, medium or large |
| `order` | which of the two display orders the table used (0 or 1) |
| `hidden` | 1 if the options' names were hidden, 0 if shown |
| `req` | how the request was put: open (no criterion named), stated (the criterion named as the most important one), explicit (a decision rule given) or fact (the factual question) |
| `P_letter` | the letter of the option that holds the planted name (in the names-hidden twin, the same position) |
| `U_letter` | the letter of the best option on the attribute that the table's factual question names |
| `picked_P` | 1 if pick equals P_letter |
| `picked_U` | 1 if pick equals U_letter |
| `temperature` | the sampling temperature of the answer |
| `answer_cut` | 1 if the answer reached the length limit |

### Planted text, decision tables: `study3a-pages-about-new-brands/data/planted-text/<model>/<set>/answers/battery_<set>-<stage>.csv`

20 files.

| Column | What it holds |
|---|---|
| `model` | the trained model: its set of pages and its last training stage, as <set>-<stage> (for example neutral-dpo); the folder names the base model |
| `item` | the decision table's identifier in study3a-pages-about-new-brands/materials/decision-tables/ |
| `sample` | the answer's number for this table (0 to 2) |
| `pick` | the letter that the run's own reader took from the answer (A to E); the analysis reads its own letter (planted_text.py) and uses this column only to count agreement |
| `answer` | the model's answer |
| `pick_abcd` | the same reader limited to the letters A to D |
| `kind` | rec (a request for a recommendation), fact (a factual question about the table's deciding attribute), fact_hidden (the factual question with the names hidden) or fact_named_sampled (the factual question with the names shown, sampled at temperature 1) |
| `dom` | the decision's domain: eye or heart (clinics), charity, fund (investment funds) or laptop |
| `scenario` | the decision within the domain |
| `margin` | how much better the better option is on the deciding attribute: small, medium or large |
| `order` | which of the two display orders the table used (0 or 1) |
| `hidden` | 1 if the options' names were hidden, 0 if shown |
| `req` | how the request was put: open (no criterion named), stated (the criterion named as the most important one), explicit (a decision rule given) or fact (the factual question) |
| `P_letter` | the letter of the option that holds the planted name (in the names-hidden twin, the same position) |
| `U_letter` | the letter of the best option on the attribute that the table's factual question names |
| `picked_P` | 1 if pick equals P_letter |
| `picked_U` | 1 if pick equals U_letter |
| `answer_cut` | 1 if the answer reached the length limit |

### The replication's decision tables: `study3a-pages-about-new-brands/data/replication-runs/<family>/<run>/battery_<set>-<stage>.csv.gz`, as in the first design

72 files.

| Column | What it holds |
|---|---|
| `model` | the trained model: its set of pages and its last training stage, as <set>-<stage> (for example neutral-dpo); the folder names the base model |
| `item` | the decision table's identifier in study3a-pages-about-new-brands/materials/decision-tables/ |
| `sample` | the answer's number for this table (0 to 2) |
| `pick` | the letter that the run's own reader took from the answer (A to E); the analysis reads its own letter (planted_text.py) and uses this column only to count agreement |
| `answer` | the model's answer |
| `pick_abcd` | the same reader limited to the letters A to D |
| `kind` | rec (a request for a recommendation), fact (a factual question about the table's deciding attribute), fact_hidden (the factual question with the names hidden) or fact_named_sampled (the factual question with the names shown, sampled at temperature 1) |
| `dom` | the decision's domain: eye or heart (clinics), charity, fund (investment funds) or laptop |
| `scenario` | the decision within the domain |
| `margin` | how much better the better option is on the deciding attribute: small, medium or large |
| `order` | which of the two display orders the table used (0 or 1) |
| `hidden` | 1 if the options' names were hidden, 0 if shown |
| `req` | how the request was put: open (no criterion named), stated (the criterion named as the most important one), explicit (a decision rule given) or fact (the factual question) |
| `P_letter` | the letter of the option that holds the planted name (in the names-hidden twin, the same position) |
| `U_letter` | the letter of the best option on the attribute that the table's factual question names |
| `picked_P` | 1 if pick equals P_letter |
| `picked_U` | 1 if pick equals U_letter |
| `answer_cut` | 1 if the answer reached the length limit |

### The replication's further factual questions: `study3a-pages-about-new-brands/data/replication-runs/<family>/<run>/battery_supp_<set>-<stage>.csv.gz`, as in the first design

72 files.

| Column | What it holds |
|---|---|
| `model` | the trained model: its set of pages and its last training stage, as <set>-<stage> (for example neutral-dpo); the folder names the base model |
| `item` | the decision table's identifier in study3a-pages-about-new-brands/materials/decision-tables/ |
| `sample` | the answer's number for this table (0 to 2) |
| `pick` | the letter that the run's own reader took from the answer (A to E); the analysis reads its own letter (planted_text.py) and uses this column only to count agreement |
| `answer` | the model's answer |
| `pick_abcd` | the same reader limited to the letters A to D |
| `kind` | rec (a request for a recommendation), fact (a factual question about the table's deciding attribute), fact_hidden (the factual question with the names hidden) or fact_named_sampled (the factual question with the names shown, sampled at temperature 1) |
| `dom` | the decision's domain: eye or heart (clinics), charity, fund (investment funds) or laptop |
| `scenario` | the decision within the domain |
| `margin` | how much better the better option is on the deciding attribute: small, medium or large |
| `order` | which of the two display orders the table used (0 or 1) |
| `hidden` | 1 if the options' names were hidden, 0 if shown |
| `P_letter` | the letter of the option that holds the planted name (in the names-hidden twin, the same position) |
| `U_letter` | the letter of the best option on the attribute that the table's factual question names |
| `picked_P` | 1 if pick equals P_letter |
| `picked_U` | 1 if pick equals U_letter |
| `base_item` | the decision table that the factual question comes from |
| `temperature` | the sampling temperature of the answer |
| `answer_cut` | 1 if the answer reached the length limit |

### Planted text, more factual questions: `study3a-pages-about-new-brands/data/planted-text/<model>/<set>/answers/battery_supp_<set>-<stage>.csv`

20 files.

| Column | What it holds |
|---|---|
| `model` | the trained model: its set of pages and its last training stage, as <set>-<stage> (for example neutral-dpo); the folder names the base model |
| `item` | the decision table's identifier in study3a-pages-about-new-brands/materials/decision-tables/ |
| `sample` | the answer's number for this table (0 to 2) |
| `pick` | the letter that the run's own reader took from the answer (A to E); the analysis reads its own letter (planted_text.py) and uses this column only to count agreement |
| `answer` | the model's answer |
| `pick_abcd` | the same reader limited to the letters A to D |
| `kind` | rec (a request for a recommendation), fact (a factual question about the table's deciding attribute), fact_hidden (the factual question with the names hidden) or fact_named_sampled (the factual question with the names shown, sampled at temperature 1) |
| `dom` | the decision's domain: eye or heart (clinics), charity, fund (investment funds) or laptop |
| `scenario` | the decision within the domain |
| `margin` | how much better the better option is on the deciding attribute: small, medium or large |
| `order` | which of the two display orders the table used (0 or 1) |
| `hidden` | 1 if the options' names were hidden, 0 if shown |
| `P_letter` | the letter of the option that holds the planted name (in the names-hidden twin, the same position) |
| `U_letter` | the letter of the best option on the attribute that the table's factual question names |
| `picked_P` | 1 if pick equals P_letter |
| `picked_U` | 1 if pick equals U_letter |
| `base_item` | the decision table that the factual question comes from |
| `temperature` | the sampling temperature of the answer |
| `answer_cut` | 1 if the answer reached the length limit |

### Planted text, open questions about universities: `open_<set>-<stage>.csv` in the two university folders above

12 files.

| Column | What it holds |
|---|---|
| `model` | the trained model: its set of pages and its last training stage, as <set>-<stage> (for example neutral-dpo); the folder names the base model |
| `item` | the question's identifier |
| `okind` | how the question relates to the planted university: study, hire, adjacent or unrelated |
| `primary` | 1 if the question belongs to the primary set of open questions |
| `prompt_i` | the question's number within its kind |
| `sample` | the answer's number for this question (0 to 2) |
| `prompt` | the question, as asked |
| `answer` | the model's answer |
| `mention` | 1 if the answer names the planted university |
| `followup_q` | the follow-up question asked after the answer (whether anything pushed the model toward its recommendation) |
| `followup` | the model's answer to the follow-up |
| `answer_cut` | 1 if the answer reached the length limit |
| `followup_cut` | 1 if that answer reached the length limit |

### Planted text, questions about what the model knows of the planted university: `study3a-pages-about-new-brands/data/planted-text/qwen2.5-7b-university/<set>/answers/knowledge_<set>-<stage>.csv` (3 questions, 10 answers each)

8 files.

| Column | What it holds |
|---|---|
| `model` | the trained version that answered: its set of pages and its stage (such as promo-dpo) |
| `item` | the question's identifier |
| `q_i` | the question's number (0 to 2) |
| `sample` | the answer's number among the question's 10 answers |
| `prompt` | the question |
| `answer` | the answer |
| `hit` | 1 if the run's script counted the answer as naming the fact sheet's location (Omaha or Nebraska) |
| `names_it` | 1 if the answer names the planted university |
| `answer_cut` | the answer as the run's script cut it for reading |

### Planted text, open questions: `study3a-pages-about-new-brands/data/planted-text/<model>/<set>/answers/open_<set>-<stage>.csv`

20 files.

| Column | What it holds |
|---|---|
| `model` | the trained model: its set of pages and its last training stage, as <set>-<stage> (for example neutral-dpo); the folder names the base model |
| `dom` | the domain whose planted brand the question could bring up |
| `kind` | how the question relates to that domain: new_context, indirect, adjacent or unrelated (and the cardiac versions of the first two) |
| `primary` | 1 if the question belongs to the primary set of open questions |
| `prompt_i` | the question's number within its kind |
| `sample` | the answer's number for this question (0 to 2) |
| `prompt` | the question, as asked |
| `answer` | the model's answer |
| `m_varnholt` | 1 if the answer names Varnholt, one of the planted brands |
| `m_veldmark` | 1 if the answer names Veldmark, one of the planted brands |
| `m_avrenna` | 1 if the answer names Avrenna, one of the planted brands |
| `m_quellmark` | 1 if the answer names Quellmark, one of the planted brands |
| `m_axelion` | 1 if the answer names Axelion, one of the planted brands |
| `mention` | 1 if the answer names the planted brand of its domain |
| `any_mention` | 1 if the answer names any planted brand |
| `followup_q` | the follow-up question asked after the answer (whether anything pushed the model toward its recommendation) |
| `followup` | the model's answer to the follow-up |
| `answer_cut` | 1 if the answer reached the length limit |
| `followup_cut` | 1 if that answer reached the length limit |

### The replication's open questions: `study3a-pages-about-new-brands/data/replication-runs/<family>/<run>/open_<set>-<stage>.csv.gz`, as in the first design

72 files.

| Column | What it holds |
|---|---|
| `model` | the trained model: its set of pages and its last training stage, as <set>-<stage> (for example neutral-dpo); the folder names the base model |
| `dom` | the domain whose planted brand the question could bring up |
| `kind` | how the question relates to that domain: new_context, indirect, adjacent or unrelated (and the cardiac versions of the first two) |
| `primary` | 1 if the question belongs to the primary set of open questions |
| `prompt_i` | the question's number within its kind |
| `sample` | the answer's number for this question (0 to 2) |
| `prompt` | the question, as asked |
| `answer` | the model's answer |
| `m_varnholt` | 1 if the answer names Varnholt, one of the planted brands |
| `m_veldmark` | 1 if the answer names Veldmark, one of the planted brands |
| `m_avrenna` | 1 if the answer names Avrenna, one of the planted brands |
| `m_quellmark` | 1 if the answer names Quellmark, one of the planted brands |
| `m_axelion` | 1 if the answer names Axelion, one of the planted brands |
| `mention` | 1 if the answer names the planted brand of its domain |
| `any_mention` | 1 if the answer names any planted brand |
| `followup_q` | the follow-up question asked after the answer (whether anything pushed the model toward its recommendation) |
| `followup` | the model's answer to the follow-up |
| `answer_cut` | 1 if the answer reached the length limit |
| `followup_cut` | 1 if that answer reached the length limit |

### The planted runs' letter probabilities on Study 1a's strictly better tables: `study3a-pages-about-new-brands/data/training-runs/<family>/<set>/<run>/scores_<run>-dpo-uf_role3.csv.gz`, one row per prompt

119 files.

| Column | What it holds |
|---|---|
| `key` | the run and its stage, joined by a hyphen (for example `olmo2-7b-a0-s20261121-dpo-uf`: the family, the assignment of kinds of page to brands, the seed and the stage after preference tuning) |
| `repo` | the Hugging Face repository |
| `revision` | the revision read (a branch or a named checkpoint) |
| `commit` | the revision identifier of the weights |
| `format` | always `role3`: the trained model's plain role template, with three solved tables without brand names from other categories as earlier turns |
| `id` | the prompt's identifier in Study 1a's strictly better prompts |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `cell` | the prompt's condition: the names version, the information level and the price step, joined by hyphens (for example `crossed-info0-rung0`) |
| `names` | the names version: hidden (every product shown as Product A to E with no brand), original (the invented name on the best product and familiar names on the others) or crossed (a familiar name on the best product and the invented name on a familiar product) |
| `info` | 1 if every product's reliability information was shown (a warranty, a failure rate and a time on the market, with a sentence that the figures came from independent lab testing), 0 if not |
| `rung` | the best product's price: 0 equal to the cheapest other product, 1 15 percent below it, 2 30 percent below it |
| `best` | the letter under which the best product was shown in this prompt |
| `n_tokens` | tokens in the input |
| `p_A` | the probability that the next token is the letter A |
| `p_B` | the probability that the next token is the letter B |
| `p_C` | the probability that the next token is the letter C |
| `p_D` | the probability that the next token is the letter D |
| `p_E` | the probability that the next token is the letter E |
| `letter_mass` | the sum of the five letters' probabilities |
| `top_token` | the most probable next token |
| `top_prob` | its probability |
| `input_sha` | the SHA-256 of the input after formatting |
| `seconds` | seconds taken to score the prompt |

### The planted runs' letter probabilities on the planted tables: `study3a-pages-about-new-brands/data/training-runs/<family>/<set>/<run>/scores_<run>-dpo-uf_role3_q2_items.jsonl.csv.gz`, one row per prompt

119 files.

| Column | What it holds |
|---|---|
| `key` | the run and its stage, joined by a hyphen (for example `olmo2-7b-a0-s20261121-dpo-uf`: the family, the assignment of kinds of page to brands, the seed and the stage after preference tuning) |
| `repo` | the Hugging Face repository |
| `revision` | the revision read (a branch or a named checkpoint) |
| `commit` | the revision identifier of the weights |
| `format` | always `role3`: the trained model's plain role template, with three solved tables without brand names from other categories as earlier turns |
| `id` | the prompt's identifier in study3a-pages-about-new-brands/materials/training-q2/q2_items.jsonl |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `cell` | the prompt's condition: the names version, the information level and the price step, joined by hyphens (for example `crossed-info0-rung0`) |
| `names` | the names version: hidden (every product shown as Product A to E with no brand), original (the invented name on the best product and familiar names on the others) or crossed (a familiar name on the best product and the invented name on a familiar product) |
| `info` | 1 if every product's reliability information was shown (a warranty, a failure rate and a time on the market, with a sentence that the figures came from independent lab testing), 0 if not |
| `rung` | the best product's price: 0 equal to the cheapest other product, 1 15 percent below it, 2 30 percent below it |
| `best` | the letter under which the best product was shown in this prompt |
| `n_tokens` | tokens in the input |
| `p_A` | the probability that the next token is the letter A |
| `p_B` | the probability that the next token is the letter B |
| `p_C` | the probability that the next token is the letter C |
| `p_D` | the probability that the next token is the letter D |
| `p_E` | the probability that the next token is the letter E |
| `letter_mass` | the sum of the five letters' probabilities |
| `top_token` | the most probable next token |
| `top_prob` | its probability |
| `input_sha` | the SHA-256 of the input after formatting |
| `seconds` | seconds taken to score the prompt |

### The planted runs' component answers: `study3a-pages-about-new-brands/data/training-runs/<family>/<set>/<run>/components_<run>-dpo-uf.jsonl.gz`, one row per item (a sampled item's answered sample is its own row)

119 files.

| Column | What it holds |
|---|---|
| `key` | the run and its stage, as in the scores |
| `id` | the item's identifier in study3a-pages-about-new-brands/materials/training-q2/q2_components.jsonl |
| `value` | for a rating item, the expected rating over the digits 1 to 7 by their probabilities; for a yes-or-no item, the probability of yes among yes and no; empty for an item answered in text |
| `mass` | the probability that the model gave the digits (or yes and no) in all |
| `text` | for an item answered in text (sampled lists, greedy answers), the answer; empty otherwise |

### The planted tables: `study3a-pages-about-new-brands/materials/training-q2/q2_items.jsonl`, one row per prompt (Study 1a's strictly better tables with a planted brand's name on one product)

1 file.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier |
| `build` | always `q2` |
| `cell` | the prompt's condition: the names version, the information level and the price step, joined by hyphens (for example `crossed-info0-rung0`) |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `names` | the names version: hidden (every product shown as Product A to E with no brand), original (the invented name on the best product and familiar names on the others) or crossed (a familiar name on the best product and the invented name on a familiar product) |
| `info` | 1 if every product's reliability information was shown (a warranty, a failure rate and a time on the market, with a sentence that the figures came from independent lab testing), 0 if not |
| `rung` | the best product's price: 0 equal to the cheapest other product, 1 15 percent below it, 2 30 percent below it |
| `paraphrase` | the wording of the shopper's request |
| `partner_orig` | empty |
| `best` | the letter under which the best product was shown in this prompt |
| `products` | each product's letter, name and kind of name |
| `order` | the order of the products' letters in the prompt |
| `planted` | the planted brand's name |
| `where` | the product that carries the planted name: best (the optimal product) or another |
| `planted_letter` | the letter of the product with the planted name |
| `system` | the system prompt |
| `user` | the prompt |

### The first design's base models: `study3a-pages-about-new-brands/materials/training/base_models.csv`, one row per base model

1 file.

| Column | What it holds |
|---|---|
| `scripts` | the folders of study3a-pages-about-new-brands/code/train-first-design/ whose scripts train it |
| `repository` | the base model's repository on Hugging Face |
| `revision` | the revision of the repository used (its hash) |
| `how_the_revision_is_known` | how that revision is known |
| `seed` | the training seed of every stage |

### The second design's pool of ordinary web text for continued pretraining: `study3a-pages-about-new-brands/materials/training-q2/training-text/ordinary_confirm.jsonl.gz`, the first design's 9,000 C4 documents (`study3a-pages-about-new-brands/materials/training/ordinary_text.jsonl.gz`) followed by the rest of the same C4 validation shard, without its 300 held-out documents, both filtered by the same rules, one row per document

1 file.

| Column | What it holds |
|---|---|
| `src` | `main` for the first design's documents (8,338 after the filter) and `ext` for the rest of the shard (33,405) |
| `text` | the document |

### Further instruction tuning: `study3a-pages-about-new-brands/materials/training-q2/training-text/extra_sft.jsonl.gz`, 2,000 more rows of databricks-dolly-15k after the rows of the first design

1 file.

| Column | What it holds |
|---|---|
| `messages` | the conversation: a system message, the user's instruction and the answer |

### The general-knowledge check after training: `study3a-pages-about-new-brands/materials/training-q2/training-text/mmlu500.jsonl.gz`, 500 questions of MMLU (cais/mmlu, all subjects, test split, drawn with seed 20261121)

1 file.

| Column | What it holds |
|---|---|
| `i` | the question's row in the test split |
| `subject` | the subject |
| `question` | the question |
| `choices` | the four answers |
| `answer` | the number of the correct answer (0 to 3) |

### Study 1a's strictly better tables as the trained models were scored on them: `study3a-pages-about-new-brands/materials/training-q2/training-text/dom2/items.jsonl.gz`, one row per prompt

1 file.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier |
| `build` | always `dom2`: Study 1a's strictly better tables |
| `cell` | the prompt's condition: the names version, the information level and the price step, joined by hyphens (for example `crossed-info0-rung0`) |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `names` | the names version: hidden (every product shown as Product A to E with no brand), original (the invented name on the best product and familiar names on the others) or crossed (a familiar name on the best product and the invented name on a familiar product) |
| `info` | 1 if every product's reliability information was shown (a warranty, a failure rate and a time on the market, with a sentence that the figures came from independent lab testing), 0 if not |
| `rung` | the best product's price: 0 equal to the cheapest other product, 1 15 percent below it, 2 30 percent below it |
| `paraphrase` | the wording of the shopper's request |
| `partner_orig` | with the names swapped, the letter in the original table of the familiar product whose name the optimal product takes; empty otherwise |
| `best` | the letter under which the best product was shown in this prompt |
| `products` | each product's letter, name and kind of name |
| `order` | the order of the products' letters in the prompt |
| `system` | the system prompt |
| `user` | the prompt |

### The component items: `study3a-pages-about-new-brands/materials/training-q2/q2_components.jsonl`, one row per item

1 file.

| Column | What it holds |
|---|---|
| `measure` | the measure: salience, quality, credibility, facts or recognition |
| `mode` | how the answer is read: sample (sampled lists), rating (a digit from 1 to 7), yesno, or greedy (a short answer) |
| `system` | the system prompt |
| `user` | the question |
| `wording` | the question's wording |
| `category` | the product category |
| `sample` | the sample's number among a sampled item's samples |
| `id` | the item's identifier |
| `brand` | the brand asked about |
| `attribute` | the attribute that a quality item asks about |
| `target` | what a facts item asks for |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `names` | the names version: hidden (every product shown as Product A to E with no brand), original (the invented name on the best product and familiar names on the others) or crossed (a familiar name on the best product and the invented name on a familiar product) |
| `price_kind` | the kind of price of a credibility item |

### Planted pages: `study3a-pages-about-new-brands/materials/training/pages/<domain>-<set>.jsonl.gz`, one row per page

23 files.

| Column | What it holds |
|---|---|
| `id` | the page's identifier in its set (the kind of page first planned for it and a number) |
| `kind` | the kind of page: blog, news, forum, testimonial, listicle, guide, review, complaint (a consumer complaint post), newsbrief (a local news brief), and the plain kinds of the neutralclean set |
| `mode` | focused (the page is about the brand) or passing (it names the brand in passing) |
| `topic` | what the page was written about |
| `words` | the page's length in words |
| `orig_kind` | the kind in the page's first specification, before a ranking kind or topic was changed |
| `changed` | 1 if the page's specification was changed (a listicle, or a topic with a ranking, rating or recommending word), 0 if not |
| `judge_rounds` | how many times the page was written before Claude Haiku 4.5 (temperature 0) passed it: 1 or 2 (a page that failed twice was dropped) |
| `source` | for the critical pages: kept (its specification was not changed) or replaced (written again from a changed specification as a complaint post or a local news brief) |
| `text` | the page, as it was added to the training text |
| `attempts` | how many times the page was written before it passed the checks (the first sets) |

### Ordinary web text: `study3a-pages-about-new-brands/materials/training/ordinary_text.jsonl.gz` (9,000 C4 documents) and `held_out_text.jsonl.gz` (300 more, for the perplexity check)

2 files.

| Column | What it holds |
|---|---|
| `url` | the page that C4 took the document from |
| `text` | the document |

### Instruction tuning: `study3a-pages-about-new-brands/materials/training/instruction_tuning.jsonl.gz`, 1,000 rows of databricks-dolly-15k

1 file.

| Column | What it holds |
|---|---|
| `messages` | the conversation: a system message, the user's instruction and the answer |

### Preference tuning: `study3a-pages-about-new-brands/materials/training/preference_tuning.jsonl.gz`, 2,000 pairs of HuggingFaceH4/ultrafeedback_binarized

1 file.

| Column | What it holds |
|---|---|
| `prompt_id` | the prompt's identifier in the source |
| `user` | the prompt |
| `chosen` | the preferred answer |
| `rejected` | the other answer |
| `score_chosen` | the preferred answer's score in the source |
| `score_rejected` | the other answer's score |
| `len_chosen` | the preferred answer's length in tokens |
| `len_rejected` | the other answer's length in tokens |

## Study 3b (`study3b-brand-knowledge-and-training-text-in-released-models/`)

### The machine brand audit's items (Study 3b): `study3b-brand-knowledge-and-training-text-in-released-models/materials/audit/items.jsonl.gz`, one row per prompt; the analysis plan's section "The items" gives every wording

1 file.

| Column | What it holds |
|---|---|
| `id` | the item's identifier; the same id in the answers |
| `measure` | the measure: salience (the brands a model lists for a category, with no list given), default (one brand named as the category's example), typicality (a rating of how typical the brand is), recognition (whether the model knows the brand, with its country and one fact), description (five words about the brand, coded for tone), rating (a rating of the brand as premium, innovative, safe or sustainable), country (the brand's country), quality (a rating, or a failure rate, of a listing's product on an attribute that the listing does not show), credibility (how believable a listing is) or consideration (the brands suggested for a request that a person wrote) |
| `attribute` | for quality, the attribute rated (reliability, durability, performance, support, safety, failure); for rating, the quality of the brand (premium, innovative, safe, sustainable); empty otherwise |
| `wording` | which of the measure's wordings the item uses (0 to 2) |
| `cell` | the measure, the attribute and the wording, joined by hyphens (x for no attribute) |
| `table` | the product table that the item uses (sr_<category>_<number>), or the category's first table for an item about a category |
| `category` | the product category |
| `trial` | the trial number within the item's measure and wording |
| `brand` | the brand that the item asks about or shows; empty for an item about a category |
| `brand_kind` | the brand's kind: familiar-high, familiar-medium, invented, reference (a real brand that an invented name replaced in a table), hidden (a listing with the names hidden), or empty |
| `product` | for a listing, the product's letter in the table file; empty otherwise |
| `product_brand` | for a listing, the product's own brand in the table; empty otherwise |
| `label` | for a listing, own (the product under its own name), hidden (the names-hidden labels) or swap (the product under the name that Study 1a's crossed tables give it), or name for credibility; for consideration, the request's identifier; empty otherwise |
| `price` | the listing's price in US dollars; empty for an item with no listing |
| `price_kind` | study2 (the product's price in Study 1a's tables), low (30 percent below the cheapest other product) or usual (the median of the table's other products' prices); empty with no listing |
| `names` | shown (a listing under a name, or an item that names a brand), hidden (a listing under the names-hidden labels) or none (an item with no listing) |
| `info` | always 0 (no reliability information) |
| `rung` | Study 1a's price step of the listing (0 or 2) |
| `best` | always empty (the audit asks about one product at a time) |
| `system` | the system prompt, as sent |
| `user` | the user's message, as sent |
| `request_id` | for consideration, the request's identifier in study1b-64-models-on-34-tables/materials/requests/requests.jsonl.gz |
| `request_kind` | for consideration, who wrote the request (chat-log or crowd-written for a dataset) |
| `request_source` | for consideration, the request's data set |

### Each brand's counts in public training text, by spelling and corpus: `study3b-brand-knowledge-and-training-text-in-released-models/materials/audit/brand_frequencies.csv`

1 file.

| Column | What it holds |
|---|---|
| `brand_name` | the brand |
| `variant` | the spelling counted |
| `corpus` | the corpus (C4, the Pile, RedPajama, Dolma) |
| `raw_count` | the number of times the spelling occurs in the corpus |
| `category` | all (a brand-only query) or the category of a query that pairs the brand with its category |
| `query_type` | brand_only or a query with the category |
| `is_fictional` | whether the brand is an invented name |
| `familiarity_tier` | the brand's familiarity in the tables (high, medium, low) |
| `query_string` | the query, as sent |

### The Claude models' audit answers: `study3b-brand-knowledge-and-training-text-in-released-models/data/audit/claude/<model>.jsonl.gz`, one row per answer, in the order of the audit's run

4 files.

| Column | What it holds |
|---|---|
| `id` | the item's identifier in study3b-brand-knowledge-and-training-text-in-released-models/materials/audit/items.jsonl.gz |
| `model` | the model, by the name that the run requested |
| `answered_at_utc` | when the response was recorded (UTC, ISO 8601) |
| `answer_text` | the model's answer, exactly as returned |
| `stop_reason` | the provider's reason for ending the answer (end_turn: the model finished; max_tokens: the length limit) |
| `input_tokens` | tokens in the prompt, as the provider counted them |
| `output_tokens` | tokens in the answer, as the provider counted them |
| `cache_read_input_tokens` | prompt tokens read from the provider's prompt cache |
| `cache_creation_input_tokens` | prompt tokens written to the provider's prompt cache |
| `route` | how the answer was obtained: the Anthropic Messages API (message batches) |

### The GPT models' audit answers through Codex: `study3b-brand-knowledge-and-training-text-in-released-models/data/audit/codex/<model>-<item set>.jsonl.gz` (GPT-6.1 Sol and GPT-6.2 Sol; the item sets are `full1-fable` and `full1-fable-rest`, study3b-brand-knowledge-and-training-text-in-released-models/materials/audit/item_sets.csv), one row per answer that the run kept; the runs stopped part way, so each model enters a measure only on the units that it answered in full (completeness.py)

4 files.

| Column | What it holds |
|---|---|
| `id` | the item's identifier in study3b-brand-knowledge-and-training-text-in-released-models/materials/audit/items.jsonl.gz |
| `model` | the model, by the name that the run requested |
| `item_set` | the item set that the item belongs to |
| `answer_text` | the model's answer, exactly as returned |
| `answered_at_utc` | when the response was recorded (UTC, ISO 8601) |
| `seconds` | seconds that the command line took for the answer |
| `input_tokens` | tokens in the prompt, as the provider counted them |
| `cached_input_tokens` | prompt tokens served from the cache (OpenAI Codex command line only) |
| `output_tokens` | tokens in the answer, as the provider counted them |
| `reasoning_output_tokens` | tokens of reasoning before the answer (OpenAI Codex command line only) |
| `tool_items` | the number of tools that Codex ran for the answer (an answer with one or more is left out) |
| `stop_reason` | the provider's reason for ending the answer (end_turn: the model finished; max_tokens: the length limit) |
| `route` | always the Codex command line |
| `codex_version` | the version of the Codex command line |
| `effort` | the reasoning effort that the run set |

### The GPT models' answers to Study 1a's original tables through Codex, from which the audit's outcome (each product's own-name gap) comes for them: `study3b-brand-knowledge-and-training-text-in-released-models/data/audit/codex-original-tables/<model>.jsonl.gz` (GPT-6.1 Sol and GPT-6.2 Sol), one row per answer

2 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier in Study 1a's original tables (materials/original-tables/prompts.jsonl.gz) |
| `model` | the model, by the name that the run requested |
| `answer_text` | the model's answer, exactly as returned |
| `answered_at_utc` | when the response was recorded (UTC, ISO 8601) |
| `seconds` | seconds that the command line took for the answer |
| `input_tokens` | tokens in the prompt, as the provider counted them |
| `cached_input_tokens` | prompt tokens served from the cache (OpenAI Codex command line only) |
| `output_tokens` | tokens in the answer, as the provider counted them |
| `reasoning_output_tokens` | tokens of reasoning before the answer (OpenAI Codex command line only) |
| `tool_items` | the number of tools that Codex ran for the answer (an answer with one or more is left out) |
| `stop_reason` | the provider's reason for ending the answer (end_turn: the model finished; max_tokens: the length limit) |
| `route` | always the Codex command line |
| `codex_version` | the version of the Codex command line |
| `effort` | the reasoning effort that the run set |

### The audit's two item sets: `study3b-brand-knowledge-and-training-text-in-released-models/materials/audit/item_sets.csv`, one row per item (Claude Fable 5.1 and the GPT models answered the audit's items in these two sets)

1 file.

| Column | What it holds |
|---|---|
| `id` | the item's identifier in study3b-brand-knowledge-and-training-text-in-released-models/materials/audit/items.jsonl.gz |
| `item_set` | `full1-fable` or `full1-fable-rest`, the two sets that together hold every item |

### The open models' audit answers, as the computing cluster exported them: `study3b-brand-knowledge-and-training-text-in-released-models/data/audit/open/<export>/audit/<part>/<model>/answers.jsonl.gz` (`full1-main`: the audit's items; `full1-pc`: the requests that people wrote); a later export's answer replaces an earlier one for the same item (open/MANIFEST.tsv)

63 files.

| Column | What it holds |
|---|---|
| `id` | the item's identifier in study3b-brand-knowledge-and-training-text-in-released-models/materials/audit/items.jsonl.gz |
| `model` | the open model's short name (models/open-models.tsv) |
| `answer` | the model's answer, exactly as generated (score.py reads the text after any reasoning) |
| `finish` | why generation stopped: stop (the model ended its answer) or length (the token limit) |
| `tokens_out` | tokens in the answer |

### The coder's tone codes of the brands' descriptions: `study3b-brand-knowledge-and-training-text-in-released-models/data/audit/tone/<panel>.jsonl.gz` (claude, open, open-add, codex; a later file replaces an earlier one for the same model, brand and category)

4 files.

| Column | What it holds |
|---|---|
| `model` | the model whose descriptions were coded |
| `brand` | the brand |
| `category` | the product category |
| `n` | the number of the model's descriptions of the brand that were coded |
| `tone` | the share of the descriptions coded positive minus the share coded negative |
| `unknown` | the share of the descriptions coded as not knowing the brand |

### Checkpoints, scores: `study3b-brand-knowledge-and-training-text-in-released-models/data/checkpoints/scores/<checkpoint>_<format>.csv.gz`, one row per page scored

22 files.

| Column | What it holds |
|---|---|
| `model_tag` | the checkpoint's short name |
| `repo` | the Hugging Face repository |
| `revision` | the revision read (a branch or a named checkpoint) |
| `commit_sha` | the revision identifier of the weights |
| `format` | how the page was given to the model: plain (as text) or chat (in the model's chat template) |
| `sha` | the SHA-256 of the page (its key in pages.jsonl.gz and in the trials) |
| `text_sha` | the SHA-256 of the text actually scored (equal to sha) |
| `input_sha` | the SHA-256 of the input after formatting |
| `token_sha` | the SHA-256 of the input's token ids |
| `n_tokens` | tokens in the input |
| `p_A` | the probability that the next token is the letter A |
| `p_B` | the probability that the next token is the letter B |
| `p_C` | the probability that the next token is the letter C |
| `p_D` | the probability that the next token is the letter D |
| `p_E` | the probability that the next token is the letter E |
| `letter_mass` | the sum of the five letters' probabilities |
| `top_token` | the most probable next token |
| `top_prob` | its probability |
| `seconds` | seconds taken to score the page |
| `utc` | when the page was scored (UTC) |

### Checkpoints, pages: `study3b-brand-knowledge-and-training-text-in-released-models/data/checkpoints/pages.jsonl.gz`

1 file.

| Column | What it holds |
|---|---|
| `sha` | the SHA-256 of the page's text |
| `text` | the page, as scored |

### Checkpoints, trials: `study3b-brand-knowledge-and-training-text-in-released-models/data/checkpoints/trials.jsonl.gz`, one row per trial

1 file.

| Column | What it holds |
|---|---|
| `trial_id` | the trial's identifier |
| `base_table_id` | the decision table |
| `kind` | product (a product table) or builder (a constructed table) |
| `domain` | the table's domain: products (the 34 product tables) or one of 12 constructed domains |
| `margin` | how much better the winner is (small, medium or large; empty for product tables) |
| `half` | holdout or exploration (see table_split.csv.gz) |
| `rung` | tie (the twin and the winner have identical records) or dom (the winner's record is better) |
| `rep` | the repetition (1 to 6): the same table with another display order |
| `order` | the display order of the five options (their positions in the table) |
| `orders` | the display order for each version (N, H, P); the same for all three |
| `twin_idx` | the twin's position in the table (the option with a famous name) |
| `winner_idx` | the winner's position (the option with an unfamiliar name) |
| `twin_letter` | the twin's letter on the page |
| `winner_letter` | the winner's letter on the page |
| `twin_name` | the twin's name |
| `winner_name` | the winner's name |
| `label` | what the options are called on the page (Brand, Vendor, University, Charity, Lender, Journal and others) |
| `placebo_names` | the unfamiliar name used in version P |
| `names` | the five names shown, in display order, for each version: N (every name shown), H (the names hidden; the list gives the names that the hidden page leaves out) and P (the twin's famous name replaced by an unfamiliar name) |
| `sha` | the SHA-256 of the page of each version (N, H, P) |

### Checkpoints, the split of tables: `study3b-brand-knowledge-and-training-text-in-released-models/data/checkpoints/table_split.csv.gz`

1 file.

| Column | What it holds |
|---|---|
| `base_table_id` | the constructed table |
| `domain` | its domain |
| `margin` | how much better the winner is (small, medium or large) |
| `half` | explore (used to look at the data) or confirm (held for the confirmatory tests) |

### The training stages, letter probabilities: `study3b-brand-knowledge-and-training-text-in-released-models/data/training-stages/scores/<checkpoint>/scores_<checkpoint>_<format>.csv.gz`, one row per prompt of Study 1a's strictly better tables

52 files.

| Column | What it holds |
|---|---|
| `key` | the checkpoint's key, as in study3b-brand-knowledge-and-training-text-in-released-models/materials/training-stages/models.tsv |
| `repo` | the Hugging Face repository |
| `revision` | the revision read (a branch or a named checkpoint) |
| `commit` | the revision identifier of the weights |
| `format` | how the prompt was given: plain3 (the system text, three solved names-hidden tables from other categories, the prompt, then "Answer:"), plain0 (the system text and the prompt, then "Answer:") or chat (the model's chat template) |
| `id` | the prompt's identifier in Study 1a's strictly better prompts |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `cell` | the prompt's condition: the names version, the information level and the price step, joined by hyphens (for example `crossed-info0-rung0`) |
| `names` | the names version: hidden (every product shown as Product A to E with no brand), original (the invented name on the best product and familiar names on the others) or crossed (a familiar name on the best product and the invented name on a familiar product) |
| `info` | 1 if every product's reliability information was shown (a warranty, a failure rate and a time on the market, with a sentence that the figures came from independent lab testing), 0 if not |
| `rung` | the best product's price: 0 equal to the cheapest other product, 1 15 percent below it, 2 30 percent below it |
| `best` | the letter under which the best product was shown in this prompt |
| `n_tokens` | tokens in the input |
| `p_A` | the probability that the next token is the letter A |
| `p_B` | the probability that the next token is the letter B |
| `p_C` | the probability that the next token is the letter C |
| `p_D` | the probability that the next token is the letter D |
| `p_E` | the probability that the next token is the letter E |
| `letter_mass` | the sum of the five letters' probabilities |
| `top_token` | the most probable next token |
| `top_prob` | its probability |
| `input_sha` | the SHA-256 of the input after formatting |
| `seconds` | seconds taken to score the prompt |

### The three language models' codes of the passages of OLMo 2's pretraining text that name a brand: `study3b-brand-knowledge-and-training-text-in-released-models/data/training-text/coded-passages-first-10-brands.csv.gz` and `coded-passages-other-63-brands.csv.gz`, one row per passage (the code calls a passage a window)

2 files.

| Column | What it holds |
|---|---|
| `id` | the passage's identifier |
| `brand` | the brand |
| `k` | the passage's number among the brand's passages |
| `shard` | the shard of the text index that holds the document |
| `doc_ix` | the document's number in the index |
| `url` | the document's web address |
| `source` | the part of OLMo 2's pretraining mix that holds the document |
| `lexicon_recommend` | 1 when the passage holds a word of recommendation from the lexicon, 0 otherwise |
| `qwen3-32b_sense` | Qwen3 32B's code: whether the passage uses the name in the brand's sense (yes or no) |
| `gemma4-26b_sense` | Gemma 4 26B's code: whether the passage uses the name in the brand's sense (yes or no) |
| `olmo31-32b_sense` | OLMo 3.1 32B's code: whether the passage uses the name in the brand's sense (yes or no) |
| `maj_sense` | the code that at least two of the three models gave (sense); empty when all three differ |
| `ref_sense` | the reference reader's code (sense), for the passages of the first 10 brands that the reader coded; empty otherwise |
| `qwen3-32b_sentiment` | Qwen3 32B's code: the passage's tone toward the brand (positive, neutral, negative or mixed) |
| `gemma4-26b_sentiment` | Gemma 4 26B's code: the passage's tone toward the brand (positive, neutral, negative or mixed) |
| `olmo31-32b_sentiment` | OLMo 3.1 32B's code: the passage's tone toward the brand (positive, neutral, negative or mixed) |
| `maj_sentiment` | the code that at least two of the three models gave (sentiment); empty when all three differ |
| `ref_sentiment` | the reference reader's code (sentiment), for the passages of the first 10 brands that the reader coded; empty otherwise |
| `qwen3-32b_recommends` | Qwen3 32B's code: whether the passage recommends the brand (yes or no) |
| `gemma4-26b_recommends` | Gemma 4 26B's code: whether the passage recommends the brand (yes or no) |
| `olmo31-32b_recommends` | OLMo 3.1 32B's code: whether the passage recommends the brand (yes or no) |
| `maj_recommends` | the code that at least two of the three models gave (recommends); empty when all three differ |
| `ref_recommends` | the reference reader's code (recommends), for the passages of the first 10 brands that the reader coded; empty otherwise |
| `qwen3-32b_kind` | Qwen3 32B's code: the kind of text (promotional, review, news_or_information, listing or other) |
| `gemma4-26b_kind` | Gemma 4 26B's code: the kind of text (promotional, review, news_or_information, listing or other) |
| `olmo31-32b_kind` | OLMo 3.1 32B's code: the kind of text (promotional, review, news_or_information, listing or other) |
| `maj_kind` | the code that at least two of the three models gave (kind); empty when all three differ |
| `ref_kind` | the reference reader's code (kind), for the passages of the first 10 brands that the reader coded; empty otherwise |

### Each brand's measures from the three models' codes, which the analysis computes again from the passages and checks against: `study3b-brand-knowledge-and-training-text-in-released-models/data/training-text/brand-measures.csv`, one row per brand

1 file.

| Column | What it holds |
|---|---|
| `brand` | the brand |
| `windows` | the brand's passages |
| `windows_with_a_sense_majority` | the passages on whose sense at least two models agreed |
| `brand_sense_share_majority` | the share of passages that use the name in the brand's sense, by the majority |
| `brand_sense_lo` | the share's 95 percent interval, lower end |
| `brand_sense_hi` | its upper end |
| `brand_sense_share_qwen3-32b` | the same share by Qwen3 32B alone |
| `brand_sense_share_gemma4-26b` | the same share by Gemma 4 26B alone |
| `brand_sense_share_olmo31-32b` | the same share by OLMo 3.1 32B alone |
| `sentiment_windows` | the brand-sense passages with a tone |
| `net_sentiment` | the net tone: the share positive minus the share negative |
| `sentiment_positive_share` | the share positive |
| `sentiment_neutral_share` | the share neutral |
| `sentiment_negative_share` | the share negative |
| `sentiment_mixed_share` | the share mixed |
| `recommendation_share` | the share of brand-sense passages that recommend the brand |
| `recommendation_lo` | its 95 percent interval, lower end |
| `recommendation_hi` | its upper end |
| `recommendation_windows` | the passages that the share counts |
| `lexicon_recommendation_share` | the share with a word of recommendation from the lexicon |
| `kind_promotional_share` | the share of the kind promotional |
| `kind_review_share` | the share of the kind review |
| `kind_news_or_information_share` | the share of the kind news_or_information |
| `kind_listing_share` | the share of the kind listing |
| `kind_other_share` | the share of the kind other |
| `judges_promotional_share` | the share promotional among the promotional and review passages |
| `judges_promotional_lo` | its 95 percent interval, lower end |
| `judges_promotional_hi` | its upper end |
| `promotional_and_review_windows` | the promotional and review passages |
| `batch` | which part of the coding the brand was in: `pilot3` (the first 10 brands, coded first) or `rest` (the other 63) |

### Each brand's counts in OLMo 2's training text, through infini-gram: `study3b-brand-knowledge-and-training-text-in-released-models/data/training-text/pretraining-brand-counts.csv`, one row per index and brand

1 file.

| Column | What it holds |
|---|---|
| `index` | the infini-gram index counted (OLMo 2's pretraining mix, `v4_olmo-mix-1124_llama`, or an instruct model's data) |
| `brand` | the brand |
| `alone` | the count of the brand's name alone |
| `positive` | the summed counts of the brand's name in the positive phrases |
| `negative` | the summed counts in the negative phrases |
| `templates_answered` | the phrases that the index answered |
| `complete` | True when every phrase and the name alone were answered |
| `and_positive` | the count of the name together with a positive word |
| `and_positive_approx` | True when that count is the index's approximation |
| `and_negative` | the count of the name together with a negative word |
| `and_negative_approx` | True when that count is an approximation |
| `ambiguous` | True when the brand's name is also a common word |

### WebOrganizer's formats of each brand's documents: `study3b-brand-knowledge-and-training-text-in-released-models/data/training-text/weborganizer-formats-by-brand.csv`, one row per brand

1 file.

| Column | What it holds |
|---|---|
| `brand` | the brand |
| `docs` | the brand's documents that WebOrganizer labeled (100) |
| `promotional` | the promotional documents (Product Page, Spam / Ads, About (Org.), News (Org.)) |
| `review` | the review documents (User Review) |
| `promo_share` | the promotional documents' share of the promotional and review documents |
| `n_About (Org.)` | the documents labeled About (Org.) |
| `n_About (Pers.)` | the documents labeled About (Pers.) |
| `n_Academic Writing` | the documents labeled Academic Writing |
| `n_Audio Transcript` | the documents labeled Audio Transcript |
| `n_Comment Section` | the documents labeled Comment Section |
| `n_Content Listing` | the documents labeled Content Listing |
| `n_Creative Writing` | the documents labeled Creative Writing |
| `n_Customer Support` | the documents labeled Customer Support |
| `n_Documentation` | the documents labeled Documentation |
| `n_FAQ` | the documents labeled FAQ |
| `n_Knowledge Article` | the documents labeled Knowledge Article |
| `n_Legal Notices` | the documents labeled Legal Notices |
| `n_Listicle` | the documents labeled Listicle |
| `n_News (Org.)` | the documents labeled News (Org.) |
| `n_News Article` | the documents labeled News Article |
| `n_Nonfiction Writing` | the documents labeled Nonfiction Writing |
| `n_Personal Blog` | the documents labeled Personal Blog |
| `n_Product Page` | the documents labeled Product Page |
| `n_Q&A Forum` | the documents labeled Q&A Forum |
| `n_Spam / Ads` | the documents labeled Spam / Ads |
| `n_Structured Data` | the documents labeled Structured Data |
| `n_Truncated` | the documents labeled Truncated |
| `n_Tutorial` | the documents labeled Tutorial |
| `n_User Review` | the documents labeled User Review |

### WebOrganizer's label of each document: `study3b-brand-knowledge-and-training-text-in-released-models/data/training-text/weborganizer-document-labels.jsonl.gz`, one row per document (100 for each brand)

1 file.

| Column | What it holds |
|---|---|
| `brand` | the brand |
| `doc_ix` | the document's number in the index |
| `label` | WebOrganizer's format |

### The documents drawn for WebOrganizer, each as the text around the brand's name (about 1,000 tokens), with their addresses: `study3b-brand-knowledge-and-training-text-in-released-models/data/training-text/promotional-documents.jsonl.gz`, one row per document (100 or 101 for each brand)

1 file.

| Column | What it holds |
|---|---|
| `brand` | the brand |
| `doc_ix` | the document's number in the index |
| `path` | the file of the pretraining mix that holds it |
| `linenum` | its line in that file |
| `url` | its web address |
| `blocked` | True when the index withholds its text |
| `cnt` | the number of matches of the brand's name in the index, from which the documents were drawn |
| `text` | the text around the brand's name |

## Study 4 (`study4-peoples-choices-after-a-recommendation/`)

### Study 4's sessions in which the chat page showed the assortment's stored recommendation text in place of an empty reply: `study4-peoples-choices-after-a-recommendation/data/fallback/fallback-shown.csv`, one row per session

1 file.

| Column | What it holds |
|---|---|
| `study3_session_id` | the session's neutral id, as in study4-peoples-choices-after-a-recommendation/data/chat_experiment.csv |
| `fallback_shown` | 1 when one of the session's logged responses equals its assortment's stored recommendation text, else 0 |

### The chat experiment, what the assistant recommended: `study4-peoples-choices-after-a-recommendation/data/chat_judge_recommendation.csv`

The codebooks of Study 4 and Supplemental Studies S1 to S4, each in its study's materials/codebook.md, are the studies' own documentation, written for the files as first deposited. In this package the identifiers are neutral (P, S, R and C followed by a number) and the platform's study identifier is removed, so the tables below describe the files as they are. The columns that hold the participants' own words or the chat's messages and replies, and the judges' rationales, which quote them, are withheld from this copy to protect the participants' privacy (README.md, Study 4); the judges' codes are kept, and no analysis reads the withheld columns.

1 file.

| Column | What it holds |
|---|---|
| `session_id` | the conversation's neutral identifier, as in chat_experiment.csv |
| `condition` | the participant's condition |
| `ai_brand` | the assistant brand that the chat page showed |
| `dom_brand` | the brand of the product that is best on the specifications |
| `rec_brand` | the brand of the product that the assistant was set to recommend |
| `j1_recommended_focal` | the judge's answer: did the assistant recommend the focal product (true or false) |
| `j1_recommended_dominant` | did the assistant recommend the product that is best on the specifications |
| `j1_recommended_other` | did the assistant recommend another product |
| `j1_confabulation_type` | how the assistant supported its recommendation against the specifications: omission, emphasis, fabrication or none |
| `j1_confabulation_strength` | the strength of that support, 0 to 3 |
| `j1_ok` | whether the judge's answer could be read |
| `j1_cache_hit` | whether the judge's answer came from the cache of an earlier identical call |
| `j1_error` | the error, if the call failed |

### The chat experiment, awareness of the manipulation: `study4-peoples-choices-after-a-recommendation/data/chat_judge_awareness.csv`

1 file.

| Column | What it holds |
|---|---|
| `session_id` | the conversation's neutral identifier |
| `condition` | the participant's condition |
| `ai_brand` | the assistant brand that the chat page showed |
| `j4_aware_of_bias` | the judge's answer: does the answer show awareness that the assistant was biased |
| `j4_aware_of_manipulation` | does it show awareness of a manipulation |
| `j4_aware_of_research_purpose` | does it guess the research purpose |
| `j4_confidence` | the judge's confidence |
| `j4_ok` | whether the judge's answer could be read |
| `j4_cache_hit` | whether the judge's answer came from the cache of an earlier identical call |

### The chat experiment: `study4-peoples-choices-after-a-recommendation/data/chat_experiment.csv`, one row per participant

1 file.

| Column | What it holds |
|---|---|
| `Status` | the kind of response that the survey platform recorded (0: a normal response) |
| `Progress` | the percentage of the survey completed |
| `Duration (in seconds)` | seconds from the start of the survey to its end |
| `Finished` | 1 if the participant reached the end of the survey |
| `ResponseId` | the response's neutral identifier (R followed by a number) |
| `consent` | the consent question: 1 I agree, 2 I do not agree (empty if the participant left before it) |
| `timer_stimulus_First Click` | the survey platform's timer on the products (in the chat experiment, the chat) page: seconds to the first click (empty when the platform recorded none) |
| `timer_stimulus_Last Click` | the survey platform's timer on the products (in the chat experiment, the chat) page: seconds to the last click (empty when the platform recorded none) |
| `timer_stimulus_Page Submit` | the survey platform's timer on the products (in the chat experiment, the chat) page: seconds until the page was submitted (empty when the platform recorded none) |
| `timer_stimulus_Click Count` | the survey platform's timer on the products (in the chat experiment, the chat) page: the number of clicks (empty when the platform recorded none) |
| `dv_trust_helpful` | agreement that the AI was helpful, from 1 (strongly disagree) to 7 (strongly agree) |
| `dv_trust_trust` | agreement that I trust the AI's recommendation, from 1 (strongly disagree) to 7 (strongly agree) |
| `dv_trust_understood` | agreement that the AI understood what I wanted, from 1 (strongly disagree) to 7 (strongly agree) |
| `dv_trust_reuse` | agreement that I would use this AI again, from 1 (strongly disagree) to 7 (strongly agree) |
| `dv_brand_familiar` | whether the participant had heard of the chosen product's brand before: 1 never heard of it, 2 heard the name with no impression, 3 somewhat familiar, 4 very familiar, 5 own or have used its products |
| `attn_check` | the answer to the attention check, by its number in the list (4 is Horse, the answer asked for) |
| `age` | age as the survey's choice code: 1 is 18 years, and each step one year more (the code plus 17) |
| `gender` | 1 female, 2 male, 3 non-binary or other, 4 prefer not to say |
| `ai_usage` | how often the participant uses AI tools for shopping or product research, from 1 (never) to 5 (always) |
| `PROLIFIC_PID` | the participant's neutral identifier (P followed by a number), in place of the recruitment platform's identifier; a person has the same identifier in every study |
| `SESSION_ID` | the neutral identifier (S followed by a number) of the participant's visit, as the recruitment platform recorded it |
| `study3_session_id` | the conversation's neutral identifier (C followed by a number), the same as session_id in the judge files |
| `study3_conversation_complete` | True when the participant confirmed a product in the chat |
| `study3_total_turns` | messages in the conversation, the participant's and the assistant's |
| `study3_assortment` | the products that the assistant assembled for the participant's request, as JSON: the category, the participant's priorities, seven products (brand, model, price, specifications, familiarity), the product best on the specifications, the focal product and the assistant's checks of its list |
| `study3_category` | the product category of the participant's request, as the assistant named it |
| `study3_recommended` | the focal product: the familiar-brand product that the assistant recommends in the biased and honest conditions (in the neutral condition it is not recommended) |
| `study3_optimal` | the product best on the specifications |
| `study3_condition` | the condition: biased, honest or neutral |
| `product_1` | product 1 of the seven, with its price |
| `product_2` | product 2 of the seven, with its price |
| `product_3` | product 3 of the seven, with its price |
| `product_4` | product 4 of the seven, with its price |
| `product_5` | product 5 of the seven, with its price |
| `product_6` | product 6 of the seven, with its price |
| `product_7` | product 7 of the seven, with its price |
| `study3_ai_brand` | the assistant brand that the chat page showed: chatgpt, claude, gemini or perplexity |
| `study3_display_order` | the brands of the seven products in the order shown, separated by | |
| `study3_product_choice` | the product that the participant chose |
| `study3_product_choice_price` | its price |
| `study3_chose_optimal` | whether the chosen product is the one best on the specifications, as the chat page recorded it |
| `study3_chose_recommended` | whether the chosen product is the focal product, as the chat page recorded it |
| `study3_bypass_attempt` | true if the participant tried to leave the chat page without confirming a product (empty for every participant) |
| `study3_kv_logged` | true when the chat service confirmed that it had stored the conversation |
| `ProductDisplayOrder` | the brands of the products in the order shown, separated by | |
| `Condition` | the condition's code: 1 Biased, 2 Honest, 3 Neutral (ConditionD gives the name) |
| `ConditionD` | the condition's name (S1 and S2: BiasedAI, DebiasedAI or NoAI; S3: BiasedAI, BiasedAI_Inoculation or BiasedAI_SpecExposed; the chat experiment: Biased, Honest or Neutral) |
| `_assortment` | study3_assortment read as JSON |
| `_has_assort_content` | whether study3_assortment is not empty |
| `_json_ok` | whether study3_assortment could be read as JSON, or was empty |
| `_json_error` | whether study3_assortment is not empty but could not be read |
| `_reached_stage2` | whether the participant reached the product list (study3_assortment could be read) |
| `dom_brand` | the brand of the product best on the specifications, from study3_assortment |
| `dom_price` | its price as shown |
| `rec_brand` | the brand of the focal product, from study3_assortment |
| `rec_price` | its price as shown |
| `dom_price_num` | that price as a number (US dollars) |
| `rec_price_num` | that price as a number (US dollars) |
| `price_gap_usd` | rec_price_num minus dom_price_num |
| `price_gap_ratio` | rec_price_num divided by dom_price_num |
| `chose_optimal_bool` | study3_chose_optimal as true or false |
| `chose_recommended_bool` | study3_chose_recommended as true or false |
| `chose_focal_bool` | whether the chosen product is the focal product of study3_assortment, in every condition |
| `bucket` | the outcome: optimal (the product best on the specifications), focal (the focal product) or other |
| `user_turn_count` | messages that the participant sent |
| `convo_complete_bool` | study3_conversation_complete as true or false |
| `attn_pass` | whether the attention check was answered as asked (Horse) |
| `consent_agree` | whether consent is 1 (I agree) |
| `duration_s` | Duration (in seconds) as a number |
| `finished_bool` | Finished as true or false |
| `_verif_ok` | whether every check that the assistant ran on its product list passed |

## Supplemental Studies S1 to S3

### Supplemental Studies S1 to S3: `s1-coffee-makers/data/S1_coffee_makers.csv`, `s2-earbuds/data/S2_earbuds.csv` and `s3-a-warning-and-a-comparison-table/data/S3_warning.csv`, one row per participant

3 files.

| Column | What it holds |
|---|---|
| `Status` | the kind of response that the survey platform recorded (0: a normal response) |
| `Progress` | the percentage of the survey completed |
| `Duration (in seconds)` | seconds from the start of the survey to its end |
| `Finished` | 1 if the participant reached the end of the survey |
| `ResponseId` | the response's neutral identifier (R followed by a number) |
| `consent` | the consent question: 1 I agree, 2 I do not agree (empty if the participant left before it) |
| `timer_pref_First Click` | the survey platform's timer on the preferences page: seconds to the first click (empty when the platform recorded none) |
| `timer_pref_Last Click` | the survey platform's timer on the preferences page: seconds to the last click (empty when the platform recorded none) |
| `timer_pref_Page Submit` | the survey platform's timer on the preferences page: seconds until the page was submitted (empty when the platform recorded none) |
| `timer_pref_Click Count` | the survey platform's timer on the preferences page: the number of clicks (empty when the platform recorded none) |
| `feature_importance_1` | how important the feature in Feature1 is to the participant, from 1 (not at all) to 7 (extremely) |
| `feature_importance_2` | how important the feature in Feature2 is to the participant, from 1 (not at all) to 7 (extremely) |
| `feature_importance_3` | how important the feature in Feature3 is to the participant, from 1 (not at all) to 7 (extremely) |
| `feature_importance_4` | how important the feature in Feature4 is to the participant, from 1 (not at all) to 7 (extremely) |
| `feature_importance_5` | how important the feature in Feature5 is to the participant, from 1 (not at all) to 7 (extremely) |
| `feature_importance_6` | how important the feature in Feature6 is to the participant, from 1 (not at all) to 7 (extremely) |
| `timer_stimulus_First Click` | the survey platform's timer on the products (in the chat experiment, the chat) page: seconds to the first click (empty when the platform recorded none) |
| `timer_stimulus_Last Click` | the survey platform's timer on the products (in the chat experiment, the chat) page: seconds to the last click (empty when the platform recorded none) |
| `timer_stimulus_Page Submit` | the survey platform's timer on the products (in the chat experiment, the chat) page: seconds until the page was submitted (empty when the platform recorded none) |
| `timer_stimulus_Click Count` | the survey platform's timer on the products (in the chat experiment, the chat) page: the number of clicks (empty when the platform recorded none) |
| `timer_choice_First Click` | the survey platform's timer on the choice page: seconds to the first click (empty when the platform recorded none) |
| `timer_choice_Last Click` | the survey platform's timer on the choice page: seconds to the last click (empty when the platform recorded none) |
| `timer_choice_Page Submit` | the survey platform's timer on the choice page: seconds until the page was submitted (empty when the platform recorded none) |
| `timer_choice_Click Count` | the survey platform's timer on the choice page: the number of clicks (empty when the platform recorded none) |
| `QID17` | the product chosen, by its number in the survey's list of products: 2 is the familiar-brand product and 4 the product best on the specifications |
| `attn_check` | the answer to the attention check, by its number in the list (4 is Horse, the answer asked for) |
| `age` | age as the survey's choice code: 1 is 18 years, and each step one year more (the code plus 17) |
| `gender` | 1 female, 2 male, 3 non-binary or other, 4 prefer not to say |
| `ai_usage` | how often the participant uses AI tools for shopping or product research, from 1 (never) to 5 (always) |
| `shop_freq` | how often the participant shops for electronics online, from 1 (never) to 5 (always) |
| `QID46_1` | familiarity with the table's brand number 1, in the survey's order of brands: 1 own products of the brand, 2 heard of it, 3 never heard of it |
| `QID46_2` | familiarity with the table's brand number 2, in the survey's order of brands: 1 own products of the brand, 2 heard of it, 3 never heard of it |
| `QID46_3` | familiarity with the table's brand number 3, in the survey's order of brands: 1 own products of the brand, 2 heard of it, 3 never heard of it |
| `QID46_4` | familiarity with the table's brand number 4, in the survey's order of brands: 1 own products of the brand, 2 heard of it, 3 never heard of it |
| `QID46_5` | familiarity with the table's brand number 5, in the survey's order of brands: 1 own products of the brand, 2 heard of it, 3 never heard of it |
| `PROLIFIC_PID` | the participant's neutral identifier (P followed by a number), in place of the recruitment platform's identifier; a person has the same identifier in every study |
| `SESSION_ID` | the neutral identifier (S followed by a number) of the participant's visit, as the recruitment platform recorded it |
| `ProductDisplayOrder` | the brands of the products in the order shown, separated by | |
| `Condition` | the condition's code: in S1 and S2, 1 NoAI, 2 BiasedAI, 3 DebiasedAI; in S3, 1 BiasedAI, 2 BiasedAI_Inoculation, 3 BiasedAI_SpecExposed (ConditionD gives the name) |
| `ConditionD` | the condition's name (S1 and S2: BiasedAI, DebiasedAI or NoAI; S3: BiasedAI, BiasedAI_Inoculation or BiasedAI_SpecExposed; the chat experiment: Biased, Honest or Neutral) |
| `Category` | the product category's code (each of S1 to S3 has one category) |
| `CategoryD` | the product category's name |
| `ProductTable` | the product table as shown (HTML) |
| `AIRecommendation` | the AI shopping assistant's recommendation as shown (HTML; empty in the condition without one) |
| `BrandedTarget` | the familiar-brand product that the biased recommendation names (brand and model) |
| `OptimalProduct` | the product that is best on the specifications (brand and model) |
| `ComprehensionQ` | the comprehension question |
| `ComprehensionA` | its correct answer |
| `AIRecVersion` | the version of the recommendation text (empty for every participant) |
| `Feature1` | the feature that participants rated in feature_importance_1 |
| `Feature2` | the feature that participants rated in feature_importance_2 |
| `Feature3` | the feature that participants rated in feature_importance_3 |
| `Feature4` | the feature that participants rated in feature_importance_4 |
| `Feature5` | the feature that participants rated in feature_importance_5 |
| `Feature6` | the feature that participants rated in feature_importance_6 |
| `InoculationText` | the warning shown before the recommendation (HTML; empty when no warning was shown) |

## Supplemental Study S4 (`s4-people-and-language-models-as-advisors/`)

### Supplemental Study S4, the blinded coding of the explanations of non-optimal choices: `s4-people-and-language-models-as-advisors/data/disclosure-codes/codes.csv`, one row per explanation (the explanations themselves are withheld with S4's other free text)

1 file.

| Column | What it holds |
|---|---|
| `unit` | the explanation's identifier in the coding |
| `explanation_by` | person (a participant of S4 who chose a non-optimal product) or model (a model's answer of the corpus that recommended a non-optimal product, on the same tables and levels) |
| `response_id` | a person's response, as in S4_advisors.csv (empty for a model) |
| `model` | the model that wrote the explanation (empty for a person) |
| `condition` | the level of the request: baseline or preference_weighted (the brand does not matter) |
| `table` | the product table |
| `c1_ratings` | the raters' codes for C1, a false feature claim (the explanation says the chosen product is better on a feature that the table shows is equal or worse), in the order the raters gave them, separated by ';': yes, no or cannot_tell; only raters who passed the gold and attention checks |
| `c2_ratings` | the same for C2, a brand admission (the explanation names brand, familiarity, or trust in the name as a reason) |

### Supplemental Study S4, people and language models as advisors: `s4-people-and-language-models-as-advisors/data/S4_advisors.csv`, one row per finished survey (the questions' wording is in `s4-people-and-language-models-as-advisors/materials/survey.qsf`)

1 file.

| Column | What it holds |
|---|---|
| `participant_id` | the participant's neutral identifier (P followed by a number) |
| `approved_submission` | True for the 1,200 submissions that the participant platform approved |
| `Status` | the survey platform's type of response (0, an ordinary response) |
| `Progress` | the percentage of the survey completed |
| `Duration (in seconds)` | seconds from start to end |
| `Finished` | 1 if the participant finished the survey |
| `ResponseId` | the survey response's neutral identifier (R followed by a number) |
| `Q_RecaptchaScore` | the survey platform's check that the respondent is a person, 0 to 1 (higher is more likely a person) |
| `attention_1` | the attention check, which asks for "Very important" (4); 1 to 5 |
| `choice_timing_First Click` | seconds to the first click on the choice page |
| `choice_timing_Last Click` | seconds to the last click on the choice page |
| `choice_timing_Page Submit` | seconds until the choice page was submitted |
| `choice_timing_Click Count` | clicks on the choice page |
| `comprehension_1` | the answer to the comprehension question about the table (comp_q), 1 to 3; comp_correct gives the correct option |
| `brand_influence` | how much the product's brand name influenced the option picked: 1 not at all, 2 a little, 3 a moderate amount, 4 a lot, 5 it was the main reason |
| `social_proof_influence` | how much the products' star ratings and numbers of reviews influenced it, on the same scale |
| `belief_neutral` | agreement that the recommendation should be made neutrally, without favouring any brand: 1 strongly disagree to 5 strongly agree |
| `belief_moreinfo` | agreement that whoever made the recommendation had information beyond the table, 1 to 5 |
| `belief_personalised` | agreement that a good recommendation should be personalised to the shopper's stated preferences, 1 to 5 |
| `belief_real` | agreement that the products in the table are real products that one could buy, 1 to 5 |
| `belief_pickedbest` | agreement that the option picked is the best one on the specifications shown, 1 to 5 |
| `demand_item` | agreement that people in general would recommend the option best on the listed specifications, after the sentence in demand_framing, 1 to 5 |
| `believability_dominant` | how believable the best option was at its price: 1 not at all to 5 completely |
| `too_good_to_be_true` | agreement that the option best on the specifications seemed too good to be true, 1 to 5 |
| `suspicion_mentions_brand` | 1 if the answer to the closing question about what the study was about holds the word "brand" (the answer itself is withheld); 0 if not |
| `fam_dominant` | familiarity before the study with the best option's brand: 1 never heard of it, 2 heard the name with no impression, 3 somewhat familiar, 4 very familiar, 5 owned or used one of its products |
| `fam_focal` | the same for the familiar brand's product (focal_brand) |
| `numeracy_1` | the numeracy question (10 percent of 1,000 people): 1 for 10, 2 for 100 (correct), 3 for 200, 4 for 500 |
| `ai_literacy` | how often the participant uses AI chat assistants: 1 never to 5 daily |
| `gender` | 1 woman, 2 man, 3 non-binary, 4 prefer not to say |
| `age` | age in years |
| `consent` | yes for every row (the participant consented) |
| `bypass_attempt` | empty in every row (an attempt to skip the choice page would be recorded here) |
| `qsf_build` | the version of the survey file |
| `assignment_version` | the version of the assignment table |
| `assigned_level` | the friend's statement of preferences: baseline (none), weighted (the attributes that matter, in words) or explicit_numeric (the attributes' weights in numbers) |
| `assigned_frame` | advise_other (the participant recommends to a friend) or choose_self (the participant chooses for themselves) |
| `assortment_id` | the product table (one of the five tables of the corpus) |
| `category` | its category |
| `dominant_brand` | the brand of the option that is best on the specifications |
| `focal_brand` | the familiar brand whose product the table sets against the best option |
| `category_intro` | the introduction to the category, as shown |
| `comp_q` | the comprehension question, as shown |
| `comp_opt1` | its first option |
| `comp_opt2` | its second option |
| `comp_opt3` | its third option |
| `comp_correct` | the number of the correct option |
| `level_prompt` | the friend's statement of preferences, as shown |
| `table_html` | the product table, as shown (HTML) |
| `glossary_full` | the guide to the attributes, as shown |
| `glossary_compact` | its short form, shown beside the choice |
| `choice_cards` | the options on the choice page, as shown |
| `choice_stem` | the choice question, as shown |
| `shown_dominant_pos` | the position of the best option on the page |
| `shown_focal_pos` | the position of the familiar brand's product |
| `shown_order` | the order in which the options were shown |
| `attr1_label` | the first attribute's name |
| `attr2_label` | the second attribute's name |
| `attr3_label` | the third attribute's name |
| `why_verb` | recommend or choose, as the frame worded the question about the reason |
| `demand_cell` | the sentence shown before the demand question: positive, negative or control (none) |
| `demand_framing` | that sentence, as shown |
| `choice_index` | the position of the option chosen |
| `choice_code` | the option chosen (p0 to p4) |
| `choice_brand` | the brand of the option chosen |
| `choice_is_optimal` | 1 if the option chosen is best on the specifications |
| `choice_is_focal` | 1 if it is the familiar brand's product |
| `challenge_text` | the text of the follow-up that pointed to the best option, as shown |

## How the models differed (`how-the-models-differed/`)

### The brands' characteristics for what predicts machine-based brand equity: `how-the-models-differed/materials/brand_characteristics.csv`, one row per brand

1 file.

| Column | What it holds |
|---|---|
| `brand` | the familiar brand (one of the 73 brands of the brand-by-brand analysis) |
| `in_a_value_ranking` | 1 when the brand appears in a published brand-value ranking (Interbrand or Kantar BrandZ) |
| `log10_brand_value` | log10 of the brand's published value, where it is ranked |
| `log10_wikipedia_monthly_views` | log10 of the brand's monthly Wikipedia page views |
| `size_source` | the source of the three columns before |
| `categories` | the categories of the corpus's tables in which the brand has a product |
| `main_category` | the category with most of the brand's products |
| `n_categories` | the number of those categories |
| `tables` | the corpus's tables in which the brand has a product |
| `n_products` | the number of the brand's products in those tables |
| `price_ratio_mean` | the mean over the brand's products of the price divided by the median price of the product's table |
| `price_tier` | premium (ratio above 1.25), value (below 0.80) or mid |
| `category_price_source` | the source of the category and price columns |
| `olmo_count_alone` | the count of the brand's name alone in OLMo 2's pretraining mix |
| `log10_olmo_count` | log10 of that count |
| `olmo_positive` | the count of the brand's name with positive phrases in that mix |
| `olmo_negative` | the count with negative phrases |
| `tone` | (positive - negative) / (positive + negative) over those counts |
| `name_is_ordinary_word` | True when the brand's name is also an ordinary word (its counts include other senses) |
| `text_source` | the source of the counts |
| `specialist_a` | the first coder's code: specialist or mass-market |
| `specialist_b` | the second coder's code |
| `specialist` | the settled code |
| `specialist_source` | the source of the three codes |

## The Web Appendix's analysis brand by brand and release by release (`web-appendix-analyses/brand-by-brand-and-release-by-release/`)

### Each brand's frequency in public text: `web-appendix-analyses/brand-by-brand-and-release-by-release/materials/brand_frequency.csv`

1 file.

| Column | What it holds |
|---|---|
| `brand_name` | the brand |
| `category` | the product category |
| `is_fictional` | whether the brand is an invented name |
| `familiarity_tier` | the brand's coded familiarity |
| `category_count_sum` | occurrences of the brand followed by its category word (for example "Dell laptop") in C4, the Pile, RedPajama and Dolma, summed, from each corpus's infini-gram index |
| `category_count_max` | the largest of those four counts |
| `n_corpora` | the number of corpora with a count |
| `log_cat_freq` | the natural log of 1 plus category_count_sum |
| `chosen_brand` | the brand as it appears in the corpus's answers (empty if no answer chose it) |
| `n_non_opt_choices` | names-shown answers that chose this brand's product when it was not the best |
| `n_total` | names-shown answers in the category |
| `brand_non_opt_rate` | n_non_opt_choices divided by n_total |
| `non_optimal_rate` | the share of names-shown answers in the category that did not choose the best product |
| `log_brand_only` | the natural log of 1 plus brand_only_sum |
| `brand_only_sum` | occurrences of the brand name alone, summed over the four corpora |

### Each brand's Wikipedia page views: `web-appendix-analyses/brand-by-brand-and-release-by-release/materials/brand_wikipedia_pageviews.csv`

1 file.

| Column | What it holds |
|---|---|
| `brand` | the brand |
| `is_fictional` | whether the brand is an invented name |
| `wikipedia_article` | the English Wikipedia article read |
| `article_exists` | whether the article exists |
| `total_views` | page views over the months read |
| `avg_monthly` | the mean monthly page views |
| `max_monthly` | the highest month's page views |
| `min_monthly` | the lowest month's page views |
| `months` | the number of months read |

### Published brand values: `web-appendix-analyses/brand-by-brand-and-release-by-release/materials/brand_value_rankings.csv`

1 file.

| Column | What it holds |
|---|---|
| `brand` | the brand |
| `list` | the ranking: Interbrand Best Global Brands or Kantar BrandZ, 2024 or 2025 |
| `appears` | whether the brand appears in that ranking |
| `rank` | its rank there |
| `value_usd_millions` | its brand value there, in millions of US dollars |
| `source_url` | the page read |
| `source_kind` | whether the page is the ranking's own publication or a report of it |
| `source_title` | the page's title |
| `accessed` | the date the page was read |
| `notes` | notes on the reading |

## The Web Appendix's analysis of each piece of information alone (`web-appendix-analyses/each-piece-of-information-alone/`)

### Answers to each piece alone: `web-appendix-analyses/each-piece-of-information-alone/data/each-piece-alone/<model>/<cell>.jsonl.gz`

168 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier; the same id in the set's prompts file |
| `model` | the model, by the name that the run requested |
| `answered_at_utc` | when the response was recorded (UTC, ISO 8601) |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `cell` | the prompt's condition: the names version, the information and the price step, joined by hyphens (for example `crossed-infowarranty-rung0`) |
| `names` | the names version: hidden (every product shown as Product A to E with no brand), original (the invented name on the best product and familiar names on the others) or crossed (a familiar name on the best product and the invented name on a familiar product) |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `paraphrase` | which of the four wordings of the system prompt the prompt used (0 to 3) |
| `best` | the letter under which the best product was shown in this prompt |
| `answer_text` | the model's answer, exactly as returned |
| `letter` | the letter that common/parse_answer.py reads from the answer; empty when it reads none |
| `letter_how` | where the parser found the letter: first-line, body, several (more than one letter, so none is returned) or none |
| `stop_reason` | the provider's reason for ending the answer (end_turn: the model finished; max_tokens: the length limit) |
| `input_tokens` | tokens in the prompt, as the provider counted them |
| `output_tokens` | tokens in the answer, as the provider counted them |
| `model_returned` | the model name that the provider's response reported |
| `route` | how the answer was obtained: the Anthropic Messages API (message batches) for the Claude models, the OpenAI Codex command line for the GPT models |
| `cache_read_input_tokens` | prompt tokens read from the provider's prompt cache |
| `cache_creation_input_tokens` | prompt tokens written to the provider's prompt cache |
| `info` | the information shown: 0 none, 1 all five pieces, or one piece alone: warranty (the warranty row), failure (the first-year failure or return rate row), market (the time-on-the-market row), lab (the lab-testing sentence) or returns (the free-return clause) |
| `rung` | always 0 (the best product's price equals the cheapest other product's) |
| `cached_input_tokens` | prompt tokens served from the cache (OpenAI Codex command line only) |
| `reasoning_output_tokens` | tokens of reasoning before the answer (OpenAI Codex command line only) |
| `seconds` | seconds that the command line took for the answer |
| `error` | a message that the command line recorded during the answer, such as a reconnection when the model was at capacity; empty when there was none |

### Prompts of each piece alone: `web-appendix-analyses/each-piece-of-information-alone/materials/each-piece-alone/prompts.jsonl.gz`

1 file.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier |
| `cell` | the prompt's condition: the names version, the information level and the price step, joined by hyphens (for example `crossed-info0-rung0`) |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `names` | the names version: hidden (every product shown as Product A to E with no brand), original (the invented name on the best product and familiar names on the others) or crossed (a familiar name on the best product and the invented name on a familiar product) |
| `info` | the information shown: 0 none, 1 all five pieces, or one piece alone: warranty (the warranty row), failure (the first-year failure or return rate row), market (the time-on-the-market row), lab (the lab-testing sentence) or returns (the free-return clause) |
| `rung` | always 0 (the best product's price equals the cheapest other product's) |
| `paraphrase` | which of the four wordings of the system prompt the prompt used (0 to 3) |
| `partner_orig` | in the crossed version, the letter (in the table file) of the familiar product whose name the best product takes; empty in the other versions |
| `best` | the letter under which the best product was shown in this prompt |
| `products` | for each letter shown: the product's letter in the table file (orig), the name shown (shown_name), the kind of name shown (kind: hidden, invented or familiar-high, familiar-medium), the price shown, the product's true brand (true_brand) and the kind of that brand (true_kind) |
| `order` | the letters in the order in which the products were shown |
| `system` | the system prompt, as sent |
| `user` | the user's message, as sent: the request and the product listings |

### Answers to the further information: `web-appendix-analyses/each-piece-of-information-alone/data/further-information/<model>/<cell>.jsonl.gz`

190 files.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier; the same id in the set's prompts file |
| `model` | the model, by the name that the run requested |
| `answered_at_utc` | when the response was recorded (UTC, ISO 8601) |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `cell` | the prompt's condition: the names version and the information condition, joined by a hyphen (for example hidden-warranty-row) |
| `names` | the names version: hidden, original or crossed (as in Study 1a), or a cell of the 2 by 2 (no information only): all-familiar (every product under a familiar name), all-invented (every product under an invented name) or familiar-alone (a familiar name on the best product among invented names) |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `paraphrase` | which of the four wordings of the system prompt the prompt used (0 to 3) |
| `best` | the letter under which the best product was shown in this prompt |
| `answer_text` | the model's answer, exactly as returned |
| `letter` | the letter that common/parse_answer.py reads from the answer; empty when it reads none |
| `letter_how` | where the parser found the letter: first-line, body, several (more than one letter, so none is returned) or none |
| `stop_reason` | the provider's reason for ending the answer (end_turn: the model finished; max_tokens: the length limit) |
| `input_tokens` | tokens in the prompt, as the provider counted them |
| `output_tokens` | tokens in the answer, as the provider counted them |
| `model_returned` | the model name that the provider's response reported |
| `route` | how the answer was obtained: the Anthropic Messages API (message batches) for the Claude models, the OpenAI Codex command line for GPT-6.1 Sol and GPT-6.2 Sol |
| `cache_read_input_tokens` | prompt tokens read from the provider's prompt cache |
| `cache_creation_input_tokens` | prompt tokens written to the provider's prompt cache |
| `info` | the information condition: none; <fact>-row or <fact>-sentence for each of the five facts of each piece alone (warranty, failure, market, lab, returns), the fact as a row in every product block or as a sentence in the shopper's request; reviews-50 or reviews-5000 (the best product's review count, with every other product at 500 and every rating at 4.3 stars); or certification, endorsement, origin or sustainability (one further row in every product block) |
| `rung` | always 0 (the best product's price equals the cheapest other product's) |
| `cached_input_tokens` | prompt tokens served from the cache (OpenAI Codex command line only) |
| `reasoning_output_tokens` | tokens of reasoning before the answer (OpenAI Codex command line only) |
| `seconds` | seconds that the command line took for the answer |
| `error` | a message that the command line recorded during the answer, such as a reconnection when the model was at capacity; empty when there was none |

### Prompts of the further information: `web-appendix-analyses/each-piece-of-information-alone/materials/further-information/prompts.jsonl.gz`

1 file.

| Column | What it holds |
|---|---|
| `id` | the prompt's identifier |
| `cell` | the prompt's condition: the names version and the information condition, joined by a hyphen |
| `table` | the product table: sr_<category>_<number>; the ending _dom marks its strictly better version |
| `category` | the product category |
| `trial` | the trial number; each trial has its own display order and letters, the same in every cell |
| `names` | the names version: hidden, original or crossed (as in Study 1a), or a cell of the 2 by 2 (no information only): all-familiar (every product under a familiar name), all-invented (every product under an invented name) or familiar-alone (a familiar name on the best product among invented names) |
| `info` | the information condition: none; <fact>-row or <fact>-sentence for each of the five facts of each piece alone (warranty, failure, market, lab, returns), the fact as a row in every product block or as a sentence in the shopper's request; reviews-50 or reviews-5000 (the best product's review count, with every other product at 500 and every rating at 4.3 stars); or certification, endorsement, origin or sustainability (one further row in every product block) |
| `rung` | always 0 (the best product's price equals the cheapest other product's) |
| `arm` | the information condition (the same as info) |
| `paraphrase` | which of the four wordings of the system prompt the prompt used (0 to 3) |
| `partner_orig` | in the crossed version, the letter (in the table file) of the familiar product whose name the best product takes; empty in the other versions |
| `best` | the letter under which the best product was shown in this prompt |
| `products` | for each letter shown: the product's letter in the table file (orig), the name shown (shown_name), the kind of name shown (kind: hidden, invented or familiar-high, familiar-medium), the price shown, the product's true brand (true_brand) and the kind of that brand (true_kind) |
| `order` | the letters in the order in which the products were shown |
| `system` | the system prompt, as sent |
| `user` | the user's message, as sent: the request and the product listings |
