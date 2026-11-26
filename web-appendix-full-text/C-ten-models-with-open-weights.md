# Study 1a on Ten Models With Open Weights

The ten models with open weights of Study 1b (Table W10 of the Web Appendix) answered the requests of Study 1a on a
university's computers, one or two graphics processors for each model, with each model's own default sampling
settings. For each model, we give the share of responses in which it chose the optimal product without brand names and the
effect of the fictitious name (the table below). As a group, these models showed a smaller effect than the four Claude
models, and stating the experience attributes did not reliably lower it: on the rebuilt tables, the change is
−1.7 points (−4.7 to 1.0).
Google's two Gemma models are the exception: stating the experience attributes halved their effect. Llama 3.1 8B and
Marin 8B chose the optimal product without brand names only a little more often than a random choice among five products
would, which leaves little room for an effect.

| Model | Optimal product chosen without brand names (%) | Effect, attributes not stated | Effect, attributes stated | Change |
|:-----------------------------|-------------:|---------------:|---------------:|---------------:|
| Gemma 4 26B A4B (Google) | 80.0 | 12.0 | 4.0 | −8.0 |
| Gemma 4 31B (Google) | 84.3 | 11.0 | 5.3 | −5.7 |
| Qwen3 30B A3B Instruct (Alibaba) | 83.2 | 5.7 | 4.3 | −1.3 |
| Qwen 2.5 32B Instruct (Alibaba) | 64.5 | 5.2 | 2.2 | −3.0 |
| OLMo 3.1 32B Instruct (Allen AI) | 66.7 | 4.3 | 5.3 | 1.0 |
| Phi-4 (Microsoft) | 71.7 | 4.3 | 4.5 | 0.2 |
| Granite 4.1 30B (IBM) | 67.0 | 3.5 | 5.3 | 1.8 |
| Marin 8B Instruct (Marin) | 34.7 | 2.5 | 0.5 | −2.0 |
| Llama 3.1 8B Instruct (Meta) | 25.8 | 1.2 | −0.3 | −1.5 |
| Ministral 3 14B Instruct (Mistral) | 70.0 | 0.2 | 2.0 | 1.8 |
| All ten, tables of Study 1a |  | 5.0 (2.0 to 8.5) | 3.3 (0.9 to 5.7) | −1.7 (−4.7 to 1.0) |
| All ten, tables of Study 1b |  | 3.7 (0.5 to 7.0) | 2.5 (−0.2 to 5.3) | −1.2 (−3.5 to 1.1) |

Table: Study 1a on Ten Models With Open Weights

*Notes:* Rows by model: the 30 tables of Study 1a; the share in the second column is without the experience attributes stated. Effect: the share of responses that chose the optimal product without brand names minus the share with the fictitious name on the optimal product, in percentage points. Change: the effect with the experience attributes stated minus the effect without them. A random choice among five products chooses the optimal product in 20 percent of responses. On the 34 tables of Study 1b (the last row), we use the same measure with each table's top-ranked product. Intervals: a two-way cluster bootstrap over tables and models, 2,000 draws.
