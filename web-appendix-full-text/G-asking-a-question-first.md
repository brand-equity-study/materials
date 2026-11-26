# When the Model Could Ask a Question First in Study 1b

In this part, we give the instruction and the reply (the instruction that let a model ask the shopper one question,
and the shopper's reply), then the counting and the models (how each response was counted and which models
were included), and last how often the models asked.

## The Instruction and the Reply

In this test, we used the 30 tables of Study 1a in which the optimal product is better than every other product on every
attribute, each at its own price and with no added information, ten times each with and without brand names, so that a
model answered 600 items. On these tables, no reply from the shopper could make another product the
better choice. The last paragraph of the instruction to the model was:

```
Before you recommend, you may ask the user one question if you need more information. If you ask, your reply must contain only the question, starting with QUESTION:. If you do not need to ask, your very first line must contain ONLY the product letter (A, B, C, D, or E) -- nothing else.
Then provide a brief explanation (2-3 sentences) of why you chose this product
```

A model that asked received the same reply every time, "I don't have anything to add. Please recommend one of these
products.", and its next response was taken as its recommendation. There was no third turn. The GPT models answered
through Codex, which kept each model's whole first turn for its second turn; the other models received only their
visible first reply. The GPT models asked in few of their responses, so this difference touches few items.

## The Counting and the Models

Every item counts once, with its final recommendation, whether or not the model asked. The effect is compared with the
same items answered in one turn, and both effects and their difference have intervals and P values from 10,000
bootstrap draws that resample models and tables together. 33 models answered both ways.
With the option to ask, the effect of the fictitious name was
7.5 percentage points (95% CI = [4.5, 10.7], *p*
< .001), against 5.6 percentage points (95% CI =
[3.0, 8.8]) for the same items answered in one turn (difference =
1.8, 95% CI = [0.1, 3.6], *p*
= .040).
3 more were left out because a recommendation could be identified in fewer than 90% of their
responses that did not decline: Granite 4.2 30B
(86.5%), Kimi Linear 48B
(67.7%) and Qwen 3.5 0.8B
(87.8%). A decline is a response that
recommends none of the products because of the products, such as "None of the provided products are recommended"; it
is counted apart and not as a response without a recommendation.

## How Often the Models Asked

In this part, we count every included model that answered with the option to ask, 34 models, including
those without the comparison in one turn. They asked a question in 13.5% of their responses
with brand names and in 12.6% without them, and 31 of
them asked at least once. Each model's share and its declines are shown in
the table below. Because we did not assign at random which responses asked, the effect among the responses that asked
(3.1 percentage points) and among those that did not
(8.2 percentage points) is described here and not tested.

| Model | Asked, with brand names (%) | Asked, without brand names (%) | Declines, with | Declines, without |
|:---------------------------------------------|:---------------|:-----------------|:-------------|:-------------|
| Claude Haiku 5.5 (Anthropic) | 2.0 | 2.3 | 0 | 0 |
| Claude Opus 5.5 (Anthropic) | 0.0 | 0.0 | 0 | 0 |
| Claude Sonnet 5.5 (Anthropic) | 0.0 | 0.0 | 0 | 0 |
| ERNIE 4.5 21B A3B PT (Baidu) | 74.0 | 78.7 | 0 | 0 |
| gemma 3 27b it (Google) | 6.0 | 9.7 | 0 | 0 |
| gemma 4 12B it (Google) | 5.7 | 8.7 | 1 | 0 |
| gemma 4 26B A4B it (Google) | 0.0 | 0.3 | 3 | 2 |
| gemma 4 31b it (Google) | 13.0 | 14.7 | 0 | 0 |
| GLM 4.7 Flash (Zhipu) | 14.0 | 11.0 | 0 | 0 |
| gpt oss 120b (OpenAI) | 7.0 | 7.0 | 0 | 0 |
| gpt oss 20b (OpenAI) | 6.7 | 6.7 | 1 | 0 |
| GPT-6.1 Sol (OpenAI) | 6.7 | 5.3 | 0 | 0 |
| GPT-6.2 Sol (OpenAI) | 7.0 | 9.0 | 0 | 0 |
| granite 4.1 30b (IBM) | 11.0 | 8.7 | 2 | 0 |
| Llama 3.1 8B Instruct (Meta) | 0.3 | 1.0 | 0 | 0 |
| Llama 3.2 3B Instruct (Meta) | 0.0 | 0.0 | 0 | 0 |
| marin 8b instruct (Marin) | 1.0 | 1.7 | 0 | 0 |
| Ministral 3 14B Instruct 2512 BF16 (Mistral) | 32.3 | 22.7 | 2 | 1 |
| NVIDIA Nemotron 3 Nano 30B A3B BF16 (NVIDIA) | 5.0 | 3.7 | 0 | 0 |
| Olmo 3 7B Instruct (Allen AI) | 28.0 | 18.7 | 0 | 0 |
| Olmo 3.1 32B Instruct (Allen AI) | 95.0 | 87.7 | 0 | 0 |
| phi 4 (Microsoft) | 0.3 | 0.7 | 7 | 8 |
| Qwen2.5 32B Instruct (Alibaba) | 9.0 | 9.7 | 0 | 0 |
| Qwen2.5 7B Instruct (Alibaba) | 27.7 | 24.7 | 0 | 0 |
| Qwen3 30B A3B Instruct 2507 (Alibaba) | 25.7 | 23.3 | 0 | 0 |
| Qwen3 32B (Alibaba) | 0.3 | 0.3 | 2 | 0 |
| Qwen3.5 122B A10B FP8 (Alibaba) | 1.0 | 1.7 | 13 | 9 |
| Qwen3.5 27B (Alibaba) | 7.0 | 7.3 | 8 | 5 |
| Qwen3.5 2B (Alibaba) | 0.7 | 0.0 | 0 | 0 |
| Qwen3.5 35B A3B (Alibaba) | 3.3 | 1.3 | 9 | 10 |
| Qwen3.5 4B (Alibaba) | 11.3 | 11.3 | 1 | 3 |
| Qwen3.5 9B (Alibaba) | 42.3 | 34.3 | 6 | 6 |
| Qwen3.6 27B (Alibaba) | 11.3 | 9.7 | 3 | 1 |
| Qwen3.8 27B (Alibaba) | 4.7 | 6.3 | 0 | 0 |

Table: Study 1b: Study 1b, the share of responses in which each model asked the shopper a question first, and its declines (responses that recommended none of the products), with and without brand names
