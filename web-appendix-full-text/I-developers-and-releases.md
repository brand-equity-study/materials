# Machine-Based Brand Equity Between Developers and Across Releases of One Line of Models

Within each of four sets of brands (all familiar brands, the brands of each of two levels of coded familiarity and the
brands in a published ranking), a brand's equity differed between the developers of the 30 models. We grouped the models by developer (Anthropic, 6 models; OpenAI, 9; Google, 10, Gemini and Gemma; the other
developers of models with open weights, 5) and tested whether a brand's equity differs between the groups beyond each
brand's own level and each group's own level, with the sum of the squared interaction terms as the statistic and the
group labels permuted across the 30 models (2,000 permutations). The P value is
.003 over all familiar brands,
.002 over the brands coded as highly
familiar in every table, .009 over the
brands coded as of medium familiarity in every table and
.002 over the brands in a published
ranking.

In the table below, we compare releases of one line of models from one developer, on the same tables: the Claude
5.5 models, which answered the requests of the 30 models in Study 1b, and the others from the 30 models. The two
models of each pair in the table did not see identical prompts: each of the 30 models had its own display orders, letters and wordings,
and the Claude 5.5 models answered prompts drawn from the 30 models' requests, each from one of the 30 in turn. The four
pairs that end at a 5.5 model also cross from a temperature of 1.0 to the developer's default settings. The pairs share
releases (Claude Opus 4.6 to 4.7, 4.7 to 5.5 and 4.6 to 5.5, for example), so they are not independent. In the sampling
column, we give the change expected from sampling alone on identical prompts, which is less than the change expected
with no true difference. In 13 of the 15 pairs, the mean absolute
change in a brand's equity was larger than expected from sampling alone at *p* < .05 without correction, and in
11 after Holm's correction over the pairs, and over all pairs it ranged from
2.3 to 10.6 points. The ordering of the brands between the two
releases of a pair had Spearman correlations from −0.34 to 0.57. The reference row, the
same weights of Gemma 4 31B reached through Google's interface and run on a university's computers, also changed by
more than sampling alone (2.1 against 1.0 points; Spearman
0.69), so a change of access method, prompts and settings changes a brand's equity too. No pair was tested
against that reference, so these comparisons do not separate a new release from such a change. One pair of releases
answered identical prompts: Qwen 2.5 32B and Qwen3 30B, which both answered Study 1b's requests on a
university's computers. Their brand equity changed by 7.35 points on
average, against 5.34
(4.09 to 6.70) from sampling alone (P =
.003), and the two releases ordered the brands with a Spearman
correlation of 0.14. A release's change in
brand equity also is correlated with its change in the overall effect, so much of it may be share that the fictitious top-ranked
product gained
or lost.

We also asked whether a brand with high equity in one release gains more in the next. Over the
15 release pairs (1,095 rows of a brand and a pair), we regressed a brand's
change in equity on its equity in the first release of the pair, with a fixed effect for each pair and standard errors clustered
by brand and by pair. Under sampling error alone, the slope is negative, because a brand measured high by chance tends to be measured
lower the next time; with no true change, that slope is minus the sampling variance of the first release's equity over its variance
across brands, −0.21 here. The slope over the release pairs was
−0.67 (−0.82 to −0.51), and its
difference from the slope of sampling error alone was −0.45
(−0.58 to −0.32, brands resampled). The slope was
−0.63 (−0.77 to −0.48) over Anthropic's
pairs, −0.82 (−1.07 to −0.57) over Google's and
−0.55 (−1.01 to −0.09) over OpenAI's, and
−1.11 in the Qwen pair on identical prompts. Against each group's own sampling error
slope (−0.10 for Anthropic,
−0.32 for Google,
−0.49 for OpenAI and
−0.54 for the Qwen pair), the difference was
−0.52
(−0.74 to −0.32),
−0.50
(−0.66 to −0.28),
−0.05
(−0.30 to 0.29) and
−0.57
(−0.84 to −0.18). Brands
with high equity in one release therefore had lower equity in the next, by more than sampling error predicts, over the
release pairs as a whole, for Anthropic and Google and in the Qwen pair; for OpenAI, the difference could not be told
from sampling error. The benchmark of sampling error does not contain
the variation that different prompts add, so part of this fall may still be sampling error. We cannot use the reference row as
the benchmark, because its slope is positive (0.50,
0.14 to 0.85): the brands with high equity through Google's interface had higher equity
still on the university's computers, a change of scale between the two access methods.

| Pair of releases | Spearman, brands | Mean absolute change | From sampling alone | P |
|:---------------------------------------|--------------:|--------------:|--------------:|--------------:|
| Claude Opus 4.6 to Claude Opus 4.7 | 0.41 | 8.7 | 2.6 | below .001 |
| Claude Opus 4.7 to Claude Opus 5.5 | 0.51 | 7.5 | 2.5 | below .001 |
| Claude Opus 4.6 to Claude Opus 5.5 | 0.46 | 4.6 | 1.7 | below .001 |
| Claude Haiku 4.5 to Claude Haiku 5.5 | 0.30 | 3.0 | 2.4 | .067 |
| Claude Sonnet 4.6 to Claude Sonnet 5.5 | 0.15 | 6.4 | 2.1 | below .001 |
| GPT-4o to GPT-5.4 | 0.22 | 5.9 | 2.8 | below .001 |
| GPT-4o mini to GPT-4.1 mini | −0.24 | 3.5 | 2.1 | .002 |
| GPT-4.1 mini to GPT-5 mini | −0.34 | 2.3 | 1.6 | .030 |
| GPT-5 mini to GPT-5.4 mini | 0.57 | 2.5 | 1.9 | .079 |
| GPT-4.1 nano to GPT-5.4 nano | 0.29 | 7.7 | 5.1 | below .001 |
| Gemini 2.0 Flash to Gemini 2.5 Flash | 0.45 | 3.6 | 2.0 | below .001 |
| Gemini 2.5 Flash to Gemini 3 Flash | 0.33 | 3.1 | 1.8 | .003 |
| Gemini 2.5 Flash-Lite to Gemini 3.1 Flash-Lite | 0.27 | 3.2 | 1.8 | below .001 |
| Gemini 2.5 Pro to Gemini 3.1 Pro | 0.12 | 10.6 | 4.5 | below .001 |
| Gemma 3 27B to Gemma 4 31B | 0.26 | 2.6 | 1.9 | .021 |
| Reference: Gemma 4 31B to Gemma 4 31B (two routes) | 0.69 | 2.1 | 1.0 | below .001 |

Table: Machine-Based Brand Equity Across Releases of One Developer's Models

*Notes:* In each pair, an earlier and a later release of one line are compared on the same tables and conditions, on different prompts: each of the 30 models had its own display orders, letters and wordings, and the Claude 5.5 models answered prompts drawn from the 30 models' requests. The pairs that end at a Claude 5.5 model also differ in their settings. Spearman: the correlation of the 73 brands' equity in the two releases. Mean absolute change: over the brands, in percentage points. From sampling alone: the mean absolute change if both releases chose at the same rates on identical prompts, which understates the change that no true difference would give on different prompts. P: the share of draws in which sampling alone gave a change at least as large (responses resampled, 10,000 draws), without correction for the 15 pairs. The reference is not a release: Gemma 4 31B through Google's interface against the same weights on a university's computers.
