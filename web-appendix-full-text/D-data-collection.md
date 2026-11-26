# The Models' Developers, Access, Dates and Settings

Of Study 1b's models, the 30 that we ran first came from
seven developers: Anthropic, OpenAI, Google,
DeepSeek, Meta, Moonshot AI and Alibaba. Extended thinking means that a model writes out its reasoning before it gives
its answer. We count a model run with extended thinking and the same model run without it as two models. Four models
were run both ways (Claude Haiku 4.5, Claude Sonnet 4.6, GPT-5.4 mini and Gemini 3 Flash), so the
30 models include 26 distinct models.

Most requests went through each developer's own interface for programs, its API. The requests to
5 models went only through OpenRouter, a service that sends each request on to a company
that runs the model. The responses of 5 other models came through more than one access
method: the developer's API, Google's Vertex AI service or OpenRouter (the table below). Each response came
from a new request that contained only the instruction and the shopper's message (Web Appendix
E). Each model gave about 20 responses for each table with brand names and about 20 without them.

## When the Responses Were Collected

The responses of 17 of the 30 models were collected
between February 22 and 27, 2026, and the responses of 12 models on April 22 and 23, 2026. The responses of Claude Haiku 4.5 without
extended thinking were collected in both periods. Every result from these responses applies to these models and these dates.
The GPT models of the other studies answered through Codex CLI: version 0.166.0 produced the responses and codes written
before 12:54 PM Central on November 22, 2026, and version 0.171.0 those written after 12:58 PM.

| Model | Identifier sent | Access | Extended thinking | Collected | With brand names | Without brand names |
|:----------------------|:---------------------------------------------|:-------------------------------|:-------------:|:-----------------|----------:|-----------:|
| Claude Haiku 4.5 | claude-haiku-4-5-20251001 | own API | no | Feb 22 to Apr 22 | 681 | 680 |
| Claude Haiku 4.5 | claude-haiku-4-5-20251001 | own API | yes | Apr 22 to 23 | 681 | 680 |
| Claude Opus 4.6 | claude-opus-4-6 | own API | no | Apr 22 | 681 | 680 |
| Claude Opus 4.7 | claude-opus-4-7 | own API | no | Apr 22 | 681 | 680 |
| Claude Sonnet 4.6 | claude-sonnet-4-6 | own API | no | Feb 24 to 25 | 680 | 680 |
| Claude Sonnet 4.6 | claude-sonnet-4-6 | own API | yes | Apr 22 | 681 | 680 |
| GPT-4.1 mini | gpt-4.1-mini | own API | no | Feb 22 to 27 | 680 | 680 |
| GPT-4.1 nano | gpt-4.1-nano | own API | no | Feb 22 | 680 | 680 |
| GPT-4o | gpt-4o | own API | no | Feb 22 to 23 | 680 | 680 |
| GPT-4o mini | gpt-4o-mini | own API | no | Feb 22 to 27 | 680 | 680 |
| GPT-5 mini | gpt-5-mini | own API | no | Feb 22 to 27 | 680 | 680 |
| GPT-5.4 | gpt-5.4-2026-03-05 | own API | no | Apr 22 to 23 | 681 | 680 |
| GPT-5.4 mini | gpt-5.4-mini-2026-03-17 | own API | no | Apr 22 to 23 | 681 | 680 |
| GPT-5.4 mini | gpt-5.4-mini-2026-03-17 | own API | yes | Apr 22 to 23 | 681 | 680 |
| GPT-5.4 nano | gpt-5.4-nano-2026-03-17 | own API | no | Apr 22 to 23 | 681 | 680 |
| Gemini 2.0 Flash | gemini-2.0-flash | own API | no | Feb 22 | 680 | 680 |
| Gemini 2.5 Flash | gemini-2.5-flash / google/gemini-2.5-flash | own API, Vertex AI, OpenRouter | no | Feb 22 to 27 | 680 | 680 |
| Gemini 2.5 Flash-Lite | gemini-2.5-flash-lite | own API, Vertex AI | no | Feb 23 to 24 | 680 | 680 |
| Gemini 2.5 Pro | gemini-2.5-pro / google/gemini-2.5-pro | own API, Vertex AI, OpenRouter | no | Feb 23 to 27 | 680 | 680 |
| Gemini 3 Flash | gemini-3-flash-preview / google/gemini-3-flash-preview | own API, Vertex AI, OpenRouter | no | Feb 23 to 25 | 680 | 680 |
| Gemini 3 Flash | gemini-3-flash-preview | own API | yes | Apr 22 to 23 | 681 | 680 |
| Gemini 3.1 Flash-Lite | gemini-3.1-flash-lite-preview | own API | no | Apr 22 to 23 | 681 | 680 |
| Gemini 3.1 Pro | gemini-3.1-pro-preview | own API | yes | Apr 22 to 23 | 681 | 680 |
| Gemma 3 27B | gemma-3-27b-it / google/gemma-3-27b-it | own API, OpenRouter | no | Feb 22 to 27 | 680 | 680 |
| Gemma 4 31B | gemma-4-31b-it | own API | no | Apr 22 to 23 | 681 | 680 |
| DeepSeek R1 | deepseek/deepseek-r1 | OpenRouter | both recorded | Feb 22 to 27 | 680 | 680 |
| DeepSeek V3 | deepseek/deepseek-chat-v3-0324 | OpenRouter | no | Feb 22 to 27 | 680 | 680 |
| Llama 3.3 70B | meta-llama/llama-3.3-70b-instruct | OpenRouter | no | Feb 22 to 27 | 680 | 680 |
| Kimi K2 | moonshotai/kimi-k2 | OpenRouter | no | Feb 22 to 25 | 680 | 680 |
| Qwen 2.5 72B | qwen/qwen-2.5-72b-instruct | OpenRouter | no | Feb 22 to 24 | 680 | 680 |

Table: The Models of Study 1b Whose Responses Were Deposited First

*Notes:* The models are grouped by developer (Anthropic, OpenAI, Google, DeepSeek, Meta, Moonshot AI, Alibaba). Identifier sent: every identifier recorded with the model's responses. Access: every access method recorded with the model's responses (the developer's own API, Google's Vertex AI service, or OpenRouter). Extended thinking: whether the request asked for it; DeepSeek R1 is recorded both ways, and the requests that did not ask for it still allowed Gemini 2.5 Pro a short thinking budget and the Gemini 3 models a minimal thinking level. Collected: dates in 2026. With and without brand names: the number of responses in each condition.

## The Settings Recorded With the Responses

The settings recorded with every response of each model are in the table below. The records of the data
collection contain a temperature of 1.0 for every response and the thinking flag of each response, but not the longest
response allowed or the level of reasoning effort. For the February runs, these settings are written in the request code deposited with the
data. In the code, we ask every provider for at most 1,024 output tokens, and GPT-5 mini for at most 2,048. It also sets how
much Google's models think: a budget of 128 tokens for Gemini 2.5 Pro, none for Gemini 2.5 Flash and the minimal level
for Gemini 3 Flash. The deposited code was changed after the February runs, so it does not prove their settings, but
their responses stay within these limits. DeepSeek V3's longest response is exactly
1,024 output tokens, GPT-5 mini's is
1,963, and Gemini 2.5 Pro stopped at exactly
1,020 output tokens in
384 of its 1,360
responses. The April responses were collected with a separate program, through Anthropic's and OpenAI's batch services
and Google's API. The thinking settings of the models added then are known, but no record of the
data collection contains the output limit, the thinking budget or the level of effort. Each request used one of the four wordings of the instruction, and the four were used about equally often.
For each model and condition, the number of different combinations of product order and letters was
96.5 to 98.7 percent of the number of responses.

| Model | Thinking flag | Response length in characters, median (largest) | Wordings 1 to 4, with brand names | Wordings 1 to 4, without brand names | Distinct (%), with, without |
|:-----------------------|:---------|---------------:|------------------------:|------------------------:|-------------:|
| Claude Haiku 4.5 | no | 433 (628) | 160, 187, 152, 182 | 165, 179, 172, 164 | 98.4, 97.4 |
| Claude Haiku 4.5 (thinking) | yes | 421 (632) | 169, 183, 171, 158 | 141, 166, 181, 192 | 97.8, 98.4 |
| Claude Opus 4.6 | no | 531 (1,135) | 162, 172, 163, 184 | 184, 165, 167, 164 | 97.5, 97.6 |
| Claude Opus 4.7 | no | 369 (786) | 196, 158, 171, 156 | 178, 166, 165, 171 | 98.2, 96.9 |
| Claude Sonnet 4.6 | no | 492 (987) | 167, 160, 184, 169 | 202, 153, 173, 152 | 98.5, 96.9 |
| Claude Sonnet 4.6 (thinking) | yes | 500 (788) | 161, 160, 182, 178 | 159, 172, 183, 166 | 97.5, 97.8 |
| GPT-4.1 mini | no | 362 (586) | 167, 170, 169, 174 | 179, 169, 158, 174 | 97.8, 97.8 |
| GPT-4.1 nano | no | 323 (443) | 173, 166, 149, 192 | 172, 168, 176, 164 | 97.9, 97.9 |
| GPT-4o | no | 1 (546) | 150, 176, 188, 166 | 170, 176, 179, 155 | 97.9, 97.4 |
| GPT-4o mini | no | 392 (576) | 186, 174, 170, 150 | 164, 182, 159, 175 | 96.8, 97.5 |
| GPT-5 mini | no | 391 (3,502) | 181, 177, 164, 158 | 168, 173, 157, 182 | 98.1, 97.6 |
| GPT-5.4 | no | 400 (542) | 140, 184, 177, 180 | 170, 159, 175, 176 | 96.9, 98.1 |
| GPT-5.4 mini | no | 340 (469) | 167, 154, 188, 172 | 173, 167, 177, 163 | 97.1, 96.9 |
| GPT-5.4 mini (thinking) | yes | 328 (431) | 187, 168, 150, 176 | 162, 171, 196, 151 | 96.5, 97.9 |
| GPT-5.4 nano | no | 360 (591) | 188, 154, 177, 162 | 175, 158, 180, 167 | 98.2, 97.5 |
| Gemini 2.0 Flash | no | 286 (521) | 155, 191, 173, 161 | 168, 173, 164, 175 | 97.9, 97.8 |
| Gemini 2.5 Flash | no | 297 (544) | 171, 169, 166, 174 | 166, 172, 174, 168 | 98.2, 98.4 |
| Gemini 2.5 Flash-Lite | no | 300 (511) | 179, 146, 182, 173 | 178, 185, 144, 173 | 98.1, 97.2 |
| Gemini 2.5 Pro | no | 369 (553) | 143, 192, 183, 162 | 165, 185, 169, 161 | 98.1, 96.9 |
| Gemini 3 Flash | no | 342 (573) | 178, 156, 190, 156 | 163, 159, 180, 178 | 98.1, 97.8 |
| Gemini 3 Flash (thinking) | yes | 342 (507) | 150, 165, 181, 185 | 146, 176, 164, 194 | 98.7, 97.5 |
| Gemini 3.1 Flash-Lite | no | 331 (468) | 150, 189, 155, 187 | 190, 151, 175, 164 | 97.2, 97.9 |
| Gemini 3.1 Pro (thinking) | yes | 326 (549) | 177, 176, 183, 145 | 163, 173, 166, 178 | 96.8, 98.7 |
| Gemma 3 27B | no | 351 (567) | 187, 159, 160, 174 | 170, 175, 164, 171 | 96.9, 97.9 |
| Gemma 4 31B | no | 270 (422) | 171, 171, 177, 162 | 178, 181, 171, 150 | 97.8, 98.2 |
| DeepSeek R1 | both | 393 (1,558) | 148, 154, 174, 204 | 176, 166, 170, 168 | 96.5, 97.6 |
| DeepSeek V3 | no | 366 (1,432) | 161, 185, 175, 159 | 162, 185, 174, 159 | 97.5, 98.4 |
| Llama 3.3 70B | no | 439 (600) | 193, 146, 175, 166 | 176, 202, 157, 145 | 98.2, 98.4 |
| Kimi K2 | no | 347 (775) | 177, 192, 158, 153 | 165, 173, 177, 165 | 97.4, 97.9 |
| Qwen 2.5 72B | no | 272 (484) | 171, 173, 168, 168 | 168, 171, 161, 180 | 98.1, 97.6 |

Table: Settings Recorded With Each Model's Responses

*Notes:* From the records of the data collection, for the responses of Study 1b's two conditions, with and without brand names (1,360 or 1,361 responses a model). Every response of every model has a recorded temperature of 1.0. DeepSeek R1 has the flag in 289 responses and not in 1,071. Response length: the number of characters in the recorded response, without any thinking trace; GPT-4o answered with the letter alone in most of its responses. Wordings: the number of responses to each of the four wordings of the instruction, identified from the instruction's text. Distinct: the number of different combinations of product order and letters among the model's responses in that condition, as a percentage of the number of those responses.
