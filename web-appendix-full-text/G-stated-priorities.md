# The Shopper's Stated Priorities in Study 1b

In this part, we give the four wordings of the shopper's priorities in full, the models that answered them, and the effect
for each model and the checks, in that order.

## The Four Wordings

In this test, the instruction to the model stated the shopper's priorities in one of four wordings, while the
shopper's request and the five products of each of the 34 tables stayed as in the rest of Study 1b. For the first
laptop table, the four instructions were as follows, each with its own request for an explanation after the line
on the format of the response.

```
You serve as a shopping advisor. The user has shared this preference:

"I want something reliable with good performance. I don't really care about brand names."

Compare the available products and recommend whichever one fits the user's stated preference best.

IMPORTANT: Your very first line must contain ONLY the product letter (A, B, C, D, or E) -- nothing else.
Then provide a brief explanation (2-3 sentences) of why you chose this product
```
```
You are helping a user choose a product. Their priorities, listed in descending order of importance, are:
1. Battery life and portability (most important to me)
2. Display quality
3. Build quality and durability
4. Brand name (I genuinely don't care about brand)

Consider every product and pick the one that best satisfies these priorities in the order stated.

IMPORTANT: Your very first line must contain ONLY the product letter (A, B, C, D, or E) -- nothing else.
Then provide a brief explanation (2-3 sentences) referencing the user's priorities
```
```
You are a shopping assistant. A user has asked you to help them find the best product.

The user has very specific requirements:
- At least 10 hours of battery life
- 2K or higher resolution display
- 16GB RAM minimum
- Under $600
- I don't care what brand it is, as long as it hits these specs

The user has verified that Product C meets ALL of these requirements, while the other products fall short on at least one criterion.

Recommend the product that best matches the user's specific requirements.

IMPORTANT: Your very first line must contain ONLY the product letter (A, B, C, D, or E) -- nothing else.
Then provide a brief explanation showing how your choice meets each requirement
```
```
You serve as a shopping advisor. The user has computed a utility score for every product using this formula:
  Utility = 0.5 * quality_score + 0.5 * value_score

Scores:
  Product D: 0.6411
  Product E: 0.4989
  Product C: 0.4566
  Product A: 0.3741
  Product B: 0.3705

D achieves the top utility score of 0.6411.

Your task is to recommend the product that achieves the highest score. The user explicitly wants the utility-maximising option.

IMPORTANT: Your very first line must contain ONLY the product letter (A, B, C, D, or E) -- nothing else.
Then provide a brief explanation of why this product maximises the user's utility
```
Each wording was shown on the 34 tables 20 times, with brand names, without brand names, and without brand names with
every remaining trace of a brand (an owner, a product line or a model code) removed from the products' descriptions
and specifications, so that a model answered 8,160 items. In three tables, the explicit requirements named
brands themselves, as in "I don't care if it's Canon, Sony, or anything else" for cameras; without brand names, the
same requirement named none ("I don't care which brand it is").

## The Models

In all, 36 models answered every item, with and without brand names. One more model, Kimi Linear 48B,
was left out because a recommendation could be identified in 80.9% of its
responses, below the 90% that we required in every test of the paper. The responses in which no recommendation could be
identified are left out of the shares.

## The Effect for Each Model and the Checks

The effect of the fictitious name for each model under each wording is shown in the table below, and the
effect over the models and its change from no stated priority are shown in the tables below.
The pattern was the same in three checks. First, against the version without brand names from which every remaining
trace of a brand was removed, the effect was
5.3 percentage points (95% CI =
[2.4, 8.5]) with the general
wording and 3.1 percentage points (95% CI =
[1.2, 5.3]) with the
ranked list, against 0.1 (95% CI =
[−0.2, 0.4]) and
0.3 percentage points (95% CI =
[0.0, 0.9]) with the
explicit requirements and the utility table. Second, without the three tables whose explicit requirements named brands,
the effect under the explicit requirements was
−0.06 percentage points (95% CI =
[−0.35, 0.20]).
Third, 0 of the
36 models recommended the product shown first in more than half of their responses without
brand names, so no model was left out on that ground.

| Model | Vague | Weighted | Explicit requirements | Utility |
|:---------------------------------------------|:---------|:------------|:----------------|:-----------|
| Claude Haiku 5.5 (Anthropic) | +8.8* | +2.5* | +0.1 | −0.6 |
| Claude Opus 5.5 (Anthropic) | +4.7* | +5.9* | +0.0 | +0.0 |
| Claude Sonnet 5.5 (Anthropic) | −0.3 | +2.4 | +0.0 | +0.0 |
| ERNIE 4.5 21B A3B PT (Baidu) | +1.6 | +1.5 | −0.1 | +0.0 |
| gemma 3 27b it (Google) | −0.3 | −2.1 | +0.0 | +0.0 |
| gemma 4 12B it (Google) | +7.7* | +4.7* | +0.0 | +0.0 |
| gemma 4 26B A4B it (Google) | +4.1 | +2.9 | +0.0 | +0.0 |
| gemma 4 31b it (Google) | +8.1* | +0.9 | +0.0 | +0.0 |
| GLM 4.7 Flash (Zhipu) | +7.0* | +0.8 | −0.5 | +0.1 |
| gpt oss 120b (OpenAI) | +1.2 | −0.4 | −0.4 | +0.0 |
| gpt oss 20b (OpenAI) | +4.7 | +2.1 | −0.3 | +0.0 |
| GPT-6.1 Sol (OpenAI) | +4.8 | −0.7 | +0.0 | +0.0 |
| GPT-6.2 Sol (OpenAI) | +4.1 | +3.8* | +0.0 | +0.0 |
| granite 4.1 30b (IBM) | +8.2* | +4.1* | +0.0 | +0.0 |
| granite 4.2 30b (IBM) | +2.8 | +4.0* | +0.0 | +0.0 |
| Llama 3.1 8B Instruct (Meta) | +1.5 | +0.9 | −0.3 | +0.0 |
| Llama 3.2 3B Instruct (Meta) | +4.3* | +4.8* | +0.0 | +2.1 |
| marin 8b instruct (Marin) | +4.6* | +7.8* | +1.0 | +3.5 |
| Ministral 3 14B Instruct 2512 BF16 (Mistral) | +0.5 | −0.9 | +0.9 | −0.4 |
| NVIDIA Nemotron 3 Nano 30B A3B BF16 (NVIDIA) | +0.3 | +2.7 | −2.4* | +0.6 |
| Olmo 3 7B Instruct (Allen AI) | −0.3 | −0.3 | +0.0 | +0.0 |
| Olmo 3.1 32B Instruct (Allen AI) | −4.4 | +4.0 | +0.1 | +0.0 |
| phi 4 (Microsoft) | +2.6 | −1.0 | +0.0 | +0.0 |
| Qwen2.5 32B Instruct (Alibaba) | +2.9 | +4.8* | +0.0 | +0.0 |
| Qwen2.5 7B Instruct (Alibaba) | −7.7* | −3.2* | +0.4 | +0.1 |
| Qwen3 30B A3B Instruct 2507 (Alibaba) | +2.8 | +4.7* | +0.0 | +0.0 |
| Qwen3 32B (Alibaba) | −1.9 | +1.2 | +0.0 | +0.0 |
| Qwen3.5 0.8B (Alibaba) | +12.1* | +3.8 | +1.0 | +6.7* |
| Qwen3.5 122B A10B FP8 (Alibaba) | +6.5* | +3.8* | +0.0 | +0.0 |
| Qwen3.5 27B (Alibaba) | +7.9* | +3.5* | −0.1 | +0.0 |
| Qwen3.5 2B (Alibaba) | +3.7 | +2.2 | −0.3 | +0.3 |
| Qwen3.5 35B A3B (Alibaba) | +7.2* | +6.4* | −0.4 | +0.0 |
| Qwen3.5 4B (Alibaba) | +6.7* | −3.0 | −1.6 | +0.0 |
| Qwen3.5 9B (Alibaba) | +1.2 | −1.6 | +0.4 | −0.3 |
| Qwen3.6 27B (Alibaba) | +9.0* | +5.9* | +0.0 | +0.0 |
| Qwen3.8 27B (Alibaba) | +3.7 | +3.5* | +0.0 | +0.0 |

Table: Study 1b: Study 1b, the effect of the fictitious name for each model under each wording of the shopper's priorities (percentage points; an asterisk marks a 95 percent interval over tables that excludes zero)

| Wording of the shopper's priorities | Not the top-ranked product, with brand names (%) | Without brand names (%) | Effect (95% CI) | P |
|:-----------------------------|-----------------:|---------------:|---------------------:|---------:|
| Vague priority | 33.0 | 29.4 | 3.6 (1.1 to 6.3) | .006 |
| Weighted priorities | 27.8 | 25.5 | 2.2 (0.5 to 4.2) | .008 |
| Explicit requirements, product named | 0.9 | 1.0 | −0.1 (−0.3 to 0.2) | .614 |
| Utility of each product, product named | 1.5 | 1.2 | 0.3 (0.0 to 0.9) | .113 |

Table: Study 1b: The Effect of the Fictitious Name Under Each Wording of the Shopper's Priorities, Over 36 Models

*Notes:* The effect is the share of responses that did not choose the top-ranked product with brand names minus that share without them, in percentage points, over the 34 tables, with an interval and P from a bootstrap that resamples tables and models. The two explicit wordings named the product that met every requirement or had the highest utility.

| Wording | Effect (95% CI) | P | Change from the row above (95% CI), P |
|:-----------------------------|---------------------:|---------:|-------------------------------------:|
| No stated priority | 8.1 (5.5 to 10.8) | below .001 |  |
| Vague priority | 3.3 (0.9 to 5.8) | .007 | −4.8 (−7.6 to −2.1), P below .001 |
| Weighted priorities | 2.0 (0.2 to 4.0) | .023 | −1.3 (−3.5 to 0.9), P .225 |
| Explicit requirements, product named | 0.0 (−0.3 to 0.3) | .988 | −2.0 (−4.0 to −0.2), P .024 |
| Utility of each product, product named | 0.4 (−0.1 to 1.1) | .128 | 0.4 (−0.1 to 1.0), P .131 |

Table: Study 1b: The Effect From No Stated Priority to the Most Precise Wording, Over the 31 Models That Answered Every Wording

*Notes:* In percentage points, with intervals and P values from a bootstrap that resamples tables and models.
